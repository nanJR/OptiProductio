# Big factory platforms run on classroom OR methods

## Summary

The big industrial IoT platforms all do the same five jobs. They connect to machines, store time-stamped data in a historian, run the shop floor with MES (manufacturing execution system) software, show key numbers on dashboards, and add analytics on top [1][16][17][27][28]. Under the AI and digital-twin language, the analytics are mostly methods any IEM student meets in class. The list is OEE split into availability, performance and quality; downtime reasons ranked in a Pareto chart; bottleneck finding; finite-capacity scheduling with "what-if" comparison; SPC control charts; and predictive models trained on sensor history [3][5][19][22][23][28][31]. None of the vendor pages we read publish their KPI formulas or algorithms. That is why OptiProductio should take its formulas from standards and textbooks such as ISO 22400 and Factory Physics, and from the vendors take only the structure, the KPI set and the screen patterns [50][51][54].

The platform scene has also changed a lot in 2025 and 2026. Microsoft stopped new Azure IoT Central apps on 23 September 2026, and existing apps stop working after 20 September 2029 [44]. PTC sold ThingWorx and Kepware to the investment firm TPG, which on 17 March 2026 merged them with GE Vernova's Proficy software into a new company called Velotic [12][42]. AWS ended support for its IoT Events alarm service on 20 May 2026 [38]. AWS IoT TwinMaker is still sold, and we found no end-of-support notice for it, but its Cookie Factory sample needs a paid AWS account and several billable services [36][37]. So for a first-year team, the platforms are things to learn from, not things to build on.

The four documents you supplied back this up. Each one comes from a company that sells what it recommends, so treat every number in them as a survey or vendor claim. The Microsoft/IoT Analytics survey (n=300) says industrial IoT has moved into the "early majority". It finds the main barriers are now skills, integration and cybersecurity rather than budget, and it lists "digitally assisted shopfloor dashboards" as a recognised use case [45]. The Audi EC4P paper names OEE (availability × performance × quality) as Audi's key operational metric, but it reports no measured results [46]. Verdantix gives process and production optimisation and predictive maintenance the highest weights (16% each) when it scores industrial AI software [47]. The Cisco brochure is a product catalogue. Its useful ideas are IEC 62443 "zones and conduits" and keeping track of every connected device. It does not mention the Purdue model at all [48].

**What OptiProductio should do with this.** Before the 1 November build deadline, keep the scope small. Add a clean event log (a "mini historian"), OEE shown as A × P × Q with the formulas printed on screen, MTBF/MTTR from the breakdown button, a CONWIP alarm with a warning level, an acknowledge button and a suggested action, a Little's-law check, and a replay mode for the viva. After the deadline, add a downtime Pareto, an active-period bottleneck finder, a SimPy what-if model calibrated on your own line data, SPC charts, and optionally MQTT. Skip cloud platforms, virtual PLCs, agentic AI and full scheduling software. **OptiProductio's own angle** is a transparent, low-cost line where every KPI formula is visible, plus a WIP-cap (CONWIP) alert. None of the product pages we read lists a CONWIP alert as a feature, though vendors may still do it in ways we could not see. The team can also show its own before/after numbers with a baseline, which most vendor claims lack.

---

## Glossary: the words this report uses

