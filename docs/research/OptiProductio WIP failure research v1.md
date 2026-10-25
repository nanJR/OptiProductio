# Rebuilding Bosch WIP could earn OptiProductio a paper

Yes, there is a realistic short paper here, but only if you write it up as an honest exploratory study and nothing bigger. In what our searches covered, nobody has rebuilt WIP, flow time and throughput series from the Bosch Production Line Performance date tables. Nobody has tested whether parts that enter a crowded line fail more often, and nobody has backtested a CONWIP-style WIP-cap alert against failure bursts on this data. Existing Bosch papers are almost all failure-prediction models [1][3][4]. The closest earlier work turns the dates into lead time [3] or "parts per 6-minute takt" features [4]. The literature suggests that if a WIP effect shows up at all, it will be small and probably threshold-shaped [9][12][13]. The main risks are reverse causation (failures cause rework, and rework causes WIP) and product-mix confounding. None of the analysis below has been run yet, so this report contains no results, only a plan. The data is widely used in peer-reviewed work [3][4][32][33], but the exact Kaggle rules wording is unverified and you have to check it yourself. Keep the EL build as the only job until Sunday 1 Nov 2026. After that, the most realistic target is the 4-page Work-in-Progress track at IEEE CONECCT 2027 in Bengaluru, with an expected deadline around February 2027 (inferred from the 2026 edition [34][35]). RVCE's CSITSS and IEEE IEEM around July 2027 are the backups [36][37].

## Nobody has rebuilt WIP from the Bosch dates, so the gap is real

The Bosch data has about **1.18 million training parts, of which 6,879 failed (about 0.58%)**, and a test set of about the same size with no labels [1][7][8]. Each set comes as three row-aligned tables (numeric, categorical and date) keyed by `Id`. Column names follow the pattern L{line}_S{station}_D{n} for timestamps [1]. The date values are anonymised. They run from about 0 to 1718 at a step of 0.01, and autocorrelation peaks at 16.75 units (read as one week) and 2.39 units (read as one day) [1][2]. That makes **0.01 units about 6 minutes, 1 unit about 10 hours, and 0.1 units about 1 hour**. Bosch never published this conversion. It comes from the community's reading of the periodicity, so the paper has to call it an assumption [1][2]. Sources disagree slightly on the train row count (1,184,687 vs 1,183,747) and on whether there are 51 or 52 stations [1][6][8], so count both yourself after downloading.

Competition teams used the dates heavily, but only as features for predicting failures. The 8th-place solution built per-station and per-line durations, timestamp kurtosis and "same timestamp as the next part" features [5]. The well-known "magic" features came from sorting parts by Id and start time, and they exploit batch adjacency. Mangal and Kumar left them out because a real line would not have them in real time [1][2]. Aslan et al. computed lead time as last date minus first date and modelled the six most common station paths, reporting a mean of 10.71 units with an SD of 17.01 [3]. At the inferred conversion that is a mean of about 4.5 days with a long tail. Nikolova et al. came closest to a congestion measure with a "number of parts in one takt" feature and failure counts over the previous and next 1, 10 and 24 hours, but they used these only as classifier inputs [4]. We found no paper that treats the data as an event log, builds a WIP time series, checks Little's law on it, or asks whether congestion goes with failure. This was a limited search (about six queries on the Bosch side), so before you write "first" anywhere, do a Google Scholar "cited by" sweep on Mangal and Kumar [1] and Aslan et al. [3].

The hardware side has a similar gap. Low-cost monitoring papers count parts, compute OEE or worker efficiency, and push numbers to a dashboard. Wicaksono et al. reported a maximum OEE error of 16% on an ESP32 board [29], and a UTHM paper built an Arduino Mega line monitor that reported about 4.5% higher worker efficiency [30]. None of the ones we found sets a WIP cap from queueing theory or checks its alert logic on a public historical dataset. So OptiProductio has three possible novelty claims: (1) WIP, flow time and throughput rebuilt from the Bosch dates, (2) a part-level WIP-and-failure association test that controls for reverse causation, and (3) a CONWIP-derived cap alert, backtested offline, which is then the same logic the Arduino UNO dashboard runs live.

