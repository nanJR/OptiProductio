"""OptiProductio dashboard. Run:  streamlit run app.py"""
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from flowloop_metrics import bosch_to_events, compute, load_events

DATA = Path("data")
st.set_page_config(page_title="OptiProductio", layout="wide")
st.title("OptiProductio: production efficiency dashboard")

# ---------- Sidebar: choose data and targets ----------
source = st.sidebar.radio("Data source", ["Live Arduino line", "Bosch sample"])
ideal_ct = st.sidebar.number_input("Ideal cycle time (s per part)", 1.0, 100000.0, 10.0)
demand = st.sidebar.number_input("Customer demand (parts in this run)", 1, 100000, 40)
planned_min = st.sidebar.number_input("Planned run time (min, 0 = since start)", 0.0, 100000.0, 0.0)
cap = st.sidebar.slider("WIP cap (parts)", 1, 15, 5)
reorder_point = st.sidebar.slider("Reorder point (parts in bin)", 0, 20, 5)
DATA.mkdir(exist_ok=True)
(DATA / "cap.txt").write_text(str(cap))

if source == "Live Arduino line":
    path = DATA / "live_events.csv"
    if not path.exists() or len(pd.read_csv(path)) == 0:
        st.info("Waiting for the Arduino... start serial_logger.py and move a part.")
        time.sleep(2)
        st.rerun()
    ev = load_events(path)
else:
    @st.cache_data
    def bosch():
        return bosch_to_events(DATA / "train_date.csv", DATA / "train_numeric.csv")
    ev, chosen = bosch()
    st.caption(f"Bosch stations used as S1, S2, S3: {', '.join(chosen)}")

m = compute(ev, ideal_ct=ideal_ct, demand=demand, planned_s=planned_min * 60 or None)

# ---------- Top row: the five numbers a supervisor looks at ----------
c = st.columns(5)
c[0].metric("Good parts", m["good"])
c[1].metric("Scrap rate", f"{m['scrap_rate']:.0%}", f"{m['scrap']} scrapped", delta_color="off")
c[2].metric("Throughput", f"{m['throughput_per_min']:.2f} /min")
c[3].metric("WIP now", m["wip_now"], f"cap {cap}", delta_color="off")
c[4].metric("OEE (approx.)", f"{m['oee']:.0%}")

if m["wip_now"] >= cap:
    st.error(f"WIP is {m['wip_now']}, at or over the cap of {cap}. Stop releasing parts into Station 1.")
else:
    st.success(f"WIP is {m['wip_now']}, under the cap of {cap}. OK to release the next part.")

# ---------- Middle: where is the line slow? ----------
left, right = st.columns(2)
with left:
    st.subheader("Cycle time per station (s)")
    ct = pd.DataFrame({"station": [f"S{s}" for s in m["cycle"]],
                       "cycle time (s)": [v or 0 for v in m["cycle"].values()]}).set_index("station")
    st.bar_chart(ct)
    if m["bottleneck"]:
        st.warning(f"Bottleneck: Station {m['bottleneck']} (slowest, {m['cycle'][m['bottleneck']]:.1f} s per part)")
    if m["takt"]:
        st.write(f"Takt time: **{m['takt']:.1f} s per part**. "
                 "A station slower than takt cannot keep up with demand.")
with right:
    st.subheader("Parts waiting in front of each station")
    q = pd.DataFrame({"station": [f"S{s}" for s in m["queue"]],
                      "parts waiting": list(m["queue"].values())}).set_index("station")
    st.bar_chart(q)

st.subheader("WIP over time")
st.line_chart(m["wip_timeline"].set_index("t"))

# ---------- Bottom: OEE, Little's Law, inventory ----------
a, b, i = st.columns(3)
with a:
    st.subheader("OEE breakdown")
    st.write(f"Availability {m['availability']:.0%} × Performance {m['performance']:.0%} "
             f"× Quality {m['quality']:.0%} = **{m['oee']:.0%}**")
    if m["downtime_by_reason"]:
        st.write("Downtime by reason (s):", {k: round(v) for k, v in m["downtime_by_reason"].items()})
with b:
    st.subheader("Little's Law check")
    if m["flow_little"] and m["flow_measured"]:
        st.write(f"Average WIP {m['avg_wip']:.1f} ÷ throughput = "
                 f"**{m['flow_little']:.0f} s** predicted flow time")
        st.write(f"Measured flow time (first in, first out): **{m['flow_measured']:.0f} s**")
with i:
    st.subheader("Raw material bin")
    status = DATA / "live_status.csv"
    if source == "Live Arduino line" and status.exists() and len(pd.read_csv(status)):
        bin_parts = int(pd.read_csv(status).iloc[-1]["bin_parts"])
        st.metric("Parts left in bin", bin_parts)
        if bin_parts <= reorder_point:
            st.error("At or below the reorder point: refill the bin now.")
    else:
        st.write("Live line only.")

if source == "Live Arduino line":
    time.sleep(2)
    st.rerun()
