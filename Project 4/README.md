# Project 4: Is 2008's liquidity / credit-spread link a one-off?

**Research question:** "Is 2008's near perfect link between liquidity and credit spreads a one-off, or does it repeat in March 2020 COVID and the 2022–23 rate shock?" The notebook reproduces slide 59 of Ch. 9 (Baa–Treasury spread vs. Treasury liquidity, Corr = 0.96), extends it to the longest sample the data allow (Jan 1986 – Sep 2026), and tests whether the link recurs. Audience: central-bank / Treasury-market staff and corporate-bond fund managers.

**Everything needed is in this folder.** `neha/` only holds process artifacts (see `neha/README.md`); `MERGE.md` explains how the notebook was built from two independent versions, what each contributed, and what matched and differed.

## Run it
```bash
python3.13 -m venv .venv && source .venv/bin/activate      # Python 3.13 was used; the original notebook was written with 3.14.6
pip install -r requirements.txt                              # exact pins: pandas 3.0.5, numpy 2.5.1, matplotlib 3.11.1, statsmodels 0.14.6, scipy 1.18.0, xlrd 2.0.2, ...
python -m ipykernel install --sys-prefix --name python3      # makes this environment the "Python 3" kernel
python -m jupyter nbconvert --to notebook --execute --inplace Project4_Merged.ipynb     # about 1 minute
```
Or open `Project4_Merged.ipynb` and **Restart Kernel and Run All**. Run it from this folder (all paths are relative: `data/`, `output/`). No internet, no WRDS, no manual steps. Verified: the notebook plus `data/` copied to an empty folder reproduces every CSV in `output/` byte-for-byte.

## Files
| Path | Purpose |
|---|---|
| `Project4_Merged.ipynb` | **The analysis** (all assignment requirements; one "what this does" explanation per code cell) |
| `data/` | **The only data folder**: the 12 inputs the notebook reads (below) |
| `output/` | Tables (`.csv`) and figures (`.png`) written by the added analyses |
| `requirements.txt` | Pinned package versions |
| `MERGE.md` | What was kept from each version, data and result differences, what matched, verification |
| `00_fetch_fred.py` | Documentation only: how the FRED CSVs were downloaded (needs internet; refreshing would change the vintage) |
| `extract_slide59.py` | One-off helper that created `data/slide59_cached_series.csv` from the lecture pptx |
| `CFM301_Project4_Credit_Spread_Liquidity_v2.pdf`, `Ch 9 Bonds.pptx` | Assignment and lecture slides (reading material) |
| `CLAUDE.md` | Handoff notes for working on the project |
| `neha/` | Artifacts: our independent notebook, the classmate's original, their outputs |

## Data in `data/`
| File | Source | Content |
|---|---|---|
| `BAA.csv`, `DBAA.csv` | FRED (Moody's seasoned Baa yield; maturities of 20+ years) | monthly average / daily, % |
| `GS10.csv`, `DGS10.csv`, `DGS20.csv`, `DGS30.csv` | FRED (Fed H.15 constant-maturity Treasury) | monthly / daily, %; `DGS20` has no data Jan 1987 – Sep 1993 |
| `VIXCLS.csv`, `VXOCLS.csv` | FRED (Cboe VIX; old VIX to Sep 2021) | daily index points |
| `TEDRATE.csv` | FRED (TED spread) | daily, % (to Jan 2022) |
| `tnc_qh_pars_1.xls`, `tnc_qh_otrpars.xls` | US Treasury, TNC fitted par-yield curve (not on FRED; downloaded from the Treasury's yield-curve data page) | monthly average par yields: all issues (2–30y) and on-the-run (2/5/10y) |
| `slide59_cached_series.csv` | the 46 points cached in slide 59's chart of the lecture file | spread in %, liquidity in bp, Jan 2006 – Oct 2009 |

Data vintage: early November 2026 (Treasury workbooks end Sep 2026, which fixes the common end of the sample).

## Key definitions
* **Credit spread** = Baa − 20-year TNC par yield (pp, monthly average). **Liquidity premium** = 100 × (10-year all-issue TNC yield − 10-year on-the-run TNC yield) in bp: a fitted-curve proxy for the on/off-the-run spread (CRSP Treasuries is not available).
* Samples: slide window Jan 2006 – Sep 2009 (N = 45); longest overlap Jan 1986 – Sep 2026 (N = 489); regressions Jan 1990 – Sep 2026 (N = 441). Cleaning: duplicates removed (none found), blanks dropped not filled, outliers flagged at 4 SD but **not winsorized** (crisis spikes are the signal; winsorizing is shown as a sensitivity). Every step is counted in `output/cleaning_log.csv`.

## Headline results
| | 2008–09 | 2020–21 | 2022–23 |
|---|---|---|---|
| 10-year gap vs Baa spread (levels r / monthly-change r) | 0.93 / 0.69 | 0.08 / 0.10 | −0.68 / −0.06 |
| VIX vs spread | 0.91 / 0.71 | 0.88 / 0.87 | 0.67 / 0.65 |
| TED vs spread | 0.53 / 0.51 | 0.75 / 0.75 | not testable |

Slide window correlation 0.967 (slide: 0.96; the slide's own cached data: 0.956); longest sample 0.466; excluding 2007–09 0.11. In levels 2008 is significantly stronger than both later episodes (bootstrap p = 0.002 and < 0.001); in monthly changes the evidence is weak (p = 0.12, 0.10) because N = 23. The 10-year gap does not move in March 2020 (−1 bp) while TED rises about five-fold, so the answer is "a one-off for the 10-year on/off-the-run gap; the credit–stress link itself repeats". Average Baa spread 1.73 pp vs 0.124 pp expected loss (about 14×); liquidity explains roughly 6–12 % of the leftover as an illustrative bound.

## Known limitations
Fitted, rounded, later-negative liquidity proxy; the slide's own spread series is not identified (same shape as ours, 1.5–1.8× the swings); 24-month episodes with low power for change-based tests; the puzzle uses the lecture's loss and recovery numbers, not raw Moody's data. Still to do for the course: 3-page report, slides, presentation roles, and a clean-start run by the group member who did not write the code.
