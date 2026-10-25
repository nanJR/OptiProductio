# CONWIP / WIP-cap alert: design, historical backtesting, and low-cost IoT carriers (OptiProductio)

Scope: how to set a WIP cap, how to evaluate a "WIP above cap, warn" alert on historical data (Bosch Production Line Kaggle), what alert metrics to report, which low-cost IoT monitoring papers to position against, and what a backtest can honestly claim. The project team already knows about Gosavi & Gosavi 2024 (IJPE 270:109169), Bokor & Altendorfer 2025 (FSMJ), Pettersen & Segerstedt 2009, Wicaksono 2024 and Raamets et al. 2025. This note adds to them.

Verification legend: [V] = checked this session against a primary page or publisher/DOI page. [P] = taken from a secondary source citing the item (bibliographic details likely right, content not read). [U] = not verified this session (from background knowledge); confirm before citing.

---

## Q1. How CONWIP / WIP caps are set in theory and practice, and how to derive a cap from observed data

### Takeaway
In theory the reference cap is the critical WIP W0 = rb·T0 (bottleneck rate × raw process time). Real lines with variability need more WIP than W0 to reach near-bottleneck throughput, and the Practical Worst Case (PWC) formula TH = w·rb/(W0+w−1) tells you how much. In practice caps are set by simulation or search (find the smallest w that hits a throughput target), or adjusted over time (Hopp & Roof's Statistical Throughput Control). From data, you estimate rb, T0 and average WIP/cycle time (Little's law) and then pick a cap from those numbers.

