# MERGE.md: how the final notebook was built from two independent versions

`Project4_Merged.ipynb` (project root) is the submission notebook. It was built from two independently written versions of Project 4:

* **Version A**: the classmate's notebook, `neha/classmate_original/Project4_Credit_Spread_Liquidity.ipynb` (47 cells, 661 lines of code).
* **Version B**: our notebook, `neha/Project4_Neha.ipynb` (56 cells, 496 lines of code), written from scratch without copying A's code.
* **Merged**: `Project4_Merged.ipynb` (70 cells, 898 lines of code). 20 of A's 47 cells are kept verbatim; the rest of A and the useful parts of B were integrated into **one pipeline** (not two notebooks stacked).

Both versions answer the same question: *"Is 2008's near perfect link between liquidity and credit spreads a one-off, or does it repeat in March 2020 COVID and the 2022–23 rate shock?"* and both reproduce slide 59 of Ch. 9 (Corr = 0.96). Contents: 1 data, 2 definitions, 3 what matched, 4 what differed, 5 what was kept from A, 6 what was kept from B, 7 duplicates removed, 8 verification, 9 repository changes, 10 caveats.

---

## 1. Data

### 1.1 What each version used
| File | Source | A | B | Merged | Notes |
|---|---|:-:|:-:|:-:|---|
| `BAA.csv` | FRED (Moody's seasoned Baa yield, monthly average) | ✔ | ✔ | ✔ | byte-identical in A and B |
| `GS10.csv` | FRED (H.15 10-year CMT, monthly average) | ✔ | ✔ | ✔ | byte-identical in A and B |
| `VIXCLS.csv` | FRED (Cboe VIX, daily) | ✔ | ✔ | ✔ | **differs by one row**: A's file ends 2026-11-05 (9,613 rows), B's pull ended 2026-11-04 (9,612 rows). Merged uses A's. |
| `tnc_qh_pars_1.xls` | US Treasury TNC curve, fitted par yields, all issues, 2–30y, monthly average | ✔ | ✔ (copied from A) | ✔ | not on FRED; B had no independent copy |
| `tnc_qh_otrpars.xls` | US Treasury TNC curve, on-the-run par yields, 2/5/10y | ✔ | ✔ (copied from A) | ✔ | as above |
| `DBAA.csv`, `DGS10.csv`, `DGS20.csv`, `DGS30.csv` | FRED, daily | – | ✔ | ✔ | daily-vs-monthly checks; daily event study; `DGS20` has a genuine gap |
| `VXOCLS.csv` | FRED (old VIX), daily, to 2021-09 | – | ✔ | ✔ | slide 51 starts in 1986, before VIX |
| `TEDRATE.csv` | FRED (TED spread), daily, to 2022-01 | – | ✔ | ✔ | funding-liquidity indicator |
| `slide59_cached_series.csv` | extracted from the lecture pptx by `extract_slide59.py` | – | ✔ | ✔ | the 46 points slide 59 actually plots |

* **A used 5 files; B used 11 plus the slide file; the merged project uses all 12** in a single `data/` folder.
* B downloaded 13 FRED series; 4 were never used (`AAA`, `DAAA`, `DTB3`, `GS20`) and were deleted, together with the duplicate data folders.
* **Vintages:** all data are the early-November-2026 vintage. FRED monthly series run to Oct 2026; daily series to 4–5 Nov 2026; the Treasury workbooks to Sep 2026, which fixes the common end of the sample (Sep 2026).
* **Effect of the one-row VIX difference:** the extra day is in November 2026, an unfinished month that A's notebook excludes (fixed `AS_OF = 2026-11-06`). It changes only the logged row counts (9,613 vs 9,612) and the "daily rows in the excluded month" note (4 vs 3), not any estimate.

### 1.2 Cleaning: what differed and what the merged notebook does
| | A | B | Merged |
|---|---|---|---|
| Loader | `clean_frame`: exact-duplicate removal, **stops** on conflicting duplicate dates, asserts numeric cells, logs each step | `load_fred`: duplicate removal, drops blanks | A's `clean_frame` for **all 9 CSVs and both workbooks**, one pass, one log |
| Series cleaned | 3 CSVs + 2 workbooks | 9 CSVs + 2 workbooks | 9 CSVs + 2 workbooks |
| Daily → monthly | VIX only (mean of observed days, valid-day counts, unfinished-month exclusion) | all daily series, mean and month-end | A's VIX logic generalised to 7 daily series (+ month-end kept for the frequency check) |
| Log display | three partial log displays | one log CSV | one log (`output/cleaning_log.csv`, 105 checks, 32 of which touched observations) |
| Outliers | 4-SD flag, nothing removed, justified in text | same | A's audit extended to VXO, TED and the extra spreads |
| Winsorizing | none, justified (crisis months are the signal) | none, plus a sensitivity (1/99 and 5/95) | none, plus B's sensitivity (Section 9.2) |

Observation counts (merged cleaning log): duplicates **0** in every file; blank/"." values: VIX 302, VXO 319, TED 554, DBAA 408, DGS10 721, DGS20 2,410 (includes the genuine **81-month gap Jan 1987 – Sep 1993**), DGS30 546, BAA and GS10 0; one unfinished month (Nov 2026) excluded from each daily series; Treasury workbooks: 6 header rows each, 0 missing yields. Months outside the joint coverage: 805 (two-spread chart sample, N = 489) and 853 (regression sample, N = 441). Daily Baa/10y/VIX panel: 414 days dropped for holiday mismatches (9,174 kept). Months beyond 4 SD (flagged, kept): VIX 4, VXO 5, TED 2, main spread 7, liquidity gap 4.

---

## 2. Definitions

### 2.1 Identical in A and B (chosen independently)
* **Credit spread** = Baa − 20-year TNC par yield, percentage points (Baa is a 20+-year index).
* **Liquidity premium** = 100 × (10-year all-issue TNC par yield − 10-year on-the-run TNC par yield), basis points; positive when the on-the-run bond is more valuable.
* **VIX** = monthly mean of observed daily closes. **Frequency** = monthly average. **Common sample** = Jan 1986 – Sep 2026 (N = 489); regressions Jan 1990 – Sep 2026 (N = 441). **Slide window** = Jan 2006 – Sep 2009 (N = 45).
* Regressions A (liquidity), B (VIX), C (both) on identical months; Newey-West with 12 lags; expected loss 0.124 pp (slide 55).
* Anchor months: Sep 2008, Mar 2020, Mar 2022.

### 2.2 Where A and B differed
| Topic | A | B | Merged |
|---|---|---|---|
| Episode windows | **calendar** 24 months (2008–09, 2020–21, 2022–23) | **event-centred** 24 months (t0−12 … t0+11) | calendar = main (A's, used by every downstream test); event-centred 12/24/36 months kept as robustness rows |
| Changes convention | difference on the full calendar, both endpoints in the window | difference inside the window | A's (identical when the window is complete) |
| Third episode in long sub-period tables | 2022–23 | 2022 – Sep 2026 | 2022–23 in the episode tables; the full-sample ledger is in non-overlapping two-year windows |
| Label of the all-issue TNC curve | "off-the-run", justified by the Treasury's XRM methodology note (A cites pp. 16, 61–62; not independently verified here) | asserted as "mostly off-the-run" without a source | A's wording and justification |
| Puzzle | fixed 0.124 pp, no liquidity share ("not identified") | default probability derived (0.124 / (1 − 0.41) = 0.21 %), three expected-loss benchmarks, illustrative liquidity bounds | both: A's caveat stays; B's numbers added and labelled as accounting bounds |
| Treasury maturities tested | 10y (GS10), 30y; 2y and 5y liquidity gaps | 2y, 5y, 10y, 30y TNC and GS10; 2y and 5y gaps | one table (6.10) covering all |

---

## 3. What matched

Every quantity computed by both versions with the same definitions agrees. All values from the notebooks' own outputs:

| Quantity | A | B | Merged |
|---|---|---|---|
| Slide-window correlation (Jan 2006–Sep 2009, N = 45) | 0.9670 | 0.966979 | 0.9670 |
| …through Oct 2009 (N = 46) | 0.9661 | 0.9661 | 0.9661 |
| Longest sample (Jan 1986–Sep 2026, N = 489) | 0.4663 | 0.466310 | 0.4663 |
| Baa − GS10, slide window | 0.9761 | 0.976 | 0.9761 |
| Baa − 30y TNC, slide window | 0.9623 | 0.962 | 0.9623 |
| Corr(spread, VIX), 1990–2026 (N = 441) | 0.6489 | 0.648900 | 0.6489 |
| R² liquidity / VIX / both | 0.2249 / 0.4211 / 0.4595 | 0.224943 / 0.421071 / 0.459507 | same |
| Model C coefficients (liquidity, VIX) | 0.0122, 0.0438 | 0.0122, 0.0438 | same |
| Newey-West t, liquidity: model A / model C | 2.10 / 1.80 | 2.1 / 1.8 | same |
| Average spread / leftover after 0.124 pp | 1.7344 / 1.6104 | 1.734444 / 1.610444 | same |
| 2008–09 calendar window: levels r, changes r, credit/VIX r | 0.9331, 0.6916, 0.9070 | 0.933127, 0.691575, 0.907029 | same |
| 2020–21 | 0.0845, 0.0979, 0.8769 | 0.084457, 0.097950, 0.876915 | same |
| 2022–23 | −0.6805, −0.0555, 0.6690 | −0.680471, −0.055529, 0.669035 | same |
| Average spread in the three windows | 3.1008 / 1.8229 / 1.6763 | same | same |
| 2y gap, 5y gap, GS10, 30y spread vs the three episodes (A's tenor table) | e.g. 5y gap −0.0146 / 0.6038 / 0.5065 | computed on event-centred windows (differs, §4.1) | A's numbers reproduced exactly (indicator table 6.10) |

The qualitative conclusion about the 10-year gap agreed from the start: strong in 2008, not repeated in 2020 or 2022–23, and tenor-specific (the 5-year gap is positive in the later episodes).

---

## 4. What differed in the results, and why

### 4.1 Window definition (the one substantive numerical difference)
B's inference tests ran on event-centred windows; the merged notebook runs them on A's calendar windows, so the integrated pipeline uses one set of main windows everywhere. Conclusions are unchanged but some p-values move:

| | B (event-centred) | Merged (calendar) |
|---|---|---|
| Levels r: GFC / COVID / rate shock | 0.946 / −0.441 / −0.631 | 0.933 / 0.084 / −0.680 |
| Changes r | 0.706 / 0.187 / −0.100 | 0.692 / 0.098 / −0.056 |
| Bootstrap 95 % interval, levels (GFC; COVID; rates) | [0.82, 0.98]; [−0.75, 0.14]; [−0.85, −0.20] | [0.71, 0.98]; [−0.71, 0.59]; [−0.83, −0.27] |
| GFC − COVID, levels: difference (p) | 1.39 (< 0.001) | 0.85 (0.002) |
| GFC − rates, levels | 1.58 (< 0.001) | 1.61 (< 0.001) |
| GFC − COVID, changes (p) | 0.52 (0.10) | 0.59 (0.12) |
| GFC − rates, changes (p) | 0.81 (**0.03**) | 0.75 (**0.10**) |
| Pooled liquidity slopes, changes: GFC / COVID / rates; Wald p | 0.034 / −0.033 / −0.007; 0.136 | 0.028 / −0.018 / −0.008; 0.196 |
| Pooled, levels with episode fixed effects; Wald p | 0.050 / −0.041 / −0.009; < 0.001 | 0.049 / 0.001 / −0.017; < 0.001 |
| Rank among all 466 rolling 24-month windows, levels / changes | GFC 96th / 97th; COVID 12th / 74th; rates 2nd / 30th | GFC 93rd / 94th; COVID 54th / 59th; rates 0th / 37th |

Reading: in **levels** the result is robust to the window (2008 significantly stronger than both later episodes). In **monthly changes** the evidence is weak either way (23 observations); B's one borderline-significant result (rate shock, p = 0.03) becomes p = 0.10 on calendar windows, so the merged text says "strong in levels, suggestive in changes". COVID's levels correlation is near zero on the calendar window and negative on the event-centred one; across all five window definitions it ranges from −0.44 to +0.55, never near 0.9.

### 4.2 Other differences
* **Rate-shock window:** A's 2022–23 levels correlation is −0.68; B's long sub-period table used 2022 – Sep 2026 and gave −0.83. Same data, different window; the merged notebook reports 2022–23 in the episode tables.
* **Slide levels:** A observed that the slide's spread peaks near 8 pp while ours peaks at 5.3 pp and that "maturity alone does not establish why". B first suggested that Baa − 2y Treasury reproduces the 8 % peak, which was **wrong**; the slide's own cached chart data (46 points, extracted from the pptx) show the slide's spread has the same shape as ours (corr 0.97–0.99) but swings 1.5–1.8× as much, and Baa − 2y does not reproduce its 2006 level or shape. The merged Section 5.2 contains the corrected, data-based statement. The slide's own data give a correlation of 0.956 (title: 0.96). Our liquidity proxy tracks the slide's liquidity line at 0.956 (peaks 58 bp vs 65 bp). Our Baa − 10y TNC averages 2.12 % over 1987–2011 (lecture: 2.09 %), whereas Baa − 20y averages 1.71 %; these two clues conflict, so the slide's series is reported as unidentified.
* **March 2020:** A could only say the monthly proxy may miss it ("cannot recover a daily event study"). B tested it with daily data: the 10-year gap moves ~1 bp, TED rises about five-fold and its daily correlation with the credit spread is 0.81 (levels) / 0.43 (changes), higher than in 2008 (0.31 / 0.14). The merged answer says part of the "no repeat" is the proxy failing to see 2020.
* **Which indicators repeat:** B added VIX and TED. Credit–VIX levels r is 0.91 / 0.88 / 0.67 in the three episodes, TED 0.53 / 0.75 / not testable, 5-year gap −0.02 / 0.60 / 0.51: no single liquidity gauge works in all three. A's own tables contained the VIX and 5-year numbers but did not draw this conclusion.
* **Puzzle:** A: 1.73 pp is 14× the 0.124 pp loss, leftover 1.61 pp, liquidity share "not identifiable". B: implied default probability 0.21 %, benchmarks 0.124 / 0.163 / 0.75 pp, liquidity bound 5.8–12.4 % of the leftover (13–28 % in 2008–09, negative later). The merged notebook keeps A's caveat and presents B's numbers as accounting bounds.

---

## 5. Kept from A (the classmate's notebook)

**Kept verbatim (20 cells; 7 code, 13 markdown; their outputs reproduce A's saved outputs exactly):** the coverage text (A cell 10), the lecture-comparison text (17), the extended-sample plot and table (19), the three-panel episode figure on common axes (23), the A–C regressions with HAC (28), the episode regressions (31–32), and markdown cells 4, 8, 13, 18, 20, 22, 24, 26, 27, 30, 35, 42, 44.

**Kept with changes (16 code and 11 markdown cells changed; the logic is A's):**
| A cell | Change in the merged notebook |
|---|---|
| 1 (motivation) | kept; test design and decision rule appended |
| 3 (setup, load) | file list extended to 9 CSVs; added `OUT`, event windows, short labels |
| 7 (cleaning) | `clean_frame`/`log_step` unchanged; three partial log displays replaced by one `show_log()` |
| 9 (monthly alignment) | Treasury/monthly part unchanged; VIX logic generalised to 7 daily series |
| 12 (panel) | VXO, TED and other maturities added as columns |
| 14 (outliers) | extended to the new columns |
| 16 (lecture figure/table) | table extended from 3 to 5 spread definitions × 3 liquidity tenors |
| 21, 25 | removed a log display / corrected a section reference |
| 29 (VIX comparison) | VXO rows added for the slide-51 sample |
| 33, 34 (puzzle) | table gains spread/loss multiple and liquidity bounds; B's default-probability paragraph appended to the intro; A's caveats (cell 35) kept verbatim |
| 37 (window sensitivity) | **moved** into Section 6.6; event-centred windows and rank correlation added; entry-boundary and benchmark tables unchanged |
| 39 (tenor/definition table) | the tenor table was merged into the indicator table (6.10); the GS10 regression part moved verbatim to 7.3 |
| 40–41 (HAC lags) | **moved** to 7.3 verbatim; the f-string "what survives" summary dropped (replaced by the findings and answer) |
| 43 (answer) | replaced by the merged answer; its content (March 2020, the 2022–23 yield decomposition, central-bank implications, limitations) is preserved |
| 45 (checks) | kept verbatim; a second checks cell added |
| 46 (sources) | PDF/pptx paths corrected; two items added |

**Contributions only A had, all retained:** per-episode regressions A–C with HAC-lag sensitivity; the anchor-month yield decomposition (Δspread = ΔBaa − ΔTreasury; in 2022–23 Baa +2.34 pp and the 20-year Treasury +2.43 pp, so the spread −0.09 pp); the entry-boundary check for six-month windows; calendar-year windows; liquidity SD/min/max and negative-month counts; the March 2020 / Fed-report discussion; the XRM-methodology justification for the proxy; assertion-based consistency checks; the pinned environment.

## 6. Kept from B (our notebook)

| B component | Where in the merged notebook |
|---|---|
| Daily FRED series (Baa, 10/20/30y, VXO, TED) | cleaned with A's `clean_frame` (Section 3), no separate loader |
| FRED monthly-vs-daily validation, `DGS20` gap accounting | Section 3 |
| Other TNC maturities (2/5/10y), TED, VXO columns | `panel` (Section 4) |
| Slide-59 cached data and level comparison | Section 5.2 |
| Event-centred 12/24/36-month windows, Spearman ranks | the one window table (6.6) |
| Block bootstrap and pooled interaction regression | 6.7 |
| Rolling-window benchmark and two-year ledger (figure) | 6.8 |
| Daily event study (TED, VIX, credit spread) | 6.9 |
| Alternative indicators (5y/2y gaps, TED, VIX) | merged with A's tenor table into the indicator table (6.10) |
| Standardised betas, variance split, regressions in changes, VXO check of slide 51 | 7.1 |
| Default probability, expected-loss benchmarks, liquidity bounds, decomposition by period (figure) | 8 |
| Frequency (daily/monthly/month-end), winsorizing, long sub-periods, summary table | 9 |
| Merged answer written as a live-computed cell | 10 |

**Dropped from B:** its own loader and cleaning log (A's is stricter), the bridge frame `P` (columns now live in `panel`), its separate window grid and alternative-proxy table (merged into 6.6 and 6.10), the slide-window/GFC/COVID/rate rows of its sub-period table (already in the window table), the 36-month rolling-correlation figure, its slide-window and changes-only regression tables (A's episode regressions cover 2008–09), its "Baa − 2y matches the 8 % peak" statement (wrong, §4.2), and its generic title framing (replaced by the group's research question).

## 7. Duplicates removed

| Done twice | Now |
|---|---|
| Cleaning pass and log (A's `clean_frame` and B's `load_fred`) | one pass over all inputs, one log |
| Monthly panel (A's `panel`, B's `P`) | one `panel` |
| Episode/window statistics (A's `window_correlations`, B's `link_stats`) | one function |
| Tenor/definition sensitivity (A's table, B's grid) | one indicator table |
| Puzzle table (A's by sample, B's by period) | one table plus a period figure |
| Bridges, helper functions, repeated plotting code | removed |

Net effect: 898 lines of code against 1,157 for the two notebooks together (and 977 in a first, stacked merge that was discarded).

---

## 8. Verification

| Check | Result |
|---|---|
| A's notebook re-run from a clean folder (5 data files) under the pinned environment | no errors; every saved output reproduced; only the printed Python version differs (3.13.0 here vs 3.14.6) |
| A's 20 verbatim cells in the merged notebook | identical outputs |
| A's 10 window-correlation rows (3 calendar windows, 4 calendar years, 3 acute windows) vs merged window table | match to 4 decimals |
| A's tenor/definition numbers vs merged indicator table | match (GS10, 30y, 2y and 5y rows) |
| B's added analyses vs B's own notebook, before the window change | shared tables agree to < 2e-15 (floating point) |
| B's notebook re-run against the single `data/` folder after the clean-up | no errors; tables agree to < 2e-15; the only substantive change is the VIX row count (A's extra day) |
| Merged notebook run from a fresh folder containing only the notebook and `data/` | all 20 CSV outputs identical to the main run |
| Merged notebook, consistency assertions (A's plus new) | pass: bridge identities, event windows equal the original anchors, calendar windows equal A's episode correlations, bootstrap size, slide data, puzzle identity, FRED monthly = mean of daily |
| Environment | `requirements.txt` (A's pins, unchanged): pandas 3.0.5, numpy 2.5.1, matplotlib 3.11.1, statsmodels 0.14.6, scipy 1.18.0, xlrd 2.0.2 |

## 9. Repository changes

| Before | After |
|---|---|
| A's data folder (5 files) and B's data folder (12 files) and B's `raw/` (13 files) | **one** `data/` (12 files) |
| `neha/Project4_Merged.ipynb`, `neha/output_merged/` | `Project4_Merged.ipynb`, `output/` at the project root |
| Assignment PDF and lecture pptx inside `neha/` (earlier in A's `data/`) | project root |
| `00_fetch_fred.py` (wrote to `../data/raw`), `extract_slide59.py` (relative to the working directory) | project root, paths resolved from the script's own location, only the 9 FRED series actually used |
| A's notebook and README at the root | `neha/classmate_original/` (byte-identical; it expects a `data/` folder next to it, so copy it to the project root to run it) |
| B's notebook | `neha/Project4_Neha.ipynb`, pointed at `../data` (one path edit) |
| Two READMEs, two requirements files, two virtual environments, `neha/data`, `neha/raw`, `neha/output_merged` | one `README.md`, A's `requirements.txt` (unchanged), `.gitignore` for `.venv`; the rest deleted |

## 10. Caveats and open items
* Text in Sections 6.11, 7.1, 8 and 9.3 (findings) is typed from verified outputs; only the Section 10 answer is computed live. Re-running with different data would require re-reading those findings.
* The slide's own spread series is not identified; the liquidity proxy is a fitted-curve measure (1 bp rounding, negative from 2019, about −1 bp in March 2020).
* Change-based tests have low power (23 observations per episode); the credible claim is "strong in levels, suggestive in changes".
* The puzzle's loss and recovery inputs come from the lecture slides, not raw Moody's data; the liquidity-share numbers are accounting bounds, not causal estimates.
* Nothing has been committed to git.
* Still to do for the course: the 3-page report, slides, and a clean-start run by the group member who did not write the code.
