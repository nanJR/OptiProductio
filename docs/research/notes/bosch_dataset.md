# Bosch Production Line Performance dataset (Kaggle 2016) as a basis for flow/WIP analysis

Scope note: Kaggle pages (data, rules, discussions, kernels) render with JavaScript and returned only metadata to the fetch tool, and the Kaggle API was blocked by the sandbox proxy (HTTP 403). Kaggle-internal facts below therefore come from secondary sources (papers, the Kaggle blog, GitHub READMEs, student write-ups) unless noted. Everything that could not be checked on a primary Kaggle page is marked UNVERIFIED.

## 1. Exact structure: files, counts, naming, failure rate, sizes, time unit, missingness

### Takeaway
There are about 1.18M training parts (6,879 failures, ≈0.58%) and a test set of the same size. Each set comes as three row-aligned CSV tables: numeric (968 columns), categorical (2,140) and date (1,156), all keyed by `Id`. Columns are named L{line}_S{station}_F{feature} (numeric/categorical) or _D{n} (date), across 4 lines and 51–52 stations. Dates are anonymised floats spanning about 0–1718 units at 0.01 resolution. Autocorrelation suggests 1 unit ≈ 0.1 hours, so 0.01 ≈ 6 min and the span is ≈102.5 weeks. Only about 7% of date cells are filled.

