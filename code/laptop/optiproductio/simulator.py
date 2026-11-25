"""A pretend production line + UNO, so everything can be tested with no hardware.

ELI5: this is a flight simulator for our line. The "physics" part moves imaginary
boxes down the chute and through S1 -> S2 -> S3, with students (operators) taking
a few seconds at each station. The "firmware" part copies the UNO sketch rule by
rule (gate sequence, buffer time, WIP limit, bottleneck, stall) and prints the exact same text lines
the real UNO prints. The laptop software cannot tell the difference.

Run it on its own:
    python -m optiproductio.simulator --print              # print UNO lines
    python -m optiproductio.simulator --mqtt 127.0.0.1     # act as the NodeMCU gateway
Scenarios: normal, breakdown, shifting, starve, balanced
"""
from __future__ import annotations

import argparse
import random
import threading
import time
from collections import deque

from . import protocol

SCENARIOS = {
    # mean operator time at S1, S2, S3 in ms; S2 is the planned bottleneck
    "normal":    {"proc": [4000, 7000, 4500]},
    "balanced":  {"proc": [5000, 5000, 5000]},
    "breakdown": {"proc": [4000, 7000, 4500], "breakdown": (1, 90_000, 135_000)},  # S2 stuck 45 s
    "shifting":  {"proc": [4000, 7500, 4500], "shift_at": 150_000, "proc2": [4000, 4000, 8500]},
    "starve":    {"proc": [4000, 7000, 4500], "stop_recycle_at": 100_000},
}


