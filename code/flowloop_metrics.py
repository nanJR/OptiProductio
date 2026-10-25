"""OptiProductio metrics: turns a list of events into IEM numbers.
An event row is: t (seconds), event (PASS / SCRAP / DOWN / UP), station, reason, source."""
import pandas as pd


def load_events(path):
    ev = pd.read_csv(path)
    ev["station"] = pd.to_numeric(ev["station"], errors="coerce")
    return ev.sort_values("t").reset_index(drop=True)


def downtime(ev, t_end):
    """Total stopped seconds, and seconds per stop reason, from DOWN/UP pairs."""
    total, by_reason, started = 0.0, {}, None
    for _, r in ev[ev["event"].isin(["DOWN", "UP"])].iterrows():
        if r["event"] == "DOWN" and started is None:
            started, reason = r["t"], r["reason"]
        elif r["event"] == "UP" and started is not None:
            by_reason[reason] = by_reason.get(reason, 0) + r["t"] - started
            total += r["t"] - started
            started = None
    if started is not None:                       # still stopped right now
        by_reason[reason] = by_reason.get(reason, 0) + t_end - started
        total += t_end - started
    return total, by_reason


def wip_timeline(ev, last):
    """WIP after every event: +1 when a part leaves S1, -1 when it leaves the line."""
    step = pd.Series(0, index=ev.index)
    step[(ev["event"] == "PASS") & (ev["station"] == 1)] = 1
    step[(ev["event"] == "PASS") & (ev["station"] == last)] = -1
    step[ev["event"] == "SCRAP"] = -1
    return pd.DataFrame({"t": ev["t"], "wip": step.cumsum()})


def compute(ev, n_stations=3, ideal_ct=10.0, demand=None, planned_s=None):
    t_start, t_end = ev["t"].min(), ev["t"].max()
    planned = planned_s or max(t_end - t_start, 1e-9)
    passes = ev[ev["event"] == "PASS"]
    count = {s: int((passes["station"] == s).sum()) for s in range(1, n_stations + 1)}
    good = count[n_stations]
    scrap = int((ev["event"] == "SCRAP").sum())
    total = good + scrap

    # Cycle time per station = time the station spent working on one part.
    # A station can start part k once part k arrives from upstream AND it has
    # finished part k-1, so: work time = finish(k) - max(arrive(k), finish(k-1)).
    # Parts are matched first-in-first-out; Station 1 is assumed never starved.
    done = {s: passes.loc[passes["station"] == s, "t"].to_list() for s in count}
    done[n_stations] = ev.loc[((ev["event"] == "PASS") & (ev["station"] == n_stations))
                              | (ev["event"] == "SCRAP"), "t"].to_list()
    cycle = {}
    for s in count:
        work = []
        for k in range(1, len(done[s])):
            arrive = done[s - 1][k] if s > 1 and k < len(done[s - 1]) else done[s][k - 1]
            work.append(done[s][k] - max(arrive, done[s][k - 1]))
        cycle[s] = float(pd.Series(work).median()) if work else None
    known = {s: c for s, c in cycle.items() if c is not None}
    bottleneck = max(known, key=known.get) if known else None

    # Parts waiting in front of each station (and inside it)
    queue = {s: count[s - 1] - count[s] for s in range(2, n_stations + 1)}
    queue[n_stations] -= scrap

    # WIP: now, and averaged over time
    wt = wip_timeline(ev, n_stations)
    wip_now = int(wt["wip"].iloc[-1])
    durations = wt["t"].shift(-1, fill_value=t_end) - wt["t"]
    avg_wip = float((wt["wip"] * durations).sum() / max(t_end - t_start, 1e-9))

    # Flow time measured by matching parts first-in-first-out (S1 exit -> line exit)
    flows = [b - a for a, b in zip(done[1], done[n_stations])]
    flow_measured = sum(flows) / len(flows) if flows else None

    # Throughput, and Little's Law check: flow time = WIP / throughput
    th = total / max(t_end - t_start, 1e-9)               # parts per second
    flow_little = avg_wip / th if th > 0 else None

    # OEE = Availability x Performance x Quality
    down, down_by = downtime(ev, t_end)
    run = max(planned - down, 1e-9)
    availability = run / planned
    performance = min(ideal_ct * total / run, 1.0)
    quality = good / total if total else 0.0

    return {
        "count": count, "good": good, "scrap": scrap, "total": total,
        "scrap_rate": scrap / total if total else 0.0,
        "throughput_per_min": good / planned * 60,
        "cycle": cycle, "bottleneck": bottleneck, "queue": queue,
        "wip_now": wip_now, "avg_wip": avg_wip, "wip_timeline": wt,
        "flow_measured": flow_measured, "flow_little": flow_little,
        "downtime": down, "downtime_by_reason": down_by,
        "availability": availability, "performance": performance, "quality": quality,
        "oee": availability * performance * quality,
        "takt": planned / demand if demand else None,
        "planned": planned,
    }


def bosch_to_events(date_csv, numeric_csv, nrows=50000, line="L3", n_stations=3, unit_s=36000):
    """Turn a slice of the Bosch Kaggle data into OptiProductio events.
    Picks the n most-visited stations on one line, keeps parts that visited all of them,
    uses each part's first timestamp at a station as its PASS time, and turns
    Response = 1 (failed QC) into SCRAP at the last station.
    unit_s: seconds per Bosch time unit. The Kaggle community estimate is that
    0.01 units is about 6 minutes; this is not confirmed by Bosch."""
    dates = pd.read_csv(date_csv, nrows=nrows)
    resp = pd.read_csv(numeric_csv, nrows=nrows, usecols=["Id", "Response"])
    cols = [c for c in dates.columns if c.startswith(line + "_")]
    stations = sorted({c.split("_")[1] for c in cols})
    first = pd.DataFrame({s: dates[[c for c in cols if c.split("_")[1] == s]].min(axis=1)
                          for s in stations})
    chosen = first.notna().sum().nlargest(n_stations).index
    chosen = sorted(chosen, key=lambda s: first[s].mean())   # put them in flow order
    first = first[chosen].dropna()
    first["Response"] = resp.set_index("Id").loc[dates.loc[first.index, "Id"], "Response"].values

    rows = []
    for _, r in first.iterrows():
        for i, s in enumerate(chosen, start=1):
            if i == n_stations and r["Response"] == 1:
                rows.append([r[s] * unit_s, "SCRAP", i, "", "bosch"])
            else:
                rows.append([r[s] * unit_s, "PASS", i, "", "bosch"])
    ev = pd.DataFrame(rows, columns=["t", "event", "station", "reason", "source"])
    return ev.sort_values("t").reset_index(drop=True), chosen