### Cited Findings
- **Rows.** Train has 1,184,687 samples and test has 1,183,748 — [Mangal & Kumar, arXiv 1701.00705](https://arxiv.org/pdf/1701.00705); same figures in [Federated learning paper, arXiv 2101.11715](https://arxiv.org/pdf/2101.11715). Other sources give 1,183,747 parts — [NYC Data Science Academy blog](https://nycdatascience.com/blog/student-works/15212/); [arXiv 2407.01644](https://arxiv.org/pdf/2407.01644); [FedCSIS 2023, Nikolova et al.](https://annals-csis.org/Volume_35/drp/pdf/677.pdf). The likely cause is 1,183,747 = number of data rows and 1,184,687 = a miscount, or that 1,183,747 is the test size minus one. UNCERTAIN: check with `wc -l` on download.
- **Failures.** 1,177,808 negatives vs 6,879 positives in train — [arXiv 2101.11715](https://arxiv.org/pdf/2101.11715). The figure of 6,879 failed parts is also given by [FedCSIS 2023](https://annals-csis.org/Volume_35/drp/pdf/677.pdf). The rarity is 0.58% — [arXiv 2407.01644](https://arxiv.org/pdf/2407.01644). 6,879 / 1,183,747 ≈ 0.581%.
- **Columns.** There are 968 numerical, 2,140 categorical and 1,156 date features — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705). That paper gives 1,157 date features in another section, which is internally inconsistent. The Kaggle blog says 4,265 features in total (2,140 cat + 968 num + 1,157 date) — [Kaggle blog (Medium)](https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe). The NYC DSA blog says 4,264 features — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/). The difference of one is probably whether `Id`/`Response` is counted. UNCERTAIN.
- **Numeric features by line.** The 968 numeric features split by line L0–L3 as 168 / 513 / 42 / 245 — [arXiv 2101.11715](https://arxiv.org/pdf/2101.11715).
- **Lines and stations.** There are 4 lines (L0–L3) and 51 stations — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705) and [Kaggle blog](https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe). Other sources say "4 segments and 52 workstations" — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/), [arXiv 2407.01644](https://arxiv.org/pdf/2407.01644), [FedCSIS 2023](https://annals-csis.org/Volume_35/drp/pdf/677.pdf). Stations are numbered S0–S51 (52 IDs). UNCERTAIN whether one ID has no date column; count the distinct `S` tokens yourself.
- **Naming.** Columns follow L{line}_S{station}_F{n} for measurements and L{line}_S{station}_D{n} for timestamps, e.g. "L3 S50 D4242" — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705). "D(n) records when F(n−1) was measured" — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/); [arXiv 2407.01644](https://arxiv.org/pdf/2407.01644). "Same stations often have same date values" — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705). Most non-null timestamps in a row take only about 3 unique values — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/).
- **Files.** The three tables (numeric, categorical, date) have identical row counts and row order, so they can be joined column-wise on `Id` — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/). The file names `train_numeric.csv` / `train_date.csv` / `train_categorical.csv`, plus `test_*` equivalents, are confirmed indirectly. For example, the IJAMT paper uses "train_numeric.csv" — [Aslan et al. 2023, IJAMT](https://link.springer.com/10.1007/s00170-023-12123-4). `Response` is only in train_numeric (UNVERIFIED on the Kaggle page, but widely assumed in repos).
- **Sizes.** The full dataset is about 14.3 GB — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705); [Kaggle blog](https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe). The NYC DSA blog says the training tables are "each about 2.8 GB, for 7.7 GB total", with test the same size — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/). The arithmetic is inconsistent (3 × 2.8 ≠ 7.7), so treat 14–15 GB uncompressed for train+test as the safe figure. Per-file zip sizes could not be retrieved from Kaggle. UNVERIFIED.
- **Paths.** The number of unique station paths is reported as 7,148 (section 2.2) or 7,158 (conclusion) — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705). Other figures are 4,700 unique station combinations — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/), [arXiv 2407.01644](https://arxiv.org/pdf/2407.01644) — and 7,928 product types (unique paths) — [Aslan et al. 2023](https://link.springer.com/10.1007/s00170-023-12123-4). These differ depending on which table, train/test, and numeric vs date presence were used.
- **Time unit.** Date values range from 0 to 1718 at a granularity of 0.01. The granularity "corresponds to ∼6 minutes in real time". Autocorrelation peaks every 16.75 units (interpreted as 1 week), and smaller peaks every 2.39 units correspond to 1 day. The span is "1718.48 time units i.e. 102.6 weeks" — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705). The Kaggle blog gives "102.5 weeks" and "granularity of 6 minutes" — [Kaggle blog](https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe). Aslan et al. reuse 16.75 units = 1 week — [IJAMT 2023](https://link.springer.com/10.1007/s00170-023-12123-4). FedCSIS 2023 normalised dates to a "takt" with 6-minute granularity — [FedCSIS 2023](https://annals-csis.org/Volume_35/drp/pdf/677.pdf).
- **Missingness.** Only about 5% of numeric, 1% of categorical and 7% of date cells are populated, because each part visits only some stations. The missingness is not random — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/); about 7% non-null timestamps — [arXiv 2407.01644](https://arxiv.org/pdf/2407.01644). About 150 categorical columns are completely empty, and about 1,490 categorical columns are single-valued — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705). Average sparsity is about 80% — [joostgp/kaggle_bosch](https://github.com/joostgp/kaggle_bosch).
- **Station heterogeneity.** S32 has a 4.7% failure rate across 24,543 parts and only one measurement, which suggests a rework or post-processing station. S31 has the lowest rate at 0.27%. Typical stations sit around 0.6% — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705); [Kaggle blog](https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe). Features with defect rates above 0.6% cluster in lines 0 and 1 — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/).
- **Mean lead time.** The first-to-last date difference across all products averages 10.71 units (SD 17.01) — [Aslan et al. 2023](https://link.springer.com/10.1007/s00170-023-12123-4). At 16.75 units per week, that is a mean of about 4.5 days with a heavy tail.

### Inferences
- **Units.** The figure of 16.75 units per week gives 1 unit ≈ 10.03 h, and 0.01 units ≈ 6.0 min. The daily peak of 2.39 units fits this (16.75 / 7 ≈ 2.393). The common wording "0.01 ≈ 6 min" is therefore internally consistent. It is still a community inference from periodicity, not a Bosch-disclosed unit, and the paper must say so.
- **Rounding of time stamps.** Because many columns within a station share one value and rows have about 3 unique timestamps, the date table behaves like coarse station-entry events rather than per-test timestamps. The 0.01 (6-minute) rounding means many parts tie at the same timestamp. Little's-law calculations should use bins of at least one tick, and ties must be handled explicitly.
- **Train/test split.** Train and test interleave in time; Ids are shared across them. The test set has no labels, but its parts occupy the same line. A WIP reconstruction should therefore use train **and** test date rows, because test parts are physically on the line. Failure-rate analysis can only use train rows. This is a key methodological point for the project.

### Gaps
- No primary Kaggle data-page text could be retrieved. Exact zip and CSV sizes per file, and the official data description wording, are UNVERIFIED.
- The exact train row count conflict (1,184,687 vs 1,183,747) and the 51 vs 52 station count are unresolved. The project should compute them directly.
- The 1,156 vs 1,157 date-column count is unresolved.

## 2. How competitors and papers used the date features; any WIP/queue/flow/process-mining or congestion work

### Takeaway
Date features drove most of the competition's signal through two families of features:
- **Per-part features:** start/end time, duration, and the stations at entry and exit.
- **Leaky "magic" ordering features:** sort parts by Id and by start time, then compute differences to the previous and next Id and whether neighbours share a timestamp.

Neighbouring-part label features (failures among nearby parts in time) and parts-per-takt counts have been used, which are the closest existing analogue to WIP/congestion. One peer-reviewed paper (Aslan et al., IJAMT 2023) derives lead time from the dates. No published work found reconstructs WIP, queue length or throughput, treats the data as a process-mining event log, or tests a congestion → failure hypothesis. This looks like a genuine gap.

### Cited Findings
- **8th place (MCC 0.50888, of 1,373 teams)**, [joostgp/kaggle_bosch](https://github.com/joostgp/kaggle_bosch):
  - Timestamp features: per-station, per-line and per-path timestamps, plus max−min durations per station, line and path.
  - Kurtosis of timestamps, which the author called "very strong, surprisingly".
  - Lead/lag response-rate features sorted by tmax and Id.
  - Correlation with the next and previous samples after sorting by tmax/tmin.
  - Same-timestamp previous/next samples, and previous/next response for duplicate records.
  - Path features: entry and exit stations, previous/next station one-hot for S29–S37, and path clusters.
  - What did not help: a timestamp-based leave-one-out error rate, and label-based timestamp density, which overfit.
- **Mangal & Kumar ("magic" features excluded):**
  - They inferred time units by autocorrelation of product counts per time unit.
  - "Time spent by a product on the line" was among the most important predictors.
  - The top-10% models used "magic" leakage features "which exploit identical sequential readings marking batches". These were excluded as not available in real time.
  - Pavlyshenko's team said sample-Id-based magic features "improved scores substantially".
  - Sources: [Kaggle blog](https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe); the engineered "time diff" (total time in line) is in [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705).
- **NYC DSA:** collapsed 1,156 date columns into a single time-lapse (max−min) feature — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/).
- **FedCSIS 2023 (Nikolova et al.)** used 19 date features ([FedCSIS 2023, pp. 291–296](https://annals-csis.org/Volume_35/drp/pdf/677.pdf)):
  - Max and min date and their difference, the stations with the max and min times, path size, week and day of week.
  - "Time-dependence" features: **number of parts in one takt** (6-minute bin), and failure counts in the next and previous 1, 10 and 24 hours.
  - This is the closest published feature to a throughput/WIP-in-window measure and to temporal failure clustering, but it is used only as a classifier input. There is no causal or congestion analysis.
- **Lead time (Aslan et al. 2023):** "Hierarchical ensemble deep learning for data-driven lead time prediction" — *Int. J. Adv. Manuf. Technol.* 128(9):4169–4188, open access ([Springer](https://link.springer.com/10.1007/s00170-023-12123-4); repository copies at [Strathprints](https://strathprints.strath.ac.uk/86600) and [Edinburgh Napier](https://napier-repository.worktribe.com/output/3169035/hierarchical-ensemble-deep-learning-for-data-driven-lead-time-prediction)).
  - Lead time = difference between the date at the first and last stations.
  - Products were grouped by station path into 7,928 types, and the six most frequent were modelled.
  - The authors also deposited a derived dataset record, "Lead time prediction with the Bosch production line dataset" (Napier, 2022) — [worktribe](https://napier-repository.worktribe.com/output/2912661/lead-time-prediction-with-the-bosch-production-line-dataset).
- **Federated-learning study:** used timing to order data for a stability analysis and to build "time-continuous samples" — [arXiv 2101.11715](https://arxiv.org/pdf/2101.11715).
- **Exploration code:** a Zenodo software record, "Bosch-Production-Line", gives exploration and visualisation code (Braverman, Ziche, Thim, Grum; University of Potsdam group, 2022, DOI 10.5281/zenodo.6384769) — [Zenodo](https://zenodo.org/records/6384769). Whether this group did process-flow modelling is not stated. UNVERIFIED.
- **Process mining:** searches for "process mining", "throughput", "work in progress" and "queue" with "Bosch production line" found no paper treating the dataset as an event log. The closest process-mining manufacturing dataset is TV-ALP (a television assembly log, *Applied Intelligence* 2024), which is unrelated — [Springer](https://link.springer.com/article/10.1007/s10489-024-05347-8).

### Inferences
- **Event log.** The date table converts naturally to an event log of (case = Id, activity = station, timestamp = min/max of that station's D columns). It is then usable with pm4py for process maps, and with Little's law, L = λW. WIP(t) = the number of parts with start ≤ t < end. Throughput = exits per bin. Flow time = end − start. This is a direct extension of Aslan et al.'s lead time and FedCSIS's parts-per-takt.
- **Leakage.** The "magic" Id features mean consecutive Ids are related, probably batches or sequence on the line. In a WIP-vs-failure regression, batch effects and Id adjacency are confounders: failures cluster in time and batches. Sliding-window failure counts are known to be predictive (FedCSIS), so the project should control for temporal autocorrelation, e.g. block bootstrap or time fixed effects.
- **Station timestamp vs. queue time.** One date per station only gives time between stations, which mixes processing and waiting. Queue time cannot be separated without assumptions. Present flow time as station-to-station sojourn, not as pure queue time.
- **CONWIP backtest.** A CONWIP WIP-cap alert has not been tested on this data per the search, so it would be novel. The dataset is observational, though: a backtest can only show whether high-WIP periods have more failures (an association), not what capping WIP would do.

### Gaps
- Kaggle discussion threads (e.g. "magic features", "time unit") and top kernels could not be read directly; the JS-rendered pages were not accessible. The specific "0.01 = 6 min" discussion thread and the 1st-place write-up are not cited directly.
- No paper relating congestion or WIP to failure rate in this dataset was found. That is absence of evidence from a limited search (roughly 6 queries), not proof. A Google Scholar "cited by" sweep of 1701.00705 is recommended.
- Whether the full-text Aslan et al. paper reports WIP or throughput statistics was not checked beyond the first 100k characters.

## 3. Data licence / competition rules / peer-reviewed use

### Takeaway
The Kaggle rules page could not be retrieved, so the exact Bosch rule wording is UNVERIFIED. One quoted Kaggle rule clause ("Participants must use the Data solely for the purpose and duration of the Competition") shows that some Kaggle competitions restrict data use. In practice, the dataset has been used in many peer-reviewed publications (IEEE, Springer, MDPI, FedCSIS) without visible licence problems. Bosch itself sponsored an academic-paper prize track, the Symposium for Advanced Manufacturing grant. The project should read the rules tab while logged in, quote it, and cite Kaggle plus Bosch as data source. Bosch's rules were never verified to grant an academic-use permission, so don't assume one.

### Cited Findings
- **Rules wording.** A fast.ai forum post quotes Kaggle competition rules (not specifically Bosch) as: "Participants must use the Data solely for the purpose and duration of the Competition" — [fast.ai forums](https://forums.fast.ai/t/kaggle-datasets-licensing-question/9191). The forum gives no authoritative interpretation.
- **Unretrievable pages.** Kaggle rules for 2016-era competitions (e.g. Grupo Bimbo, Santander) exist at /rules pages but were not retrievable as text — [Grupo Bimbo rules](https://www.kaggle.com/competitions/grupo-bimbo-inventory-demand/rules), [Santander rules](https://www.kaggle.com/c/santander-customer-satisfaction/rules). The Bosch rules page (https://www.kaggle.com/c/bosch-production-line-performance/rules) returned only metadata. UNVERIFIED: many Kaggle competitions of this era included a clause permitting use "for the purposes of the Competition, participation on Kaggle Website forums, academic research and education, and other non-commercial purposes". This could not be confirmed for Bosch and must not be quoted until checked.
- **Bosch's academic track.** Bosch and Kaggle ran a "Symposium for Advanced Manufacturing" grant for papers based on the competition. Mangal & Kumar were grant winners — [Kaggle blog](https://medium.com/kaggle-blog/bosch-production-line-performance-competition-symposium-for-advanced-manufacturing-grant-winners-6aa9dfd6d2fe); [CMU news](https://www.cmu.edu/engineering/materials/news_and_events/news/archive/2016/november/mangal-wins-prize-in-data-science-challenge.html). The symposium is generally reported as held at IEEE BigData 2016. An IEEE BigData 2016 proceedings entry exists at [computer.org CSDL 07840832](https://computer.org/csdl/proceedings-article/big-data/2016/07840832/12OmNzWOB9m), but its content could not be read. UNVERIFIED that this is the Mangal & Kumar paper.
- **Peer-reviewed and other uses found:**
  1. Aslan, Vasantha, El-Raoui, Quigley, Hanson, Corney, …, Sherlock. "Hierarchical ensemble deep learning for data-driven lead time prediction." *Int. J. Advanced Manufacturing Technology* 128(9):4169–4188, 2023. Open access. — [Springer](https://link.springer.com/10.1007/s00170-023-12123-4)
  2. Nikolova, Lameski, Pires, Zdravevski. "Towards Industry 4.0: Machine malfunction prediction based on IIoT streaming data." *FedCSIS 2023*, ACSIS Vol. 35, pp. 291–296. — [annals-csis.org](https://annals-csis.org/Volume_35/drp/pdf/677.pdf). The paper states no dataset licence, only "©2023, PTI".
  3. Carbery, Woods, Marshall. "A Bayesian network based learning system for modelling faults in large-scale manufacturing." *IEEE ICIT 2018*, DOI 10.1109/ICIT.2018.8352377 — [QUB Pure](https://pure.qub.ac.uk/en/publications/a-bayesian-network-based-learning-system-for-modelling-faults-in-/). It uses "a large manufacturing dataset from Bosch"; that this is the Kaggle set is likely but not stated on the abstract page.
  4. Park & Baek. "Data-Driven Defect Prediction for Manufacturing Quality Monitoring Under Class Imbalance and Missing Data: A Performance–Efficiency Trade-Off Analysis." MDPI *Machines* 14(7):716, 2026, DOI 10.3390/machines14070716 — [CiteDrive](https://www.citedrive.com/en/discovery/data-driven-defect-prediction-for-manufacturing-quality-monitoring-under-class-imbalance-and-missing-data-a-performanceefficiency-trade-off-analysis/)
  5. Mangal & Kumar. arXiv 1701.00705 (2016), Symposium grant paper — [arXiv](https://arxiv.org/pdf/1701.00705)
  6. Preprints: federated learning failure prediction, arXiv 2101.11715 — [arXiv](https://arxiv.org/pdf/2101.11715); rare-event data enrichment, arXiv 2407.01644 — [arXiv](https://arxiv.org/pdf/2407.01644)
  7. Further hits not opened: a University of Porto thesis — [repositorio-aberto.up.pt](https://repositorio-aberto.up.pt/handle/10216/121189); a UPC thesis — [upcommons](https://upcommons.upc.edu/bitstreams/ce2e3583-6eb7-4ae7-83c6-c0b2c02b0df8/download); a UKIM repository item — [repository.ukim.mk](https://repository.ukim.mk/handle/20.500.12188/30413); an IPP item — [recipp.ipp.pt](https://recipp.ipp.pt/handle/10400.22/18266); a Fraunhofer IPT dataset overview — [Fraunhofer IPT PDF](https://www.ipt.fraunhofer.de/content/dam/ipt/en/documents/projects/20190708_DataSet_ML_v23.pdf).

### Inferences
- **Publication norm.** Multiple peer-reviewed journals (IJAMT/Springer, MDPI, IEEE ICIT, FedCSIS) have published papers using this dataset. Its use in academic publications is an established norm. The safe practice is to:
  - not redistribute the raw CSVs;
  - point readers to the Kaggle download;
  - cite the competition, e.g. "Bosch Production Line Performance, Kaggle, 2016";
  - quote the rules clause after reading it while logged in.
- **Redistribution.** Publishing derived aggregates (WIP time series, flow-time distributions) is less risky than republishing rows. Still, check the rules for any redistribution restriction.

### Gaps
- The verbatim Bosch competition rules (data access and use section) are not retrieved. This is the single most important item to verify by hand: open https://www.kaggle.com/c/bosch-production-line-performance/rules while signed in and copy the "Data Access and Use" section.
- Whether the data download is still allowed post-competition without accepting rules is UNVERIFIED. Kaggle normally requires rules acceptance for "late submission" or download.

## 4. Practical handling: memory, chunked loading, Kaggle API

### Takeaway
Plan for about 14–15 GB uncompressed (train+test, all three tables), and at least 16 GB RAM if loading naively. For a flow/WIP study, only `train_date` and `test_date` (plus `Id`/`Response` from `train_numeric`) are needed. Read them in chunks with float32 dtypes, collapse each row to per-station min times plus overall start/end, and keep only that compact event table (a few hundred MB at most).

### Cited Findings
- **RAM.** The 8th-place solution states a memory requirement of at least 16 GB — [joostgp/kaggle_bosch](https://github.com/joostgp/kaggle_bosch). It converted dense to sparse matrices (about 80% sparsity) to speed up feature generation and reduce the memory footprint — same source.
- **Sparse formats.** Converting sparse numeric and categorical data to libSVM format, together with feature reduction, cut the data from 7.7 GB to 1.7 GB — [NYC DSA](https://nycdatascience.com/blog/student-works/15212/).
- **Size.** The total size is 14.3 GB — [arXiv 1701.00705](https://arxiv.org/pdf/1701.00705).
- **Download.** The Kaggle API could not be tested here (proxy 403). The standard command is `kaggle competitions download -c bosch-production-line-performance`. It requires `~/.kaggle/kaggle.json` and accepting the competition rules on the website first. This is standard Kaggle CLI behaviour, not verified against this competition in this session. UNVERIFIED.

### Inferences
- **Practical recipe** (my synthesis, not from a source):
  - Use `pd.read_csv('train_date.csv.zip', chunksize=100_000, dtype=np.float32)`, or polars/pyarrow `scan_csv`.
  - For each chunk, group the date columns by station prefix (`L\d_S\d+`) and take the row-wise min (or max), giving about 52 station-time columns.
  - Compute `start = min`, `end = max`, `path = set of stations with non-null`.
  - Melt to a long table (Id, station, t) and write to Parquet.
  - Repeat for test_date, so WIP counts the test parts that are also on the line.
  - Join `Response` from train_numeric, reading only `usecols=['Id','Response']`.
  - With about 2.37M parts and about 3 distinct station times each, the long table is about 7–10M rows. That fits easily in memory.
- **Time conversion.** Convert units at 1 unit = 1/16.75 week ≈ 10.03 h. Report results in both "units" and "≈hours", with the caveat that this conversion is inferred.

### Gaps
- Exact per-file compressed and uncompressed sizes were not obtained.
- Kaggle CLI behaviour for this specific (closed, 2016) competition was not tested.