class SimLine:
    # copied from the UNO sketch
    GATE_REOPEN_MS = 1000      # S1 must stay empty this long before the gate reopens
    STALL_FACTOR = 2           # busy for 2 x buffer time = STALL
    STATUS_EVERY_MS = 1000

    def __init__(self, emit, scenario="normal", limit=0, buffer_s=10, boxes=8, seed=1):
        self.emit_line = emit
        self.sc = SCENARIOS[scenario]
        self.rng = random.Random(seed)
        self.ms = 0
        self.seq = 0
        self.lock = threading.Lock()
        # physics
        self.chute = boxes                 # boxes waiting behind the gate
        self.slide_until = None            # a released box is sliding down to S1
        self.platform = [None, None, None]  # remaining work (ms) of the box on each station, or None
        self.finished = [False, False, False]
        self.transit = [deque(), deque()]   # boxes between S1->S2 and S2->S3 (ready time)
        self.recycle = deque()              # finished boxes walking back to the chute
        # firmware state
        self.limit = limit
        self.buffer_s = max(1, min(3600, int(buffer_s)))
        self.released = 0
        self.done = 0
        self.fifo = [deque(), deque(), deque()]
        self.active_since = [0, 0, 0]
        self.over = [False] * 3
        self.stall_sent = [False] * 3
        self.frozen = [False] * 3            # breakdown lock: station frozen by a breakdown elsewhere
        self.frozen_at = [0, 0, 0]
        self.lock_mask = 0
        self.s1_armed = True                 # gate opened since the last box reached S1
        self.gate_open = False
        self.s1_empty_since = -self.GATE_REOPEN_MS   # S1 empty at boot: the gate opens at once
        self.hold_sent = False
        self.bn = 0
        self.last_status = 0
        self.ev(0, "BOOT", self.limit)
        self.ev(0, "BUF", self.buffer_s)

    # ---------- firmware copy ----------
    def out(self, msg):
        msg["seq"] = self.seq
        self.seq = (self.seq + 1) % 65536
        self.emit_line(protocol.to_line(msg))

    def ev(self, st, name, val):
        self.out({"type": "E", "ms": self.ms, "st": st, "ev": name, "val": int(val)})

    def wip(self):
        return max(0, self.released - self.done)

    def set_gate(self, open_):
        if open_ == self.gate_open:
            return
        self.gate_open = open_
        if open_:
            self.s1_armed = True
        self.ev(0, "GATE", 1 if open_ else 0)

    def on_in(self, i):
        if self.frozen[i] and not (i == 0 and self.s1_armed and not self.fifo[0]):
            return                           # sensor ignored during a breakdown lock
        self.fifo[i].append(self.ms)
        if len(self.fifo[i]) == 1:
            self.active_since[i] = self.ms
            self.over[i] = False
            self.stall_sent[i] = False
        if self.frozen[i]:
            self.frozen_at[i] = self.ms     # in-flight box landed on a frozen S1: clock starts paused
        if i == 0:
            self.released += 1
            self.s1_armed = False
            self.set_gate(False)
        self.ev(i + 1, "IN", len(self.fifo[i]))

    def active_ms(self, i):
        """Same as the UNO: a frozen station's clock is stopped."""
        return (self.frozen_at[i] if self.frozen[i] else self.ms) - self.active_since[i]

    def on_out(self, i):
        if self.frozen[i]:
            return
        ct = 0
        if self.fifo[i]:
            ct = self.ms - self.fifo[i].popleft()
            if self.stall_sent[i] and self.fifo[i]:     # stuck box left: next box starts fresh
                self.active_since[i] = self.ms
                self.over[i] = False
                self.stall_sent[i] = False
        else:
            self.ev(i + 1, "ERR", 1)
        if not self.fifo[i]:
            self.over[i] = False
            if i == 0:
                self.s1_empty_since = self.ms
        if i == 2:
            self.done += 1
        self.ev(i + 1, "OUT", ct)

    def firmware_tick(self):
        w = self.wip()
        limit_ok = self.limit == 0 or w < self.limit
        s1_free = len(self.fifo[0]) == 0
        s1_settled = s1_free and self.ms - self.s1_empty_since >= self.GATE_REOPEN_MS
        if not limit_ok:
            if not self.hold_sent:
                self.ev(0, "HOLD", w)
                self.hold_sent = True
        else:
            self.hold_sent = False
        if self.gate_open:
            if not limit_ok or not s1_free or self.lock_mask:
                self.set_gate(False)
        elif limit_ok and s1_settled and not self.lock_mask:
            self.set_gate(True)
        # buffer time -> red LED, bottleneck among the red stations, stall
        buf_ms = self.buffer_s * 1000
        bn, best = 0, -1
        for i in range(3):
            if self.fifo[i]:
                d = self.active_ms(i)
                if not self.over[i] and d > buf_ms:
                    self.over[i] = True
                if self.over[i] and d > best:
                    bn, best = i + 1, d
        if bn != self.bn:
            self.bn = bn
            self.ev(0, "BN", bn)
        for i in range(3):
            if self.fifo[i] and not self.stall_sent[i] and self.active_ms(i) > buf_ms * self.STALL_FACTOR:
                self.stall_sent[i] = True
                self.ev(i + 1, "STALL", self.active_ms(i))
        # breakdown lock (copy of updateLock() in the sketch)
        mask = sum(1 << i for i in range(3) if self.fifo[i] and self.stall_sent[i])
        for i in range(3):
            freeze = bool(mask) and not mask & (1 << i)
            if freeze and not self.frozen[i]:
                self.frozen[i], self.frozen_at[i] = True, self.ms
            elif not freeze and self.frozen[i]:
                shift = self.ms - self.frozen_at[i]
                self.frozen[i] = False
                self.active_since[i] += shift
                self.fifo[i] = deque(t + shift for t in self.fifo[i])
        if mask != self.lock_mask:
            self.lock_mask = mask
            self.ev(0, "LOCK", mask)
            if mask:
                self.set_gate(False)
        if self.ms - self.last_status >= self.STATUS_EVERY_MS:
            self.last_status = self.ms
            self.out({"type": "S", "ms": self.ms, "wip": self.wip(), "limit": self.limit,
                      "gate": 1 if self.gate_open else 0, "occ": [len(f) for f in self.fifo],
                      "bn": self.bn, "released": self.released, "done": self.done, "buf": self.buffer_s})

    def leds(self):
        """What the 6 LEDs on the table show: 'green', 'blink' (green blinking) or 'red' per station."""
        return ["green" if not self.fifo[i] else ("red" if self.over[i] else "blink") for i in range(3)]

    def command(self, cmd: str):
        with self.lock:
            c = cmd.strip().upper()
            if c.startswith("L"):
                self.limit = max(0, min(20, int(c[2:] or 0)))
                self.ev(0, "LIMIT", self.limit)
            elif c.startswith("B"):
                self.buffer_s = max(1, min(3600, int(c[2:] or 0)))
                self.ev(0, "BUF", self.buffer_s)
            elif c == "R":
                # a reset with boxes on the table: put them all back in the chute
                n = sum(1 for p in self.platform if p is not None) + sum(len(t) for t in self.transit) + len(self.recycle)
                self.chute += n + (1 if self.slide_until is not None else 0)
                self.platform = [None, None, None]
                self.finished = [False] * 3
                self.transit = [deque(), deque()]
                self.recycle.clear()
                self.slide_until = None
                self.released = self.done = 0
                self.fifo = [deque(), deque(), deque()]
                self.stall_sent = [False] * 3
                self.frozen = [False] * 3
                self.lock_mask = 0
                self.over = [False] * 3
                self.s1_empty_since = self.ms - self.GATE_REOPEN_MS
                self.bn = 0
                self.hold_sent = False
                self.ev(0, "RESET", 0)
            elif c == "P":
                self.ev(0, "PONG", self.limit)

    # ---------- physics ----------
    def proc_time(self, i):
        sc = self.sc
        base = sc["proc"]
        if "shift_at" in sc and self.ms >= sc["shift_at"]:
            base = sc["proc2"]
        return base[i] * self.rng.uniform(0.85, 1.15)

    def physics_tick(self, dt):
        sc = self.sc
        # chute: gate open and a box waiting -> it slides to S1 in 0.6 s
        if self.gate_open and self.chute > 0 and self.slide_until is None and self.platform[0] is None:
            self.chute -= 1
            self.slide_until = self.ms + 600
        if self.slide_until is not None and self.ms >= self.slide_until:
            self.slide_until = None
            self.platform[0] = self.proc_time(0)
            self.finished[0] = False
            self.on_in(0)
        for i in range(3):
            if self.frozen[i]:
                continue          # line locked by a breakdown elsewhere: nobody moves boxes here
            # work on the box
            if self.platform[i] is not None and not self.finished[i]:
                bd = sc.get("breakdown")
                if not (bd and bd[0] == i and bd[1] <= self.ms < bd[2]):
                    self.platform[i] -= dt
                if self.platform[i] <= 0:
                    self.finished[i] = True
                    self.platform[i] = self.ms + self.rng.uniform(200, 700)  # time to push it off
            elif self.platform[i] is not None and self.finished[i] and self.ms >= self.platform[i]:
                self.platform[i] = None
                self.finished[i] = False
                self.on_out(i)
                if i < 2:
                    self.transit[i].append(self.ms + self.rng.uniform(1200, 2000))
                else:
                    stop = sc.get("stop_recycle_at")
                    if not (stop and self.ms >= stop):
                        self.recycle.append(self.ms + 6000)
            # take the next box from the buffer in front of S2/S3
            if i > 0 and self.platform[i] is None and self.transit[i - 1] and self.transit[i - 1][0] <= self.ms:
                self.transit[i - 1].popleft()
                self.platform[i] = self.proc_time(i)
                self.finished[i] = False
                self.on_in(i)
        while self.recycle and self.recycle[0] <= self.ms:
            self.recycle.popleft()
            self.chute += 1

    def step(self, dt=50):
        with self.lock:
            self.ms += dt
            self.physics_tick(dt)
            self.firmware_tick()

    def run_for(self, ms, dt=50):
        for _ in range(int(ms // dt)):
            self.step(dt)


def main():
    ap = argparse.ArgumentParser(description="OptiProductio line simulator")
    ap.add_argument("--scenario", default="normal", choices=SCENARIOS)
    ap.add_argument("--limit", type=int, default=0, help="0 = gate follows S1 only; n > 0 = CONWIP limit")
    ap.add_argument("--buffer", type=int, default=10, help="buffer time in seconds")
    ap.add_argument("--speed", type=float, default=1.0, help="2 = twice as fast as real time")
    ap.add_argument("--print", action="store_true", help="print the UNO lines")
    ap.add_argument("--mqtt", metavar="BROKER_IP", help="publish like the NodeMCU gateway")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--root", default="rvce/idealab/line1")
    a = ap.parse_args()

    client = None
    sim = None

    def emit(line):
        if a.print or not a.mqtt:
            print(line, flush=True)
        if client is not None:
            msg = protocol.parse_line(line)
            topic, payload, retain = protocol.to_mqtt(msg, a.root)
            client.publish(topic, payload, retain=retain)

    if a.mqtt:
        import paho.mqtt.client as mqtt
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="optiproductio-sim-gw")
        client.will_set(f"{a.root}/gateway/state", "offline", retain=True)

        def on_connect(c, u, f, rc, p=None):
            c.publish(f"{a.root}/gateway/state", "online", retain=True)
            c.subscribe(f"{a.root}/cmd/#", qos=1)

        def on_message(c, u, m):
            t = m.topic
            if t.endswith("/cmd/wip_limit"):
                sim.command("L," + m.payload.decode())
            elif t.endswith("/cmd/buffer"):
                sim.command("B," + m.payload.decode())
            elif t.endswith("/cmd/reset"):
                sim.command("R")
            elif t.endswith("/cmd/ping"):
                sim.command("P")

        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(a.mqtt, a.port, keepalive=10)
        client.loop_start()
        print(f"Simulated gateway publishing to {a.mqtt}:{a.port} under {a.root}/ (Ctrl+C to stop)")

    sim = SimLine(emit, a.scenario, a.limit, a.buffer)
    dt = 50
    try:
        while True:
            sim.step(dt)
            time.sleep(dt / 1000 / a.speed)
    except KeyboardInterrupt:
        pass
    finally:
        if client is not None:
            client.publish(f"{a.root}/gateway/state", "offline", retain=True)
            client.loop_stop()


if __name__ == "__main__":
    main()
