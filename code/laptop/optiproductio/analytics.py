"""All the numbers on the dashboard, worked out from the historian's events.

Everything uses the UNO clock (`ms`), so network delays never distort a cycle time.

Main ideas (ELI5 versions are in docs/phase2/HOW_IT_WORKS.md):
  * Active period (Roser): a station is ACTIVE while a box is on it (working or
    waiting to be taken away) and IDLE while it is empty (starved). At any moment
    the bottleneck is the station whose current active period is the longest.
    When the longest active period passes from one station to another and the
    two periods overlap, that overlap is a "shifting bottleneck" time.
  * ISO 22400-2 KPI names: PBT, APT, ADOT, PQ, GQ, SQ, PRI, A, E, QR, OEE.
  * Little's law (Hopp & Spearman): WIP = throughput x lead time.
"""
from __future__ import annotations

from collections import deque

DEFAULT_CFG = {
    "ideal_ct_s": 6.0,       # PRI: planned run time per item (design cycle time of the line)
    "down_after_s": 18.0,    # no part out of S3 for this long = line is DOWN (Vorne-style)
    "stall_s": 20.0,         # a station active this long = suspected breakdown (same as UNO)
    "timeline_s": 600,       # how much history the timeline chart shows
}


def _clip(a, b, t0, t1):
    a, b = max(a, t0), min(b, t1)
    return (a, b) if b > a else None


def _station_periods(events, init, session_start, t_end):
    """Active periods (start_ms, end_ms, ongoing) for S1..S3 over the whole session."""
    periods = [[], [], []]
    occ = list(init.get("occ", [0, 0, 0]))
    start = [session_start if occ[i] > 0 else None for i in range(3)]
    for e in events:
        s = e["st"] - 1
        if s < 0 or s > 2:
            continue
        if e["ev"] == "IN":
            if occ[s] == 0:
                start[s] = e["ms"]
            occ[s] += 1
        elif e["ev"] == "OUT" and occ[s] > 0:
            occ[s] -= 1
            if occ[s] == 0:
                periods[s].append((start[s], e["ms"], False))
    for s in range(3):
        if occ[s] > 0:
            periods[s].append((start[s], t_end, True))
    return periods, occ


