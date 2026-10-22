# Methodology, Decisions and Conclusion

Everything below is implemented in `proj2.ipynb` (run top to bottom, about 2 minutes).

## 1. Question and rationale
**Factor:** LEV = return of high-leverage stocks minus low-leverage stocks, where leverage = `debt / (debt + market equity)`. This is a monotonic transformation of debt / market cap, so it ranks stocks identically.
**Rationale (bad times):** leveraged firms have fixed claims ahead of equity, so in recessions and credit crunches they face distress and refinancing risk. Investors should demand a premium for holding that exposure.
**Audience (suggested, group to confirm):** quantitative fund managers deciding whether to add a leverage tilt.

## 2. Data
| Source | Used for |
|---|---|
| Compustat quarterly | debt (`dlcq` + `dlttq`), assets (`atq`), announcement date (`rdq`) |
| CRSP monthly | total returns (`MthRet`), price, shares, exchange |
| CCM link table | stock (PERMNO) to company (GVKEY), with valid dates |
| Ken French library | Mkt-RF, SMB, HML, RF, UMD |

Sample: **Jan 1974 - Dec 2018**, 2,005,744 stock-months, 16,801 stocks, 540 months.

## 3. Key decisions and why
| Decision | Reason |
|---|---|
| Returns = CRSP `MthRet`, monthly | Total return (dividends included, split-adjusted), so no manual price adjustment. `MthRetx` and raw price are not used. |
| Debt = `dlcq` + `dlttq`; one missing piece counts as 0 | Needs at least one reported. Book value of debt is the standard stand-in for market value. |
| Financials (SIC 6000-6999) excluded | Debt is part of their business, so leverage means something different. |
| Market equity summed across a company's share classes | Leverage is a company-level concept. |
| Fundamentals used only after `rdq` (else quarter-end + 3 months) | Avoids look-ahead bias. |
| Sort at end of month t, earn the t+1 return | Forward-looking: the sort uses only information known beforehand. |
| 30/70 breakpoints, value-weighted, all stocks | Mirrors Fama-French style factors. Value weights limit micro-cap influence. |
| Winsorize next-month returns at 1/99, by month | Controls extreme returns (max was +1,900%). About 40,000 observations changed. |
| Market leverage not winsorized | Bounded in [0,1] and only used for ranking, so clipping would change no portfolio. Book leverage (max 855) is clipped at the 99th percentile. |
| Sample ends 2018 | Zero-debt share falls from about 19% to 6% in 2019Q1 because lease liabilities (ASC 842) appear to enter reported debt. The series is not comparable across 2019. |
| Expected return = average realized return | Expected returns are not observable. Premium = sample mean of the monthly factor, tested with a t-stat. |
| OLS with Newey-West t-stats (6 lags), written in numpy | Corrects for autocorrelation and heteroskedasticity. `statsmodels` does not import in this environment. |
| Test assets: 25 portfolios (5 size x 5 leverage) | Standard two-way sort. Caveat: sorted on leverage, so LEV partly explains them by construction. |

Cleaning counts for every step are printed in the notebook (Compustat: 1,215,146 to 862,296 rows; CRSP: 2,961,391 to 2,500,417 rows, including 7,976 exact duplicates removed).

## 4. Tests run
1. Factor premium: mean monthly return and t-stat.
2. Is LEV spanned? LEV regressed on CAPM, FF3 and FF4 (the alpha is the question).
3. 25 test portfolios on market + LEV (requirement 5), and on CAPM, FF3, FF4, CAPM+LEV and FF4+LEV (requirement 6, by R-squared).
4. Sensitivity (requirement 7): quintiles, terciles, equal weights, book leverage, no winsorizing, 1974-95, 1996-2018, excluding 2007-09. Each reports premium, FF4 alpha and added R-squared.
5. Bad times: LEV return in NBER recessions, down-market months and the worst 10% of market months.

## 5. Results
- **No premium:** +0.07% per month (about 0.9% a year), t = 0.36.
- **LEV is mostly value:** loads +1.02 on HML (t = 13.3), -0.21 on UMD, -0.10 on the market, none on SMB. FF4 alpha is -0.04% (t = -0.39).
- **Little added explanatory power:** average R-squared across the 25 portfolios goes from 0.842 (FF4) to 0.853 (FF4+LEV). In market-plus-LEV regressions LEV is significant in 17 of 25 portfolios.
- **Not robust:** the premium changes sign across subperiods and weighting schemes and is never significant. Added R-squared stays at about 1 point in every specification. The only significant number is the book-leverage FF4 alpha (-0.30%, t = -2.6), one result out of nine.
- **Bad times:** LEV earns +0.02% in recessions, +1.39% in down-market months and +2.77% in the worst 10% of market months, so it behaves like a hedge, not like compensation for bad-times risk.

## 6. Conclusion
Market leverage is not a separately priced factor. Its return is explained by exposure to value (and, negatively, momentum and the market), and it pays off in bad times, which is the opposite of what a risk premium requires.
- **Rational vs behavioral:** there is no premium to explain, and the hedge-like pattern does not support a distress-risk story. Nothing here shows behavioral mispricing either.
- **Efficiency:** leverage is built from public accounting and price data, so the test speaks to **semi-strong** efficiency. A zero abnormal return after controlling for known factors is consistent with an efficient market, so the Grossman-Stiglitz question (why an inefficiency is not traded away) does not arise.
- **For the audience:** a leverage tilt duplicates a value tilt, adds no return and is unstable across periods. There is no reason to add it as a separate factor.

## 7. Check against the assignment guidelines
| Req | Status |
|---|---|
| 1 Rationale, bad times, audience | Drafted above. **Group should confirm audience and write it up in their own words.** |
| 2 Factor and test assets | Done. |
| 3 Total returns, variable, frequency | Done (`MthRet`, monthly). **Not verified: that `MthRet` includes delisting returns.** The last-month return pattern suggests it does. Confirm in the CRSP documentation. |
| 4 Cleaning, winsorizing, counts | Done. Missing, duplicate and outlier handling are logged. |
| 5 OLS on factor + market | Done (loadings, t-stats, R-squared for all 25 portfolios). |
| 6 Compare to benchmark | Done. The comparison is by R-squared. There is no formal test of the increase (e.g. GRS). |
| 7 Sensitivity | Done, with 9 specifications. |
| 8 Rational vs behavioral | Evidence done. **Group should link it to the specific theories from class.** |
| 9 Market efficiency | Drafted above. **Group should write it in the course's terms.** |

## 8. Limitations
- Leverage uses current market equity, so it partly proxies for past returns (value and momentum).
- The 25 test portfolios are sorted on leverage, which flatters LEV's explanatory power.
- Breakpoints use all stocks (not NYSE-only), so micro-caps affect the breakpoints.
- Nine sensitivity specifications means one significant result is weak evidence.
- Compustat debt is book value. It is not comparable across 2019, so results do not cover 2019-2025.

## 9. Fixes made while auditing the work
- **Book-leverage sensitivity bug:** stocks with missing book leverage (70% in 1974, 11% in 1975-79) were silently placed in the low-leverage group. They are now excluded. The headline result did not change.
- **Missing outputs:** requirement 5 (market-plus-LEV regressions) and added R-squared in the sensitivity table are now reported.
- **Wrong explanation corrected:** the 2019 zero-debt break was attributed to missing data. It is more likely the lease-accounting change (the firms that jumped are store-heavy retailers).
