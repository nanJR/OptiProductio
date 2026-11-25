"""Automatic checks that need no hardware. Run:  python -m pytest -q   (from code/laptop)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optiproductio import analytics, protocol  # noqa: E402
from optiproductio.engine import Engine  # noqa: E402
from optiproductio.server import make_app  # noqa: E402
from optiproductio.simulator import SimLine  # noqa: E402


class FakeSource:
    kind = "sim"

    def __init__(self):
        self.sim = None
        self.sent = []

    def describe(self):
        return {"kind": "sim", "connected": True}

    def start(self, cb):
        pass

    def send(self, cmd):
        self.sent.append(cmd)
        if self.sim:
            self.sim.command(cmd)


def make(scenario="normal", limit=4, buffer_s=10):
    src = FakeSource()
    eng = Engine(src, ":memory:")
    sim = SimLine(lambda line: eng.on_msg(protocol.parse_line(line)), scenario, limit, buffer_s)
    src.sim = sim
    return eng, sim


# ---------- protocol ----------
def test_parse_event_and_status():
    e = protocol.parse_line("E,12,34567,2,IN,1")
    assert e == {"type": "E", "seq": 12, "ms": 34567, "st": 2, "ev": "IN", "val": 1}
    s = protocol.parse_line("S,13,35000,3,4,0,1,0,1,1,20,17")
    assert s["wip"] == 3 and s["occ"] == [1, 0, 1] and s["done"] == 17
    assert s["buf"] is None and protocol.to_line(s) == "S,13,35000,3,4,0,1,0,1,1,20,17"
    s3 = protocol.parse_line("S,13,35000,3,0,0,1,0,1,1,20,17,15")   # firmware v3: buffer time last
    assert s3["buf"] == 15 and protocol.to_line(s3) == "S,13,35000,3,0,0,1,0,1,1,20,17,15"
    assert protocol.parse_line("E,1,2,0,BUF,15")["ev"] == "BUF"


def test_garbage_is_ignored():
    for bad in ["", "# comment", "E,1,2", "E,1,2,3,NOPE,4", "S,a,b,c", "hello"]:
        assert protocol.parse_line(bad) is None


def test_mqtt_round_trip():
    root = "rvce/idealab/line1"
    for line in ["E,5,1000,3,OUT,4200", "E,6,1100,0,GATE,1", "S,7,2000,2,4,1,1,0,1,1,9,7",
                 "S,7,2000,2,0,1,1,0,1,1,9,7,12", "E,8,2100,0,BUF,12"]:
        m = protocol.parse_line(line)
        topic, payload, _ = protocol.to_mqtt(m, root)
        assert protocol.from_mqtt(topic, payload, root) == m
    assert protocol.to_mqtt(protocol.parse_line("E,5,1,2,IN,1"), root)[0] == root + "/s2/event"
    assert protocol.command_to_mqtt("L,3", root) == (root + "/cmd/wip_limit", "3")
    assert protocol.command_to_mqtt("B,15", root) == (root + "/cmd/buffer", "15")


# ---------- Roser active-period method on a hand-made example ----------
def test_roser_sole_and_shifting():
    # S1 active 0-10 s, S2 active 5-30 s, S3 active 25-28 s
    periods = [[(0, 10_000, False)], [(5_000, 30_000, False)], [(25_000, 28_000, False)]]
    r = analytics.roser(periods, 0, 30_000, step_ms=100)
    # 0-5 s only S1 is active: S1 is the sole bottleneck.
    # 5-10 s S1 and S2 overlap while the bottleneck passes to S2: shifting for both.
    # 10-30 s S2's 25 s period is the longest: S2 sole (S3's 3 s period never wins).
    assert abs(r["sole_ms"][0] - 5_000) < 200
    assert abs(r["shift_ms"][0] - 5_000) < 200
    assert abs(r["shift_ms"][1] - 5_000) < 200
    assert abs(r["sole_ms"][1] - 20_000) < 300
    assert r["sole_ms"][2] == 0


# ---------- whole system with the simulator ----------
def test_normal_run_finds_s2_and_respects_limit():
    eng, sim = make("normal", 4)
    max_wip = 0
    for _ in range(600):
        sim.run_for(1000)
        max_wip = max(max_wip, sim.wip())
    k = eng.snapshot()["kpi"]
    assert max_wip <= 4, "CONWIP gate let WIP go over the limit"
    assert k["bn_overall"] == 2 and k["bn_avg_method"] == 2
    assert k["produced"] > 60
    # Little's law within 15 %
    assert abs(k["little_rhs"] - k["wip_avg"]) / k["wip_avg"] < 0.15
    assert 0.9 < k["availability"] <= 1.0


def test_breakdown_shows_in_pareto():
    eng, sim = make("breakdown", 4)
    sim.run_for(200_000)
    k = eng.snapshot()["kpi"]
    reasons = [p["reason"] for p in k["pareto"]]
    assert "Breakdown suspected at S2" in reasons
    ev = eng.hist.events(eng.session_id)
    assert any(e["ev"] == "STALL" and e["st"] == 2 for e in ev)


def test_starve_scenario():
    eng, sim = make("starve", 4)
    sim.run_for(250_000)
    k = eng.snapshot()["kpi"]
    assert k["pareto"][0]["reason"].startswith("Starved")


def test_limit_change_starts_new_run_and_lowers_wip():
    eng, sim = make("normal", 0)
    sim.run_for(240_000)
    eng.set_limit(2)
    sim.run_for(240_000)
    runs = eng.run_summaries()
    assert [r["limit"] for r in runs] == [0, 2]
    assert runs[1]["wip_avg"] < runs[0]["wip_avg"]
    assert runs[1]["lead_avg_s"] < runs[0]["lead_avg_s"]


def test_reset_starts_new_session():
    eng, sim = make("normal", 4)
    sim.run_for(60_000)
    first = eng.session_id
    eng.reset_line()
    sim.run_for(5_000)
    assert eng.session_id != first
    assert eng.snapshot()["kpi"]["produced"] <= 1


def test_server_endpoints():
    eng, sim = make("normal", 4)
    sim.run_for(60_000)
    app = make_app(eng)
    c = app.test_client()
    assert c.get("/").status_code == 200
    assert c.get("/report").status_code == 200
    d = c.get("/api/state").get_json()
    assert d["title"] == "Arduino-Based Real-Time WIP Monitoring and Bottleneck Detection"
    assert d["kpi"]["produced"] >= 1
    assert c.post("/api/scrap").get_json()["ok"]
    assert c.post("/api/limit", json={"limit": 3}).get_json()["limit"] == 3
    assert eng.run["wip_limit"] == 3
    csv = c.get(f"/api/export/{eng.run['id']}.csv").data.decode()
    assert csv.startswith("run_id,")


# ---------- new in v3: gate sequence, buffer time, LED rule ----------
def test_gate_opens_at_start_and_one_box_at_s1():
    """Limit 0: gate opens at boot, closes when a box reaches S1, reopens when S1 is empty."""
    lines = []
    sim = SimLine(lines.append, "normal", 0, 10)
    sim.step(50)
    assert sim.gate_open, "gate should open once right after boot"
    for _ in range(4000):                                # 200 s
        sim.step(50)
        assert len(sim.fifo[0]) <= 1, "more than one box on S1"
        if sim.fifo[0]:
            assert not sim.gate_open, "gate open while a box is on S1"
    ev = [protocol.parse_line(x) for x in lines]
    ev = [e for e in ev if e and e["type"] == "E"]
    # every S1 IN is followed by a gate close, and every reopen comes after an S1 OUT
    seq = [(e["ev"], e["st"], e["val"]) for e in ev if e["ev"] in ("GATE",) or (e["ev"] in ("IN", "OUT") and e["st"] == 1)]
    opens = [i for i, x in enumerate(seq) if x == ("GATE", 0, 1)]
    for i in opens[1:]:
        assert ("OUT", 1) == seq[i - 1][:2], "gate reopened before S1 was empty"
    assert sum(1 for e in ev if e["ev"] == "HOLD") == 0, "no WIP-limit holds when the limit is off"


def test_led_rule_follows_buffer_time():
    sim = SimLine(lambda _l: None, "breakdown", 0, 5)   # S2 stuck from 90 s to 135 s
    seen = {"green", "blink", "red"}
    got = set()
    t_box = None
    for _ in range(3000):                                # 150 s
        sim.step(50)
        leds = sim.leds()
        got.update(leds)
        busy = sim.ms - sim.active_since[1] if sim.fifo[1] else None
        if busy is not None:
            if busy <= 5000:
                assert leds[1] == "blink", "red before the buffer time ran out"
            elif busy > 5100:
                assert leds[1] == "red"
                t_box = t_box or sim.ms
        else:
            assert leds[1] == "green"
    assert got == seen and t_box is not None


def test_buffer_command_round_trip_and_bottleneck_waits_for_buffer():
    eng, sim = make("normal", 0, 30)
    sim.run_for(60_000)
    assert eng.snapshot()["status"]["buf"] == 30
    eng.set_buffer(4)
    sim.run_for(2_000)
    snap = eng.snapshot()
    assert snap["status"]["buf"] == 4 and snap["pending_buffer"] is None
    assert snap["kpi"]["cfg"]["buffer_s"] == 4
    # any live bottleneck the laptop names must be over the buffer time
    for _ in range(60):
        sim.run_for(1000)
        eng._cache = (0, None)
        k = eng.snapshot()["kpi"]
        if k["bn_now"]:
            assert k["stations"][k["bn_now"] - 1]["active_now_s"] > 4
        for st in k["stations"]:
            assert st["led"] == ("green" if st["occ"] == 0 else ("red" if st["active_now_s"] > 4 else "blink"))


def test_server_buffer_endpoint():
    eng, sim = make("normal", 0, 10)
    sim.run_for(5_000)
    c = make_app(eng).test_client()
    assert c.post("/api/buffer", json={"buffer_s": 20}).get_json()["buffer_s"] == 20
    assert eng.snapshot()["status"]["buf"] in (10, 20)
    sim.run_for(1_500)
    assert eng.status["buf"] == 20


# ---------- new in v3.1: breakdown lock, good-part rule, all bottlenecks listed ----------
def test_breakdown_lock_freezes_other_stations():
    """S2 stuck: once it STALLs, no IN/OUT from S1 or S3 until the stuck box leaves S2."""
    eng, sim = make("breakdown", 0, 10)
    sim.run_for(200_000)
    ev = eng.hist.events(eng.session_id)
    locks = [e for e in ev if e["ev"] == "LOCK"]
    assert locks and locks[0]["val"] == 2 and locks[-1]["val"] == 0
    t_on = locks[0]["ms"]
    t_off = next(e["ms"] for e in locks if e["val"] == 0)
    during = [e for e in ev if t_on < e["ms"] < t_off and e["ev"] in ("IN", "OUT")]
    # only exception: one box the gate had already let go before the lock lands on S1 and is counted
    in_flight = [e for e in during if e["st"] == 1 and e["ev"] == "IN" and e["ms"] - t_on < 1000]
    assert len(in_flight) <= 1
    assert all(e["st"] == 2 or e in in_flight for e in during), "a frozen station's sensor was used during the lock"
    assert not any(e["ev"] == "GATE" and e["val"] == 1 and t_on < e["ms"] < t_off for e in ev), "gate opened during lock"
    assert not any(e["ev"] == "STALL" and e["st"] != 2 for e in ev), "frozen station wrongly declared broken"


def test_good_parts_exclude_breakdown_box_only():
    eng, sim = make("breakdown", 0, 10)
    sim.run_for(200_000)
    k = eng.snapshot()["kpi"]
    assert k["breakdown_parts"] == 1, "exactly the box stuck on S2 is a breakdown part"
    assert k["good"] == k["produced"] - k["scrap"] - 1
    assert k["quality"] < 1.0
    # slow (red) boxes are still good: in the normal run S2 often goes red with a 5 s buffer
    eng2, sim2 = make("normal", 0, 5)
    sim2.run_for(120_000)
    k2 = eng2.snapshot()["kpi"]
    assert k2["breakdown_parts"] == 0 and k2["good"] == k2["produced"]


def test_good_part_rule_on_hand_made_events():
    def E(ms, st, ev, val):
        return {"ms": ms, "st": st, "ev": ev, "val": val, "seq": 0}
    # buffer 5 s -> breakdown after 10 s. Box A: 8 s on S1 (red, still good). Box B: 12 s on S2 (breakdown part).
    ev = [E(0, 0, "BUF", 5),
          E(1000, 1, "IN", 1), E(9000, 1, "OUT", 8000), E(10000, 2, "IN", 1), E(12000, 2, "OUT", 2000),
          E(13000, 3, "IN", 1), E(15000, 3, "OUT", 2000),
          E(16000, 1, "IN", 1), E(18000, 1, "OUT", 2000), E(19000, 2, "IN", 1), E(31000, 2, "OUT", 12000),
          E(32000, 3, "IN", 1), E(34000, 3, "OUT", 2000)]
    k = analytics.compute(ev, {"occ": [0, 0, 0]}, 0, 0, 40_000)
    assert k["produced"] == 2 and k["breakdown_parts"] == 1 and k["good"] == 1


def test_bottleneck_now_lists_every_station_over_buffer():
    def E(ms, st, ev, val):
        return {"ms": ms, "st": st, "ev": ev, "val": val, "seq": 0}
    ev = [E(0, 0, "BUF", 5), E(1000, 1, "IN", 1), E(2000, 1, "OUT", 1000), E(3000, 2, "IN", 1),
          E(4000, 1, "IN", 1)]
    k = analytics.compute(ev, {"occ": [0, 0, 0]}, 0, 0, 12_000)
    assert k["bn_list"] == [2, 1] and k["bn_now"] == 2


def test_frozen_time_does_not_count_on_laptop():
    def E(ms, st, ev, val):
        return {"ms": ms, "st": st, "ev": ev, "val": val, "seq": 0}
    # S2 box from 1 s; S1 box from 2 s; S2 stalls at 11 s (buffer 5) -> LOCK,2 freezes S1 until 41 s
    ev = [E(0, 0, "BUF", 5), E(1000, 2, "IN", 1), E(2000, 1, "IN", 1), E(11000, 0, "LOCK", 2)]
    k = analytics.compute(ev, {"occ": [0, 0, 0]}, 0, 0, 40_000)
    s1 = k["stations"][0]
    assert s1["frozen"] and abs(s1["active_now_s"] - 9) < 0.01 and not s1["stalled"]
    assert k["lock_now"] == 2 and k["stations"][1]["stalled"]
