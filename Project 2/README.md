# Project 2: Market-Leverage Factor (LEV)

Tests whether high-minus-low market leverage, `debt / (debt + market equity)`, is a priced factor beyond the market, size, value and momentum factors (CRSP + Compustat, main sample Jan 1974 - Dec 2018; 2019-2025 is used only as a sensitivity test).

## How to run
1. Install Python 3 and the packages: `pip install pandas numpy matplotlib jupyter`
2. Open **`Project2_Leverage.ipynb`** and choose **Run All** (about 2-3 minutes, roughly 4 GB of RAM, no internet access needed).

The notebook reads only the three input files below, which must stay in the same folder as the notebook. Everything else is produced by the notebook:
- `stock_timed.csv` (about 200 MB) and `permnos.txt` are written during the run;
- `fig1_lev_vs_hml.png` and `fig2_bad_times_quintiles.png` are saved by the charts cell.

It was tested on pandas 1.5 and pandas 3.1.

## Files
| File | What it is |
|---|---|
| `Project2_Leverage.ipynb` | The full analysis: rationale, data cleaning, factor construction, regressions, test assets, sensitivity, bad times, charts, results and interpretation, requirements checklist |
| `compustat.csv.gz` | Raw WRDS Compustat quarterly fundamentals (short- and long-term debt, assets, announcement date) with the CRSP-Compustat Merged link table |
| `crsp_monthly.csv.gz` | Raw WRDS CRSP monthly stock file (total return `MthRet`, price, shares, exchange and security-type flags) |
| `04_Fama_French_Monthly_Factors.csv` | Monthly Mkt-RF, SMB, HML, momentum (UMD) and risk-free rate, in decimals, 1950-2025 (matches the Ken French Data Library) |

`pandas` reads the `.csv.gz` files directly; do not unzip them.

