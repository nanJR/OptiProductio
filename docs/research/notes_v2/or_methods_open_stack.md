# OR / Industrial-Intelligence Methods in Smart-Manufacturing Platforms, and Open-Source Equivalents for OptiProductio

Scope note: covers methods, standards, open/free tools and datasets. Vendor platforms (Siemens, AVEVA, GE, AWS, PTC, Azure) are covered by other researchers. Items marked **[UNVERIFIED]** come from background knowledge and were not confirmed against a fetched source this session.

## Q1. Which OR / IE methods appear in production-ops, APS and MES products, with plain explanations and standard references?

### Takeaway
Commercial MES/APS "intelligence" mostly packages long-established IE/OR methods: OEE and its six big losses (Nakajima/TPM, formalised in ISO 22400-2), Little's law and CONWIP (Factory Physics), data-driven bottleneck detection (Roser's active-period method), constraint-programming job-shop scheduling (e.g. CP-SAT), discrete-event simulation, SPC and predictive maintenance. Every one of these has a free Python route a student can demonstrate on small data.

### Cited Findings
**OEE and the six big losses**
- The Six Big Losses come from Seiichi Nakajima, *Introduction to TPM: Total Productive Maintenance* (Productivity Press, 1988), part of the TPM framework from the Japan Institute of Plant Maintenance (JIPM). How they map to OEE: Breakdowns → Availability; Setup & adjustment → Availability; Idling & minor stops → Performance; Reduced speed → Performance; Defects & rework → Quality; Startup/yield losses → Quality. — [TEEPTRAK: Six Big Losses](https://teeptrak.com/en/six-big-losses-2026/) (vendor blog, but the attribution is standard)
- OEE = Availability × Performance × Quality. ISO 22400-2 keeps this structure and defines time-model terms such as Planned Busy Time (PBT), Actual Unit Busy Time (AUBT) and Actual Unit Downtime (AUDT). — [Fabrico: OEE ISO 22400](https://www.fabrico.io/blog/oee-iso-22400/)
- Plain explanation for students: Availability = run time ÷ planned time; Performance = (ideal cycle time × total count) ÷ run time; Quality = good count ÷ total count. **[UNVERIFIED that these are word-for-word the ISO 22400 formulas. The ISO 22400 equivalents are reportedly Availability = APT/PBT, Effectiveness = (PRI × PQ)/APT, Quality ratio = GQ/PQ, where APT = actual production time, PRI = planned run time per item, PQ = produced quantity, GQ = good quantity. Check against the standard text or the Kang et al. 2016 IJPR paper before quoting.]**

**Little's law, WIP, throughput, cycle time (Factory Physics)**
- Little's law: WIP = Throughput × Cycle time (L = λW). Factory Physics (Hopp & Spearman, McGraw-Hill 1996; 3rd ed. Waveland 2008) is the standard IE textbook that applies it to production lines, along with "best case / worst case / practical worst case" line performance. **[UNVERIFIED: edition details from background knowledge]**
- Use in OptiProductio: once you measure any two of WIP, throughput (TH) and cycle time (CT) from the IR counters, the third follows. Comparing measured CT with WIP/TH is a quick sanity check on the sensor data.

**CONWIP / kanban (pull control)**
- CONWIP caps total WIP with one shared set of cards for the whole line. A part may enter only with a card, and the card goes back to the first station when a finished part leaves the last station. Kanban instead uses separate cards at each station. CONWIP is easier to set up and adjust, and in Spearman et al.'s simulation it reached lower WIP than kanban. — [Wikipedia: CONWIP](https://en.wikipedia.org/wiki/CONWIP)
- Original paper: Spearman, Woodruff & Hopp (1990), "CONWIP: a Pull Alternative to Kanban", DOI 10.1080/00207549008942761 (reprinted by the Project Production Institute in 2018). — [PPI reprint](https://projectproduction.org/journal/conwip-a-pull-alternative-to-kanban/). Journal details: *International Journal of Production Research* 28(5):879–894. **[Taken from secondary citation; volume and pages not checked on the publisher page]**

**Bottleneck detection: active-period method**
- Developed by Christoph Roser (Toyota Central R&D Labs). A station counts as *active* whenever it is not waiting, so working, broken down, under repair or in changeover all count. It is *inactive* when starved or blocked. At any moment, the station with the longest uninterrupted active period is the momentary bottleneck. Where two stations' active periods overlap, the bottleneck is "shifting" between them. Outside the overlaps, one station is the "sole" bottleneck. The method needs exact active/inactive timestamps for each station. — [AllAboutLean: Active Period Method](https://www.allaboutlean.com/active-period-method)
- Papers: Roser, Nakano & Tanaka, "A Practical Bottleneck Detection Method", Winter Simulation Conference 2001 — [preprint](https://www.allaboutlean.com/publications/2001_roser_wsc-a-practical-bottleneck-detection-method_preprint/); "Shifting Bottleneck Detection", WSC 2002, pp. 1079–1086 — [informs-sim.org PDF](https://www.informs-sim.org/wsc02papers/145.pdf)
- A Python package `active-period-method` exists on PyPI — [PyPI](https://pypi.org/project/active-period-method/); Chalmers has published an enhanced data-driven shifting-bottleneck algorithm — [Chalmers](https://research.chalmers.se/en/publication/?id=526180)
- AllAboutLean has a worked example with raw data and solution, good for a viva — [initial data](https://www.allaboutlean.com/active-period-method/activeperiodraw/), [solution](https://www.allaboutlean.com/active-period-method/activeperiodsolved/)

**Job-shop scheduling with solvers (APS)**
- Job-shop problem: several jobs, each a fixed sequence of tasks on given machines. The goal is to minimise makespan, the time until the last job finishes. Google OR-Tools solves it with the CP-SAT constraint-programming solver. The full Python example runs to about 100–110 lines, and the code samples are Apache 2.0. — [OR-Tools job shop](https://developers.google.com/optimization/scheduling/job_shop)
- Dispatching rules (SPT, EDD, FIFO, critical ratio) are the simple heuristic alternative used on MES dispatch lists. Reference: Pinedo, *Scheduling: Theory, Algorithms, and Systems* (Springer). **[UNVERIFIED: standard textbook reference, not fetched]**

**Line balancing**
- Assign tasks to stations so that each station's work content stays at or under takt time = available time ÷ demand. Balance efficiency = Σ task times ÷ (number of stations × cycle time). Classic heuristic: ranked positional weight (Helgeson & Birnie 1961). Reference: Groover, *Automation, Production Systems, and Computer-Integrated Manufacturing*. **[UNVERIFIED: background knowledge]**

**Discrete-event simulation (DES) "digital twins"**
- SimPy is a process-based DES framework in standard Python, MIT-licensed. Processes are Python generators, and Resources model limited-capacity stations or queues. — [SimPy docs](https://simpy.readthedocs.io/en/latest/)
- Roser's active-period method was itself designed and tested in simulation. — [AllAboutLean](https://www.allaboutlean.com/active-period-method)

**SPC / control charts**
- Shewhart X-bar/R and p-charts with 3-sigma limits. For OptiProductio, a p-chart of reject fraction per time window is the natural choice. Reference: Montgomery, *Introduction to Statistical Quality Control* (Wiley). **[UNVERIFIED: standard reference, not fetched]**

**Predictive maintenance**
- Benchmark data such as AI4I 2020 encodes failure modes (tool wear, heat dissipation, power, overstrain, random). See Q4. — [UCI AI4I](https://archive.ics.uci.edu/dataset/601)
- ISO 22400-2 maintenance KPIs include MTBF, MTTR and MTTF. — [Fabrico](https://www.fabrico.io/blog/oee-iso-22400/)

### Inferences
- With IR timestamps and breakdown buttons, OptiProductio can compute OEE components, Little's-law checks, CONWIP alerts and active-period bottlenecks directly. These cover most of the "analytics" layer that MES vendors sell.
- Job-shop CP-SAT is a credible "APS-lite" demo even with only 3 stations, but a 3-station flow line is a trivial scheduling case. A small job-shop toy (e.g. 3 product types × 3 stations with different routings) shows the method better.

### Gaps
- Could not fetch the ISO 22400-2 text (paywalled), so the exact formula symbols are unverified.
- Textbook editions and pages for Factory Physics, Pinedo, Groover and Montgomery are not verified online.

## Q2. ISA-95 levels and ISO 22400 KPI definitions: what should a student copy for credibility?

### Takeaway
Place OptiProductio on the ISA-95 (IEC 62264) level diagram: sensors and Arduino at L0–L1, serial logger at L2, Streamlit dashboard at L3 (MOM/MES). Name the KPIs with ISO 22400-2 terms (OEE, availability, effectiveness/performance, quality ratio, throughput rate, scrap ratio, MTBF/MTTR). That gives the project real vocabulary without buying the standard.

### Cited Findings
- ISA-95 = IEC/ISO 62264. It is the international standard for integrating enterprise and control systems (ERP ↔ MES/MOM). — [Siemens: ISA-95 framework](https://www.siemens.com/en-us/technology/isa-95-framework-layers/)
- Levels: L0 physical process; L1 sensing and manipulating; L2 monitoring and control (PLC/DCS/SCADA); L3 manufacturing operations workflow (MES/MOM); L4 business planning (ERP). — [Siemens](https://www.siemens.com/en-us/technology/isa-95-framework-layers/)
- ISA-95 Part 3 MOM activity areas: production, maintenance, quality, inventory/material handling. — [Siemens](https://www.siemens.com/en-us/technology/isa-95-framework-layers/)
- Commonly cited time frames: L4 months/weeks/days, L3 days/shifts/hours/minutes/seconds, L2 down to sub-seconds. **[UNVERIFIED: Siemens page did not state these. Commonly shown in ISA-95 diagrams, see e.g. [IT/OT Insider](https://itotinsider.substack.com/p/isa-95-and-the-purdue-model-explained), not fetched]**
- ISO 22400-2:2014 "Automation systems and integration — Key performance indicators (KPIs) for manufacturing operations management — Part 2: Definitions and descriptions". For each KPI it gives the formula, elements, time behaviour, unit, user group and production methodology. Equipment KPIs apply to IEC 62264 work units. Edition 1 (Jan 2014). Status: published, but flagged "to be revised" (stage 90.92). Amendment 1 (2017) adds energy-management KPIs. — [ISO 22400-2](https://www.iso.org/standard/54497.html)
- Part 2 defines 34 KPIs, including worker productivity, allocation ratio, throughput rate, performance rate, availability, quality ratio, MTBF, MTTR, MTTF, scrap ratio, rework ratio, fall-off ratio, inventory turns and finished-goods ratio. Part 1 covers concepts and terminology. — [Fabrico](https://www.fabrico.io/blog/oee-iso-22400/)
- A free "ISO 22400 KPI and data dictionary" PDF is offered by an OEE vendor. — [TEEPTRAK](https://teeptrak.com/en/?p=147334) (vendor marketing; not reviewed)

### Inferences
- Copy into the report: (1) an ISA-95 pyramid with OptiProductio components mapped to each level; (2) a KPI table with an "ISO 22400 name" column, a formula column, and a column for the sensor or button that supplies each data element; (3) the time-model breakdown (planned time → planned downtime → busy time → unplanned downtime from the breakdown button).
- Call the metric an "OEE proxy" unless a planned/ideal cycle time is defined, because Performance needs an ideal rate.

### Gaps
- Exact ISO 22400 symbols are behind a paywall (see Q1 gaps).

## Q3. Open-source / free stack equivalents: which are realistic for first-years in a week?

### Takeaway
For a team with little CS background and one week, the realistic stack is Arduino → USB serial → Python (pyserial) → CSV/SQLite → Streamlit, plus SimPy for what-if simulation and optionally OR-Tools for a scheduling page. Node-RED + Mosquitto + InfluxDB + Grafana is a credible "industry-style" option only if someone already knows Docker. BaSyx/Ditto, PLC4X and FUXA should be mentioned as "future work" only.

### Cited Findings
- Arduino's own docs walk through the MQTT → Node-RED → InfluxDB → Grafana data-logging stack (on Portenta X8 with Docker). — [Arduino docs: Data logging with MQTT, Node-RED, InfluxDB and Grafana](https://docs.arduino.cc/tutorials/portenta-x8/datalogging-iot)
- There is a ready-made Node-RED flow that bridges "Arduino/ESP32 Serial → InfluxDB, MQTT", so serial data from an UNO can enter that stack without Wi-Fi. — [Node-RED flows library](https://flows.nodered.org/flow/6621fc32c681d4a0635fb20a7239e501)
- SimPy: pure-Python DES, MIT licence; stations become Resources, parts become processes. — [SimPy docs](https://simpy.readthedocs.io/en/latest/)
- Google OR-Tools CP-SAT job-shop example in about 100 lines of Python. — [OR-Tools](https://developers.google.com/optimization/scheduling/job_shop)
- Eclipse BaSyx Python SDK (formerly PyI40AAS) implements the Asset Administration Shell (Industry 4.0 digital-twin metamodel) and has tutorials. — [PyPI basyx-python-sdk](https://www.pypi.org/project/basyx-python-sdk), [tutorials](https://basyx-python-sdk.readthedocs.io/en/stable/tutorials/index.html)
- Apache PLC4X documents an integration with Eclipse Ditto (a digital-twin framework). — [PLC4X: Eclipse Ditto integration](https://plc4x.apache.org/plc4x/pre-release/users/integrations/eclipse-ditto.html)
- FUXA is an open-source web-based SCADA/HMI on GitHub (frangoteam). — [FUXA wiki](https://github.com/frangoteam/FUXA/wiki/Home)

Feasibility table (judgement for a 4-person first-year team, 1 week; licences marked [UNVERIFIED] unless cited):

| Tool | Role (ISA-95) | Licence | One-week realistic? |
|---|---|---|---|
| pyserial + pandas + Streamlit | L2→L3 logger + dashboard | BSD/Apache [UNVERIFIED] | **Yes, core** |
| SQLite / CSV | Historian | Public domain [UNVERIFIED] | **Yes** |
| SimPy | DES what-if twin | MIT ([docs](https://simpy.readthedocs.io/en/latest/)) | **Yes**, 50–100 lines |
| OR-Tools CP-SAT | APS scheduling | Apache 2.0 samples ([docs](https://developers.google.com/optimization/scheduling/job_shop)) | **Yes**, copy-adapt the example |
| Node-RED | Flow-based integration/HMI | Apache 2.0 [UNVERIFIED] | Maybe: easy GUI, but a second tool to learn |
| Mosquitto (MQTT) | Message broker | EPL/EDL [UNVERIFIED] | Maybe: needed only if Wi-Fi/ESP32 or several PCs |
| InfluxDB / TimescaleDB | Time-series historian | MIT/Apache (InfluxDB OSS) [UNVERIFIED] | Stretch: setup overhead |
| Grafana | Dashboards | AGPLv3 [UNVERIFIED] | Stretch: looks professional, but duplicates Streamlit |
| Eclipse BaSyx / Ditto (AAS) | Digital-twin metamodel | EPL/MIT [UNVERIFIED] | No: future work only |
| FUXA / OpenSCADA | Web SCADA/HMI | MIT / GPL [UNVERIFIED] | No (low value over Streamlit) |
| Apache PLC4X | PLC protocol drivers | Apache 2.0 [UNVERIFIED] | No: no PLC in the build |

### Inferences
- Streamlit already covers the HMI and dashboard roles of Grafana, FUXA and Node-RED dashboards. Adding them costs time for little marks unless the evaluators specifically value the "IIoT stack" look.
- A cheap credibility gain: write each event as a JSON message with an ISA-95-style topic name (e.g. `rvce/ie-lab/line1/station2/count`, mimicking the Unified Namespace pattern) even if it only goes to CSV. That makes a later move to MQTT trivial. **[Unified Namespace naming is common industry practice; not sourced here]**

### Gaps
- Licences for Node-RED, Mosquitto, InfluxDB, Grafana, FUXA, Ditto, BaSyx and PLC4X were not individually verified this session. Check each GitHub LICENSE file before stating them.
- No first-hand evidence on how long first-year students take to learn Node-RED or Grafana. The feasibility column is judgement.

## Q4. Public manufacturing datasets besides Bosch suited to OEE / WIP / scheduling

### Takeaway
None of the classic public datasets is a clean "OEE log". AI4I 2020 (CC BY 4.0) suits failure/downtime modelling, SECOM (CC BY 4.0) suits quality/SPC, Levy's 4TU production event log suits cycle-time/WIP/flow analysis (process mining), and NASA C-MAPSS suits RUL prediction but is currently listed as unavailable on data.gov.

### Cited Findings
- **AI4I 2020 Predictive Maintenance (UCI #601)**: 10,000 rows. Fields: product type L/M/H, air and process temperature, rotational speed, torque, tool wear, a machine-failure flag and 5 failure modes (TWF, HDF, PWF, OSF, RNF). Synthetic. Licence CC BY 4.0. DOI 10.24432/C5HS5C. — [UCI AI4I 2020](https://archive.ics.uci.edu/dataset/601)
- **SECOM (UCI #179)**: semiconductor process, 1,567 rows × 591 sensor features with missing values, pass/fail label (104 fails) plus timestamp. Licence CC BY 4.0. McCann & Johnston 2008, DOI 10.24432/C54305. — [UCI SECOM](https://archive.ics.uci.edu/dataset/179/secom)
- **Production Analysis with Process Mining Technology (Dafna Levy, 2014, 4TU.ResearchData)**: a CSV event log from a production process with case, activity, resource and timestamp. Licence: 4TU General Terms of Use. DOI 10.4121/uuid:68726926-5ac5-4fab-b873-ee76ea412399. — [4TU citation file](https://data.4tu.nl/export/cff/datasets/12697997)
- **BPI Challenge logs**: annual process-mining event logs from industry, hosted on 4TU. Most are business processes (loans, purchase-to-pay), not shop-floor. — [BPIC page](https://www.win.tue.nl/bpi/challenge.html), [4TU BPI collection](https://community.data.4tu.nl/?p=2298). **[UNVERIFIED which year, if any, is a manufacturing log. BPIC 2019 is purchase-order handling at a coatings/paint company, not production]**
- **NASA C-MAPSS turbofan degradation**: simulated engine run-to-failure data used for remaining-useful-life benchmarks. The data.gov catalog states "C-MAPSS and C-MAPSS40K ARE CURRENTLY UNAVAILABLE FOR DOWNLOAD", the rights field is null and access is listed as "non-public". — [data.gov C-MAPSS](https://catalog.data.gov/dataset/c-mapss-aircraft-engine-simulator-data). Mirrors exist on IEEE DataPort and Kaggle — [IEEE DataPort](https://ieee-dataport.org/documents/c-mapss-dataset). **[Mirror licences unverified; NASA data is usually US-government public domain, but confirm]**
- **Bosch Production Line Performance (Kaggle)**: already in use by the team; licence and terms not checked in this session (competition data, may be restricted to competition use). **[UNVERIFIED]**

### Inferences
- For WIP/cycle-time and bottleneck demos, the Levy event log is the closest public analogue to OptiProductio's own station-timestamp data: per-activity timestamps allow Little's-law and active-period-style analysis. The Bosch dataset has station timestamps but is huge and anonymised.
- For downtime Pareto and MTBF/MTTR, AI4I failure-mode labels can be re-framed as "breakdown reasons".
- For SPC, SECOM's pass/fail over time supports a p-chart.

### Gaps
- No public dataset found that directly provides OEE time-model states (planned/run/down) for a line. Microsoft's Azure predictive maintenance sample (telemetry, errors, maintenance, failures) may fit but was not verified this session.
- Kaggle licences (Bosch, C-MAPSS mirrors) not checked.

## Q5. Features OptiProductio should add that mirror commercial platforms but stay cheap

### Takeaway
Five features, each about a day's Python work, make the dashboard read like a mini-MES: (1) downtime/reject Pareto by reason, (2) an auto-generated shift report with ISO 22400 KPIs, (3) a live active-period bottleneck finder, (4) a SimPy what-if slider for the CONWIP WIP cap, (5) a toy OR-Tools schedule suggestion. Add SPC on rejects and MTBF/MTTR if time allows.

### Cited Findings (method basis for each feature)
- Downtime Pareto by the six big losses → Availability/Performance/Quality buckets — [TEEPTRAK](https://teeptrak.com/en/six-big-losses-2026/)
- Shift report KPIs (availability, quality ratio, throughput rate, scrap ratio, MTBF, MTTR) — [Fabrico ISO 22400](https://www.fabrico.io/blog/oee-iso-22400/), [ISO 22400-2](https://www.iso.org/standard/54497.html)
- Bottleneck finder from per-station active/inactive timestamps — [AllAboutLean](https://www.allaboutlean.com/active-period-method)
- WIP-cap what-if: CONWIP card count as the control knob — [Wikipedia CONWIP](https://en.wikipedia.org/wiki/CONWIP); simulate with SimPy Resources/containers — [SimPy](https://simpy.readthedocs.io/en/latest/)
- Schedule suggestion: CP-SAT job-shop minimising makespan — [OR-Tools](https://developers.google.com/optimization/scheduling/job_shop)

Implementation sketch (judgement, no source):
1. **Downtime & reject Pareto**: give the breakdown button a reason code (e.g. press count or a second button = "setup" vs "breakdown") and log reject events. Show a Pareto bar chart plus a cumulative-% line in Streamlit. Map each reason to a six-big-loss category.
2. **Shift report**: a "Generate report" button builds a table (planned time, downtime, run time, total/good count, OEE components, TH, average CT, average WIP, MTBF/MTTR) and exports it as CSV or PDF.
3. **Bottleneck finder**: each station logs state changes (busy when its IR detects a part, down when the breakdown button is pressed, idle otherwise). Compute the active periods, then label the sole or shifting bottleneck per time window and show a percentage bar per station.
4. **What-if WIP cap**: a SimPy model of 3 stations using measured mean cycle times and breakdown rates. A slider sets the CONWIP cap from 1 to 10 and plots throughput and cycle time against WIP. This shows the Factory Physics "practical worst case" curve and Little's law, and the knee of the curve gives the recommended cap.
5. **Schedule suggestion**: 3–5 toy jobs with different routings. OR-Tools CP-SAT minimises makespan, the result is drawn as a Gantt chart (plotly timeline) and compared with FIFO and SPT dispatching.
6. **Optional**: p-chart of reject fraction; Little's-law consistency check (WIP vs TH × CT); andon-style buzzer when the WIP cap or an SPC limit is breached.

### Inferences
- Features 1–4 use only data the existing hardware already produces, plus a reason code. Feature 5 is fully offline, so it carries no hardware risk.
- Calibrating the SimPy what-if model with measured line data and checking it against the physical line ("sim vs real throughput") is what turns a simulation into a defensible "digital twin" claim at student level.

### Gaps
- No sourced benchmark of which features evaluators at RVCE value. The prioritisation above is judgement.
