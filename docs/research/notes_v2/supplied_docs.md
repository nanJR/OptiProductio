# Industrial IoT platforms for OptiProductio: the four supplied industry documents

Method note: all four PDFs were read in full. Cisco, Microsoft and Verdantix were extracted page by page with `pdftotext -layout`. The Audi PDF is a scanned print of a web page with no text layer, so each of its 19 pages was rendered to an image and read visually. Page numbers below are PDF page numbers. They match the printed page numbers in all four documents. "Source" links point to the local files supplied by the student.

Abbreviations for sources:
- **MS-DOS** = /home/claude/refdocs/Microsoft_DOS.pdf
- **AUDI** = /home/claude/refdocs/Audi_EC4P_Whitepaper.pdf
- **VDX** = /home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf
- **CISCO** = /home/claude/refdocs/Cisco_IIoT.pdf

---

## Q1. What is each document, who wrote it, and how far can its numbers be trusted?

### Takeaway
None of the four is independent academic research. One is a vendor-sponsored survey (Microsoft with IoT Analytics, n=300). One is an analyst case study part-sponsored by the company it describes (ARC on Audi). One is an analyst vendor ranking, licensed to and redistributed by one of the vendors it rates (Verdantix, ABB reprint). The last is a product brochure (Cisco). Use them for industry context, vocabulary and reference architectures. Label every number as a survey or vendor claim.