| Term | ELI5 meaning | Real-world analogy |
|---|---|---|
| **IIoT** (industrial internet of things) | Machines with sensors that send their readings to a computer automatically. | A fitness band, but for a machine. |
| **OEE** (overall equipment effectiveness) | One percentage for how close a machine gets to "perfect" production: always running, at full speed, with no bad parts. OEE = Availability × Performance × Quality [50]. | A cricket batter's score: did they stay at the crease (availability), score fast (performance), and avoid getting out on bad shots (quality)? |
| **Availability** | Share of planned time the machine was actually running. | Share of a class period the teacher actually taught, not counting the projector breaking. |
| **Performance** | How fast it ran compared with its ideal speed. | Running a lap in 80 s when your best is 60 s gives 75%. |
| **Quality** | Share of parts that came out good. | Good rotis out of all rotis made. |
| **OEE proxy** | OEE estimated from limited sensors, so not the full official version. | A thermometer reading taken by touching someone's forehead: useful, but not lab-grade. |
| **Six big losses** | The six ways a machine loses OEE: breakdowns, setup, minor stops, reduced speed, defects, and start-up losses [49]. | Six leaks in a water tank. |
| **WIP** (work in process) | Parts that have started but not yet finished. | Plates on the table at a canteen that have food but have not yet been eaten. |
| **Throughput** | Finished parts per unit of time. | Students served per minute at the canteen counter. |
| **Cycle time / flow time** | How long one part takes from entering the line to leaving it. (Some people use "cycle time" for one station's time per part; say which one you mean.) | Your total wait from joining the queue to getting your food. |
| **Little's law** | WIP = throughput × flow time. Know any two and you get the third [54][65]. | 30 people in the queue, served at 2 per minute, so each waits about 15 minutes. |
| **CONWIP** | A rule that caps total WIP. A new part may enter only when a finished part leaves [52]. | A club bouncer letting one person in only when one comes out. |
| **Kanban** | Like CONWIP, but with a separate cap between each pair of stations [53]. | A bouncer at every room in the club, not just the front door. |
| **Bottleneck** | The slowest station, which limits the whole line. | The narrowest part of a bottle. |
| **Active-period method** | Find the bottleneck by checking which station works the longest without a break (not waiting for parts or space) [55]. | Spotting the busiest cashier by who never gets a pause between customers. |
| **Takt time** | Available time ÷ customer demand: the pace the line must keep. (unverified textbook definition, check before citing) | A metronome for the factory. |
| **Pareto chart** | A bar chart sorted from biggest cause to smallest, usually showing a few causes do most of the damage. | Finding that 2 of your 10 subjects cause most of your stress. |
| **SPC / control chart** | A chart of a measurement over time, with upper and lower limits. Points outside the limits mean "something changed, check it" [60]. | Your weekly weight chart with a "normal range" band. |
| **MTBF / MTTR** | Mean time between failures (how long it usually runs before breaking) and mean time to repair (how long fixing takes) [50]. | How often your bike chain falls off, and how long it takes to put back. |
| **PLC** | A rugged small computer that controls a machine. | The Arduino's industrial big brother. |
| **SCADA / HMI** | The operator's screen for watching and controlling machines, including alarms [1]. | The dashboard and warning lights in a car. |
| **Historian** | A database built for time-stamped sensor readings [16][27]. | A diary where every entry has the exact time written on it. |
| **Store and forward** | If the network drops, keep the data locally and send it later [1]. | Writing a WhatsApp message offline; it sends when you get signal. |
| **Edge computing** | Doing the processing close to the machine instead of in a far-away cloud [4]. | Cooking in your hostel room instead of ordering from across the city. |
| **MES** | Software that runs the shop floor: releases orders, tells operators what to do, records what was made and traces each part [6]. | The traffic police at a busy junction. |
| **MOM** | Manufacturing operations management: a wider version of MES that also covers quality, maintenance and inventory [1]. | The whole traffic department, not just one officer. |
| **ERP** | Company-wide business software: orders, money, purchasing [11]. | The college's admin office. |
| **APS** | Advanced planning and scheduling: decides what to make, when, and on which machine, without overloading any machine [7]. | A timetable maker who knows how many classrooms exist. |
| **ISA-95** | A standard that splits a factory's systems into levels, from sensors (level 0) up to business systems (level 4) [11]. | A school's org chart: students, teachers, HOD, principal, management. |
| **ISO 22400** | A standard that defines manufacturing KPIs and their formulas [51]. | An official rulebook for how to calculate marks. |
| **Message broker / MQTT** | A central post office for data. Devices "publish" messages on topics, and apps "subscribe" to the topics they need [1]. | A WhatsApp group: post once, everyone in it gets it. |
| **Unified Namespace (UNS)** | A naming scheme for broker topics so every app agrees on where data lives, often following ISA-95 levels [1]. | A postal address format everyone uses. |
| **Digital twin** | A computer model of a real system that stays updated with live data. If it runs only on assumed data, it is a simulation, not a twin [32][34]. | A live cricket scorecard app versus a video game of cricket. |
| **Digital thread** | One connected data trail from design to production to use, so a change at one stage is visible at the others [10]. | A shared Google Doc that everyone edits, versus emailing copies around. |
| **Discrete-event simulation (DES)** | A program that steps from event to event ("part arrives", "machine breaks") to predict how a line behaves [59]. | Playing out a board game on paper to see who wins before playing for real. |
| **Knowledge graph** | A database of things and how they connect ("station 2 is part of line 1") [34]. | A family tree. |

---

## The ten categories in your screenshot, in plain words

Your screenshot shows a Siemens-style menu with two columns. The menu itself gives no definitions, and we could not find Siemens pages that define each item. So these are our plain-language readings, tied to Siemens sources where possible. Treat them as explanations, not official Siemens definitions.

**Smart manufacturing column**

| Category | What it means | Where OptiProductio sits |
|---|---|---|
| **Smart manufacturing digital thread** | One connected data trail from product design, to how it is made, to what actually happened on the line. A change at one stage shows up at the others. Siemens describes this as integrating intelligence and connectivity across the whole product life cycle [10]. | Not really. You have no design data. |
| **Line automation engineering** | Designing and programming a line's automation (PLCs, operator screens, robots, conveyors), often tested on a virtual model before the real line is built. The IT/OT framework mentions related Siemens tools such as the TIA Portal-based automation framework [1]. | A little: your Arduino code is the "automation" layer. |
| **Plant process design & engineering** | Planning a whole plant or process (equipment, layout, material flow) and simulating it before anything is built. This matches Siemens' "digital twin of production" idea [8]. | A little, if you build a SimPy model of the line. |
| **Production operations & optimization** | Watching the running factory live (OEE, downtime, energy, quality) and improving it. In Siemens' range this is Insights Hub, Industrial Edge and Performance Insight [3][4][5][10]. | **This is OptiProductio's main home.** |
| **Production planning & scheduling software** | Deciding what to make, in what order, on which machine and when, within real capacity limits. Siemens' product here is Opcenter APS [7]. | Partly. Your CONWIP cap is a release-control rule, which is related but much simpler than full scheduling. |
| **MES software** | The shop-floor "traffic controller": releases work orders, guides operators, records output and quality, and traces each part [1][6]. | Partly. Counting parts and rejects is a small slice of MES. |
| **Manufacturing process planning** | Deciding how a product will be built: the steps, their order, which station does what, tools and time standards (the "bill of process"), often checked in simulation first [10]. | Only if you set "ideal cycle time" per station. That is a process-planning number. |

**Supply chain collaboration column**

| Category | What it means | Where OptiProductio sits |
|---|---|---|
| **Supply chain collaboration digital thread** | The same connected-data idea, stretched outside the factory to suppliers and partners, so design changes and demand are shared with them. | Out of scope. |
| **Logistics management software** | Moving and storing materials: goods coming in, deliveries going out, and transport inside the plant such as AGVs (self-driving carts). The IT/OT framework treats this as a site-level function [1]. | Out of scope. |
| **Supply chain management software** | Planning purchasing, stock and distribution across the whole network so materials arrive when production needs them. | Out of scope. |

So OptiProductio sits firmly in "production operations & optimization", touches MES (counting and rejects) and planning (the WIP cap), and has nothing to do with the supply-chain column. Saying this clearly in your report shows you understand where a 3-station line fits in a real factory.

---

## The platforms side by side

| Platform | What it is, in one line | ISA-95 layer | Key KPIs and methods | Cost / access for a student (Oct 2026) | Status |
|---|---|---|---|---|---|
| **Siemens Industrial Edge** | Small computers and apps next to the machines that collect, clean and process data locally [4]. | L2 (control/monitoring) to L3 | OEE monitoring, predictive maintenance, AI defect detection, virtual PLC [4] | No student tier found | Active |
| **Siemens Insights Hub** (formerly MindSphere) | Cloud IoT and AI app for production KPIs [3]. | L3 to L4 | OEE (A, P, Q, with cycle time and WIP listed under P), energy, asset health, quality prediction, "Copilot" AI agents [3] | Free trial mentioned, terms not checked (unverified, check before citing) | Active |
| **Siemens Opcenter** (Execution Discrete MES; APS) | MES for orders, quality and tracing; APS for finite-capacity planning and scheduling [6][7] | L3 | KPIs and reports; Gantt charts, scheduling rules, what-if, dispatch lists [6][7] | Enterprise licence, no student route found | Active |
| **AVEVA PI System** | The best-known industrial historian (originally OSIsoft) [27]. | L2 to L3 | Asset models, event analysis, trends, alerts [27] | Enterprise licence | Active |
| **AVEVA MES / Production Management / Insight / Predictive Analytics** | MES; loss accounting against a best sustainable rate; cloud dashboards; machine-health prediction [28][29][30][31] | L3 to L4 | OEE, schedule adherence, first-time quality, SPC; "delay accounting"; anomaly detection, time-to-failure [28][29][31] | Enterprise licence | Active |
| **Velotic Proficy** (formerly GE Vernova Proficy) | Historian, MES, Tracker, Scheduler, CSense analytics, Operations Hub dashboards, iFIX HMI/SCADA [16]–[21] | L2 to L3 | OEE, downtime, scrap, SPC, WIP visibility, finite-capacity scheduling, root cause, process twin and what-if [17]–[20] | Enterprise licence | Now owned by Velotic (TPG-backed), launched 17 Mar 2026 [12] |
| **Velotic ThingWorx** (formerly PTC) | Low-code platform for building industrial IoT apps, plus ready-made apps such as DPM and RTPPM [22][23][39] | L3 | OEE, MTBF, MTTR, downtime reason trees, bottleneck and loss ranking [22][23] | Old 120-day trial and academic routes, current status unknown after the sale [43] | Sold by PTC to TPG, sale completed by March 2026 [41][42] |
| **Velotic Kepware** | One server that "speaks" 150+ machine protocols and passes data on [15]. | L2 | Connectivity only | Free trial advertised in Velotic's menu [24] | Moved to Velotic [12] |
| **AWS IoT TwinMaker** | A service for building live digital twins: a model of your equipment, linked to live data, shown in 3D [34]. | L3 (visual and data layer) | Whatever data you connect; alarms as properties [34][37] | Needs an AWS account with a card. Free tier: 50 million data-access API calls per month for 12 months; then $0.05 per entity per month [36] | Active; no end-of-support notice found (that is not a guarantee) |
| **Azure IoT Central** | A ready-made web app for connecting devices, with dashboards, rules and email alerts [44]. | L3 | Rules on telemetry with time windows; dashboards [44] | **New apps cannot be created since 23 Sep 2026** [44] | Retiring; existing apps end after 20 Sep 2029 [44] |

All prices are vendor list prices from the pages cited. All OEE "improvement" numbers on these vendors' sites are vendor claims, with no baseline or method given.

---

## Siemens: a blueprint first, products second

### The IT/OT framework swaps the pyramid for a central "post office"

Siemens' IT/OT Framework (version 1.0, January 2026) is the most useful single document in this set for OptiProductio. It is a reference design for connecting machines (OT, operational technology) to business software (IT), and it says it is "product agnostic" [1]. Its legal page restricts copying and AI-training use, so what follows is a paraphrase, and your report should also paraphrase and cite it rather than copy passages [1].

The framework starts from ISA-95, the standard that arranges factory systems as a pyramid of levels. It points out that ISA-95 does not define data models, and that passing data up and down many pyramid levels causes delay, cost and lost information [1]. Wiring every system directly to every other system is no better, because it becomes hard to scale, secure and debug [1]. Its answer is a **central message broker**: machines publish messages on named topics, and any app subscribes to what it needs. On top of the broker sits a **Unified Namespace**, a shared naming scheme, which the framework suggests should follow the ISA-95 equipment hierarchy (enterprise, site, area, line, cell). It also notes that there is no official standard for UNS [1]. A **data repository** (historian) keeps the long-term history, because the broker usually holds only the latest values [1]. The framework is honest about the downsides. The broker becomes a single point of failure and a security target, and the first setup is more complex [1].

It keeps four levels for organising who is responsible for what: enterprise, site, cell/line, and machine. A level describes which equipment a function covers, not where its software runs [1]. Its rule of thumb is to put each app at the highest level that still works. Only fast jobs such as alarms belong at line level, and KPI calculation is better done higher up [1]. For a company with one site, site and enterprise levels can be merged [1]. That rule matters for you: a single laptop running one dashboard is a fair scaled-down version of the blueprint, not a shortcut.

The part most worth copying is the **data integration layer**, the software between the machines and everything else [1]:

1. **Southbound connectors** read PLCs, sensors and barcode readers.
2. **Harmonisation and filtering** rename fields, turn integer codes into readable states, convert units, smooth noise, and check data against a schema.
3. **Contextualisation** attaches each value to its place in the equipment hierarchy, with unit, limits and description. The framework calls this mandatory, because otherwise IT systems cannot tell where data came from.
4. **Storage** includes rolling aggregates (its example is a 15-minute average) and store-and-forward buffering for when the link drops.
5. **Northbound connectors** publish to the broker, ideally with timestamps and quality flags in every message, and with triggers such as "send everything when the machine state changes".

On security, it follows IEC 62443 and says the most important goal is keeping the plant available [1].

### Insights Hub, Industrial Edge and Performance Insight sell the KPIs

Siemens' products fill in that blueprint. Its IIoT page sells them as four steps: connect and explore, monitor and find insights, predict and optimise, then change the business model, with tracking production KPIs to improve OEE named as a core use [2]. **Industrial Edge** is the computing platform next to the machines, used for OEE monitoring, predictive maintenance, AI defect detection and even a software PLC [4]. **Insights Hub**, which "evolved" from MindSphere, is the cloud layer. Its product page splits OEE into availability (unplanned downtime), performance (throughput, **cycle time**, **work in progress**) and quality (defect rate, rework) [3]. That is a useful reference for you, because it lists cycle time and WIP right next to OEE, which is exactly OptiProductio's KPI set. Insights Hub also has energy, asset health, quality prediction and "Production Copilot" AI agents for root-cause analysis [3]. **Performance Insight**, a smaller SIMATIC app, calculates OEE, MTBF, MTTR and TEEP, lets users write custom KPI formulas, and offers chart, value, gauge, pie, heatmap and Gantt widgets [5]. Siemens names these KPIs but does not publish the exact formulas, for example how "ideal cycle time" is set [3][5].

### Opcenter covers the MES and scheduling jobs

**Opcenter Execution Discrete** is Siemens' MES. It tracks production, runs work orders against bills of materials and process, handles non-conformances and root cause, and traces each component [6]. **Opcenter APS** has two halves [7]. Planning works in time buckets (day, week, month). Scheduling is "bucketless": it loads each order onto real machines with finite capacity and several constraints, shows the result as a Gantt chart, supports what-if comparison, and outputs a dispatch list for each machine. Its stated aims are better utilisation, fewer setups, less inventory and WIP, and better on-time delivery [7]. Siemens does not say which algorithms it uses.

The bigger umbrella is **Xcelerator**, which describes a "comprehensive digital twin" in three parts: a twin of the product, a twin of production (lines and whole plants planned digitally), and a twin of performance (fed by real operating data) [8].

### The TotalEnergies case is a story, not a result

The March 2026 Insights Hub blog on TotalEnergies Gas Mobility describes capturing technicians' diagnostic know-how as reusable AI-agent "skills" across hydrogen and bioCNG refuelling stations [9]. Its only result-like statement is that quality is emerging as a leading driver of low OEE. It gives no percentages, station counts or savings, and its author attribution is inconsistent on the page [9]. Do not cite any number from it. The useful idea is the pattern: break OEE into its parts, find which part hurts most, and when an issue is detected, show the user context and a recommended action [9]. Siemens' own product page also carries customer quotes, for example Vorwerk reporting OEE improvement of "around 3 to 5%" with 500 machines connected. These are vendor claims [3].

---

## AVEVA: the historian comes first, and losses are counted in time

AVEVA's portfolio is built around the **PI System**, the historian that came from OSIsoft. It collects sub-second sensor data, buffers it through network drops, stores it with asset models and events, and shows it in PI Vision dashboards [27]. AVEVA says PI is used by all of the top 25 pharma companies and by over 1,000 utilities. These are vendor claims [27].

On top of the historian, **AVEVA MES** handles paperless shop-floor execution: operator task screens, work orders, recipe enforcement, SPC quality sampling and material genealogy [28]. It claims "OEE +15% to 20%" for unnamed customers, which is a vendor claim with no baseline [28]. **AVEVA Production Management** is the one to learn from. It uses "delay accounting", which means every minute of downtime, slow running or quality loss is logged against a maximum sustainable rate (MSR), and its KPI engine recalculates when late data arrives [29]. That is OEE thinking expressed in time: measure the gap between actual output and the best sustainable output, then put every lost minute in a category. **AVEVA Insight** is the cloud dashboard layer, with alerts to phone and desktop and unsupervised machine learning to flag unusual patterns [30]. **AVEVA Predictive Analytics** learns how a healthy machine behaves and flags deviations, which AVEVA says can come "weeks or months before failure" [31]. **AVEVA Process Simulation** is a physics-based simulator for chemical and process plants, mainly relevant to continuous industries rather than a discrete line like yours [33].

AVEVA's digital-twin page gives the clearest definition in this whole set. A twin is a synchronised replica of an asset or process. A **simulation** runs on assumed or historical data, while a **digital twin** stays connected to live data [32]. Use this line in your viva. A SimPy model is a simulation. It becomes a twin-like tool only when it is fed and checked with live data from your line.

---

## GE Vernova Proficy is now Velotic, and ThingWorx came with it

### Who Velotic is

Velotic launched on 17 March 2026 as an independent industrial software company backed by TPG. It combines **Proficy** (from GE Vernova) with **Kepware** and **ThingWorx** (from PTC), and TPG's purchases of those businesses closed at launch [12]. The press release gives revenue of more than $300 million, a Boston-area headquarters, Brian Shepherd as CEO and former PTC CEO James Heppelmann as executive chairman [12]. Velotic's own About page claims 1,200+ employees and 8,000+ active customers. These are vendor claims [13]. On the PTC side, TPG agreed in November 2025 to pay up to $725 million for Kepware and ThingWorx [41], and ARC Advisory reported the sale complete in March 2026 [42]. The TPG release does not say whether GE Vernova or PTC kept any stake, so do not claim either way.

### What the Proficy and ThingWorx products do

| Product | Plain meaning | Ideas you can borrow |
|---|---|---|
| **Kepware** | A translator that talks to over 150 kinds of machine protocol [15]. | Your Python serial reader is a one-protocol Kepware. |
| **Proficy Historian** | Time-series database with store-and-forward buffering, on-site or in the cloud [16]. | Log raw events first, never edit them, compute KPIs on top. |
| **Proficy Smart Factory MES** | Runs the floor: orders, materials, quality checks, genealogy. Tracks OEE and its parts, downtime, scrap, schedule adherence, and uses SPC and alarms [17]. | The A × P × Q card and SPC on cycle time. |
| **Proficy Tracker** | Follows each part through the plant and gives real-time **WIP visibility** "to reduce excess inventory, avoid shortages and support Lean" [18]. | WIP per buffer, which is the base for your CONWIP alert. |
| **Proficy Scheduler** | Finite-capacity scheduling with what-if comparison and bottleneck visibility [19]. | A toy schedule page, later. |
| **Proficy CSense** | Analytics in five steps: Analyze, Monitor, Predict, Simulate, Optimize. Includes a process digital twin for testing changes before making them [20]. | The five verbs as tab names. |
| **Proficy Operations Hub** | Low-code builder for role-based dashboards [21]. | Separate "operator" and "engineer" views. |
| **ThingWorx DPM** (Digital Performance Management) | Finds the bottleneck automatically, ranks losses by how much throughput they cost, and tracks fixes until the hours are recovered [22]. | Rank losses by minutes of output lost; keep a small "actions" table. |
| **ThingWorx RTPPM** | Ready-made OEE dashboards with drill-down by asset, line, shift and crew, plus MTBF, MTTR and downtime **reason trees** [23]. | A reason code for each breakdown, and a Pareto chart. |

Velotic's site carries many vendor claims, for example NEI's OEE rising from 78% to 81% with 500+ machines connected across 2 plants, with no timeframe given [25], and homepage stat callouts such as "15%+ OEE" for Bharat Forge [24]. Present these only as vendor claims.

### The Velotic whitepaper and the GE Vernova twin blog

Velotic's whitepaper *Why AI still falls short on the plant floor* (2026) has no numeric results. It is useful for its examples [14]. It lists questions a plant manager might ask, such as why Line 5's output is lower this morning than yesterday's first shift, or to break down short stops in a time window by reason code [14]. It describes a default dashboard: hourly throughput, scrap by product, and downtime split between changeovers and mechanical stops [14]. It also argues that industrial AI should be explainable, auditable and built into existing HMI, MES and historian screens rather than sitting in a separate tool [14]. That supports showing *why* each alert fired on your dashboard.

The older GE Vernova blog by Steve Pavlosky says process digital twins in CSense let plants test changes in simulation before applying them, and it gives anonymised results such as a 33% drop in product-weight complaints and a 10% throughput increase [26]. These are vendor claims with no names, baselines or method. His practical advice is more useful: start with "low-hanging fruit", expand in phases, and move off paper and Excel data collection [26]. Note that in this blog "simulation" means a data-driven process model, not the discrete-event line simulation taught in IE courses [26].

---

## What is AWS IoT TwinMaker?

**In one sentence:** AWS IoT TwinMaker is an Amazon Web Services cloud service for building a live digital copy of a factory or building. You describe your equipment as a family tree of "entities", link each one to its live sensor data, and show the result as a clickable 3D model or a dashboard [34].

**The analogy:** think of Google Maps for a factory. There is a 3D map of the plant, each pin on it shows a live reading (and turns red when something is wrong), and behind the map sits a database of what is inside what.

**How it works, in five pieces** [34]:

1. A **workspace** is the project folder. It is tied to an S3 storage bucket, and access is controlled with IAM roles.
2. **Entities** are the things: a factory, a line, a mixer, a conveyor. They form a hierarchy, which AWS calls a knowledge graph.
3. **Components** attach data to an entity. A component type is a JSON template (for example "cookie line machine"), and it can pull live data through a connector. AWS provides a built-in connector for its IoT SiteWise service; other data stores need a small Lambda function that you write [35].
4. **Properties** are the values: fixed ones (a serial number), time-series ones (temperature over time; TwinMaker stores only a pointer to where that data lives), and relationships to other entities [34].
5. **Scenes** are 3D views built from glTF/glb model files. A **tag** pins an x, y, z point in the scene to an entity's property, and can change colour on an alarm [34].

Dashboards come from a Grafana plug-in or from AWS's open-source React library, iot-app-kit [34][37]. AWS warns that TwinMaker should not replace human monitoring in safety-critical settings [34].

**The Cookie Factory v2 sample.** This is AWS's showcase app, "Bakersville Cookie Factory Digital Twin Monitoring Application" [37]. It is a React web app built on iot-app-kit; the older v1 sample used Grafana instead [37]. Its model has 132 entities: a factory, rooms, 25 mixers, and cookie lines made of a cookie former, freezer tunnel, conveyors, liner, box erector, labelling belt and box sealer [37]. Line machines carry time-series properties such as speed, temperature, alarm status and alarm message. A "process step" component has a `flowTo` list that records which step feeds which [37]. The data is not from a real factory. A Lambda function replays a JSON-lines file of fake telemetry every 10 seconds by default, and sample videos stand in for the mixer-room cameras [37]. Alarms are just properties in the replayed data, not a separate rules engine [37]. To deploy it you need an AWS account, Node 16+, AWS CDK 2.76 or later and Docker 20+. It runs only in us-east-1, us-west-2 or eu-west-1, so not in AWS's Mumbai region. It also creates Timestream, Kinesis Video Streams, Lambda, Cognito and S3 resources, which can bill you until you run `cdk destroy` [37].

**Cost and status.** TwinMaker's free tier gives 50 million data-access API calls per month for the first 12 months, and new customers from 15 July 2025 get up to $200 in free-tier credits. After that, the standard plan is $0.05 per entity per month [36]. By our arithmetic, a 6-entity model of OptiProductio would cost about $0.30 a month in entity fees. The side services in the Cookie Factory sample are extra, and we did not price them. We found no end-of-support notice for TwinMaker [34][36]. A related AWS alarm service, IoT Events, stopped taking new customers in May 2025 and lost support on 20 May 2026 [38], so check TwinMaker's status again before relying on it.

**Should OptiProductio use it?** Not for the 1 November build. The learning that matters for an IEM project (OEE, Little's law, CONWIP) lives in your Python logic, not in AWS setup. Four ideas are worth copying into plain Python:

1. A typed data model: one "station type", three station instances, each with a `flow_to` link, all read from one config file.
2. Alarms as properties: each station has a `state` and the line has an `alarm_status` and a message.
3. Tags bound to live data: your three.js model can recolour each station from the latest reading.
4. A replay mode that streams a saved CSV into the dashboard, as the synthetic connector does [37].

If a mentor has an AWS account later, deploying the sample once and destroying it the same day would give you real screenshots for the report.

---

## ThingWorx and Azure IoT Central: same idea, uncertain futures

**ThingWorx** is a low-code builder for industrial apps. Its building blocks are **Things** (a machine, product or process), **Thing Templates** (the blueprint a Thing inherits from) and **Thing Shapes** (sets of properties, services and events that can be mixed into templates) [39][40]. Change a shape, and every Thing that uses it changes too [40]. Think of LEGO: define a brick type once, then stamp out many machines. A 3-station line would be a `CountingStation` shape, a `StationTemplate`, three station Things, and a `Line1` Thing with a WIP property and a rule that fires above the cap (our modelling, not a PTC example). Free access used to come through a trial page (last updated in 2022) and academic programmes. After the TPG sale, we do not know whether those routes still work [43].

**Azure IoT Central** was Microsoft's "pre-furnished flat" for IoT. You defined a **device template** (telemetry, properties, commands), connected devices, and got dashboards, rules and email alerts out of the box [44]. Its rule example uses a time window, for example a 5-minute aggregate, so you get at most one email per device every five minutes. That is a simple way to stop alert spam, and worth copying [44]. But **new IoT Central apps cannot be created from 23 September 2026**, and existing ones stop after 20 September 2029. Microsoft now points users to Azure IoT Hub plus Microsoft Fabric [44]. Treat it as history.

The common thread across all three platforms is "type, then instance": component type and entity, Thing Template and Thing, device template and device [34][39][44]. You can copy that pattern with a Python dataclass. Also note what the retirements and the sale suggest: big vendors are stepping back from turnkey IoT app platforms. That is our reading of the evidence, not something any vendor said. It is another reason not to build a short student project on one of them.

---

## What the four supplied documents say, and how far to trust them

None of the four is independent academic research. Rank them by evidence weight: the Microsoft survey first (biggest sample, method disclosed), then Verdantix (structured method, but a vendor-licensed reprint), then ARC on Audi (one case, part-sponsored, no measured results), then Cisco (marketing).

### Microsoft Digital Operations Signals (July 2023): adoption has moved past pilots

Microsoft wrote this with the research firm IoT Analytics, from a survey of 300 people at manufacturing firms between October and December 2022. Respondents were split evenly across North America, Europe and Asia-Pacific (mostly China and Japan), and 66% worked at firms with more than 5,000 employees [45]. Interviewees were selected by Microsoft, and India barely appears [45].

Its main claim is that industrial IoT has "crossed the chasm" into the early majority [45]. Key numbers, with their caveats:

- "65% of organizations are now executing an IoT strategy." The body text says this figure comes from the previous (2022) report [45].
- "14% higher success rate than five years ago". The underlying data is 43% of recent projects exceeding expectations against 38% of older ones, a 5 percentage-point gap, on a subsample of 141 [45]. Quote it as 5 percentage points; "14%" is the relative change.
- Median break-even fell from 24 to 20 months (N=141) [45].
- Barriers shifted. For recent projects, missing end-user skills rose to 28% and cyber threats to 22%, while constrained budget fell to 16% [45]. The summary page gives 24% for the talent gap, so the report contradicts itself slightly [45]. It also gives 79% of assets connected on one page and 76% on another [45].
- In smart operations (n=192), the use case most often custom-built was **production planning and scheduling** (67% built in-house, n=83) [45]. **Digitally assisted shopfloor dashboards** appear as a separate use case (n=29), most often bought and integrated (55%) [45]. Those sample sizes are small.
- Physical device connection was a minor pain point (14%), but interviewees said mapping physical assets to logical devices is manual and time-consuming [45]. That is a hint to keep a clean sensor-to-station mapping table.
- Practical advice: start a proof of concept with one to five scenarios, for example on part of a line, and "define business process first" [45].

The survey also includes one unnamed partner anecdote: a 10% OEE improvement and a 20–30% cut in unplanned downtime [45]. That is a vendor-interview claim, not survey data. The report says nothing about CONWIP, WIP caps or Little's law.

### Audi EC4P (ARC Advisory, January 2026): move the logic to software, keep safety local

David Humphrey's ARC paper describes Audi's "Edge Cloud 4 Production". Audi is replacing thousands of shop-floor industrial PCs, and now hardware PLCs, with virtual machines on standard servers in data centres 6–13 km from the plants, linked by a redundant software-defined network [46]. The partners are Cisco, Broadcom (VMware) and Siemens [46]. Examples include a virtual Siemens PLC running axle pre-assembly stations for the Audi e-tron GT, and a certified failsafe virtual PLC for body-shop robot cells [46]. The reasons given are lower hardware and energy cost, easier updates, built-in cybersecurity, and readiness for AI [46]. The paper names OEE (availability × performance × quality) as a key metric and says OEE is "likely" to improve with less hardware to maintain [46]. That is a prediction, not a measured result.

Caveats: the paper is sponsored in part by Audi, your copy is printed from siemens.com (Siemens is one of the three suppliers it describes), and it gives **no figures** for savings, OEE change or payback [46]. The lessons for you are the split of jobs and the people side. Audi keeps safety and motion control on strict real-time control, while visualisation and production management "have less stringent requirements" [46]. So OptiProductio's emergency stop, if any, should stay on the Arduino side, and the dashboard should only monitor and alert. The paper also says that bringing IT and OT together starts with bringing the people together, and Audi set up a 24x7 team with both skill sets [46].

### Verdantix Green Quadrant 2025: industrial AI is scored on optimisation and maintenance

Verdantix compared 19 industrial AI analytics vendors on 14 capability and 7 momentum criteria. It used a 105-point questionnaire, two-hour demos and 11 buyer interviews, with weights informed by a survey of 304 decision-makers [47]. Nine vendors came out as Leaders: ABB, Augury, AVEVA, C3 AI, Cognite, GE Vernova, IBM, Seeq and SymphonyAI [47]. Siemens did not actively take part and was assessed from public information. Reading the chart by eye, it sits among the Specialists, but dots near the lines are hard to place, so check before quoting [47]. The two heaviest capability weights are **process and production optimisation (16%)** and **predictive maintenance (16%)**. Visualisation and reporting gets 4% [47]. Verdantix says the market is moving "from pilots to enterprise-wide platforms" and that plain dashboards are no longer enough on their own [47]. Its questionnaire asks how data errors, missing values and inconsistencies are caught at ingestion, and which KPIs the system tracks [47].

Caveats: your copy is ABB's licensed reprint, containing only ABB's full profile. Verdantix says it does not endorse vendors and cannot check every vendor claim [47]. The reprint also mentions a "DIY MING stack" as the alternative to commercial platforms without expanding the acronym. It is commonly read as MQTT, InfluxDB, Node-RED and Grafana (unverified, check before citing) [47].

### Cisco Industrial IoT brochure (2026): know your devices, limit who talks to whom

Cisco's brochure is a catalogue of rugged switches, routers, wireless and security products [48]. It frames an industrial IoT setup as four pillars (network connectivity, device management, data control and exchange, edge computing) wrapped in security [48]. Its security ideas are asset visibility (knowing every connected device), IEC 62443 "zones and conduits" (restricting what can talk to what), and least-privilege remote access [48]. Its edge data pipeline is Extract, Transform, Govern, Deliver [48]. The brochure claims 67,000 customers and quotes a customer gaining "over 10 percent" floor productivity within a month. These are unaudited testimonials [48]. **It does not mention the Purdue model**, so if your slides need the Purdue or ISA-95 level diagram, cite an ISA-95 source instead [11]. At your scale, Cisco's lessons become four habits: keep a list of every device and sensor, keep the Arduino on USB or a closed local network, send only the data you need, and watch for a dead link or a stuck sensor.

### What all four agree on

All four describe the same layering: devices, then network or edge, then a data platform that ingests, cleans and adds context, then applications, then people [45][46][47][48]. All four stress OEE, downtime, throughput and quality. All four give the same non-technical advice: start small, define the process first, train the users. None of them discusses CONWIP, WIP caps or Little's law. Your report has to justify those from operations-management sources.

---

## The OR and IE methods underneath the platforms

This is the section to lean on in your viva. Each method below shows up inside commercial products, and each has a free Python route.

### OEE and the six big losses

The six big losses come from Seiichi Nakajima's work on Total Productive Maintenance (1988) [49]. They map onto OEE like this [49]:

| OEE part | Losses in it | What OptiProductio measures |
|---|---|---|
| Availability | Breakdowns; setup and adjustment | Breakdown button press-to-release time |
| Performance | Idling and minor stops; reduced speed | Actual cycle time vs an ideal cycle time you set |
| Quality | Defects and rework; start-up losses | Reject button count |

ISO 22400-2 keeps the A × P × Q structure and defines the time terms behind it, such as planned busy time and actual unit downtime [50]. The usual student formulas are Availability = run time ÷ planned time, Performance = (ideal cycle time × total count) ÷ run time, and Quality = good count ÷ total count. We could not confirm that these match the ISO 22400 wording exactly, because the standard is paywalled (unverified, check before citing) [50][51]. Because Performance needs an ideal rate, call your number an **"OEE proxy"** unless you define and justify the ideal cycle time. Vendors use OEE everywhere (Siemens, AVEVA, Proficy, ThingWorx, Audi) [3][17][23][28][46], but none of the pages we read gives its formula.

### Little's law and the Factory Physics view of a line

Little's law says WIP = throughput × flow time [54][65]. If your IR counters give any two of the three, the third follows, and comparing the measured flow time with WIP ÷ throughput is a quick check that your sensors are not missing parts. *Factory Physics* by Hopp and Spearman is the standard IE textbook that applies this to production lines, including the "best case / worst case / practical worst case" curves of throughput against WIP (edition details unverified, check before citing) [54].

### CONWIP and kanban

CONWIP caps total WIP on the whole line with one shared set of "cards". A part enters only with a card, and the card returns when a finished part leaves the last station [52][53]. Kanban uses a separate set of cards between each pair of stations [53]. Spearman, Woodruff and Hopp introduced CONWIP in 1990 and argued it is simpler to set up than kanban [52]. A systematic review by Jaegler and colleagues covers how the idea has been used since [67]. The closest published idea to a monitored WIP-cap alert is Hopp and Roof's "statistical throughput control" for setting WIP levels in CONWIP lines (details unverified, check before citing) [66]. On the vendor side, the nearest feature we found is Proficy Tracker's real-time WIP visibility [18] and Opcenter APS's aim of reducing WIP [7]. Neither describes a CONWIP cap alert.

### Bottleneck detection: the active-period method

Christoph Roser's active-period method marks each station as **active** (working, broken, under repair, or in changeover) or **inactive** (starved of parts or blocked by a full buffer). At any moment, the station with the longest unbroken active period is the bottleneck. Where two stations' active periods overlap, the bottleneck is "shifting" between them [55][56][57]. It needs exact state timestamps for each station, which your IR sensors and breakdown buttons can give. There is a Python package on PyPI [71], and AllAboutLean has a worked example with data and solution that is good viva material [55]. ThingWorx DPM and Proficy Scheduler both advertise bottleneck finding but do not say how they do it [19][22].

### Scheduling

APS products such as Opcenter APS and Proficy Scheduler do finite-capacity scheduling with Gantt charts and what-if comparison [7][19]. The textbook version is the job-shop problem: several jobs, each a fixed sequence of tasks on given machines, with the goal of finishing the last job as early as possible (minimising makespan). Google OR-Tools solves it with its CP-SAT solver in an example of about 100 lines of Python [58]. The simpler alternatives used on MES dispatch lists are rules such as SPT (shortest job first), EDD (earliest due date) and FIFO [61]. A 3-station line making one product is a trivial scheduling case, so a toy job shop with a few products on different routings shows the method better.

### Simulation and the "digital twin"

Discrete-event simulation steps through events such as "part arrives" and "machine breaks" to predict how a line will behave. SimPy is a free Python library for this, MIT-licensed, where stations become Resources and parts become processes [59]. The vendors' "digital twin" ranges from 3D models linked to live data (TwinMaker [34]) to data-driven process models (CSense [20][26]) to physics-based plant simulators (AVEVA Process Simulation [33]). For a student, what turns a SimPy model into something you can honestly call twin-like is **calibration and checking**. Feed it your measured cycle times and breakdown rates, then compare its predicted throughput with what your real line produced. AVEVA's distinction (simulation uses assumed data, a twin stays connected to live data) is the line to quote [32].

### SPC

Shewhart control charts plot a measurement over time with limits, usually at ±3 standard deviations. For OptiProductio, an individuals chart on cycle time and a p-chart on the reject fraction per time window are the natural choices (reference: Montgomery, edition unverified, check before citing) [60]. AVEVA MES and Proficy MES both list SPC [17][28].

### ISA-95 and ISO 22400: the vocabulary that makes the project look professional

ISA-95 (also IEC/ISO 62264) is the standard for joining business systems and control systems. Its levels run from L0 (the physical process) and L1 (sensing) through L2 (monitoring and control, such as PLCs and SCADA) and L3 (manufacturing operations: MES/MOM) to L4 (business planning: ERP) [11]. ISO 22400-2:2014 defines KPIs for manufacturing operations, giving each one's formula, unit and user group. The standard is marked "to be revised" [51]. Its list includes availability, performance rate, quality ratio, throughput rate, scrap ratio, MTBF, MTTR and others [50]. Mapping OptiProductio onto these is cheap and adds a lot of credibility:

| ISA-95 level | OptiProductio part |
|---|---|
| L0 – L1 | Parts on the line; IR sensors, breakdown and reject buttons |
| L2 | Arduino UNO firmware; Python serial reader (the mini data integration layer) |
| L3 | CSV/SQLite event log (historian) and Streamlit dashboard (KPIs, alarms) |
| L4 | Not built. The Bosch Kaggle history plays the "offline analytics" role. |

### Predictive analytics on history

AVEVA Predictive Analytics and CSense both learn normal behaviour from history and flag deviations [20][31], and Verdantix calls this "predictive analytics" [47]. Your Bosch Kaggle data fills this role. If you want a second public dataset later, AI4I 2020 (10,000 synthetic rows with five failure modes, CC BY 4.0) suits downtime and failure modelling, and SECOM (1,567 rows of semiconductor process data with pass/fail labels, CC BY 4.0) suits quality and SPC [62][63].

---

## What OptiProductio should borrow, skip, and claim

Today is 24 October 2026, so the build is due in eight days. The "before 1 Nov" list is deliberately short and uses only data your hardware already produces.

### Before 1 November (in priority order)

1. **A clean raw event log, the "mini historian".** Have the Python serial reader timestamp every Arduino event, give it a readable name, flag suspicious values (such as a double count within a few milliseconds), and append it to CSV or SQLite. Never edit raw rows; compute KPIs on top. This copies the data integration layer and historian idea [1][16][27]. A suggested row: `ts, line, station, event_type (count | reject | breakdown_start | breakdown_end), value, quality (good | suspect)`.
2. **OEE proxy shown as A × P × Q, with formulas printed on screen.** Show the three parts as separate tiles so a viewer can see which one drags OEE down, as Insights Hub and RTPPM do [3][23]. State your ideal cycle time and where it came from.
3. **MTBF and MTTR from the breakdown button.** Each press and release gives one failure and one repair time [5][23].
4. **A CONWIP alarm that behaves like a real SCADA alarm.** WIP = parts released at station 1 minus parts completed at station 3. Add a warning level (for example 80% of the cap) and an alarm level at the cap, with colour, timestamp, an "acknowledge" button and an alarm log [1]. Add a short suggested action next to it, such as "hold release at station 1; check station 2", borrowing the "detect, then recommend" idea [9]. Wait a few seconds before raising the alarm so it does not flicker, as IoT Central's time window does [44].
5. **A Little's-law check tile.** Show measured average flow time next to WIP ÷ throughput. If they disagree a lot, a sensor is missing parts [54][65].
6. **A replay mode.** A toggle that streams a saved CSV into the dashboard, so the demo still works if the Arduino or USB cable fails during the viva. This is the Cookie Factory's synthetic-replay trick [37].
7. **One config file for the line.** List each station's id, name, sensor pin, `flow_to` and ideal cycle time, plus the line's WIP cap. Both Streamlit and the three.js model read from it [37][45].
8. **ISA-95 mapping and ISO 22400 names in the report.** Use the level table above and a KPI table with columns for KPI name, formula, and the sensor or button that supplies it [11][51].

### After 1 November (later)

1. **Downtime reason codes and a Pareto chart**, mapped to the six big losses [23][29][49].
2. **Active-period bottleneck finder**, showing each station's share of time as the bottleneck [55][71].
3. **SimPy what-if model.** A slider sets the WIP cap from 1 to 10, and the chart shows throughput and flow time against WIP. Calibrate it on your measured line data and report simulated against real throughput [54][59].
4. **SPC charts:** an individuals chart on cycle time and a p-chart on rejects [60].
5. **Shift report button** that exports a KPI table (planned time, downtime, counts, A/P/Q, throughput, average WIP, MTBF/MTTR) [50].
6. **Operator vs engineer views**, as Operations Hub and RTPPM offer [21][23].
7. **Optional MQTT** with a local Mosquitto broker and ISA-95-style topic names such as `rvce/ielab/line1/station2/count`, to show the broker and Unified Namespace idea [1][64]. Only worth it if someone already knows the tools.
8. **Toy OR-Tools schedule page**, comparing CP-SAT with FIFO and SPT on a few made-up jobs, drawn as a Gantt chart [58].
9. **Small "actions" table** (problem, action, date, KPI before and after), copying ThingWorx DPM's closed loop [22].

### Skip: overkill for a 3-station first-year line

- **Cloud IoT platforms** (Insights Hub, TwinMaker, IoT Central, ThingWorx). They cost money or are closed to new users, and the learning sits in your Python logic, not the platform [36][44][43].
- **Virtual PLCs, VMware, redundant network fabrics, off-site data centres** (Audi). These solve multi-plant scale and safety certification problems you do not have [46].
- **Rugged switches, SD-WAN, Cisco Cyber Vision and similar enterprise security products** [48].
- **Agentic AI, multimodal AI and RAG** (Verdantix's newer categories) [47].
- **Full APS or MES software.** A 3-station single-product line has nothing to schedule beyond the WIP cap.
- **Grafana, Node-RED, InfluxDB, FUXA** as replacements for Streamlit. They duplicate what you already have.
- **Formal business case and vendor selection.** A one-paragraph cost note is enough [45].

### OptiProductio's own angle

What the team can honestly claim as its own:

1. **A CONWIP WIP-cap alert built into a live line dashboard.** On every product page and document we read, WIP shows up only as something to see (Tracker) or reduce (APS). None of them advertises a CONWIP cap alert [7][18]. Say "we did not find it advertised", not "nobody does it".
2. **Formulas you can see.** Vendors name their KPIs but do not publish the formulas [3][5]. OptiProductio prints every formula next to its number and ties each to a standard.
3. **Your own before/after numbers with a baseline.** Vendor OEE claims (AVEVA "+15–20%", NEI 78% to 81%) come without baselines or methods [25][28]. If you run the line with and without the cap and report both, your evidence is more transparent than theirs, even at tiny scale.
4. **A teaching-scale copy of the industry stack.** It has the same layers as the IT/OT framework and the supplied documents [1][45][47], but built from an Arduino and free Python tools. That speaks to the skills gap the Microsoft survey names as a top barrier [45].

---

## Front-end lessons from Velotic

You treat velotic.com as your front-end reference. Be aware that **we could not capture the site's visual styling from here.** The browser and direct downloads were blocked by this session's network proxy, and the text tool we used strips out CSS. So we have no screenshots, colours, fonts, spacing or animations, and we have not guessed any. What we could read is the page structure and the writing style, which is what makes a site feel organised anyway.

**What we could confirm about the structure** [24][25]:

- The top menu has five items: Solutions, Products, Learn & Support, Partners, Why Velotic. The Solutions menu is split three ways: by business goal, by industry and by technology [24].
- The homepage runs from a short hero ("Turn Industrial Intelligence into action", one "Get in touch" button), to a product trio, outcome cards, a customer logo strip, **big-number stat callouts**, case-study cards and a resource library [24].
- Every product page follows the same template: hero, overview, how to get started, core capabilities (6–8 items with images), related products, resources, case studies, then an FAQ accordion [16][17][20][21].
- The business-goal page uses a "The Challenge" section followed by a "What Progress Looks Like" section with stat callouts, then product cards that each have the same three labelled fields [25].
- Headlines are short, two-part and parallel ("Three proven products. One industrial purpose."), and buttons start with a verb [24].

**How to copy this in Streamlit** (our suggestions):

1. A one-line headline that states the line's status, then a row of 4–5 big-number tiles (count, throughput per hour, average cycle time, WIP vs cap, OEE with A/P/Q), then charts below.
2. Tabs named with verbs, borrowing CSense's sequence: Monitor, Analyze, Predict, Simulate, Improve [20].
3. One card per station with the same three fields every time (status, cycle time, role in line).
4. A "challenge, then progress" story on the landing tab: manual tallying and hidden WIP, then your own before/after numbers.
5. An FAQ section at the bottom using `st.expander`, explaining OEE, CONWIP and Little's law.
6. The same order on every tab (title, tiles, chart, explanation). Consistency is most of why the site looks polished.

**Checklist for inspecting velotic.com yourself in a browser:**

1. Open velotic.com in Chrome and take full-page screenshots of the homepage, one product page (such as Smart Factory MES) and the "Optimize production performance" page.
2. Right-click a headline, choose **Inspect**, open the **Computed** tab and note `font-family`, `font-size`, `font-weight` and `line-height`. Repeat for body text and buttons.
3. In the same panel, note `color` and `background-color` for the page background, headings, buttons and stat numbers. A colour-picker extension such as ColorZilla speeds this up.
4. Note the spacing: padding inside cards, gaps between sections, and the maximum content width.
5. Scroll slowly and note any motion: fade-ins, counters that animate up, hover effects on cards and buttons.
6. Resize the window to phone width and see how the tiles and menu rearrange.
7. Write down 3–5 colours and 2 fonts, then set them in Streamlit's `.streamlit/config.toml` theme (primary colour, background, text, font).
8. Copy the layout ideas, not Velotic's logo, images, text or brand, since those belong to Velotic.

---

## How this connects to our paper idea

The earlier research looked at a possible short paper using the Bosch Kaggle data. The idea is to rebuild WIP, flow time and throughput from the Bosch station timestamps, test whether parts entering a crowded line fail more often, and backtest a CONWIP-style WIP-cap alert against bursts of failures. In what that search covered, nobody had done this; existing Bosch papers are mostly failure-prediction models, and the closest ones turn the dates into lead-time features [68][69]. The literature suggests any WIP effect will be small and may only appear above a threshold [72]. The main risks are reverse causation (failures cause rework, which raises WIP) and product-mix confounding. Because the Bosch line was not run under CONWIP, the most the paper can claim is that a WIP threshold *would have flagged* later failure bursts with some measured precision and recall. It cannot claim that a cap would have prevented failures [52][66]. The Kaggle data-use rules still need to be read while logged in.

This report adds industry context to that plan. Real platforms show WIP and OEE side by side [3][18], but none of the product pages we read advertises a WIP-cap alert. That makes the alert a fair research angle for the live line and for the Bosch backtest. Keep the order the same as before: finish the EL build by 1 November first. After that, the earlier report's best-fit target was the 4-page work-in-progress track at IEEE CONECCT 2027 in Bengaluru, with a deadline expected around February 2027, inferred from the 2026 edition [70].

---

## Open items to verify before citing

1. **ISO 22400 exact formulas and symbols.** The standard is paywalled; our formulas are the common textbook versions [50][51].
2. **Siemens category definitions.** The screenshot explanations are our readings, not Siemens text.
3. **Insights Hub free trial terms** and whether any Siemens academic access fits a first-year project.
4. **ThingWorx trial and academic access after the TPG sale** [43].
5. **TwinMaker's future.** We found no end-of-support notice, which is not a guarantee. Also check whether Amazon Timestream, which the Cookie Factory sample uses, still accepts new customers [36][37].
6. **Whether GE Vernova or PTC kept any stake in Velotic** [12].
7. **Velotic visual styling** (colours, fonts, motion). Use the browser checklist above.
8. **Verdantix quadrant placements other than the nine Leaders**, which were read by eye from a chart [47].
9. **The "MING stack" expansion** in the Verdantix reprint [47].
10. **Textbook details** for Factory Physics, Montgomery and Pinedo (editions and page numbers) [54][60][61], and Hopp and Roof's 1998 paper [66].
11. **Bosch Kaggle data-use rules**, from the competition's rules tab.
12. **Licences** for Node-RED, Mosquitto, InfluxDB and Grafana, if you mention them, from each project's LICENSE file.
13. **Your own cost estimate** for the hardware. No source in this set gives one.

---

## References

[1] Siemens AG. (2026). *IT/OT framework* (Application example, Entry ID 109998257, V1.0) [PDF]. Siemens Industry Online Support. https://support.industry.siemens.com/cs/ww/en/view/109998257

[2] Siemens. (n.d.). *Industrial internet of things (IIoT)*. https://www.siemens.com/en-us/solutions/industrial-internet-of-things-iiot/

[3] Siemens. (n.d.). *Insights Hub*. https://www.siemens.com/en-us/products/insights-hub/

[4] Siemens. (n.d.). *Industrial Edge*. https://www.siemens.com/en-us/products/industrial-edge/

[5] Siemens. (n.d.). *SIMATIC Performance Insight*. https://www.siemens.com/en-us/products/simatic-apps/performance-insight/

[6] Siemens. (n.d.). *Opcenter Execution Discrete*. https://www.siemens.com/en-us/products/opcenter/execution/discrete/

[7] Siemens Digital Industries Software. (n.d.). *Opcenter APS* [E-book]. https://assets.new.siemens.com/siemens/assets/api/uuid:87f07fef-52c5-4349-a7f4-95f5733a0646/siemens-sw-opcenter-aps-e-book.pdf

[8] Siemens. (2025, June 3). *The comprehensive digital twin explained*. Siemens Xcelerator Blog. https://blogs.sw.siemens.com/xcelerator/2025/06/03/the-comprehensive-digital-twin-explained/ (author not recorded)

[9] Thompson, R. (2026, March 30). *How TotalEnergies Gas Mobility is scaling hydrogen and bioCNG refueling operations with connected data and agentic AI*. Siemens Insights Hub Blog. https://blogs.sw.siemens.com/insights-hub/2026/03/30/how-totalenergies-gas-mobility-is-scaling-hydrogen-and-biocng-refueling-operations-with-connected-data-and-agentic-ai/ (the page also lists Eric Mitchell as author; attribution unverified, check before citing)

[10] Siemens. (2025, January 10). *Boosting profits with smart manufacturing software for heavy equipment*. Siemens Heavy Equipment Blog. https://blogs.sw.siemens.com/heavy-equipment/2025/01/10/boosting-profits-with-smart-manufacturing-software-for-heavy-equipment (author not recorded)

[11] Siemens. (n.d.). *ISA-95 framework and layers*. https://www.siemens.com/en-us/technology/isa-95-framework-layers/

[12] TPG. (2026, March 17). *Velotic launches to shape future of industrial manufacturing software* [Press release]. https://www.tpg.com/news-and-insights/velotic-launches-to-shape-future-of-industrial-manufacturing-software

[13] Velotic. (n.d.). *About*. https://www.velotic.com/about

[14] Velotic. (2026). *Why AI still falls short on the plant floor* [White paper, PDF supplied by the student].

[15] Velotic. (n.d.). *Kepware*. https://www.velotic.com/products/kepware

[16] Velotic. (n.d.). *Proficy Historian*. https://www.velotic.com/products/proficy/historian

[17] Velotic. (n.d.). *Proficy Smart Factory MES*. https://www.velotic.com/products/proficy/smart-factory-mes

[18] Velotic. (n.d.). *Proficy Tracker*. https://www.velotic.com/products/proficy/tracker

[19] Velotic. (n.d.). *Proficy Scheduler*. https://www.velotic.com/products/proficy/scheduler

[20] Velotic. (n.d.). *Proficy CSense*. https://www.velotic.com/products/proficy/csense

[21] Velotic. (n.d.). *Proficy Operations Hub*. https://www.velotic.com/products/proficy/operations-hub

[22] Velotic. (n.d.). *ThingWorx Digital Performance Management*. https://www.velotic.com/products/thingworx/digital-performance-management

[23] Velotic. (n.d.). *ThingWorx Real-time Production Performance Monitoring*. https://www.velotic.com/products/thingworx/real-time-production-performance-monitoring

[24] Velotic. (n.d.). *Velotic* [Home page]. https://www.velotic.com/

[25] Velotic. (n.d.). *Optimize production performance*. https://www.velotic.com/solutions/business-goal/optimize-production-performance

[26] Pavlosky, S. (2025, October 15). *How digital twin simulation software improves manufacturing operations*. GE Vernova. https://www.gevernova.com/software/blog/how-digital-twin-simulation-software-improves-manufacturing-operations ("last updated" date; original publication date unverified)

[27] AVEVA. (n.d.). *AVEVA PI System*. https://aveva.com/en/products/aveva-pi-system/

[28] AVEVA. (n.d.). *AVEVA Manufacturing Execution System*. https://www.aveva.com/en/products/manufacturing-execution-system/

[29] AVEVA. (n.d.). *AVEVA Production Management*. https://www.aveva.com/en/products/production-management/

[30] AVEVA. (n.d.). *AVEVA Insight*. https://www.aveva.com/en/products/insight/

[31] AVEVA. (n.d.). *AVEVA Predictive Analytics*. https://www.aveva.com/en/products/predictive-analytics/

[32] AVEVA. (n.d.). *Digital twin*. https://www.aveva.com/en/solutions/digital-transformation/digital-twin/

[33] AVEVA. (n.d.). *AVEVA Process Simulation*. https://www.aveva.com/en/products/process-simulation/

[34] Amazon Web Services. (n.d.). *What is AWS IoT TwinMaker?* AWS IoT TwinMaker User Guide. https://docs.aws.amazon.com/iot-twinmaker/latest/guide/what-is-twinmaker.html

[35] Amazon Web Services. (n.d.). *AWS IoT TwinMaker data connector interface*. AWS IoT TwinMaker User Guide. https://docs.aws.amazon.com/iot-twinmaker/latest/guide/data-connector-interface.html

[36] Amazon Web Services. (n.d.). *AWS IoT TwinMaker pricing*. https://aws.amazon.com/iot-twinmaker/pricing/

[37] AWS Samples. (n.d.). *aws-iot-twinmaker-samples: cookiefactoryv2* [Source code]. GitHub. https://github.com/aws-samples/aws-iot-twinmaker-samples/tree/main/src/workspaces/cookiefactoryv2

[38] Amazon Web Services. (n.d.). *AWS IoT Events end of support*. AWS IoT Events Developer Guide. https://docs.aws.amazon.com/iotevents/latest/developerguide/iotevents-end-of-support.html

[39] PTC. (n.d.). *Things*. ThingWorx Help Center. https://support.ptc.com/help/thingworx_hc/thingworx_8_hc/en/ThingWorx/Help/Composer/Things/Things.html

[40] PTC. (n.d.). *Thing shapes*. ThingWorx 9 Help Center. https://support.ptc.com/help/thingworx/platform/r9/en/ThingWorx/Help/Composer/ThingShapes.html

[41] RCR Wireless News. (2025, November 11). *PTC sells Kepware and ThingWorx*. https://www.rcrwireless.com/20251111/internet-of-things/ptc-sells-kepware-thingworx (exact headline and author unverified, check before citing)

[42] ARC Advisory Group. (2026, March 17). *PTC completes sale of Kepware and ThingWorx to TPG*. https://www.arcweb.com/blog/ptc-completes-sale-kepware-thingworx-tpg (exact headline and author unverified, check before citing)

[43] PTC. (2022). *Where to find free trial versions of ThingWorx Foundation* (Article CS323525). https://www.ptc.com/en/support/article/CS323525

[44] Microsoft. (2025–2026). *Azure IoT Central documentation* (including "What is Azure IoT Central?" and "Azure IoT Central is evolving", updated 23 September 2026) [PDF export of Microsoft Learn, supplied by the student]. https://aka.ms/AzureIoTCentralEvolution

[45] Microsoft & IoT Analytics. (2023). *Digital operations signals: Industrial IoT solution spotlight* [Report, PDF supplied by the student]. Microsoft.

[46] Humphrey, D. W. (2026). *Building Audi's EC4P platform for shop floor virtualization* [White paper]. ARC Advisory Group. (Copy supplied by the student, printed from siemens.com; sponsored in part by AUDI AG.)

[47] Kirkman, H., Devgun, J., & Graessle, J., with Tohani, M. (2025). *Green quadrant: Industrial AI analytics software (2025)* [ABB reprint, PDF supplied by the student]. Verdantix.

[48] Cisco Systems. (2026). *Industrial IoT portfolio* (Brochure C02-741513-19) [PDF supplied by the student].

[49] TEEPTRAK. (2026). *The six big losses*. https://teeptrak.com/en/six-big-losses-2026/ (vendor blog; original source is Nakajima, S. (1988). *Introduction to TPM: Total productive maintenance*. Productivity Press. Unverified, check before citing.)

[50] Fabrico. (n.d.). *OEE and ISO 22400*. https://www.fabrico.io/blog/oee-iso-22400/ (vendor blog)

[51] International Organization for Standardization. (2014). *Automation systems and integration: Key performance indicators (KPIs) for manufacturing operations management. Part 2: Definitions and descriptions* (ISO 22400-2:2014). https://www.iso.org/standard/54497.html

[52] Spearman, M. L., Woodruff, D. L., & Hopp, W. J. (1990). CONWIP: A pull alternative to kanban. *International Journal of Production Research, 28*(5), 879–894. https://doi.org/10.1080/00207549008942761

[53] Wikipedia contributors. (n.d.). *CONWIP*. Wikipedia. https://en.wikipedia.org/wiki/CONWIP

[54] Hopp, W. J., & Spearman, M. L. (2008). *Factory physics* (3rd ed.). Waveland Press. (unverified, check before citing)

[55] Roser, C. (n.d.). *The active period method*. AllAboutLean. https://www.allaboutlean.com/active-period-method

[56] Roser, C., Nakano, M., & Tanaka, M. (2001). A practical bottleneck detection method. In *Proceedings of the 2001 Winter Simulation Conference*. https://www.allaboutlean.com/publications/2001_roser_wsc-a-practical-bottleneck-detection-method_preprint/

[57] Roser, C., Nakano, M., & Tanaka, M. (2002). Shifting bottleneck detection. In *Proceedings of the 2002 Winter Simulation Conference* (pp. 1079–1086). https://www.informs-sim.org/wsc02papers/145.pdf

[58] Google. (n.d.). *The job shop problem*. OR-Tools. https://developers.google.com/optimization/scheduling/job_shop

[59] SimPy Team. (n.d.). *SimPy documentation*. https://simpy.readthedocs.io/en/latest/

[60] Montgomery, D. C. (n.d.). *Introduction to statistical quality control*. Wiley. (edition and year unverified, check before citing)

[61] Pinedo, M. L. (n.d.). *Scheduling: Theory, algorithms, and systems*. Springer. (edition and year unverified, check before citing)

[62] Matzka, S. (2020). *AI4I 2020 predictive maintenance dataset* [Data set]. UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C (author unverified, check before citing)

[63] McCann, M., & Johnston, A. (2008). *SECOM* [Data set]. UCI Machine Learning Repository. https://doi.org/10.24432/C54305

[64] Arduino. (n.d.). *Data logging with MQTT, Node-RED, InfluxDB and Grafana* (Portenta X8 tutorial). https://docs.arduino.cc/tutorials/portenta-x8/datalogging-iot

[65] Kim, S.-H., & Whitt, W. (2013). Statistical analysis with Little's law. *Operations Research, 61*(4), 1030–1045. https://doi.org/10.1287/opre.2013.1193

[66] Hopp, W. J., & Roof, M. L. (1998). Setting WIP levels with statistical throughput control (STC) in CONWIP production lines. *International Journal of Production Research, 36*(4), 867–882. (unverified, check before citing)

[67] Jaegler, Y., Jaegler, A., Burlat, P., Lamouri, S., & Trentesaux, D. (2018). The ConWip production control system: A systematic review and classification. *International Journal of Production Research, 56*(17), 5736–5757. https://doi.org/10.1080/00207543.2017.1380325

[68] Aslan, A., Vasantha, G., El-Raoui, H., Quigley, J., Hanson, J., Corney, J., & Sherlock, A. (2023). Hierarchical ensemble deep learning for data-driven lead time prediction. *The International Journal of Advanced Manufacturing Technology, 128*(9), 4169–4188. https://doi.org/10.1007/s00170-023-12123-4 (full author list unverified, check before citing)

[69] Nikolova, D., Lameski, P., Pires, I. M., & Zdravevski, E. (2023). Towards Industry 4.0: Machine malfunction prediction based on IIoT streaming data. In *Proceedings of the 18th Conference on Computer Science and Intelligence Systems (FedCSIS 2023)*, ACSIS Vol. 35 (pp. 291–296). https://annals-csis.org/Volume_35/drp/pdf/677.pdf (author initials unverified, check before citing)

[70] IEEE Bangalore Section. (2026). *IEEE CONECCT 2026 call for papers*. https://2026.connect.ieeebangalore.org/?p=37

[71] Python Package Index. (n.d.). *active-period-method* [Software package]. https://pypi.org/project/active-period-method/

[72] Kuntz, L., Mennicken, R., & Scholtes, S. (2015). Stress on the ward: Evidence of safety tipping points in hospitals. *Management Science, 61*(4), 754–771. https://doi.org/10.1287/mnsc.2014.1917
