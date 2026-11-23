"""SQLite historian: the line's diary. Every event goes in with a timestamp.

Tables
  sessions  one per UNO power-on or reset (the UNO clock `ms` restarts there)
  runs      a time slice of a session with one WIP limit (for A/B tests: L=2 vs L=4 ...)
  events    every E line (and operator entries such as SCRAP)
  samples   the S status line, at most one per second (WIP over time)
  commands  what the dashboard sent to the line
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY, started_wall REAL, start_ms INTEGER,
  init_json TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY, session_id INTEGER, label TEXT, wip_limit INTEGER,
  start_ms INTEGER, end_ms INTEGER, started_wall REAL, ended_wall REAL);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY, session_id INTEGER, seq INTEGER, ms INTEGER,
  st INTEGER, ev TEXT, val INTEGER, wall REAL, source TEXT);
CREATE INDEX IF NOT EXISTS ix_events_session ON events(session_id, ms);
CREATE TABLE IF NOT EXISTS samples (
  id INTEGER PRIMARY KEY, session_id INTEGER, ms INTEGER, wip INTEGER, wip_limit INTEGER,
  gate INTEGER, occ1 INTEGER, occ2 INTEGER, occ3 INTEGER, bn INTEGER,
  released INTEGER, done INTEGER, wall REAL);
CREATE INDEX IF NOT EXISTS ix_samples_session ON samples(session_id, ms);
CREATE TABLE IF NOT EXISTS commands (id INTEGER PRIMARY KEY, wall REAL, cmd TEXT, source TEXT);
"""


class Historian:
    def __init__(self, path: str):
        self.path = path
        self.lock = threading.Lock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        if path != ":memory:":
            self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.db.commit()

    # ---------- writes ----------
    def _exec(self, sql, args=()):
        with self.lock:
            cur = self.db.execute(sql, args)
            self.db.commit()
            return cur.lastrowid

    def new_session(self, start_ms: int, init: dict, source: str) -> int:
        return self._exec("INSERT INTO sessions(started_wall,start_ms,init_json,source) VALUES(?,?,?,?)",
                          (time.time(), start_ms, json.dumps(init), source))

    def new_run(self, session_id: int, label: str, wip_limit: int, start_ms: int) -> int:
        return self._exec("INSERT INTO runs(session_id,label,wip_limit,start_ms,started_wall) VALUES(?,?,?,?,?)",
                          (session_id, label, wip_limit, start_ms, time.time()))

    def end_run(self, run_id: int, end_ms: int):
        self._exec("UPDATE runs SET end_ms=?, ended_wall=? WHERE id=? AND end_ms IS NULL",
                   (end_ms, time.time(), run_id))

    def add_event(self, session_id: int, m: dict, source: str):
        self._exec("INSERT INTO events(session_id,seq,ms,st,ev,val,wall,source) VALUES(?,?,?,?,?,?,?,?)",
                   (session_id, m.get("seq", -1), m["ms"], m["st"], m["ev"], m["val"], time.time(), source))

    def add_sample(self, session_id: int, m: dict):
        o = m["occ"]
        self._exec("INSERT INTO samples(session_id,ms,wip,wip_limit,gate,occ1,occ2,occ3,bn,released,done,wall)"
                   " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                   (session_id, m["ms"], m["wip"], m["limit"], m["gate"], o[0], o[1], o[2], m["bn"],
                    m["released"], m["done"], time.time()))

    def add_command(self, cmd: str, source: str = "dashboard"):
        self._exec("INSERT INTO commands(wall,cmd,source) VALUES(?,?,?)", (time.time(), cmd, source))

    # ---------- reads ----------
    def _all(self, sql, args=()):
        with self.lock:
            return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def session(self, session_id: int) -> dict | None:
        r = self._all("SELECT * FROM sessions WHERE id=?", (session_id,))
        if not r:
            return None
        r[0]["init"] = json.loads(r[0]["init_json"] or "{}")
        return r[0]

    def events(self, session_id: int, until_ms: int | None = None) -> list[dict]:
        if until_ms is None:
            return self._all("SELECT * FROM events WHERE session_id=? ORDER BY ms, id", (session_id,))
        return self._all("SELECT * FROM events WHERE session_id=? AND ms<=? ORDER BY ms, id",
                         (session_id, until_ms))

    def recent_events(self, session_id: int, n: int = 20) -> list[dict]:
        return self._all("SELECT * FROM events WHERE session_id=? ORDER BY id DESC LIMIT ?", (session_id, n))

    def runs(self) -> list[dict]:
        return self._all("SELECT * FROM runs ORDER BY id")

    def run(self, run_id: int) -> dict | None:
        r = self._all("SELECT * FROM runs WHERE id=?", (run_id,))
        return r[0] if r else None
