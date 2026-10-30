# Project 3: Equity Return Predictability

Question: are post-2011 equity returns more predictable during economic downturns than during normal market conditions? Audience: pension fund managers and long-term institutional investors.

## Notebooks
| Notebook | What it is |
|---|---|
| **`Project3_Merged.ipynb`** | **The group's submission.** Merges both versions below: data and cleaning, the predictability table, comparison with the slides, dividend discount model and buckets, GARCH (in-sample and out-of-sample), sensitivity, downturn tests, summary, requirements checklist |
| `Equity Predictability Submission.ipynb` | Bodhana's version |
| `Project3_Predictability.ipynb` | Kamakshi's version |

## How to run
1. Python 3.13 with: pandas 2.3, numpy 2.3, statsmodels 0.14, scipy 1.16, matplotlib 3.10, jinja2 3.1 (for the styled tables), jupyter.
   `pip install pandas numpy statsmodels scipy matplotlib jinja2 jupyter`
2. Open **`Project3_Merged.ipynb`** and choose **Restart & Run All** (about 30 seconds, roughly 1.5 GB of RAM). No internet access or WRDS login is needed; nothing is downloaded or written.

The notebooks read only the files in `data/`, using relative paths.

## Data (`data/`)
| File | What it is |
|---|---|
| `crsp_index.csv` | WRDS CRSP monthly market index, 1926–2025: value- and equal-weighted returns with and without dividends |
| `crsp_stock_compact.csv` | WRDS CRSP monthly market value of US-incorporated ordinary common shares, 1926–2025 |
| `compustat_annual.csv` | WRDS Compustat annual fundamentals, 1950–2025 |
| `ccm_links.csv` | WRDS CRSP–Compustat Merged link table |
| `cay_current.csv` | Lettau's consumption–wealth ratio (Lettau & Ludvigson, 2001), 1952–2019, from Martin Lettau's data page |
| `lecture_benchmarks.csv` | Ch. 8 slide values (predictability table), transcribed |
| FRED `*.csv` | Downloaded unmodified from fred.stlouisfed.org: AAA, BAA, CPIAUCSL, DCOILWTICO, GDPC1, INDPRO, T10Y3M, TB3MS, UNRATE, USREC, VIXCLS |

The full raw WRDS downloads are in the group Drive (Group 8 → Project3) and, locally, in `raw/` (git-ignored).
