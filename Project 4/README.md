# Project 4: Does the 2008 Liquidity-Credit Link Repeat?

**Research question:** "Is 2008’s near perfect link between liquidity and credit spreads a one-off, or does it repeat in March 2020 COVID and the 2022–23 rate shock?"

The notebook compares the three named episodes for central bank policymakers. It retains the assignment's lecture replication, longest-sample extension, default-risk regressions and credit spread puzzle, then adds explicit episode comparisons, March 2020 movements and window/proxy sensitivities.

## Files and execution order

1. Keep the five original numerical files in `data/`.
2. Open `Project4_Credit_Spread_Liquidity.ipynb` with this directory as the working directory.
3. Select a Python environment with the packages below and use **Restart Kernel and Run All Cells**. The saved notebook includes 23 executed code cells, actual tables, and three inline figures, including a three-panel episode comparison on common axis scales. Execution takes roughly a minute, depending on kernel startup.

The notebook uses relative paths and never downloads data, calls an API, requests credentials, or writes to the source files. It does not require the earlier projects. The PDF and lecture deck document the assignment and benchmarks but are not required for numerical execution.

For command-line execution from this folder:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=180 \
  --ExecutePreprocessor.kernel_name=python3 \
  Project4_Credit_Spread_Liquidity.ipynb
