"""The brain on the laptop: takes every message, files it in the historian,
splits time into sessions and runs, and builds the dashboard snapshot."""
from __future__ import annotations

import json
import os
import threading
import time

from . import analytics
from .historian import Historian


def run_label(limit: int) -> str:
    return "S1 gate, no WIP limit" if limit == 0 else f"CONWIP, WIP limit {limit}"


class Engine:
    def __init__(self, source, db_path: str, settings_path: str | None = None):
        self.source = source
        self.hist = Historian(db_path)
        self.settings_path = settings_path
        self.cfg = dict(analytics.DEFAULT_CFG)
        if settings_path and os.path.exists(settings_path):
            try:
                with open(settings_path) as f:
                    self.cfg.update(json.load(f))
            except ValueError:
                pass
        self.lock = threading.RLock()
        self.session_id = None
        self.session = None
        self.run = None
        self.status = None
        self.last_ms = None
        self.last_mono = None
        self.last_sample_ms = -10_000
        self.expected_seq = None
        self.lost = 0
        self.pending_limit = None
        self.pending_buffer = None
        self._cache = (0, None)
        self._run_cache = {}

    # ---------- incoming ----------
    def start(self):
        self.source.start(self.on_msg)

    def on_msg(self, m: dict):
        with self.lock:
            self._track_seq(m)
            if self.last_ms is not None and m["ms"] + 5000 < self.last_ms:
                self._close_session()                 # UNO clock went back: it rebooted
            self.last_ms, self.last_mono = m["ms"], time.monotonic()

            if m["type"] == "E" and m["ev"] in ("BOOT", "RESET"):
                prev_limit = (self.status or {}).get("limit", self.run["wip_limit"] if self.run else 0)
                self._close_session()
                limit = m["val"] if m["ev"] == "BOOT" else prev_limit
                self._open_session(m["ms"], {"occ": [0, 0, 0], "released": 0, "done": 0}, limit)
            elif self.session_id is None:
                if m["type"] != "S":
                    return                            # joined mid-run: wait for a status line
                self._open_session(m["ms"], {"occ": m["occ"], "released": m["released"],
                                             "done": m["done"]}, m["limit"])

            if m["type"] == "E":
                self.hist.add_event(self.session_id, m, self.source.kind)
                if m["ev"] == "LIMIT":
                    self.pending_limit = None
                    self._new_run(m["ms"], m["val"])
                elif m["ev"] == "BUF":
                    self.pending_buffer = None
                    self._cache = (0, None)
            else:
                self.status = m
                if m["ms"] - self.last_sample_ms >= 1000:
                    self.last_sample_ms = m["ms"]
                    self.hist.add_sample(self.session_id, m)

    def _track_seq(self, m):
        if self.expected_seq is not None and m["seq"] != self.expected_seq:
            gap = (m["seq"] - self.expected_seq) % 65536
            if 0 < gap < 1000:
                self.lost += gap
        self.expected_seq = (m["seq"] + 1) % 65536

    def _open_session(self, start_ms, init, limit):
        self.session_id = self.hist.new_session(start_ms, init, self.source.kind)
        self.session = {"id": self.session_id, "start_ms": start_ms, "init": init}
        self._new_run(start_ms, limit)

    def _close_session(self):
        if self.run and self.last_ms is not None:
            self.hist.end_run(self.run["id"], self.last_ms)
        self.session_id = self.session = self.run = None
        self.status = None
        self.last_sample_ms = -10_000

    def _new_run(self, start_ms, limit, label=None):
        if self.run:
            self.hist.end_run(self.run["id"], start_ms)
            self._run_cache.pop(self.run["id"], None)
        rid = self.hist.new_run(self.session_id, label or run_label(limit), limit, start_ms)
        self.run = self.hist.run(rid)
        self._cache = (0, None)

    # ---------- commands from the dashboard ----------
    def now_ms(self):
        if self.last_ms is None:
            return None
        return self.last_ms + int(min(1.5, time.monotonic() - self.last_mono) * 1000)

    def set_limit(self, n: int):
        n = max(0, min(20, int(n)))
        self.pending_limit = n
        self.hist.add_command(f"L,{n}")
        self.source.send(f"L,{n}")      # the run changes when the UNO confirms with a LIMIT event

    def set_buffer(self, s: int):
        """Buffer time in seconds: how long a station may stay busy before its LED turns red."""
        s = max(1, min(3600, int(s)))
        self.pending_buffer = s
        self.hist.add_command(f"B,{s}")
        self.source.send(f"B,{s}")      # the UNO saves it in EEPROM and answers with a BUF event

    def reset_line(self):
        self.hist.add_command("R")
        self.source.send("R")

    def ping(self):
        self.source.send("P")

    def new_run(self, label=None):
        with self.lock:
            if self.session_id is None:
                return False
            limit = (self.status or {}).get("limit", self.run["wip_limit"] if self.run else 0)
            self._new_run(self.now_ms(), limit, label or run_label(limit))
            return True

    def mark_scrap(self):
        with self.lock:
            if self.session_id is None:
                return False
            self.hist.add_event(self.session_id, {"seq": -1, "ms": self.now_ms(), "st": 3, "ev": "SCRAP", "val": 1},
                                "operator")
            self._cache = (0, None)
            return True

    def update_cfg(self, new: dict):
        for k in ("ideal_ct_s", "down_after_s", "timeline_s"):
            if k in new:
                self.cfg[k] = float(new[k])
        if self.settings_path:
            with open(self.settings_path, "w") as f:
                json.dump(self.cfg, f, indent=2)
        self._cache = (0, None)
        self._run_cache.clear()

    # ---------- outgoing ----------
    def _compute(self, run, t1):
        sess = self.hist.session(run["session_id"])
        ev = self.hist.events(run["session_id"], t1)
        cfg = dict(self.cfg)
        if self.status and self.status.get("buf") is not None:
            cfg["buffer_s"] = self.status["buf"]   # used only if no BUF event is in the history
        return analytics.compute(ev, sess["init"], sess["start_ms"], run["start_ms"], t1, cfg)

    def snapshot(self):
        with self.lock:
            now = time.time()
            if self._cache[1] is not None and now - self._cache[0] < 0.7:
                return self._cache[1]
            snap = {"title": "Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection",
                    "project": "OptiProductio", "source": self.source.describe(),
                    "lost_lines": self.lost, "pending_limit": self.pending_limit,
                    "pending_buffer": self.pending_buffer,
                    "status": self.status, "run": self.run, "kpi": None, "events": [], "cfg": self.cfg}
            if self.run and self.now_ms() is not None:
                snap["kpi"] = self._compute(self.run, self.now_ms())
                snap["events"] = self.hist.recent_events(self.session_id, 14)
            self._cache = (now, snap)
            return snap

    def run_summaries(self):
        out = []
        with self.lock:
            for r in self.hist.runs():
                live = self.run is not None and r["id"] == self.run["id"]
                if r["end_ms"] is None and not live:
                    continue            # a run whose session ended without a clean close
                if live:
                    k = self._compute(r, self.now_ms())
                elif r["id"] in self._run_cache:
                    k = self._run_cache[r["id"]]
                else:
                    k = self._compute(r, r["end_ms"])
                    self._run_cache[r["id"]] = k
                if k["pbt_s"] < 5:
                    continue
                st = k["stations"]
                out.append({
                    "id": r["id"], "label": r["label"], "limit": r["wip_limit"], "live": live,
                    "started": r["started_wall"], "duration_s": k["pbt_s"], "produced": k["produced"],
                    "good": k["good"], "th_per_min": k["th_per_min"], "wip_avg": k["wip_avg"],
                    "lead_avg_s": k["lead_avg_s"], "little_rhs": k["little_rhs"], "oee": k["oee"],
                    "availability": k["availability"], "effectiveness": k["effectiveness"],
                    "quality": k["quality"], "adot_s": k["adot_s"], "bn_overall": k["bn_overall"],
                    "bn_pct": [round(s["sole_pct"] + s["shift_pct"], 1) for s in st],
                    "ct_avg": [s["ct_avg_s"] for s in st], "holds": k["holds"],
                })
        return out

    def export_events_csv(self, run_id: int) -> str:
        r = self.hist.run(run_id)
        if not r:
            return ""
        t1 = r["end_ms"] if r["end_ms"] is not None else (self.now_ms() or 0)
        rows = [e for e in self.hist.events(r["session_id"], t1) if e["ms"] >= r["start_ms"]]
        lines = ["run_id,session_id,seq,uno_ms,station,event,value,wall_time,source"]
        for e in rows:
            lines.append(f"{run_id},{e['session_id']},{e['seq']},{e['ms']},{e['st']},{e['ev']},{e['val']},"
                         f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e['wall']))},{e['source']}")
        return "\n".join(lines) + "\n"
