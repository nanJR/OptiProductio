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


def make(scenario="normal", limit=4):
    src = FakeSource()
    eng = Engine(src, ":memory:")
    sim = SimLine(lambda line: eng.on_msg(protocol.parse_line(line)), scenario, limit)
    src.sim = sim
    return eng, sim


# ---------- protocol ----------
def test_parse_event_and_status():
    e = protocol.parse_line("E,12,34567,2,IN,1")
    assert e == {"type": "E", "seq": 12, "ms": 34567, "st": 2, "ev": "IN", "val": 1}
    s = protocol.parse_line("S,13,35000,3,4,0,1,0,1,1,20,17")
    assert s["wip"] == 3 and s["occ"] == [1, 0, 1] and s["done"] == 17
    assert protocol.to_line(s) == "S,13,35000,3,4,0,1,0,1,1,20,17"


def test_garbage_is_ignored():
    for bad in ["", "# comment", "E,1,2", "E,1,2,3,NOPE,4", "S,a,b,c", "hello"]:
        assert protocol.parse_line(bad) is None


def test_mqtt_round_trip():
    root = "rvce/idealab/line1"
    for line in ["E,5,1000,3,OUT,4200", "E,6,1100,0,GATE,1", "S,7,2000,2,4,1,1,0,1,1,9,7"]:
        m = protocol.parse_line(line)
        topic, payload, _ = protocol.to_mqtt(m, root)
        assert protocol.from_mqtt(topic, payload, root) == m
    assert protocol.to_mqtt(protocol.parse_line("E,5,1,2,IN,1"), root)[0] == root + "/s2/event"
    assert protocol.command_to_mqtt("L,3", root) == (root + "/cmd/wip_limit", "3")


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