```

Use a `python3` Jupyter kernel belonging to the environment that has the dependencies. If needed, register that environment with `python -m ipykernel install --user --name python3 --display-name 'Python 3'`.

## Verified environment

Executed using **Python 3.14.6**, Anaconda, on macOS. Exact direct and execution package versions:

| Package | Version | Purpose |
|---|---|---|
| pandas | 3.0.5 | Data loading, monthly alignment and tables |
| numpy | 2.5.1 | Numerical operations and consistency checks |
| matplotlib | 3.11.1 | Inline time-series figures |
| statsmodels | 0.14.6 | OLS and HAC covariance estimates |
| scipy | 1.18.0 | Numerical dependency of statsmodels |
| xlrd | 2.0.2 | Read the legacy XLS workbooks |
| IPython | 9.15.0 | Notebook display and inline plotting |
| ipykernel | 6.31.0 | Python Jupyter kernel |
| nbformat | 5.10.4 | Notebook format |
| nbclient | 0.11.0 | Clean-kernel execution |
| nbconvert | 7.17.1 | Command-line execution and optional export |

`requirements.txt` pins these versions. Install them into a compatible environment before running, for example `python -m pip install -r requirements.txt`. Initial package installation may require internet access or an offline wheel cache. **Once the packages are installed, all notebook execution uses only the submitted local files.** No package installation occurs inside the notebook. The PDF/PowerPoint readers used during preparation are not runtime dependencies.

## Source files

Coverage below describes the supplied local vintage, inspected November 6, 2026. Original download dates are not recorded in the files.

| File in `data/` | Description | Supplied coverage |
|---|---|---|
| `BAA.csv` | Moody's seasoned Baa yield via FRED, monthly annual percentage yield | Jan 1919-Oct 2026; 1,294 rows |
| `GS10.csv` | Federal Reserve H.15 10-year constant-maturity Treasury yield via FRED, monthly annual percentage yield | Apr 1953-Oct 2026; 883 rows |
| `VIXCLS.csv` | Cboe VIX daily close via FRED, index points | Jan 2, 1990-Nov 5, 2026; 9,613 rows, including 302 missing closes |
| `tnc_qh_pars_1.xls` | US Treasury TNC fitted monthly average par yields, percent; 2, 3, 5, 7, 10, 20 and 30 years | Jan 1976-Sep 2026; 609 observations |
| `tnc_qh_otrpars.xls` | US Treasury TNC fitted monthly average on-the-run par yields, percent; 2, 5 and 10 years | Jan 1986-Sep 2026; 489 observations |
| `CFM301_Project4_Credit_Spread_Liquidity_v2.pdf` | Assignment instructions and rubric | Reading material |
| `Ch 9 Bonds.pptx` | Lecture, especially displayed slides 48-59 | Reading material |

Each Treasury workbook has data on `Sheet1`, with six heading/spacer rows and a blank second column. `Sheet2` and `Sheet3` are empty. Treasury date labels use `Jan 1976`; CSV dates use `YYYY-MM-DD`.

Definitions and provenance: [BAA](https://fred.stlouisfed.org/series/BAA), [GS10](https://fred.stlouisfed.org/series/GS10), [VIXCLS](https://fred.stlouisfed.org/series/VIXCLS), [Treasury TNC files](https://home.treasury.gov/data/treasury-coupon-issues-and-corporate-bond-yield-curves/treasury-coupon-issues/), and [Treasury XRM methodology](https://home.treasury.gov/system/files/226/The-XRM-Yield-Curve-Methodology.pdf). These links are documentation only. The notebook does not fetch them.

## Definitions and treatment choices

- Main credit spread: `BAA - TNC 20-year par yield`, in percentage points. BAA covers maturities of 20 years and above. Twenty years is a closer available match, but exact maturity/duration matching remains impossible with these aggregate files. Baa minus GS10 and minus 30-year TNC are sensitivity comparisons.
- Liquidity premium: `100 * (TNC off-the-run 10-year yield - TNC on-the-run 10-year yield)`, in basis points. The methodology validation and limitations are documented in notebook Section 4. This is a fitted curve proxy, not the yield difference for a specific transaction pair or a verified copy of the lecture series.
- Monthly VIX: arithmetic mean of observed daily closes. Holiday blanks remain missing daily observations. November 2026 is unfinished as of the fixed inspection date and is excluded. October is complete but lies beyond the Treasury coverage, so the regression sample ends in September.
- Exact duplicates are counted and removed. Conflicting dates and malformed values cause explicit errors. No missing values are filled. No crisis spikes, negative liquidity gaps or other statistical outliers are removed or winsorized. The notebook displays cleaning counts and outlier diagnostics.
- Main original window: Jan 2006-Sep 2009, 45 months. The lecture's cached chart extends to Oct 2009, tested separately.
- Extended two-spread sample: Jan 1986-Sep 2026, 489 months.
- Identical regression sample: Jan 1990-Sep 2026, 441 months. All models contain an intercept. Both conventional and Newey-West HAC t-statistics are shown, using 12 monthly lags and a finite-sample correction.
- Main episode windows: Jan 2008-Dec 2009, Jan 2020-Dec 2021, and Jan 2022-Dec 2023. Each contains exactly 24 complete months. These equalize sample size without assuming the economic phases are identical. The lecture's original window is a separate benchmark.
- Episode regressions: Models A-C are estimated separately for every window on identical months, with coefficients, conventional t-statistics, HAC t-statistics and R². Episode HAC uses three monthly lags and a finite-sample correction. One- and six-lag sensitivity estimates are also reported; the full-sample benchmark retains 12 lags.
- Monthly differences are computed on the full calendar before filtering. Within-window changes require both endpoints inside the window, yielding 23 changes per 24-month episode. The acute-window sensitivity separately includes the initial entry change, including February-to-March 2020.
- Window sensitivities: calendar 2008, 2020, 2022 and 2023; and six-month windows Sep 2008-Feb 2009, Mar-Aug 2020 and Mar-Aug 2022. Six observations are insufficient for a reliable multivariable event regression, so those windows are used for descriptive correlations only.
- March 2020 is one monthly observation, so a March-only time-series correlation is undefined. Its levels and changes from February are shown directly. The monthly Treasury files cannot support a daily March event study.
- Expected-loss assumption: the lecture's Baa annual credit loss of 0.124% for 1982-2008. The notebook does not invent separate default-probability/recovery inputs or reinterpret regression R² as a decomposition of the average spread.

## Principal computed results

The main Baa minus 20-year TNC spread and 10-year TNC liquidity proxy produce the following results. Each episode has 24 levels observations and 23 within-window monthly changes:

| Episode | Credit/liquidity levels r | Monthly-change r | Credit/VIX levels r |
|---|---:|---:|---:|
| 2008-09 | 0.933127 | 0.691575 | 0.907029 |
| COVID 2020-21 | 0.084457 | 0.097950 | 0.876915 |
| Rate shock 2022-23 | -0.680471 | -0.055529 | 0.669035 |

| Episode | R² A: Liquidity | R² B: VIX | R² C: Both | Model C liquidity coefficient | Model C VIX coefficient |
|---|---:|---:|---:|---:|---:|
| 2008-09 | 0.8707 | 0.8227 | 0.9025 | 0.04939 | 0.03287 |
| COVID 2020-21 | 0.0071 | 0.7690 | 0.7690 | 0.00125 | 0.04921 |
| Rate shock 2022-23 | 0.4630 | 0.4476 | 0.5922 | -0.01742 | 0.01312 |

Liquidity coefficients are percentage points of corporate spread per liquidity basis point. VIX coefficients are percentage points per VIX index point. The notebook contains every intercept and conventional/HAC t-statistic for all nine episode models.

In March 2020, the main credit spread rises 1.26 pp from February while the fitted liquidity gap increases 1 bp to -1 bp. In Dec 2021-Dec 2023, BAA rises 2.34 pp and the 20-year Treasury yield rises 2.43 pp, leaving the credit spread down 0.09 pp. This separates rising borrowing yields from widening credit spreads.

**Sensitivity matters:** The COVID levels correlation is -0.275 in calendar 2020 but +0.553 in Mar-Aug 2020. Its acute change correlation is -0.239 for five within-window changes and +0.429 when the February-to-March change is included. The 5-year liquidity alternative produces +0.604 for COVID and +0.506 for the rate shock, versus the main 10-year results above. The later episodes therefore do not consistently repeat 2008's near-perfect positive 10-year relationship, but other windows and proxies can show positive co-movement.

The lecture-window correlation remains 0.966979 (Jan 2006-Sep 2009, N=45). The longest pair-sample correlation is 0.466310 (Jan 1986-Sep 2026, N=489). The full-sample credit/VIX correlation is 0.648900 (Jan 1990-Sep 2026, N=441). Full-sample regression R² values remain 0.224943, 0.421071 and 0.459507 for A-C.

The average main spread in the regression sample is 1.734444 pp. Subtracting the illustrative annual expected loss of 0.124 pp leaves 1.610444 pp. That residual cannot be attributed entirely to liquidity. Source definitions, common shocks, persistence, omitted fundamentals and the historical loss assumption limit causal interpretation.

The same baseline applied to the episode mean spreads of 3.1008, 1.8229 and 1.6763 pp leaves residuals of 2.9768, 1.6989 and 1.5523 pp, respectively. These are illustrative comparisons using a historical loss assumption, not estimates of each episode's true expected losses.

## Interpretation and unresolved limitations

The conclusion concerns recurrence of the observed 10-year proxy relationship across these three named episodes. It does not prove that 2008 was unique among all crises, nor that liquidity was unimportant during COVID. The [Federal Reserve's June 2020 report](https://www.federalreserve.gov/monetarypolicy/2020-06-mpr-part2.htm) documents substantial Treasury market dislocations in March 2020. Our fitted monthly relative-yield measure differs from direct trading measures and can miss common or intramonth deterioration. Negative later-period gaps and yield rounding are preserved and documented.

Small samples, persistent levels, approximate corporate maturity matching, and the absence of direct corporate liquidity/default measures constrain inference. VIX measures equity volatility rather than interest-rate volatility. The 2022-23 window also includes banking stress, as discussed in the [May 2023 Financial Stability Report](https://www.federalreserve.gov/publications/2023-may-financial-stability-report-asset-valuations.htm). No episode is treated as a clean causal experiment, and no regression R² is interpreted as a decomposition of the spread level.

## Verification and assignment scope

The revised notebook was executed from a fresh kernel with no cell errors. Calendar, units, identical regression samples, episode boundaries, anchor-month identities and regression arithmetic checks are included at the end. The five numerical inputs and prior project files were preserved. A separate temporary-folder run, containing just the notebook and five numerical inputs, reproduced all outputs; independent numerical checks also verified the episode regression coefficients and HAC covariance calculation.

This provides the requested notebook, raw-data-based analysis and execution documentation. The assignment PDF separately requires a maximum-three-page report, presentation slides, group presentation and peer review. Those are separate course submission items and are not created by this notebook task.