def roser(periods, t0, t1, step_ms=None):
    """Roser active-period bottleneck analysis between t0 and t1.

    Returns per-station sole and shifting bottleneck time (ms), plus the bottleneck
    segments for the timeline. A step of ~0.2 s is plenty for boxes moved by hand.
    """
    span = t1 - t0
    res = {"sole_ms": [0, 0, 0], "shift_ms": [0, 0, 0], "segments": [], "shift_segments": []}
    if span <= 0:
        return res
    dt = step_ms or max(100, span // 4000)
    n = int(span // dt)
    ptr = [0, 0, 0]
    seq = []                      # per step: (station, period_index) or None
    for k in range(n):
        t = t0 + (k + 0.5) * dt
        best, bestd = None, -1
        for s in range(3):
            P = periods[s]
            i = ptr[s]
            while i < len(P) and P[i][1] <= t:
                i += 1
            ptr[s] = i
            if i < len(P) and P[i][0] <= t:
                d = P[i][1] - P[i][0]
                if d > bestd:
                    best, bestd = (s, i), d
        seq.append(best)

    # collapse into segments of the same (station, period)
    segs = []
    for k, b in enumerate(seq):
        if segs and segs[-1][0] == b:
            segs[-1][2] = k + 1
        else:
            segs.append([b, k, k + 1])
    shifting = [False] * n
    real = [sg for sg in segs if sg[0] is not None]
    for a, b in zip(real, real[1:]):
        (sa, ia), (sb, ib) = a[0], b[0]
        if sa == sb:
            continue
        pa, pb = periods[sa][ia], periods[sb][ib]
        ov = _clip(max(pa[0], pb[0]), min(pa[1], pb[1]), t0, t1)
        if not ov:
            continue
        k0 = max(0, int((ov[0] - t0) // dt))
        k1 = min(n, int((ov[1] - t0) // dt) + 1)
        for k in range(k0, k1):
            shifting[k] = True
        res["shift_ms"][sa] += (k1 - k0) * dt
        res["shift_ms"][sb] += (k1 - k0) * dt
        res["shift_segments"].append({"a": sa + 1, "b": sb + 1, "t0": t0 + k0 * dt, "t1": t0 + k1 * dt})
    for k, b in enumerate(seq):
        if b is not None and not shifting[k]:
            res["sole_ms"][b[0]] += dt
    for b, k0, k1 in segs:
        if b is not None:
            res["segments"].append({"st": b[0] + 1, "t0": t0 + k0 * dt, "t1": t0 + k1 * dt})
    return res


def _down_intervals(out_times, t0, t1, ideal_ms, down_ms):
    """Line is DOWN when no box has left S3 for longer than down_ms.
    The lost time counts from one ideal cycle after the last box (Vorne-style)."""
    downs = []
    prev = t0
    for t in out_times:
        if t <= t0:
            prev = max(prev, t)
            continue
        if t > t1:
            break
        if t - prev > down_ms:
            downs.append((prev + ideal_ms, t))
        prev = t
    if t1 - prev > down_ms:
        downs.append((prev + ideal_ms, t1))
    return [d for d in (_clip(a, b, t0, t1) for a, b in downs) if d]


def _down_reason(a, b, periods, stall_ms):
    """Why was the line down between a and b? Look at what the stations were doing."""
    span = b - a
    busy, longest = [0, 0, 0], [0, 0, 0]
    for s in range(3):
        for p in periods[s]:
            c = _clip(p[0], p[1], a, b)
            if c:
                busy[s] += c[1] - c[0]
                longest[s] = max(longest[s], p[1] - p[0])
    s = max(range(3), key=lambda i: busy[i])
    if busy[s] < 0.25 * span:
        return "Starved: no box at S1 (chute empty or gate held)"
    if longest[s] >= stall_ms:
        return f"Breakdown suspected at S{s + 1}"
    return f"Slow station S{s + 1}"


def compute(events, init, session_start, t0, t1, cfg=None):
    """Everything for one run: the window [t0, t1] (UNO ms) of a session."""
    c = dict(DEFAULT_CFG)
    c.update(cfg or {})
    ideal_ms = c["ideal_ct_s"] * 1000
    down_ms = c["down_after_s"] * 1000
    stall_ms = c["stall_s"] * 1000
    t1 = max(t1, t0)
    pbt = t1 - t0

    events = [e for e in events if e["ms"] <= t1]
    periods, occ_now = _station_periods(events, init, session_start, t1)

    # --- counts, cycle times, lead times, WIP curve ---
    released0, done0 = init.get("released", 0), init.get("done", 0)
    cum_in, cum_out = released0, done0
    in_queue = deque([None] * max(0, released0 - done0))   # S1 IN times waiting to leave S3
    cycle = [[], [], []]
    lead = []
    out_times = []
    released = produced = scrap = 0
    wip_pts = []                                         # (ms, wip) steps
    hold_ms, gate_open_ms = [], []
    gate_state, gate_since = None, None
    gate_segments = []
    wip_start = None
    for e in events:
        ms, s, ev = e["ms"], e["st"], e["ev"]
        if wip_start is None and ms >= t0:
            wip_start = max(0, cum_in - cum_out)
        if ev == "IN" and s == 1:
            cum_in += 1
            in_queue.append(ms)
            if ms >= t0:
                released += 1
        elif ev == "OUT":
            if e["val"] > 0 and ms >= t0:
                cycle[s - 1].append(e["val"] / 1000)
            if s == 3:
                cum_out += 1
                out_times.append(ms)
                tin = in_queue.popleft() if in_queue else None
                if ms >= t0:
                    produced += 1
                    if tin is not None:
                        lead.append((ms - tin) / 1000)
        elif ev == "SCRAP" and ms >= t0:
            scrap += 1
        elif ev == "HOLD" and ms >= t0:
            hold_ms.append(ms)
        elif ev == "GATE":
            if gate_state is not None and gate_state == 1:
                cl = _clip(gate_since, ms, t0, t1)
                if cl:
                    gate_segments.append(cl)
            gate_state, gate_since = e["val"], ms
        if ev in ("IN", "OUT") and ms >= t0:
            wip_pts.append((ms, max(0, cum_in - cum_out)))
    if wip_start is None:
        wip_start = max(0, cum_in - cum_out)
    if gate_state == 1:
        cl = _clip(gate_since, t1, t0, t1)
        if cl:
            gate_segments.append(cl)
    wip_now = max(0, cum_in - cum_out)
    # boxes waiting between stations (out of S1 but not yet into S2, etc.)
    n_in = [sum(1 for e in events if e["st"] == i and e["ev"] == "IN") for i in (1, 2, 3)]
    n_out = [sum(1 for e in events if e["st"] == i and e["ev"] == "OUT") for i in (1, 2, 3)]
    transit = [max(0, n_out[0] - n_in[1]), max(0, n_out[1] - n_in[2])]

    # time-weighted average WIP
    area, t_prev, w_prev = 0.0, t0, wip_start
    for ms, w in wip_pts:
        area += w_prev * (ms - t_prev)
        t_prev, w_prev = ms, w
    area += w_prev * (t1 - t_prev)
    wip_avg = area / pbt if pbt > 0 else float(wip_now)

    # --- downtime and its reasons (Pareto) ---
    downs = _down_intervals(out_times, t0, t1, ideal_ms, down_ms)
    adot = sum(b - a for a, b in downs)
    pareto = {}
    down_list = []
    first_out = next((t for t in out_times if t > t0), None)
    for a, b in downs:
        if first_out is None or b <= first_out:
            r = "Start-up: line filling (no box out yet)"
        else:
            r = _down_reason(a, b, periods, stall_ms)
        pareto[r] = pareto.get(r, 0) + (b - a)
        down_list.append({"t0": a, "t1": b, "reason": r})
    pareto_rows, cum = [], 0
    total_down = sum(pareto.values()) or 1
    for r, v in sorted(pareto.items(), key=lambda kv: -kv[1]):
        cum += v
        pareto_rows.append({"reason": r, "s": v / 1000, "cum_pct": 100 * cum / total_down})

    # --- ISO 22400-2 style KPIs ---
    apt = max(0, pbt - adot)
    good = max(0, produced - scrap)
    A = apt / pbt if pbt > 0 else None
    E = min(1.0, ideal_ms * produced / apt) if apt > 0 else None
    QR = good / produced if produced > 0 else None
    oee = A * E * QR if None not in (A, E, QR) else None
    tr_per_min = produced / (apt / 60000) if apt > 0 else 0.0
    th_per_s = produced / (pbt / 1000) if pbt > 0 else 0.0
    lt_avg = sum(lead) / len(lead) if lead else None
    little_rhs = th_per_s * lt_avg if lt_avg is not None else None

    # --- per-station figures + Roser ---
    rz = roser(periods, t0, t1)
    stations = []
    for s in range(3):
        busy = sum((cl[1] - cl[0]) for cl in (_clip(p[0], p[1], t0, t1) for p in periods[s]) if cl)
        full = [p[1] - p[0] for p in periods[s] if _clip(p[0], p[1], t0, t1)]
        ongoing = periods[s][-1] if periods[s] and periods[s][-1][2] else None
        ct = cycle[s]
        stations.append({
            "st": s + 1,
            "occ": occ_now[s],
            "busy_ratio": busy / pbt if pbt > 0 else 0,
            "active_s": busy / 1000,
            "avg_active_period_s": (sum(full) / len(full) / 1000) if full else 0,
            "n_periods": len(full),
            "ct_avg_s": sum(ct) / len(ct) if ct else None,
            "ct_last_s": ct[-1] if ct else None,
            "ct_min_s": min(ct) if ct else None,
            "ct_max_s": max(ct) if ct else None,
            "count": len(ct),
            "active_now_s": (t1 - ongoing[0]) / 1000 if ongoing else 0,
            "stalled": bool(ongoing and t1 - ongoing[0] >= stall_ms),
            "sole_pct": 100 * rz["sole_ms"][s] / pbt if pbt > 0 else 0,
            "shift_pct": 100 * rz["shift_ms"][s] / pbt if pbt > 0 else 0,
        })
    # momentary bottleneck now = longest ongoing active period
    live = [st for st in stations if st["occ"] > 0]
    bn_now = max(live, key=lambda st: st["active_now_s"])["st"] if live else 0
    score = [st["sole_pct"] + st["shift_pct"] for st in stations]
    bn_overall = (max(range(3), key=lambda i: score[i]) + 1) if any(score) else 0
    aap = [st["avg_active_period_s"] for st in stations]
    bn_avg_method = (max(range(3), key=lambda i: aap[i]) + 1) if any(aap) else 0

    # --- output per minute vs target ---
    minutes = []
    n_bins = int(pbt // 60000) + 1 if pbt > 0 else 0
    for k in range(min(n_bins, 120)):
        a = t0 + k * 60000
        b = min(t1, a + 60000)
        cnt = sum(1 for t in out_times if a < t <= b)
        minutes.append({"k": k + 1, "count": cnt, "target": (b - a) / ideal_ms, "partial": b - a < 60000})
    minutes = minutes[-30:]

    # --- timeline window (last timeline_s seconds) ---
    w0 = max(t0, t1 - c["timeline_s"] * 1000)
    tl = {"t0": w0, "t1": t1, "stations": [], "down": [], "gate": [], "bn": [], "shift": [], "wip": []}
    for s in range(3):
        tl["stations"].append([list(cl) for cl in (_clip(p[0], p[1], w0, t1) for p in periods[s]) if cl])
    tl["down"] = [[cl[0], cl[1], d["reason"]] for d in down_list for cl in [_clip(d["t0"], d["t1"], w0, t1)] if cl]
    tl["gate"] = [list(cl) for cl in (_clip(a, b, w0, t1) for a, b in gate_segments) if cl]
    tl["bn"] = [[sg["st"], *cl] for sg in rz["segments"] for cl in [_clip(sg["t0"], sg["t1"], w0, t1)] if cl]
    tl["shift"] = [[sg["a"], sg["b"], *cl] for sg in rz["shift_segments"] for cl in [_clip(sg["t0"], sg["t1"], w0, t1)] if cl]
    w_at_w0 = wip_start
    for ms, w in wip_pts:
        if ms <= w0:
            w_at_w0 = w
    tl["wip"] = [[w0, w_at_w0]] + [[ms, w] for ms, w in wip_pts if ms > w0]

    target = pbt / ideal_ms if ideal_ms > 0 else 0
    def pct(x):
        return None if x is None else round(100 * x, 1)

    kpis = [
        {"sym": "PBT", "name": "Planned busy time", "formula": "run end - run start", "value": pbt / 1000, "unit": "s"},
        {"sym": "ADOT", "name": "Actual unit down time", "formula": "sum of DOWN intervals (no part out of S3 for > %.0f s)" % c["down_after_s"], "value": adot / 1000, "unit": "s"},
        {"sym": "APT", "name": "Actual production time", "formula": "PBT - ADOT", "value": apt / 1000, "unit": "s"},
        {"sym": "PQ", "name": "Produced quantity", "formula": "boxes out of S3", "value": produced, "unit": "pcs"},
        {"sym": "SQ", "name": "Scrap quantity", "formula": "boxes marked scrap by the operator", "value": scrap, "unit": "pcs"},
        {"sym": "GQ", "name": "Good quantity", "formula": "PQ - SQ", "value": good, "unit": "pcs"},
        {"sym": "PRI", "name": "Planned run time per item", "formula": "set in Settings", "value": c["ideal_ct_s"], "unit": "s"},
        {"sym": "A", "name": "Availability", "formula": "APT / PBT", "value": pct(A), "unit": "%"},
        {"sym": "E", "name": "Effectiveness (performance)", "formula": "PRI x PQ / APT (capped at 100 %)", "value": pct(E), "unit": "%"},
        {"sym": "QR", "name": "Quality ratio", "formula": "GQ / PQ", "value": pct(QR), "unit": "%"},
        {"sym": "OEE", "name": "OEE index", "formula": "A x E x QR", "value": pct(oee), "unit": "%"},
        {"sym": "TR", "name": "Throughput rate", "formula": "PQ / APT (APT used in place of order execution time)", "value": round(tr_per_min, 2), "unit": "pcs/min"},
    ]
    flow = [
        {"sym": "WIP", "name": "Average WIP (time-weighted)", "formula": "area under WIP(t) / PBT", "value": round(wip_avg, 2), "unit": "pcs"},
        {"sym": "TH", "name": "Throughput", "formula": "PQ / PBT", "value": round(th_per_s * 60, 2), "unit": "pcs/min"},
        {"sym": "LT", "name": "Lead time (S1 in to S3 out)", "formula": "mean of t_out(S3) - t_in(S1)", "value": None if lt_avg is None else round(lt_avg, 1), "unit": "s"},
        {"sym": "TH x LT", "name": "Little's law check", "formula": "should be close to average WIP", "value": None if little_rhs is None else round(little_rhs, 2), "unit": "pcs"},
    ]

    return {
        "t0": t0, "t1": t1, "pbt_s": pbt / 1000,
        "released": released, "produced": produced, "good": good, "scrap": scrap,
        "target": target, "efficiency_pct": pct(good / target) if target > 0 else None,
        "wip_now": wip_now, "transit": transit, "wip_avg": wip_avg, "lead_avg_s": lt_avg, "lead_last_s": lead[-1] if lead else None,
        "little_rhs": little_rhs, "th_per_min": th_per_s * 60, "tr_per_min": tr_per_min,
        "availability": A, "effectiveness": E, "quality": QR, "oee": oee,
        "adot_s": adot / 1000, "apt_s": apt / 1000,
        "line_down_now": bool(downs and downs[-1][1] >= t1),
        "down_reason_now": down_list[-1]["reason"] if downs and downs[-1][1] >= t1 else None,
        "holds": len(hold_ms),
        "stations": stations, "bn_now": bn_now, "bn_overall": bn_overall, "bn_avg_method": bn_avg_method,
        "pareto": pareto_rows, "minutes": minutes, "timeline": tl, "kpis": kpis, "flow": flow,
        "cfg": c,
    }