## The literature expects a small, threshold-shaped WIP effect, if there is one at all

No peer-reviewed manufacturing study we found reports a part-level odds ratio between defect probability and concurrent line WIP. That absence is part of why the paper is worth writing, but it also means you have no benchmark effect size, and you should not guess one. The manufacturing evidence is at firm or plant level and over long time spans. Lieberman and Demeester found that **each 10% cut in inventory went with roughly a 1% gain in labour productivity about a year later** across 52 Japanese auto firms [9]. Note that the outcome there is productivity, not defects. Alles et al. modelled how low inventory helps workers see and understand the process, and they report that data from 116 plants support a link from lower inventory to better reliability and quality. The abstract gives no effect size [10]. Wein argued that shorter cycle time raises semiconductor yield (unverified, check before citing) [45].

Hospital studies give the clearest picture of what the curve might look like. KC and Terwiesch found that staff speed up under load, but sustained overwork backfires: a **10% rise in overwork went with about a 2% rise in mortality likelihood** [11]. Kuntz et al. found a **mortality tipping point at about 92.5% bed occupancy** across 83 German hospitals [12]. Berry Jaeker and Tucker found an N-shaped occupancy curve with a second tipping point at 93% [13]. A factory is not a hospital, but these results suggest you should test WIP as a curve (splines or deciles), not only as a straight-line slope. A flat linear result would not rule out a threshold.