### Cited Findings
- **Original CONWIP paper** [V]: Spearman, M.L., Woodruff, D.L. & Hopp, W.J. (1990). "CONWIP: a pull alternative to kanban." *International Journal of Production Research* 28(5), 879–894. DOI: 10.1080/00207549008942761. Reprint page: [Project Production Institute reprint](https://projectproduction.org/journal/conwip-a-pull-alternative-to-kanban/). Volume, issue and pages come from [Comeau & Venkatadri, U. Moncton working paper](https://www.umoncton.ca/umcm-administration/files/umcm-administration/wf/wf/pdf/cahier_09-2014.pdf).
- In CONWIP a fixed set of cards caps total line WIP. A part cannot enter without a card, and the card returns to the start when a finished part leaves the last station. Spearman et al. used simulation to compare CONWIP with kanban and push, and found CONWIP reached lower WIP than kanban — [Wikipedia: CONWIP](https://en.wikipedia.org/wiki/CONWIP) (secondary).
- **Critical WIP** [V]: W0 = rb × T0, where rb is the bottleneck rate and T0 the raw process time. It is the WIP that gives maximum throughput (rb) and minimum cycle time (T0) in a line with no variability. More WIP only adds waiting, and less WIP loses throughput. The source calls it "a benchmark rather than a target." Attributed to Hopp & Spearman, *Factory Physics* (1996) — [Choo, PPI 2016, "Little's Law – A Practical Approach…"](https://projectproduction.org/journal/littles-law-a-practical-approach-to-understanding-production-system-performance/).
- **Little's law** [V]: TH = WIP / CT. It holds for long-run averages in a stable system — [Choo 2016](https://projectproduction.org/journal/littles-law-a-practical-approach-to-understanding-production-system-performance/). Queue time grows sharply as utilisation rises (Kingman 1961, cited there).
- **Best / worst / practical worst case formulas** [V], from [Columbia course notes based on Factory Physics](https://www.columbia.edu/~gmg2/4000/pdfold/throughput.pdf):
  - Best case: CT = T0 if w ≤ W0, else w/rb. TH = w/T0 if w ≤ W0, else rb.
  - Worst case: CT = w·T0, TH = 1/T0.
  - **Practical worst case** (balanced line, exponential process times): CT_PWC = T0 + (w−1)/rb, and TH_PWC = rb·w/(W0+w−1).
  - Use: plot the observed (WIP, TH) points against these three curves. A line below PWC is "bad" and above PWC is "good" (Factory Physics convention [P]). The cap is then the w where PWC (or the empirical curve) reaches the target share of rb. Solving TH_PWC = α·rb gives **w = α(W0−1)/(1−α)**. For example, α = 0.9 gives w ≈ 9(W0−1). (Algebra derived here from the formula above, not quoted.)
- **Ways the cap is set in the literature** (summarised in [Comeau & Venkatadri 2014 working paper](https://www.umoncton.ca/umcm-administration/files/umcm-administration/wf/wf/pdf/cahier_09-2014.pdf)) [P]:
  - Hopp, W.J. & Roof, M.L. (1998). "Setting WIP levels with statistical throughput control (STC) in CONWIP production lines." *IJPR* 36(4), 867–882. STC adjusts the allowed card count within upper and lower control limits as observed throughput drifts from target. This is the closest existing analogue to a monitored "WIP vs cap" alert. [P; DOI not retrieved, likely 10.1080/002075498193435 [U]]
  - Hopp & Spearman, *Factory Physics* (2001 edn.): the cap can be stated as total processing-time content instead of a count of lots. The two are the same only when products have similar processing times [P].
  - Ryan & Vorasayan (2005) *IJPR* 43(2), 223–246: separate card counts per product family [P]. Ryan & Choobineh (2003) *IIE Transactions* 35, 405–418: total WIP and WIP mix in a job shop [P].
  - Comeau & Venkatadri's own CUWIP: caps in "units of equivalence" proportional to processing time, tested at 10–70 UE [P].
- **Reviews** [V/P]: Framinan, González & Ruiz-Usano (2003). "The CONWIP production control system: review and research issues." *Production Planning & Control* 14(3), 255–265 [P]. Jaegler, Jaegler, Burlat, Lamouri & Trentesaux (2018). "The ConWip production control system: a systematic review and classification." *IJPR* 56(17), 5736–5757, DOI 10.1080/00207543.2017.1380325. It classifies papers by sizing, performance, context and comparison with other systems — [IDEAS/RePEc](https://ideas.repec.org/a/taf/tprsxx/v56y2018i17p5736-5757.html) [V]. Parameter setting with response-surface methodology in dynamic CONWIP: [Inderscience aid=42106](https://inderscience.com/filter.php?aid=42106) [U, abstract not read].

### Inferences
- **Recipe for deriving a cap from the Bosch data**:
  1. Reconstruct each part's entry time (min over its D-columns) and exit time (max over its D-columns).
  2. WIP(t) = number of parts with entry ≤ t < exit, sampled every 0.01 time units (about 6 min).
  3. TH(t) = exits per window, and CT = exit − entry.
  4. Estimate T0 as a low percentile (e.g. 5th) of per-part CT, and rb as a high percentile (e.g. 95th) of windowed TH, or the maximum sustained rate.
  5. W0 = rb·T0.
  6. Check Little's law: mean WIP should be close to mean TH × mean CT. A large gap means the entry/exit reconstruction is wrong.
  7. Candidate caps: (a) W0; (b) the PWC-based w for α = 0.9; (c) an empirical cap, the WIP level beyond which TH stops rising on a binned (WIP, TH) scatter (the "knee"); (d) a statistical cap, for example the 95th percentile of WIP or mean + 3σ from a training window.
- Option (d) is a control-chart limit, not a CONWIP cap. Say clearly in the report which kind of threshold the alert uses.
- The Bosch line is not CONWIP-controlled, so the observed data show uncapped (push) behaviour. The alert therefore says "WIP exceeded the level a CONWIP cap would have allowed." It does not say "a CONWIP cap was violated."
- The Bosch line has 4 lines and 51 stations with heterogeneous routings. A product-family or line-specific cap (as in Ryan & Vorasayan) may make more sense than one global cap.

### Gaps
- Exact DOI and pages for Hopp & Roof 1998 were not confirmed on the publisher site.
- I did not read the Factory Physics text directly. The PWC formula comes from course notes that reproduce it.
- I found no published paper deriving a CONWIP cap specifically from the Bosch Kaggle data.

---

## Q2. Evaluating a WIP cap counterfactually on historical data, and alert evaluation metrics

### Takeaway
Papers use three methods, from cheapest to strongest. (1) An analytic what-if with Little's law and PWC curves. (2) Trace-driven simulation, which replays real orders and arrival times through a discrete-event model with different caps. (3) Simulation calibrated to historical data and validated against it. Alerts are evaluated as event detection: precision and recall against failure bursts (range-based, Tatbul et al. 2018), lead time, false alarms per day, and for control-chart alerts, ARL0/ARL1. Classification-style scores (MCC) are what Bosch Kaggle work reports.

### Cited Findings
- **Trace-driven CONWIP evaluation, a real-factory example** [V]: Gunn & Nahavandi (2002), "Why initial conditions are important," *Proc. Winter Simulation Conference* — [PDF](https://www.informs-sim.org/wsc02papers/071.pdf).
  - Data and model: they took over 4,000 work orders from company databases and rebuilt the initial WIP from two months of transaction records. The deterministic discrete-event model has about 600 work centres and was validated against transaction files and hand-written logs.
  - Experiment: the CONWIP cap started at 1,800 buckets and was cut by 200 per run.
  - Results: a cap of about 1,200 buckets was estimated to save about $1.4M in WIP and about 12 days of lead time, and the savings were implemented. Starting the model from the real initial WIP changed the results noticeably: max WIP was about 33M pieces vs about 25M with zero initial WIP, and lead times differed by about 2–3 days.
  - Lesson for OptiProductio: a replay must start from the observed WIP, not an empty line.
- **Bosch dataset facts relevant to a replay** [V], from [Mangal & Kumar, arXiv:1701.00705](https://arxiv.org/html/1701.00705):
  - Size: 1,184,687 training parts and 968 numeric, about 2,140 categorical and 1,156 date features (the paper also says 1,157). Lines and stations are encoded in names such as L3_S50_D4242, with 4 lines and 51 stations.
  - Failures: under 1% of parts fail. Station 32 has a 4.7% error rate vs about 0.6% elsewhere.
  - Time: date values run 0–1718 at 0.01 resolution. The paper maps 0.01 to about 6 min (about 102.6 weeks in total), with week ≈ 16.75 units and day ≈ 2.39 units. This mapping is inferred from periodicity and is not ground truth.
  - Methods: a "time_diff" (time in line) feature correlates positively with failure. The paper used **random**, not time-ordered, 3-fold splits.
  - Results: best training MCC was 0.227, and public leaderboard MCC was 0.215.
- **Range-based precision/recall** [V]: Tatbul, Lee, Zdonik, Alam & Gottschlich (2018), "Precision and Recall for Time Series," *NeurIPS 31* — [proceedings](https://proceedings.neurips.cc/paper/2018/hash/8f468c873a32bb0619eaeb2050ba45d1-Abstract.html). Classical point-based precision and recall fit poorly when anomalies span time ranges. The paper extends both to ranges, with tunable weights for existence, overlap size, position and cardinality (these four components are from the full paper [U, abstract only read]). Fits "alert window vs failure-burst window" directly.
- **Data leakage** [V]: Kaufman, Rosset, Perlich & Stitelman (2012), "Leakage in data mining: formulation, detection, and avoidance," *ACM TKDD* 6(4). DOI: [10.1145/2382577.2382579](https://www.doi.org/10.1145/2382577.2382579). (Fourth author from background knowledge [U].)
- **Control-chart metrics** [U, standard SPC; search results pointed only to secondary pages]:
  - ARL0 is the mean number of samples to a false alarm when the process is in control. ARL1 is the mean number of samples to detection after a shift. EWMA and CUSUM detect small persistent shifts faster than a Shewhart chart at equal ARL0.
  - Standard reference: Montgomery, *Introduction to Statistical Quality Control* (Wiley, any edition).
  - Examples of EWMA ARL studies: [SJST 43(5)](https://sjst.psu.ac.th/journal/43-5/25.pdf), [Frontiers Appl. Math. Stat. 2023, DOI 10.3389/fams.2023.1268340](https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2023.1268340/pdf) (not read in detail).
- **Numenta Anomaly Benchmark (NAB)** [U]: Lavin & Ahmad (2015), IEEE ICMLA. It scores streaming detectors with windows around labelled anomalies, rewards early detection and penalises false positives. A good model for a lead-time-weighted score.

### Inferences
- **Suggested evaluation protocol for the student project**:
  1. Define target events, for example "failure burst": a time window (e.g. 0.24 units ≈ 1 h) whose failure rate is above the training-period 95th percentile. Or use a per-line or per-station definition.
  2. The alert fires when WIP(t) > cap, optionally only after k consecutive samples (debounce). An EWMA version uses z_t = λ·WIP_t + (1−λ)·z_{t−1}, with λ ≈ 0.1–0.3 and limits L·σ·√(λ/(2−λ)), L ≈ 2.7–3. A CUSUM version uses S_t = max(0, S_{t−1} + WIP_t − μ0 − k), with an alarm when S_t > h.
  3. Metrics to report:
     - event-level precision (alerts followed by a burst within horizon H / all alerts) and recall (bursts preceded by an alert within H / all bursts), and F1;
     - median lead time (burst start − first alert);
     - false alarms per simulated day;
     - in-control ARL0 measured on a quiet period;
     - a **baseline comparison** with a random alert at the same rate, "always alert", and a pure failure-rate alarm (a p-chart on recent failures).
  4. Test whether WIP even carries signal first: correlate binned WIP with next-window failure rate. The Kaggle finding that time-in-line predicts failure gives a plausible but not guaranteed reason to expect it.
  5. Show a precision–recall or "alerts/day vs recall" curve as the cap changes. This is more honest than one tuned cap.
- **Counterfactual tiers to state in the report**: (a) "detection backtest": the alert fires on observed WIP, with no change to the line. This is what the Bosch data supports. (b) "Little's-law what-if": if WIP had been held at cap w with the same TH, CT would have been w/TH. This is an analytic estimate that assumes TH is unchanged. (c) "Trace-driven DES": replay observed entry times and per-station times through SimPy with a card limit, as Gunn & Nahavandi did. This is the strongest option, but it assumes process times and failures do not depend on congestion.

### Gaps
- I found no paper that evaluates a WIP-threshold alert against quality-failure bursts specifically. This is a plausible novelty point, but my search was not exhaustive.
- I did not retrieve EWMA/CUSUM papers specific to WIP monitoring.
- How Bosch timestamps were anonymised is undocumented, so the 6-minute unit is an inference.

---

## Q3. Recent low-cost IoT / Arduino / ESP32 production-monitoring work (positioning)

### Takeaway
There are many low-cost monitoring papers, mostly in Malaysian and Indonesian journals and IEEE conferences in India. They count parts, compute OEE or efficiency, and push data to a cloud dashboard. None I found does WIP-cap (CONWIP) alerting or validates the alert logic on a public historical dataset. That combination is the defensible novelty for OptiProductio.

### Cited Findings
- Wicaksono, Ningsih & Surjati (2024). "Implementation of MQTT Protocol on ESP32-Based OEE Analysis Development Board." *Emitor: Jurnal Teknik Elektro* 24(2), 169–175. DOI 10.23917/emitor.v24i2.3908. Tested on a production floor, with a maximum OEE error of 16% — [journal page](https://journals2.ums.ac.id/index.php/emitor/article/view/3908) [V].
- "An IoT-based Production Monitoring System for Assembly Line in Manufacture," *International Journal of Integrated Engineering* (UTHM), Scopus 2-s2.0-85081939303. Built on Arduino Mega, an IR part sensor, an LCD timer and ESP8266 to the cloud, it reported about 4.5% higher worker efficiency — [UTHM page](https://penerbit.uthm.edu.my/ojs/index.php/ijie/article/view/5298) and [UiTM record](https://update.library.uitm.edu.my/Record/2-s2.0-85081939303/Description) [V content; authors and year not shown, likely 2019–2020 [U]].
- "A Metal Bed Production Monitoring System using Internet of Things," *Evolution in Electrical and Electronic Engineering* (UTHM) — [page](https://penerbit.uthm.edu.my/periodicals/index.php/eeee/article/view/11975) [P, not read].
- "Automated Conveyor Belt Object Counting with Integrating Real-Time Monitoring Dashboard," *Progress in Engineering Application and Technology* (UTHM) — [page](https://periodical.uthm.edu.my/index.php/peat/article/view/22555) [P, not read].
- Samal, Mahapatra & Swain (2024). "Application of Secure and Energy-Efficient Data Access Solutions in Industrial IoT for Small-Scale Industry." *16th IEEE CICN*, Indore, India. It uses an ESP32 soft-AP with authenticated web access, drawing about 195 mA transmitting and 148 mA idle — [NIT Rourkela repository](https://dspace.nitrkl.ac.in/dspace/handle/2080/4923) [V]. This is an Indian IEEE conference example, though it is about security and energy, not flow control.
- "Intelligent Low-Cost Monitoring for Smart Digital Manufacturing" (Univ. Salamanca) — [record](https://produccioncientifica.usal.es/documentos/66939b6c19f8ae74e233af0d) [P, not read].
- "Real-Time Monitoring of Shop Floor Machines with Open Sources Technologies: A Case Study," *Engineering Headway* 22, 31 — [Scientific.net](https://www.scientific.net/EH.22.31) [P, not read].

### Inferences
- **Positioning statement**: earlier low-cost systems measure (counts, OEE, efficiency). OptiProductio adds a theory-grounded control signal: a WIP cap derived from Factory Physics and CONWIP, with an alert validated offline on a 1.18M-part public dataset before it runs live. The existing small-hardware OEE reference is Wicaksono's 16% error figure. Report the demo line's own count and WIP accuracy against a manual tally in the same way.
- Arduino UNO has no networking, so pair it with an ESP8266/ESP32 or a serial link to a PC dashboard. Live WIP needs **two sensors per controlled loop** (entry and exit counters): WIP = entries − exits, with periodic manual resets to correct drift.

### Gaps
- I did not find a strong IEEE Xplore list of Indian student-conference (e.g. ICCCNT, I2CT, INDICON) papers on Arduino/ESP32 production monitoring this session. Search IEEE Xplore with "ESP32 production monitoring" filtered 2018–2026 and conference location India.
- Most low-cost monitoring papers found are in regional journals of uneven quality. Cite them as context, not as validation evidence.

---

## Q4. What an honest "backtest" can and cannot claim

### Takeaway
A Bosch backtest can show that a WIP-threshold signal, chosen on earlier data, would have flagged later failure bursts with some measured precision, recall and lead time, compared with baselines. It cannot show that capping WIP would have prevented failures or improved throughput, because nobody intervened in the data. Results are only credible with a time-ordered train/test split and thresholds frozen before test.

### Cited Findings
- **Leakage**: features or thresholds that use information unavailable at prediction time inflate performance. Kaufman et al. formalise this, and detecting and avoiding it is the paper's focus — [Kaufman et al. 2012, TKDD, DOI 10.1145/2382577.2382579](https://www.doi.org/10.1145/2382577.2382579) [V bibliographic; content from background [U]].
- The main Bosch Kaggle write-up used random 3-fold splits, not time-ordered ones. Its "time_diff" feature uses the part's exit time, which is only known after the part finishes — [arXiv:1701.00705](https://arxiv.org/html/1701.00705) [V]. Both are leakage risks a time-aware backtest must avoid.
- **Initial conditions matter in replay**: models started from empty WIP misstate WIP and lead times compared with models started from observed WIP — [Gunn & Nahavandi 2002](https://www.informs-sim.org/wsc02papers/071.pdf) [V].
- Little's law needs long-run averages from a stable system, so applying it to short windows or ramp-ups is approximate — [Choo 2016](https://projectproduction.org/journal/littles-law-a-practical-approach-to-understanding-production-system-performance/) [V].

### Inferences
- **Must do**:
  1. Use a chronological split, e.g. first 60% of time for train, the next 20% for choosing the cap and debounce, and the last 20% for test, touched once. Or use rolling-origin evaluation.
  2. Compute WIP(t) only from parts whose entry time is ≤ t. For "in-WIP" status at t, use only whether the part has exited by t, never its later exit time or Response label.
  3. Freeze the cap, λ, L and k before scoring test.
  4. Report the baselines and confidence intervals, e.g. a block bootstrap over days.
  5. Report how many caps and settings were tried, because multiple-testing inflation is a risk.
- **Cannot claim**: causal effects ("capping WIP reduces failures"), throughput or lead-time gains from a cap without a simulation model, or generalisation to the demo line (different process and scale).
- **Selection and representativeness bias**:
  - Kaggle Bosch is a cleaned, anonymised subset. Its time window and parts may not be the full production population.
  - Parts that were scrapped mid-line or are missing date columns distort entry and exit reconstruction.
  - The <1% failure rate makes precision fragile.
  - The test set has no Response labels on Kaggle, so only the train file can be backtested.
- **Confounding**: high WIP and high failure rate may both come from a third factor, such as a product mix change, a shift pattern (weekly and daily periodicity is visible in the data) or station 32. Control for time-of-week, or stratify by line.
- **Wording for the report**: "Retrospective detection backtest (no intervention)", "counterfactual WIP-cap estimates via Little's law (analytic, assumes unchanged throughput)", and optionally "trace-driven simulation (model-based)".

### Gaps
- There is no published guidance specific to backtesting CONWIP alerts. The rules above are adapted from ML leakage and SPC practice.
- The Kaggle test labels were never released, which limits the out-of-sample period to a slice of the training file.