### Cited Findings
- **Microsoft "Digital Operations Signals – Industrial IoT Solution Spotlight", July 2023.** Microsoft wrote it "in close collaboration with IoT Analytics, a boutique market research company". It is the "fifth edition" of the series formerly called IoT Signals. — [MS-DOS p.1, p.2, p.6](/home/claude/refdocs/Microsoft_DOS.pdf)
- Survey method: "a survey conducted between October and December 2022 with a total of 300 respondents worldwide". Respondents were split 33% North America, 33% Europe and 33% Asia-Pacific. 66% work at firms with more than 5,000 employees, 23% at firms with 1,000–5,000, and 10% at firms with fewer than 1,000. Interviewees were "selected by Microsoft". — [MS-DOS p.6](/home/claude/refdocs/Microsoft_DOS.pdf)
- "Respondents from APAC are mainly based in China and Japan." Industry mix: F&B 16%, automotive 14%, pharma 10%, machinery 9%, electronics 7%, others 19%. — [MS-DOS p.7–8](/home/claude/refdocs/Microsoft_DOS.pdf)
- The appendix spotlights five solutions, all built on or with Microsoft Azure: Uptake, e-Magic, PTC, ICONICS and Capgemini. They were picked from "a pool of Microsoft partners". Their benefit claims are marked "* = Based on vendor interview". — [MS-DOS p.70, p.81](/home/claude/refdocs/Microsoft_DOS.pdf)
- **ARC Advisory Group White Paper "Building Audi's EC4P Platform for Shop floor Virtualization", January 2026,** by David W. Humphrey, Research Director. — [AUDI p.1](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Sponsorship disclosure: "This research has been sponsored in part by AUDI AG. However, the opinions expressed by ARC in this paper are based on ARC's independent analysis." — [AUDI p.18](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- The supplied PDF is a browser print from siemens.com: every page footer reads "siemens.com Global Website © Siemens 1996 – 2026". Siemens is one of the three suppliers the paper describes. — [AUDI p.1–19](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- **Verdantix "Green Quadrant: Industrial AI Analytics Software (2025)", September 2025,** by Henry Kirkman, Jatinder Devgun and Josh Graessle with Malavika Tohani. "This version of the report contains Verdantix's summary of ABB's offerings … It does not contain other vendor profiles." — [VDX p.1](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Verdantix disclaimer: it "does not endorse any vendor" and "does not advise technology users to select only those vendors with the highest ratings". Its publications "consist of the opinions of the Verdantix research team". — [VDX p.3](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Verdantix admits a limit: "As it is not feasible to check all data and claims made by vendors, we emphasize the need for professional integrity." — [VDX p.8](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- **Cisco "Industrial IoT Portfolio" brochure ("Brochure Cisco public")**, © 2026, document code "C02-741513-19 06/26". It is a product catalogue of switches, routers, wireless, embedded networking, security, management and edge software. — [CISCO p.1, p.2, p.33](/home/claude/refdocs/Cisco_IIoT.pdf)

### Inferences
- Rough order of evidential weight for a student report: Microsoft survey (largest sample, method disclosed) > Verdantix (structured method, but vendor-licensed reprint) > ARC/Audi (single case study, part-sponsored, no measured results) > Cisco (marketing).
- Each document comes from a company that sells the thing it recommends. Microsoft sells cloud. Cisco sells networks. ABB is a rated Leader in the Verdantix reprint it distributes. Audi/Siemens/Cisco/Broadcom are the subjects of the ARC paper. Say this on the references slide.

### Gaps
- None of the documents covers India specifically. The Microsoft survey's only India mention is that "No respondents in Japan, South Korea, and India used [the BUY] approach" ([MS-DOS p.46](/home/claude/refdocs/Microsoft_DOS.pdf)). No India sample size is given.

---

## Q2. Microsoft Digital Operations Signals: adoption, use cases and barriers (for the "problem/motivation" slide)

### Takeaway
The survey's main claim is that industrial IoT has "crossed the chasm" from early adopters into the "early majority". Projects succeed more often, break even sooner, and are more often bought off the shelf. The main pain points are now skills, integration with existing systems, and cybersecurity, not budget. The single most relevant data point for OptiProductio: "digitally assisted shopfloor dashboards" are a recognised smart-operations use case, and production planning and scheduling is the use case most often custom-built.

### Cited Findings
**Main argument and framework**
- "This report confirms that the adoption of IIoT technology has advanced to a point that it is crossing the chasm … IIoT technology has reached the broader uptake and acceptance that characterizes the 'early majority' stage of adoption." The report uses Geoffrey Moore's 1991 "Crossing the Chasm" theory. — [MS-DOS p.10–11](/home/claude/refdocs/Microsoft_DOS.pdf)
- **Five-stage framework**, with median durations across the 300 projects:
  1. Business case: 8 months
  2. Build vs. buy: 6 months
  3. Proof of concept: 6 months
  4. Initial pilot rollout: 7 months
  5. Commercial deployment: 9 months

  The report admits the framework "simplifies reality … and suggests a fully linear process". — [MS-DOS p.13–14](/home/claude/refdocs/Microsoft_DOS.pdf)
- PoC best practice: "starting with one to five scenarios or feature designs … starting small during the PoC phase (for instance, testing in part of a production line) allows companies to experiment rapidly and iterate continuously." — [MS-DOS p.13](/home/claude/refdocs/Microsoft_DOS.pdf)
- **Three approaches:** BUILD (end user builds most of the stack), BUY-AND-INTEGRATE, and BUY (plug-and-play). — [MS-DOS p.15–16](/home/claude/refdocs/Microsoft_DOS.pdf)
- **Three-layer tech stack:** "Core compute infrastructure", "Platform components" (data ingestion, device management, analytics, data management), and "Application" (UI plus configuration). — [MS-DOS p.17](/home/claude/refdocs/Microsoft_DOS.pdf)
- **Three project types:** smart operations, smart supply chain, connected product. Smart operations examples: "remote asset monitoring and control, process optimization, quality control, and developing an operational digital twin." — [MS-DOS p.18](/home/claude/refdocs/Microsoft_DOS.pdf)
- Initiative mix (N=300): smart operations 64%, smart supply chain 21%, connected products 14%. — [MS-DOS p.8](/home/claude/refdocs/Microsoft_DOS.pdf)

**Adoption statistics (survey/vendor claims)**
- "65% of organizations are now executing an IoT strategy." — [MS-DOS p.3](/home/claude/refdocs/Microsoft_DOS.pdf). The body text attributes this figure to the previous August 2022 IoT Signals report: "79% of manufacturing assets are now connected in some form, and 65% of manufacturers have partially or fully implemented IoT strategies." — [MS-DOS p.10](/home/claude/refdocs/Microsoft_DOS.pdf)
- Internal inconsistency: a later page says "76% of manufacturing assets are now connected" — [MS-DOS p.55](/home/claude/refdocs/Microsoft_DOS.pdf), against 79% on p.10.
- "IIoT projects today have a 14% higher success rate than five years ago." — [MS-DOS p.3](/home/claude/refdocs/Microsoft_DOS.pdf). The underlying data: "43% of respondents say that their recent projects exceeded expectations, compared to 38% … of older projects", shown as "+5 pp", N=141 (42 older and 99 newer projects). — [MS-DOS p.20–21](/home/claude/refdocs/Microsoft_DOS.pdf)
- Break-even: "median break-even time of 20 months, compared to 24 months five years ago" (about a 17% reduction; N=141). — [MS-DOS p.3, p.22](/home/claude/refdocs/Microsoft_DOS.pdf)
- Business case phase fell "from eight to three months, a significant reduction of 63%". The build-vs-buy phase fell "by 50%, from six to three months" (N=139). — [MS-DOS p.23](/home/claude/refdocs/Microsoft_DOS.pdf)
- "58% of early majority respondents consider it necessary to create a detailed business case, compared with 68% of early adopters." — [MS-DOS p.24](/home/claude/refdocs/Microsoft_DOS.pdf)
- Approach mix: "42% of all projects … were implemented in BUILD mode." "30% of the early majority prefer the BUY approach, compared with 9% of early adopters." In Exhibit 6, recent projects split Buy 30% / Buy & Integrate 28% / Build 43%, and older projects 9% / 50% / 41% (N=141). — [MS-DOS p.25](/home/claude/refdocs/Microsoft_DOS.pdf)
- "89% of respondents reported that their initiatives met or exceeded their expectations." The share that "exceeded" expectations was 40% for BUILD, 40% for BUY-AND-INTEGRATE and 13% for BUY. Median time to amortize was 20, 24 and 12 months respectively. — [MS-DOS p.30–31](/home/claude/refdocs/Microsoft_DOS.pdf)
- Partner anecdote, unnamed and not survey data: a Microsoft partner's performance-management project gave "a 10% improvement in overall equipment effectiveness (OEE), a 20% to 30% reduction in unplanned downtime, and a 40% reduction of unproductive time for workers on the shop floor." — [MS-DOS p.21](/home/claude/refdocs/Microsoft_DOS.pdf)
- Typical success outcomes reported: "increased operational efficiency; improved asset utilization; reduced downtime; improved product quality; better supply chain visibility; and increase in revenue via improved production throughput". — [MS-DOS p.21](/home/claude/refdocs/Microsoft_DOS.pdf)

**Top use cases (smart operations, N=192)**
- Top BUILD use cases: "production planning and scheduling (67%), AI and modern machine vision-based quality control and management (54%), and remote asset monitoring and control … (53%)". Top BUY-AND-INTEGRATE use cases: "predictive maintenance of equipment AI (61%), AR-assisted operations (60%), and remote or smart service and maintenance (56%)". — [MS-DOS p.37](/home/claude/refdocs/Microsoft_DOS.pdf)
- From Exhibit 15 (n per use case in brackets):
  - Production planning and scheduling (n=83): Build 67%
  - **Digitally assisted shopfloor dashboards** (n=29): Build 28%, Buy-and-integrate 55%, Buy 17%
  - Asset or plant performance optimization: n=71
  - Condition-based maintenance: n=58

  — [MS-DOS p.38](/home/claude/refdocs/Microsoft_DOS.pdf)
- "BUILD is the most common approach for smart operations" (54% Build, 34% Buy-and-integrate, 12% Buy; n=192). — [MS-DOS p.36–37](/home/claude/refdocs/Microsoft_DOS.pdf)
- Comparable commercial products in the appendix:
  - PTC ThingWorx DPM: a "Production dashboard", an "Action tracker" and a "Performance analysis dashboard: To confirm that the improvements make a difference in the OEE". It is "pre-built for bottleneck analysis". — [MS-DOS p.77](/home/claude/refdocs/Microsoft_DOS.pdf)
  - Capgemini MPP: "shop-floor monitoring, OEE calculation, inline quality monitoring, condition-based monitoring, planning and scheduling, and predictive analytics." — [MS-DOS p.80](/home/claude/refdocs/Microsoft_DOS.pdf)

**Barriers**
- Headline: "Budget constraints have faded, while cybersecurity and knowledge gaps have become key pain points." "Implementation challenges and budget restrictions have dropped by 30 and 13 percentage points." The previous report found "securing the OT network (43%) and securing the cloud (41%)" as top technical issues. The talent gap was cited by "24% of the respondents". — [MS-DOS p.4](/home/claude/refdocs/Microsoft_DOS.pdf)
- Exhibit 7, older vs. recent projects (N=139):
  - Complexity of implementation: 52% → 22%
  - Constrained budget: 29% → 16%
  - Missing end-user capabilities: 14% → 28%
  - Inability to tackle cyber threats: 10% → 22%
  - Missing IT capabilities: 10% → 18%
  - Inability to use data effectively: 33% → 20%

  — [MS-DOS p.27–28](/home/claude/refdocs/Microsoft_DOS.pdf). Inconsistency: p.4 says 24% for the talent gap, while p.27–28 shows 28% for recent projects.
- Prior-report top technical challenges: "developing new applications (49%), securing OT networks (43%), and interfacing with enterprise applications such as ERP or MES (42%)". — [MS-DOS p.27](/home/claude/refdocs/Microsoft_DOS.pdf)
- Overall challenges (Exhibit 21, N=246, multiple answers allowed):
  1. Missing end-user capabilities: 17%
  2. Complexity of implementation and integration: 16%
  3. Budget: 14%
  4. Missing IT capabilities: 12%
  5. Lack of internal cooperation: 11%
  6. Resistance to change: 11%
  7. Inability to use data: 10%
  8. Cyber threats: 9%

  — [MS-DOS p.46–47](/home/claude/refdocs/Microsoft_DOS.pdf)
- Most painful integration aspects (Exhibit 25, **N=43 only**):
  - Interfacing with OT systems (MES, SCADA, DCS, PLC): 34%
  - Training users: 33%
  - Interfacing with IT systems: 27%
  - Closer OT/IT network integration: 26%
  - Securing the OT network: 23%
  - Managing data formats: 21%
  - Physical connection of devices: 14%

  — [MS-DOS p.54](/home/claude/refdocs/Microsoft_DOS.pdf)
- "Physical connection of devices (14%) is relatively low on the list … However, almost all interviewees indicated that the logical connections (that is, mapping physical assets to logical devices) entail a fairly manual and labor-intensive exercise." — [MS-DOS p.55](/home/claude/refdocs/Microsoft_DOS.pdf)
- Earlier failure context: "A 2018 McKinsey report coined the term 'pilot purgatory' … while a 2017 Cisco study claimed that nearly 75% of IoT projects failed." These are secondhand citations with no reference details. — [MS-DOS p.12](/home/claude/refdocs/Microsoft_DOS.pdf)
- Enablers named: "protocol converters supporting connectivity protocols (such as OPC-UA and MQTT)" and "Industrial security frameworks (such as IEC 62443 and NIST SP 800-53)". — [MS-DOS p.12](/home/claude/refdocs/Microsoft_DOS.pdf)
- Why firms BUILD (N=142): "Had to meet specific business requirements for which no standard products are available" 96%. "Wanted to create a defendable competitive advantage" 92%. "IT security considerations could be better addressed this way" 84%. — [MS-DOS p.32](/home/claude/refdocs/Microsoft_DOS.pdf). Cons of BUILD: "Requires major in-house (IT) capabilities", "Typically leads to unpredictable costs", "Typically has the longest project timeline". — [MS-DOS p.31](/home/claude/refdocs/Microsoft_DOS.pdf)
- Practitioner quote (Uptake): teams that build from scratch "achieved successful first results in just a few months, but then they realize that it takes an enormous effort to make the solution industrial strength. One issue is to ensure the system handles all major exceptions correctly." — [MS-DOS p.26](/home/claude/refdocs/Microsoft_DOS.pdf)
- Key learnings (N=83): "Involve stakeholders early on" 13%, "Plan the technology specifications well" 13%, "Define the business case clearly" 11%. One respondent: "Define business process first. Do not focus only on the technology". — [MS-DOS p.51](/home/claude/refdocs/Microsoft_DOS.pdf)
- BUY selection factors (N=43): "Reliability" 98%, "Ease of set up" 93%, "Scalability" 91%, "Ease of use" 88%. — [MS-DOS p.61](/home/claude/refdocs/Microsoft_DOS.pdf). The narrative on p.62 instead gives ease of use as 91%, a minor inconsistency.

### Inferences
- Problem/motivation slide: "Industry has moved past pilots: 65% are executing IIoT strategies, but skills (28% of recent projects), integration and cybersecurity (22%) are the main barriers (Microsoft/IoT Analytics survey, n=300, 2023)." A low-cost, transparent, student-built line speaks to the skills-gap barrier.
- The "14% higher success rate" headline is a relative change (43% vs 38%, i.e. +5 percentage points) on a subsample of 141. Quote the percentage-point figure rather than "14%" to avoid overstating it.
- OptiProductio fits the report's "smart operations" type and its "BUILD" approach. The report's best practice of starting small, e.g. "testing in part of a production line" with 1–5 scenarios, supports the 3-station scope.

### Gaps
- Subgroup sample sizes are small and sometimes inconsistent. Exhibit 6 says "47 recent … 94 older" while N=141. Exhibit 8 says "94 new projects … 94 old projects". Treat sub-percentages as indicative only.
- Lean/WIP/CONWIP, cycle time and takt are not discussed anywhere in the Microsoft report.

---

## Q3. Audi EC4P: why move shop-floor control to edge/cloud, what changed, and results

### Takeaway
Audi's "Edge Cloud 4 Production" replaces thousands of shop-floor industrial PCs, and now hardware PLCs, with virtual machines on standardised servers. The servers sit in off-premises data centres 6–13 km away, linked by a redundant, software-defined network. The motivation is lower hardware/energy cost, easier updates, cybersecurity, and readiness for AI. The paper describes it as running in production (body shop, final assembly, e-tron GT axle pre-assembly), but it gives **no quantified results**.

### Cited Findings
**What and why**
- "'Software, not hardware' – this simple tenet is the basis of what AUDI AG calls 'IT-based factory automation' … the concept is to replace thousands of decentralized industrial PCs with a much more efficient and flexible IT-like architecture of scalable local servers, effectively uniting the cloud and the edge on the shop floor." Tenets: "Centralized, not decentralized"; "Local servers instead of thousands of IPCs"; "Solution delivery in software, not hardware". — [AUDI p.3](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Context: the auto industry is changing "in the face of new cost structures driven by the electric vehicle transition and fierce competition from China". Audi is part of Volkswagen AG, which "employs more than 600,000 workers", so the project could change "plant architectures in well over 100 plants worldwide". — [AUDI p.3](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Challenges and strategies table:
  - High energy costs: "Lower energy costs by reducing legacy hardware"
  - Legacy hardware: consolidate it, "Lower hardware costs and procurement process", "Eliminate need for time-consuming shop floor updates"
  - Cybersecurity: "built-in cybersecurity"
  - Production strategy: "360 factory"

  — [AUDI p.4](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Technical challenges: guaranteed performance ("equipment availability, real-time performance and guaranteed latency must be maintained for applications such as safety and motion control"), functional safety certification, and resilience. "In a software-defined factory, the first step may be to pick up a mouse and keyboard rather than the key to an electrical cabinet." — [AUDI p.5–6](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Organisation: EC4P "established a 24x7 operational team with both IT and OT skillsets". "If you want to bring IT and OT together, you first need to bring the people together." — [AUDI p.6](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Business drivers, starting from "first ideas in 2018": cut capex and opex, reduce hardware and energy, reduce complexity by shifting "from special purpose hardware (PLC, IPC) to standard server hardware". Faster deployment from any location. Continuous health monitoring "opening the door for sophisticated AI-driven predictive maintenance". — [AUDI p.7](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Key metrics: "reducing hardware costs is a top metric", offset against new server investment. "Equipment availability is a key metric, usually calculated as overall equipment effectiveness (OEE) … three factors: availability, performance, and quality. With less hardware to maintain, OEE is likely to improve thanks to EC4P." Other metrics: scalability (time to update), rollout velocity, and stability/availability. — [AUDI p.7–8](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)

**Architecture (what changed)**
- "Today vs Tomorrow" diagram:
  - Today: a mix of hardware and software (control PC, firewall, L2/L3 switches, PLC, plant PC).
  - Tomorrow: "Solution is software only" (vPLC and apps on an "Edge Layer"), over "Generic Hardware" and "Industrial and Enterprise Networks".

  — [AUDI p.8](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Reference architecture of three domains:
  - "Shop floor: Manufacturing equipment, automation devices, networks"
  - "Enterprise network: Resilient, low-latency/high-bandwidth networking infrastructure"
  - "Data center: EC4P virtualization platform hosts a variety of applications"

  Data-centre apps shown: QC, tool control, PdM, vPLC, failsafe vPLC, HMI. Shop floor shows thin clients. — [AUDI p.9](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Partners: "Cisco, Broadcom (VMware), and Siemens" ("the top IT consulting firms lacked domain-specific experience"). — [AUDI p.9](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Use cases:
  - Virtual HMI running TIA Portal and WinCC in a VM
  - Siemens S7-1500V vPLC "for rear and front axle pre-assembly stations for the Audi e-tron GT"
  - S7-1517VF "TÜV certified failsafe vPLC for bodyshop robot cells"
  - MES, screw fastening, car diagnostics

  — [AUDI p.10](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Networking: Profinet RT works at Layer 2, so EC4P uses VXLAN through Cisco Software-Defined Access to stretch Layer 2 over routed networks ("vPLC thinks it's local"). It uses the Parallel Redundancy Protocol (PRP, IEC 62439-3) for "zero recovery time", with dual fabrics to the data centre. — [AUDI p.10, p.12](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Data centre location: "servers are in data centers that serve multiple production sites located at varying distances (currently 6-13 km) from the production sites due to server requirements (cooling, access control, failover batteries)." — [AUDI p.10–11](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Cisco's security and observability role: "Segment and protect cell/area zones with Cisco TrustSec", latency monitoring between vPLC and devices, Splunk "full-stack monitoring", Catalyst Center. Cisco also supplied an end-to-end test lab and a "Cisco validated design". — [AUDI p.12–13](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Broadcom's VMware Cloud Foundation (VCF) 9.0 offers encryption "of data at rest and data in motion" and faster patching. Its industrial virtual switch "ensures deterministic latency and jitter". The paper says the implementation "required no process changes or retraining for factory teams and is TÜV-certified for safety". — [AUDI p.13–14](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Siemens: the vPLC "is a drop-in replacement for the classic hardware-based PLC … legacy code … can be used seamlessly". It uses the same TIA Portal tool and connects to existing IO over Ethernet. It is also used for "a body shop application for a Lamborghini model". — [AUDI p.14–15](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)

**Results and next steps**
- "Now that the concept is shop floor-tested, Audi is extending its shop floor digital transformation to real-time control via the first virtual PLC." — [AUDI p.4](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- "Now that EC4P has proven itself in the body shop (and final assembly), the next step is to roll out the architecture within Audi's production sites", including Bentley, Lamborghini and Ducati. A Remote Operations Center in Germany will manage the platforms. — [AUDI p.16](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Next step is AI: "add support for AI workloads … data analytics, anomaly detection, and computer vision (quality)." — [AUDI p.16](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- The conclusion asserts "tangible benefits … greater efficiency, flexibility, and readiness for advanced AI" and says EC4P "has enabled Audi to consolidate legacy systems, reduce energy and hardware costs". It also says "Key challenges remain, particularly in ensuring resilience and maintaining critical functionality during migration." — [AUDI p.17](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Success factors: buy-in from OT maintenance teams, and joint architecture sessions with suppliers "without fear of being wrong in the initial stages". — [AUDI p.15–16](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)

### Inferences
- For OptiProductio, the useful idea is the separation of concerns. Field devices stay simple (Audi: thin clients and IO; OptiProductio: Arduino with IR sensors and buttons). The logic and analytics run in software on general-purpose computers (Audi: data-centre VMs; OptiProductio: the Python/Streamlit laptop). OEE is explicitly Audi's operational KPI, defined as availability × performance × quality, which validates the project's OEE proxy.
- Audi keeps safety and motion control under strict real-time, certified control. OptiProductio should likewise keep any stop/safety function local to the Arduino or hardware, and use the dashboard only for monitoring and alerts.

### Gaps
- **No quantified results.** The paper gives no figures for cost saving, energy reduction, OEE change, number of IPCs removed, downtime or payback. Claims are qualitative and the paper is part-sponsored by Audi.
- No number of vPLCs or servers deployed is given. "Thousands" of IPCs (p.3, p.17) is not quantified further.

---

## Q4. Verdantix Green Quadrant 2025: vendors, criteria, leaders and market trends in industrial AI analytics

### Takeaway
Verdantix benchmarked 19 industrial AI analytics vendors on 14 capability and 7 momentum criteria. Nine are Leaders: ABB, Augury, AVEVA, C3 AI, Cognite, GE Vernova, IBM, Seeq and SymphonyAI. The market is moving "from pilots to enterprise-wide platforms". Predictive maintenance and process/production optimisation carry the most weight. Generative and agentic AI is emerging. Data contextualisation, unplanned downtime, skills gaps and scaling beyond pilots are the core buyer problems.

### Cited Findings
**Scope and method**
- "A detailed, fact-based benchmark of 19 of the most prominent industrial AI analytics software providers … live briefings, customer interviews and vendor responses to a detailed 105-point questionnaire, covering 14 capability and seven momentum categories." — [VDX p.2](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Evidence base: "two-hour demonstrations, a 105-point questionnaire and 11 buyer interviews". Weightings were informed by a survey of "304 senior industrial transformation decision-makers". — [VDX p.4, p.8–9](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Definition: industrial AI analytics software is "Computer programs that can ingest operational technology (OT) and other industrial data, such as time series, events and control logs – and/or visual data, audio and free text – and use learned pattern recognition and even reasoning to deliver real-world automation, such as highlighting anomalies, predicting asset failure, optimizing processes and completing open-ended, multi-step tasks." — [VDX p.5](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Inclusion criteria:
  - Functionality across "(1) user-configurable acquisition of industrial data; (2) transformation and contextualization of these data to prepare for analytics; and (3) generation of insights through AI-based methods"
  - "At least 10 named asset-heavy customers"
  - "At least $5 million in annual revenues from industrial AI analytics solutions"

  — [VDX p.9](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- **The 19 vendors:** ABB, AspenTech, Augury, Avathon, AVEVA, C3 AI, Cognite, GE Vernova, Honeywell, IBM, Imubit, Nanoprecise, Optimistik, Rockwell Automation, Seeq, Siemens, SymphonyAI, TrendMiner and TwinThread. "Avathon, IBM, Rockwell Automation and Siemens … did not actively" participate, and were assessed from public information. — [VDX p.8–9](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- **Leaders:** "nine emerged as Leaders: ABB, Augury, AVEVA, C3 AI, Cognite, GE Vernova, IBM, Seeq and SymphonyAI." — [VDX p.4](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Other quadrants, read visually from Figure 6 (dots near the dividing lines are approximate):
  - Innovators: TwinThread
  - Challengers: Avathon, Rockwell Automation, Imubit
  - Specialists: TrendMiner, Siemens, Honeywell, AspenTech, Optimistik, Nanoprecise

  — [VDX p.16](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)

**Criteria and weights (capabilities, Figure 2)**
- Data acquisition & integration: 5%
- Data storage & management: 4%
- Data processing & transformation: 6%
- Model development: 7%
- Model training: 7%
- User interfaces: 4%
- Platform APIs: 3%
- Workflow automation: 5%
- Visualization & reporting: 4%
- Supply chain & logistics optimization: 7%
- **Process & production optimization: 16%**
- Quality management: 8%
- **Predictive maintenance: 16%**
- Resource & energy management: 8%

— [VDX p.11–12](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Data acquisition questions ask about "protocols or methods used (e.g. OPC-UA, MQTT)" and "How are data errors, missing values or inconsistencies identified and corrected during the ingestion process?" — [VDX p.11](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Visualization & reporting asks: "Which key KPIs does the system track? Can customers set and monitor these KPIs over time?" — [VDX p.12](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- **Momentum weights (Figure 3):**
  - Market vision & business strategy: 15%
  - Product strategy: 20%
  - Innovation process: 20%
  - Organizational resources & growth: 10%
  - Financial resources: 15%
  - Customers: 15%
  - Brand preference: 5%

  The momentum questions refer to "the CMMS market" and "revenue specific to CMMS", which looks like an editorial carry-over from another Green Quadrant. — [VDX p.13](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Scoring runs from 0 ("Lack of evidence …") to 3 ("market-leading"). — [VDX p.10, p.14](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)

**Market trends**
- "The industrial AI analytics market is evolving from pilots to enterprise-wide platforms that unify complex data, embed predictive intelligence into daily operations, and deliver measurable improvements in uptime, efficiency and sustainability. Growth is being driven by rising demand for predictive maintenance, the need to bridge workforce expertise gaps, and executive pressure to optimize yield and sustainability." — [VDX p.4](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- "Traditional reporting and dashboards are no longer sufficient: organizations are increasingly turning to AI-enabled platforms that can detect anomalies, anticipate failures and optimize production in real time. Yet barriers such as fragmented data architectures, limited scalability of proofs of concept, and shortages of AI expertise continue to slow progress." — [VDX p.5](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Four core technologies: agentic automation, multimodal AI, predictive analytics ("Task-specific machine learning models capable of using historical data from sensors"), and RAG. — [VDX p.6](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Four buyer challenges:
  - Contextualising siloed data
  - "Combatting the plague of unplanned downtime"
  - "Bridging the expertise gap"
  - "Optimizing yield, quality and sustainability"; also "Scaling AI for enterprise-wide impact"

  — [VDX p.6–7](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Survey statistic (Verdantix 2025 survey, n=304 executives): "44% plan double-digit budget increases for production and yield optimization and 31% expect single-digit growth". — [VDX p.7](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Vendor case claim: Nanoprecise "detected severe unbalance in a critical methanol/water pump within three weeks, preventing a $9 million batch failure". — [VDX p.6](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Buyer priorities: "deep domain expertise, scalable deployment capabilities, seamless integration with existing systems … Selection often depends on the quality of an organization's data and a vendor's proven track record, ease of platform deployment and cost-effectiveness." — [VDX p.7](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)

**ABB profile (the reprint's sponsor)**
- ABB Ability Genix scored "2.7/3.0 for data acquisition and integration", "2.5/3.0 for model development" and "the highest score, of 2.6/3.0, for resource and energy management". — [VDX p.18](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Vendor customer claim: "A UK-based construction materials firm implemented Genix Datalyzer and witnessed an 8% to 12% reduction in CO2 emissions at monitored sites." — [VDX p.18](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- ABB facts: 110,000 employees, revenues of $11bn–$50bn, partnerships with AWS, IBM Red Hat and Microsoft. — [VDX p.17](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Genix suits firms "that need edge-to-cloud connectivity, strong data governance and pre-built industrial AI applications, rather than a DIY MING stack". — [VDX p.18](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)

### Inferences
- The score table (Figure 4, p.14) appears to list vendors in alphabetical order, starting with ABB. ABB's printed scores (2.7, 2.5, 2.6) match the first column. On that reading, Cognite scores 3.0 on data storage, data processing, UI and APIs, Imubit 2.9 on process optimisation, and C3 AI 2.8 on predictive maintenance. The column headers did not extract cleanly, so check visually before quoting individual non-ABB scores.
- "DIY MING stack" (commonly MQTT, InfluxDB, Node-RED, Grafana; Verdantix does not expand the acronym) is the open-source route a student project would take. Verdantix frames it as the alternative to commercial platforms. The three inclusion capabilities (acquire → contextualise → generate insight) give a neat pipeline for the OptiProductio architecture slide.
- OptiProductio's "AI" layer would be the Bosch Kaggle history, which fits Verdantix's "predictive analytics" category (models on historical sensor data). The other three technologies (agentic AI, multimodal AI, RAG) are out of scope.

### Gaps
- The reprint omits all non-ABB vendor profiles, so strengths and weaknesses of the other eight Leaders cannot be cited.
- No market size or growth rate is given for industrial AI analytics.

---

## Q5. Cisco IIoT portfolio: network/OT layers, security, the Purdue model, and what matters for connecting sensors

### Takeaway
Cisco presents an "end-to-end Industrial IoT architecture" of four functional pillars: network connectivity, device management, data control and exchange, and edge computing. Security wraps around all four. Its security story centres on OT asset visibility, IEC 62443 "zones and conduits" segmentation, and zero-trust remote access, mostly built into the network hardware. **The brochure never mentions the Purdue model.** It mostly lists ruggedised switches, routers and wireless products.

### Cited Findings
- Problem framing: "Deploying Industrial IoT at scale isn't easy. It requires configuring and managing countless assets and devices … This increase in connected 'things' can also create visibility gaps that increase security risks." The network is "the critical foundation upon which Industrial AI thrives". — [CISCO p.3](/home/claude/refdocs/Cisco_IIoT.pdf)
- Use cases shown: "Remote monitoring, Asset tracking, Worker safety, Operational agility, Industrial automation, Industrial AI". — [CISCO p.3](/home/claude/refdocs/Cisco_IIoT.pdf)
- **Architecture pillars:**
  - "Network connectivity – Extend the network you know and trust to operational environments"
  - "Device management – Manage industrial assets and devices at scale"
  - "Data control and exchange – Efficiently move the right data to the right place at the right time"
  - "Edge computing – Push data processes to the edge to enable fast decision-making"
  - "Security – Protect your business from end to end"

  — [CISCO p.4](/home/claude/refdocs/Cisco_IIoT.pdf)
- Vendor claims: "Our 67,000 customers". Customer quotes: "Within a month, we increased our manufacturing floor productivity by over 10 percent" (Lordan COO) and "Cyber Vision found more than 20 instances of malware in our substations" (CPFL Energia CISO). These are unaudited testimonials. — [CISCO p.4](/home/claude/refdocs/Cisco_IIoT.pdf)
- Industrial protocols: switches support "PROFINET and EtherNet/IP". They are developed under a secure development lifecycle that "conforms to the requirements of ISA/IEC 62443-4-1 as well as ISA/IEC 62443-4-2". — [CISCO p.7](/home/claude/refdocs/Cisco_IIoT.pdf)
- Built-in OT security functions:
  - "OT visibility" (Cyber Vision inventories ICS/OT assets, vulnerabilities and communications, and "detects malicious traffic and abnormal behaviors")
  - "Microsegmentation: Protect operations by restricting what can communicate to what and limiting lateral movement of threats … recommend zones and conduits and simulate policies to ensure they will not disrupt production"
  - "Secure remote access … enforce least-privilege access policies"

  — [CISCO p.8](/home/claude/refdocs/Cisco_IIoT.pdf)
- Cyber Vision "enforces IEC 62443 zones and conduits, and controls who can remotely access your assets". It offers "AI-assisted network segmentation that can be implemented in weeks, not years" and "self-service zero trust remote access". — [CISCO p.25](/home/claude/refdocs/Cisco_IIoT.pdf)
- Management: Catalyst Center "gives OT a curated view … increasing Overall Equipment Effectiveness (OEE) and uptime". This is a vendor claim with no figure. Functions: discover devices and topology, Plug and Play provisioning, patching at scale, telemetry, root cause, segmentation, and "Integrate operational and enterprise security". — [CISCO p.26](/home/claude/refdocs/Cisco_IIoT.pdf)
- SD-WAN uses "service VPNs to segregate traffic (such as Supervisory Control and Data Acquisition [SCADA], closed-circuit television [CCTV] …)", centralised logging to help comply "with cybersecurity mandates like NIS2", and "end-to-end network security that extends to the edge routers" protecting "connected sensors". — [CISCO p.28](/home/claude/refdocs/Cisco_IIoT.pdf)
- Meraki dashboard: "encrypted data transmission, two-factor authentication, and detailed logging". — [CISCO p.27](/home/claude/refdocs/Cisco_IIoT.pdf)
- Connecting sensors and legacy devices: routers offer "4 x asynchronous serial ports", "digital I/Os for dry/wet contacts" and RS-232/485 and CAN bus ports. The IE1000 entry switch offers "Port security, TACACS, 802.1X". — [CISCO p.12, p.17, p.18](/home/claude/refdocs/Cisco_IIoT.pdf)
- Edge Intelligence pipeline: "Extract – From disparate sources; Transform – Into intelligent data; Govern – When and where data goes; Deliver – Secure data to its destination". It promises "Full data ownership, control, and governance". — [CISCO p.31](/home/claude/refdocs/Cisco_IIoT.pdf)
- Edge Application Hosting (IOx) runs containers or VMs, Linux or Windows, on network devices, for "closed loop system control in real time". — [CISCO p.32](/home/claude/refdocs/Cisco_IIoT.pdf)
- Wireless: "Losing connection in OT means stopping machines and processes". URWB can "reconfigure the network on redundant hardware in less than 500 ms". — [CISCO p.20–21](/home/claude/refdocs/Cisco_IIoT.pdf)
- Hardware ruggedness examples: IP67 switches with M12 connectors, operating ranges of -50°C to +75°C, conformal coating. — [CISCO p.9, p.14, p.21](/home/claude/refdocs/Cisco_IIoT.pdf)

### Inferences
- What matters for OptiProductio's sensors, translated down to student scale:
  1. Know every connected device (an asset inventory: Arduino ID, sensor-to-station mapping).
  2. Restrict who can talk to what (keep the Arduino on USB serial or an isolated local network, with no inbound internet access).
  3. Move only the data needed ("right data to the right place"), i.e. timestamped count/state events.
  4. Watch connectivity health (detect a dropped serial link, a stale data timestamp or a stuck sensor).

  Cisco's Extract–Transform–Govern–Deliver pipeline maps onto Arduino → Python parser → CSV/SQLite → Streamlit.
- The Purdue model is not in the supplied Cisco brochure. If a slide needs the Purdue model (Level 0 sensors to Level 4/5 enterprise), cite a separate source, such as ISA-95/IEC 62443 material. The nearest concept in the brochure is IEC 62443 "zones and conduits" (p.8, p.25), plus "cell/area zones" in the Audi paper ([AUDI p.12](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)).

### Gaps
- No Purdue model, no layer diagram of Levels 0–5, and no quantified security or performance outcomes beyond the two testimonials.
- No prices are given, so the cost of "industrial grade" cannot be compared with the student's budget from this document.

---

## Q6. Lessons for a low-cost student line: what applies and what is overkill

### Takeaway
All four documents describe the same layered pattern: devices/sensors → network/edge → data platform (ingest, clean, contextualise) → application/analytics → people. They stress the same KPIs (OEE, downtime, throughput, quality) and the same non-technical lessons (start small, define the business process first, train users, bring IT and OT people together). OptiProductio can borrow the layering, KPIs, data-quality discipline and basic security hygiene. Redundant networks, virtual PLCs, ruggedised hardware, enterprise security suites and agentic AI are overkill.

### Cited Findings
**Architecture layers the project can mirror**
- Microsoft three-layer stack: core compute → platform components (data ingestion, device management, analytics) → application. — [MS-DOS p.17](/home/claude/refdocs/Microsoft_DOS.pdf)
- Verdantix three core capabilities: data acquisition → transformation/contextualisation → AI-based insight. — [VDX p.9](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Audi three domains: shop floor → enterprise network → data centre. — [AUDI p.9](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Cisco pillars: connectivity, device management, data exchange, edge compute, plus security. — [CISCO p.4](/home/claude/refdocs/Cisco_IIoT.pdf)

**KPIs**
- OEE = availability, performance, quality is named as Audi's key operational metric. — [AUDI p.8](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)
- Survey success outcomes include reduced downtime, product quality and "improved production throughput". — [MS-DOS p.21](/home/claude/refdocs/Microsoft_DOS.pdf)
- Commercial analogues track OEE and bottlenecks (PTC DPM, Capgemini MPP). — [MS-DOS p.77, p.80](/home/claude/refdocs/Microsoft_DOS.pdf)

**Use cases**
- "Digitally assisted shopfloor dashboards" and "production planning and scheduling" are both recognised smart-operations use cases. — [MS-DOS p.38](/home/claude/refdocs/Microsoft_DOS.pdf)

**Data quality**
- Verdantix asks how "data errors, missing values or inconsistencies [are] identified and corrected during the ingestion process". — [VDX p.11](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)
- Uptake warns that custom builds struggle to make "the system handle all major exceptions correctly". — [MS-DOS p.26](/home/claude/refdocs/Microsoft_DOS.pdf)

**Asset mapping**
- "mapping physical assets to logical devices … a fairly manual and labor-intensive exercise". — [MS-DOS p.55](/home/claude/refdocs/Microsoft_DOS.pdf)

**Protocols**
- OPC-UA and MQTT are named as standard connectivity protocols. — [MS-DOS p.12](/home/claude/refdocs/Microsoft_DOS.pdf); [VDX p.11](/home/claude/refdocs/ABB_Verdantix_Green_Quadrant_2025.pdf)

**Security basics**
- Segmentation ("restricting what can communicate to what"), least-privilege access, and asset visibility. — [CISCO p.8, p.25](/home/claude/refdocs/Cisco_IIoT.pdf)
- Cyber threats were reported by 22% of recent projects. — [MS-DOS p.28](/home/claude/refdocs/Microsoft_DOS.pdf)

**Process lessons**
- Start with 1–5 scenarios on part of a line. — [MS-DOS p.13](/home/claude/refdocs/Microsoft_DOS.pdf)
- "Define business process first. Do not focus only on the technology". — [MS-DOS p.51](/home/claude/refdocs/Microsoft_DOS.pdf)
- Training users was the second most painful aspect (33%). — [MS-DOS p.54](/home/claude/refdocs/Microsoft_DOS.pdf)
- "If you want to bring IT and OT together, you first need to bring the people together." — [AUDI p.6](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)

**Real-time vs. non-real-time split**
- Audi keeps safety and motion control on strict latency guarantees. "Visualization and production management have less stringent requirements." — [AUDI p.5](/home/claude/refdocs/Audi_EC4P_Whitepaper.pdf)

### Inferences
**Apply (low cost, high value):**
1. **A four-layer architecture slide:**
   - Sensing: Arduino UNO, IR counters, breakdown/reject buttons
   - Edge/ingest: Python serial reader with timestamping, debouncing and validation
   - Data: CSV/SQLite, plus Bosch Kaggle history as the "historical data" layer
   - Application: Streamlit KPIs and alerts

   Cite Microsoft p.17, Verdantix p.9 and Audi p.9 as industry analogues.
2. **KPIs:** OEE proxy (availability from breakdown time, performance from cycle time vs. ideal, quality from rejects), throughput, WIP, and cycle time. This matches the industry's OEE framing (Audi p.8). The CONWIP WIP-cap alert is a lean/IE addition that **none of the four documents discusses**, so the project's own literature must justify it.
3. **Data quality at ingestion:** debounce IR counts, flag missing heartbeats and impossible values, and log raw events. This mirrors Verdantix's acquisition criteria and the "exceptions" warning.
4. **Asset mapping:** a simple config table (sensor pin → station → event type) addresses the "logical mapping" pain point (MS-DOS p.55).
5. **Basic security hygiene:** keep the Arduino on USB serial or an isolated LAN. Do not expose the Streamlit port to the internet, or add a password if it is shared. Keep the control/stop function local to hardware (Audi p.5 split). This is the student-scale version of Cisco's segmentation and least-privilege access.
6. **Optional, still cheap:** publish events over MQTT (a free broker such as Mosquitto on the laptop) to show the industry-standard protocol named in Microsoft p.12 and Verdantix p.11.
7. **Positioning:** OptiProductio is a "BUILD" smart-operations project. The survey's reason for BUILD, "specific requirements for which no standard products are available" (96%, MS-DOS p.32), and its warning about the downsides ("unpredictable costs", "longest project timeline", MS-DOS p.31) can frame the project's scope and risk slide.

**Overkill for a first-year student line:**
- Virtual PLCs, VMware VCF, VXLAN, PRP dual fabrics, and off-premises data centres (Audi). These solve multi-plant scale, functional-safety certification and zero-packet-loss needs that a 3-station demo does not have.
- Ruggedised IP67/M12 switches, 5G/LTE routers, URWB wireless, SD-WAN, Catalyst Center, and Cyber Vision/TrustSec/ISE (Cisco).
- Enterprise AI platforms, agentic automation, multimodal AI and RAG (Verdantix), plus formal MLOps.
- Formal 5-stage business case and vendor selection (Microsoft). At most, include a one-paragraph cost–benefit sketch. Microsoft reports that "a rough cost–benefit analysis was sufficient to start PoC" for 42% of BUY and BUY-AND-INTEGRATE projects (MS-DOS p.35–36).

### Gaps
- None of the documents gives costs for small or low-cost deployments, Arduino-class hardware, or educational settings. Cost comparisons need other sources.
- None of the documents discusses CONWIP, WIP caps, Little's Law, cycle-time analysis or the Bosch Kaggle production dataset. The project needs separate lean/operations-management references for these.
- None of the documents defines a standard "OEE proxy" for sensor-limited lines. Audi gives only the three-factor definition (p.8).