The mechanisms point both ways, and that matters for the design. In the "WIP causes defects" direction there is detection delay: more parts sit between where a defect is made and where it is caught (Cordon [15]; Hopp and Spearman [16]; Porteus's lot-size model [17], all unverified, check before citing). There is also lost visibility [10] and worker overload [11]. In the "defects cause WIP" direction, failed parts get held, retested and reworked, which stretches their flow time and adds to WIP. FabTime makes exactly this point for fabs, where held lots have both longer cycle times and worse yields [14]. The Bosch data likely contains this too: station S32 has a 4.7% failure rate against about 0.6% elsewhere and may be a rework step [1][2]. Product mix is probably the biggest confounder. Parts follow thousands of different station paths (reported counts range from 4,700 to 7,928 [3][6]) with different base failure rates, and a shift in mix changes WIP and failure rate together.

## The method: an event sweep, WIP measured at entry, and a time-ordered split

The standard way to build WIP from timestamps is the sample-path method. For each part, take entry time a and exit time d. WIP at time t is the number of parts with a ≤ t < d, and you get it by sorting +1 (entry) and −1 (exit) events and taking a running sum. Flow time is d − a, and throughput is exits per time bin. Kim and Whitt show how to apply Little's law to a finite, non-stationary observation window, with confidence intervals from batch means and a fix for edge effects when the line does not start and end empty [18]. Brochado et al. showed that station exit timestamps alone are enough to rebuild a line layout and find bottlenecks at a real Bosch Thermotechnology plant (unverified, check before citing) [19]. That plant is not the Kaggle one, but it is a useful precedent.

Bosch has four quirks you have to handle. First, the timestamps are measurement times, not true entry and exit times, so flow time is a lower bound and mixes processing with waiting. Call it station-to-station sojourn, not queue time. Second, train and test parts were on the line at the same time, so WIP has to be built from `train_date` plus `test_date`, while failure labels come only from train. Check that the two time ranges overlap before you rely on this. Third, rounding to 0.01 units means many parts share a timestamp, so pick a tie rule (for example, exits before entries) and state it. Fourth, the edges of the window are biased. Drop a warm-up and cool-down margin at least as long as the 95th-percentile flow time [18], and watch for shutdown gaps that look like zero WIP.

To reduce reverse causation, measure each part's exposure at its **entry** time and leave the part itself out of the count (WIP at entry minus 1). Also use the average WIP over the hour or few hours before entry, which follows the lagged reasoning in Lieberman and Demeester [9]. Add a placebo test: if WIP after the part has already left also "predicts" its failure, the association probably comes from common shocks or reverse causation, not from congestion. Do not use the part's own flow time as a predictor in the alert. It depends on the exit time, which is not known until the part leaves. Mangal and Kumar's "time in line" feature has this problem, and they also used random rather than time-ordered folds [1]. Both are leakage in Kaufman et al.'s sense [27].

### Table of analysis parameters

| Item | What to use | Why / source |
|---|---|---|
| Data | `train_date` + `test_date` (all parts, for WIP); `Id`, `Response` from `train_numeric` (labels). Read in chunks, take the row-wise min/max per station prefix, save a long (Id, station, t) table to Parquet | Test parts share the line; date tables are sparse, about 7% filled [6][8]; about 14–15 GB in total [1] |
| Time unit | Raw units, also shown as approximate hours (1 unit ≈ 10 h; 0.01 ≈ 6 min) | Inferred from periodicity, not from Bosch [1][2] |
| Entry / exit | Entry = min non-null timestamp, exit = max, per part (and per station for station-level WIP) | Sample-path method [18]; same as Aslan's lead time [3] |
| Unit of analysis (H1, WIP and failure) | One row per labelled train part | Gives one exposure per part |
| Unit of analysis (H2, alert) | Time bins of 0.1 units (about 1 h) | Matches failure-burst windows |
| Inputs (exposure) | WIP at entry minus 1; mean WIP over 0.1–0.4 units (about 1–4 h) before entry; throughput in the same window | Exposure at entry limits reverse causation [9][14] |
| Label | H1: `Response` (0/1). H2: "failure burst" = a 1-h bin whose failure rate is above the 95th percentile of the calibration block | Burst definition adapted from the CONWIP notes; fix it before testing |
| Model (H1) | Logistic regression with WIP as a natural spline or deciles; Firth (penalised) logistic for small strata. Cross-check: hourly Poisson or negative binomial on failure counts with log(parts exited) as offset | Rare outcome (0.58%); nonlinearity expected [12][13] |
| Controls | Line fixed effects; the most common station paths as dummies, with an "other" bucket (or stratify on the top paths as in [3]); week fixed effects; hour of day (t mod 2.39); day of week (t mod 16.75); throughput | Product mix and time patterns are the main confounders [1][3] |
| Standard errors | Clustered by day; block bootstrap over days for intervals | Failures cluster in time [4] |
| Sensitivity checks | Drop parts that pass S32; placebo with future WIP; linear vs spline; train-only WIP vs train+test WIP | S32 looks like rework [1] |
| Alert rule (H2) | Alert when WIP > cap for k bins in a row. Candidate caps: (a) critical WIP W0 = rb·T0; (b) practical-worst-case cap w = α(W0−1)/(1−α) with α = 0.9; (c) the "knee" where throughput stops rising with WIP; (d) 95th percentile or mean + 3σ of WIP (a control limit, not a CONWIP cap). EWMA version with λ = 0.1–0.3 and L = 2.7–3 | [16][20][21][22][28]; formula (b) is our own algebra from the PWC curve in [22] |
| Cap inputs | T0 = 5th percentile of flow time; rb = 95th percentile (or max sustained) of binned throughput | From the CONWIP notes, based on [21][22] |
| Split | Chronological, on the labelled timeline: first 60% for exploring and fitting, next 20% for choosing cap, k and λ, last 20% for the test, run once | Avoids leakage [27]; Kaggle test labels were never released |
| Metrics | H1: odds ratio per +1 SD of WIP and the absolute risk difference, with 95% CI. H2: event-level precision, recall and F1; range-based precision/recall [26]; median lead time; false alarms per day; ARL0 on a quiet period; MCC at bin level (not comparable to the Kaggle part-level leaderboard) | [26][28] |
| Baselines (H2) | Random alerts at the same rate; always-on alert; a p-chart on recent failures | Without these, precision numbers mean little |
| Targets (decision rules, set before the test run) | H1: call it an "association" only if the test-block CI excludes no effect and the placebo is null. H2: claim the alert "carries signal" only if its precision and recall beat the random same-rate baseline with a bootstrap CI on the difference that excludes zero. Little's law check: report the gap between mean WIP and mean throughput × mean flow time, with a tolerance you pick in advance (our suggestion: 10%, not from a source) | No published benchmark exists to set a numeric target, so none is given here |
| Reporting | Number of caps and settings tried; a recall vs alerts-per-day curve across caps, not just one tuned cap | Guards against multiple-testing inflation |

Write this table, the burst definition and the split dates into a dated file in your repo before you open the test block. That is your pre-registration, and reviewers will trust the results more because of it.

## The CONWIP alert is a detection backtest, not a cap trial

CONWIP caps total line WIP with a fixed number of cards: a part cannot enter until a finished part frees a card [20]. The textbook reference cap is the critical WIP, W0 = rb × T0, which is the lowest WIP that reaches full throughput on a line with no variability. The source calls it "a benchmark rather than a target" [21]. Real lines need more than W0, and the practical-worst-case curve, TH = w·rb/(W0 + w − 1), tells you how much more [22]. In practice, caps are found by simulation or adjusted over time, for example with Hopp and Roof's statistical throughput control, which is the closest published analogue to a monitored WIP-cap alert [23][24]. The Bosch line has many product families, so a cap per line or per family may make more sense than one global cap [44].

The Bosch line was not run under CONWIP, so the data shows uncapped behaviour. That limits what you can say. You **can** say that a WIP threshold chosen on earlier data would have flagged later failure bursts with a measured precision, recall and lead time, compared with baselines. You can also say whether parts entering at high WIP had higher failure rates, after controls, in this dataset. You **cannot** say that capping WIP would have prevented failures, raised throughput or cut lead time, because nobody intervened. You cannot claim causation from the association test, and you cannot claim the result carries over to the OptiProductio demo line, which is a different process at a much smaller scale. The alert means "WIP went above the level a CONWIP cap would have allowed", not "a CONWIP cap was broken". If you want a what-if number, label it clearly. A Little's-law estimate (flow time ≈ cap ÷ throughput) assumes throughput stays the same. A trace-driven simulation in SimPy is stronger, but it assumes process times do not change with congestion. Gunn and Nahavandi showed that such a replay must start from the observed WIP, not an empty line [25]. For a 4-page first paper, the detection backtest plus the Little's-law what-if is enough. Leave the simulation for later.

Treat a null result as a real possibility, and plan for it. If WIP shows no association with failure and the alert does no better than random, the paper is still useful: it gives a reusable WIP reconstruction of a public dataset, a Little's-law consistency check, and an honest negative result for a common lean assumption. Frame the paper that way from the start so it does not depend on getting a positive result.

## The data is usable, provided you read the rules tab first

The dataset has been used in peer-reviewed journals and conferences: IJAMT (Springer) [3], FedCSIS [4], IEEE ICIT [32] and MDPI *Machines* [33]. Bosch and Kaggle also ran an academic grant track for papers on it [2]. So publishing analysis of this data is normal practice. What we could not check is the exact wording of the Bosch competition's data-use rules. Kaggle's pages did not render for our tools. One quoted Kaggle rule from another competition says data may be used "solely for the purpose and duration of the Competition" [31], which shows that some competitions restrict use. Do not assume Bosch allows academic use until you have read the rules tab while logged in and copied the "Data Access and Use" section. Whatever it says, the safe practice is the same: do not redistribute the raw CSVs, point readers to the Kaggle page, cite the competition as the data source, and share only your code and derived aggregates (WIP series, flow-time histograms) if the rules allow it. In practice you only need the two date files plus the `Id` and `Response` columns, and the long event table should fit in a laptop's memory (about 7–10 million rows by our estimate). The 8th-place team needed at least 16 GB of RAM because they loaded everything [5].

## CONECCT 2027's 4-page track fits the timeline after 1 November

| Venue | Fit | Deadline | Status |
|---|---|---|---|
| IEEE CONECCT 2027, Work-in-Progress/Position track (IEEE Bangalore Section, Bengaluru) | 4 pages including references, open to all; Industrial Automation track [35] | Around early-to-mid Feb 2027 (2026 edition: 9 Feb 2026 [34]) | Inferred; 2027 call not out yet |
| CSITSS 2027 (hosted by RVCE) | Up to 6 pages [36] | Around late July 2027 (2024 edition: 30 Jul 2024 [36]) | Inferred; IEEE co-sponsorship and a 2025/26 edition unconfirmed |
| IEEE IEEM 2027 | Best topic match (industrial engineering), IEEE Xplore [37] | Around 1 Jul 2027 (2026 edition: 1 Jul 2026 [37]) | Inferred; international and probably expensive |
| IEEE INDICON 2027 | IEEE India Council flagship [38] | Around late Aug 2027 (2026 edition: 31 Aug 2026 [38]) | Inferred |
| SCES-2027 (MNNIT Allahabad) | Student conference, INR 5,900 student fee [39] | 15 Nov 2026 | Confirmed date, but IEEE sponsorship for 2027 not stated; too soon after the EL deadline |
| IISE Lean student paper / IEOM undergraduate competitions | Undergrad-friendly; IEOM allows online participation and course projects [40][41] | IISE abstracts likely around 10 Nov 2026 (inferred); IEOM dates not found | Skip IISE for this cycle; check IEOM |

CONECCT is the best first target. It is local, run by the IEEE Bangalore Section, and its Work-in-Progress track takes exactly the kind of 4-page exploratory paper this would be [35]. SCES's 15 November deadline comes two weeks after the EL demo, before you have even downloaded the data, so it would push you into rushing the analysis or into overclaiming. Before you submit anywhere, look the event up in IEEE Conference Search and check that the IEEE Section's own site links to it [42][43]. Remember that IEEE expects an in-person presentation for a paper to go into Xplore [42].

A realistic timeline, with the EL build as the priority:

| Dates | Work |
|---|---|
| 24 Oct – Sun 1 Nov 2026 | EL build only. One 15-minute task: log in to Kaggle, accept the rules, and save the rules-tab wording. |
| 2 – 15 Nov | Download the date files. Sanity checks: row counts, station count, train/test time overlap, the 16.75 and 2.39 periodicity. Build the event table. |
| 16 Nov – 6 Dec | WIP, flow time and throughput series; Little's law check; descriptive figures. Write and date the analysis plan (the parameter table above). |
| 7 Dec 2026 – 3 Jan 2027 | Fit models on the first 60%; choose the cap, k and λ on the next 20%. Measure the OptiProductio demo line's count and WIP accuracy against a manual tally (as in [29]). |
| First week of Jan 2027 | Run the test block once. Record every setting tried. |
| Jan – early Feb 2027 | Write 4 pages in the IEEE template; faculty mentor review; plagiarism and PDF checks. Watch for the CONECCT 2027 call (expected around Dec 2026). |
| Around early–mid Feb 2027 | Submit to the CONECCT 2027 WIP track (date inferred, confirm it). |
| Fallback, Jul – Aug 2027 | Extend to 6 pages (add a SimPy replay) for CSITSS, IEEM or INDICON 2027. |

We do not know RVCE's exam dates, so line this plan up against the academic calendar, especially for December and January.

## Conclusion

The paper's value is not a striking result, because there may not be one. Its value is that it brings Factory Physics into a dataset that has so far been treated only as a classification contest. Little's law, critical WIP and an honest time-ordered backtest are new on this data, and they connect directly to what the OptiProductio dashboard does on real hardware. That gives a first-year team something most low-cost monitoring papers lack: alert logic checked against a million-part public dataset before it runs live, with its limits stated plainly.

The biggest risk is not the venue or the deadline. It is a leak sneaking into the analysis through exit times, Id adjacency or a cap tuned on the test block. If the plan is frozen in December and the test block is opened once in January, whatever comes out, positive or null, will hold up in review.

## Glossary

| Term | Plain meaning | ELI5 |
|---|---|---|
| WIP (work in progress) | Parts that have entered the line but not left it yet | How many toys are on the table, half-built, right now |
| Flow time | Time from a part's entry to its exit | How long one toy spent on the table |
| Throughput | Finished parts leaving the line per unit time | How many toys get finished each hour |
| Little's law | Average WIP = throughput × average flow time | If 10 toys finish an hour and each takes 2 hours, about 20 are on the table |
| CONWIP | Pull control that caps total line WIP with a fixed number of cards | You can only start a new toy when a finished one frees up a ticket |
| Critical WIP (W0) | Bottleneck rate × raw process time; the smallest WIP that gives full throughput on an ideal line | Just enough toys on the table to keep the slowest helper always busy |
| MCC (Matthews correlation coefficient) | A single score from −1 to 1 for yes/no predictions that stays fair when one class is rare | A grade that can't be fooled by always guessing "no failure" |
| Precision / recall | Precision: share of alerts that were real. Recall: share of real events that got an alert | Precision: how often the alarm was right. Recall: how many fires the alarm caught |
| EWMA | Exponentially weighted moving average; recent values count more than old ones | A running average that cares most about what just happened |
| Leakage | Using information the model would not have at the time of the decision | Peeking at the answer sheet before the test |

## Open items you must check before writing

1. **Kaggle rules tab.** Log in, open the Bosch competition rules, and copy the "Data Access and Use" wording word for word. Check that it allows academic publication [31].
2. **Basic counts.** Run `wc -l` for the train row count (1,184,687 vs 1,183,747), count the distinct station IDs (51 vs 52), and count the date columns (1,156 vs 1,157) [1][6].
3. **Train/test overlap.** Confirm that test parts share the same time range as train parts before you build WIP from both.
4. **Time unit.** Recheck the 16.75-unit weekly and 2.39-unit daily periodicity yourself. One of our notes says "1 unit ≈ 6 minutes" and another gives "0.24 units ≈ 1 hour"; both conflict with 0.01 units ≈ 6 minutes, which is the reading in [1] and [2]. Use 0.01 ≈ 6 min.
5. **Novelty sweep.** Do a Google Scholar "cited by" check on [1] and [3] for any WIP, queue or process-mining paper on this data.
6. **Unverified references.** Check [15], [16], [17], [19], [23], [28], [44] and [45], plus the titles and authors marked unverified in the list below.
7. **Venue status.** Confirm CONECCT 2027 dates when the call comes out, whether CSITSS runs in 2027 and is IEEE co-sponsored, and IEEE sponsorship for SCES-2027 [39][42].
8. **Fees and travel.** Student registration fees for CONECCT, CSITSS and IEEM were not found. Ask the department whether it will fund them.

## References

[1] Mangal, A., & Kumar, N. (2016). *Using big data to enhance the Bosch production line performance: A Kaggle challenge* (arXiv:1701.00705). arXiv. https://arxiv.org/pdf/1701.00705 (title unverified, check before citing)

[2] Kaggle Team. (n.d.). *Bosch Production Line Performance competition: Symposium for Advanced Manufacturing grant winners*. Kaggle Blog (Medium). https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe (author and date unverified, check before citing)

[3] Aslan, A., Vasantha, G., El-Raoui, H., Quigley, J., Hanson, J., Corney, J., & Sherlock, A. (2023). Hierarchical ensemble deep learning for data-driven lead time prediction. *The International Journal of Advanced Manufacturing Technology, 128*(9), 4169–4188. https://doi.org/10.1007/s00170-023-12123-4 (full author list unverified, check before citing)

[4] Nikolova, D., Lameski, P., Pires, I. M., & Zdravevski, E. (2023). Towards Industry 4.0: Machine malfunction prediction based on IIoT streaming data. In *Proceedings of the 18th Conference on Computer Science and Intelligence Systems (FedCSIS 2023)*, ACSIS Vol. 35 (pp. 291–296). https://annals-csis.org/Volume_35/drp/pdf/677.pdf (author initials unverified, check before citing)

[5] joostgp. (n.d.). *kaggle_bosch* [Source code]. GitHub. https://github.com/joostgp/kaggle_bosch

[6] NYC Data Science Academy. (n.d.). *[Bosch Production Line Performance student project]*. NYC Data Science Academy Blog. https://nycdatascience.com/blog/student-works/15212/ (title, author and date unverified, check before citing)

[7] (Authors unverified). (2021). *[Federated learning for failure prediction on the Bosch production line]* (arXiv:2101.11715). arXiv. https://arxiv.org/pdf/2101.11715 (title and authors unverified, check before citing)

[8] (Authors unverified). (2024). *[Rare-event data enrichment study]* (arXiv:2407.01644). arXiv. https://arxiv.org/pdf/2407.01644 (title and authors unverified, check before citing)

[9] Lieberman, M. B., & Demeester, L. (1999). Inventory reduction and productivity growth: Linkages in the Japanese automotive industry. *Management Science, 45*(4), 466–485. https://doi.org/10.1287/mnsc.45.4.466 (title unverified, check before citing)

[10] Alles, M., Amershi, A., Datar, S., & Sarkar, R. (2000). Information and incentive effects of inventory in JIT production. *Management Science, 46*(12), 1528–1544. https://doi.org/10.1287/mnsc.46.12.1528.12079

[11] KC, D. S., & Terwiesch, C. (2009). Impact of workload on service time and patient safety: An econometric analysis of hospital operations. *Management Science, 55*(9), 1486–1498. https://doi.org/10.1287/mnsc.1090.1037 (title unverified, check before citing)

[12] Kuntz, L., Mennicken, R., & Scholtes, S. (2015). Stress on the ward: Evidence of safety tipping points in hospitals. *Management Science, 61*(4), 754–771. https://doi.org/10.1287/mnsc.2014.1917

[13] Berry Jaeker, J. A., & Tucker, A. L. (2017). Past the point of speeding up: The negative effects of workload saturation on efficiency and patient severity. *Management Science, 63*(4), 1042–1062. https://doi.org/10.1287/mnsc.2015.2387 (full title and volume/issue unverified, check before citing)

[14] INFICON/FabTime. (n.d.). *Fab tradeoffs: Higher cycle time for higher yield?* https://www.inficon.com/en/news/fab-tradeoffs-higher-cycle-time-for-higher-yield (not peer-reviewed)

[15] Cordon, C. (1995). [Paper on quality defects and work-in-process inventory]. *European Journal of Operational Research*. https://consensus.app/papers/details/ce9857ee9ddf55eeaa01750c03119f11/ (title, volume and pages unverified, check before citing)

[16] Hopp, W. J., & Spearman, M. L. (2008). *Factory physics* (3rd ed.). Waveland Press. (unverified, check before citing; chapter and page numbers not checked)

[17] Porteus, E. L. (1986). Optimal lot sizing, process quality improvement and setup cost reduction. *Operations Research, 34*(1), 137–144. https://doi.org/10.1287/opre.34.1.137 (unverified, check before citing)

[18] Kim, S.-H., & Whitt, W. (2013). Statistical analysis with Little's law. *Operations Research, 61*(4), 1030–1045. https://doi.org/10.1287/opre.2013.1193

[19] Brochado, et al. (2022). [Production metrics and bottleneck detection from station exit timestamps at a Bosch Thermotechnology plant]. *International Journal of Management Science and Engineering Management*. https://consensus.app/papers/details/19e0c24a112e5763ada25034bee15b2a/ (title, authors and volume unverified, check before citing)

[20] Spearman, M. L., Woodruff, D. L., & Hopp, W. J. (1990). CONWIP: A pull alternative to kanban. *International Journal of Production Research, 28*(5), 879–894. https://doi.org/10.1080/00207549008942761

[21] Choo, H. J. (2016). *Little's law – A practical approach to understanding production system performance*. Project Production Institute Journal. https://projectproduction.org/journal/littles-law-a-practical-approach-to-understanding-production-system-performance/ (author initials unverified, check before citing)

[22] Columbia University. (n.d.). *Throughput* [Course notes, IEOR 4000]. https://www.columbia.edu/~gmg2/4000/pdfold/throughput.pdf (author unverified, check before citing)

[23] Hopp, W. J., & Roof, M. L. (1998). Setting WIP levels with statistical throughput control (STC) in CONWIP production lines. *International Journal of Production Research, 36*(4), 867–882. (DOI not confirmed; unverified, check before citing)

[24] Jaegler, Y., Jaegler, A., Burlat, P., Lamouri, S., & Trentesaux, D. (2018). The ConWip production control system: A systematic review and classification. *International Journal of Production Research, 56*(17), 5736–5757. https://doi.org/10.1080/00207543.2017.1380325

[25] Gunn, E. A., & Nahavandi, S. (2002). Why initial conditions are important. In *Proceedings of the 2002 Winter Simulation Conference*. https://www.informs-sim.org/wsc02papers/071.pdf (author initials unverified, check before citing)

[26] Tatbul, N., Lee, T. J., Zdonik, S., Alam, M., & Gottschlich, J. (2018). Precision and recall for time series. In *Advances in Neural Information Processing Systems 31*. https://proceedings.neurips.cc/paper/2018/hash/8f468c873a32bb0619eaeb2050ba45d1-Abstract.html

[27] Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, detection, and avoidance. *ACM Transactions on Knowledge Discovery from Data, 6*(4). https://doi.org/10.1145/2382577.2382579 (fourth author unverified, check before citing)

[28] Montgomery, D. C. (n.d.). *Introduction to statistical quality control*. Wiley. (edition and year unverified, check before citing)

[29] Wicaksono, Ningsih, & Surjati. (2024). Implementation of MQTT protocol on ESP32-based OEE analysis development board. *Emitor: Jurnal Teknik Elektro, 24*(2), 169–175. https://doi.org/10.23917/emitor.v24i2.3908 (author initials unverified, check before citing)

[30] (Authors unverified). (n.d.). An IoT-based production monitoring system for assembly line in manufacture. *International Journal of Integrated Engineering*. https://penerbit.uthm.edu.my/ojs/index.php/ijie/article/view/5298 (authors and year unverified, check before citing)

[31] fast.ai Forums. (n.d.). *Kaggle datasets licensing question*. https://forums.fast.ai/t/kaggle-datasets-licensing-question/9191 (forum post, not an official source)

[32] Carbery, C. M., Woods, R., & Marshall, A. H. (2018). A Bayesian network based learning system for modelling faults in large-scale manufacturing. In *2018 IEEE International Conference on Industrial Technology (ICIT)*. https://doi.org/10.1109/ICIT.2018.8352377 (initials unverified, and whether it uses the Kaggle data is unverified, check before citing)

[33] Park, & Baek. (2026). Data-driven defect prediction for manufacturing quality monitoring under class imbalance and missing data: A performance–efficiency trade-off analysis. *Machines, 14*(7), 716. https://doi.org/10.3390/machines14070716 (author initials unverified, check before citing)

[34] IEEE Bangalore Section. (2026). *IEEE CONECCT 2026*. https://2026.connect.ieeebangalore.org/

[35] IEEE Bangalore Section. (2026). *IEEE CONECCT 2026 call for papers*. https://2026.connect.ieeebangalore.org/?p=37

[36] RV College of Engineering. (2024). *CSITSS-2024* [Conference flyer]. https://rvce.edu.in/sites/default/files/CSITSS-2024-n.pdf

[37] BINUS University, Department of Industrial Engineering. (2026). *IEEE IEEM 2026 call for papers* [Repost]. https://mie.binus.ac.id/?p=73667

[38] IEEE India Council. (2026). *IEEE India Council International Conference (INDICON 2026)*. https://ieeeindiacouncil.org/ieee-india-council-international-conference-indicon-2026/

[39] Motilal Nehru National Institute of Technology Allahabad. (2026). *SCES-2027 brochure*. https://www.mnnit.ac.in/sces2027/assets/files/broucher.pdf

[40] Institute of Industrial and Systems Engineers. (n.d.). *Lean Systems Track best student paper competition*. https://www.iise.org/Details.aspx?id=4042

[41] IEOM Society International. (n.d.). *Undergraduate paper competition, Kuala Lumpur 2027*. https://ieomsociety.org/malaysia2027/undergraduate-paper-competition/

[42] IEEE. (n.d.). *Find an IEEE conference*. IEEE Author Center. https://conferences.ieeeauthorcenter.ieee.org/become-an-ieee-conference-author/find-an-ieee-conference/

[43] California State University, Northridge, University Library. (n.d.). *Predatory publishing: Conferences*. https://libguides.csun.edu/predatory_publishing/conferences

[44] Ryan, S. M., & Vorasayan, J. (2005). Allocating work in process in a multiple-product CONWIP system with lost sales. *International Journal of Production Research, 43*(2), 223–246. (title unverified, check before citing)

[45] Wein, L. M. (1992). On the relationship between yield and cycle time in semiconductor wafer fabrication. *IEEE Transactions on Semiconductor Manufacturing, 5*(2), 156–158. (unverified, check before citing)
