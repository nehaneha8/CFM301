# Rationale Behind Each Step of `Project2_Combined_Submission.ipynb`

Each entry says what the step does, why it is done that way, and what the alternative would have cost. Section numbers match the notebook.

## 1. Research design (Section 1)
| Choice | Reason |
|---|---|
| Factor = high minus low **market leverage** | Leveraged firms have fixed claims ahead of equity, so recessions and credit crunches (the "bad times") should hurt them most. A risk-based premium requires exactly that exposure. |
| Four testable predictions (positive mean, nonzero alpha, losses in bad times, extra explanatory power) | Makes the hypothesis falsifiable, so a null result is a finding and not a failure. |
| Alternative explanations stated up front (overlap with value; behavioral mispricing) | Debt / market cap has market equity in the denominator, as book-to-market does. We have to test overlap with HML explicitly. |
| Audience: quant managers and pension funds | The practical question is whether a tilt adds anything beyond the value and momentum exposure they already hold, and whether it survives costs. |

## 2. Data and cleaning (Section 2)
### Sources and returns
- **Compustat quarterly, not annual:** quarterly data gives fresher debt figures and includes the earnings-announcement date (`rdq`), so we know when each number became public.
- **CRSP `MthRet`:** a *total* return (dividends included, split- and distribution-adjusted), as the assignment requires. `MthRetx` excludes dividends and raw price is not split-adjusted, so neither is used. No manual `CFACPR` adjustment is needed.
- **Link table:** a stock (PERMNO) must be mapped to its company (GVKEY), because debt belongs to the company and a company can have several share classes.

### 2a. Compustat cleaning
| Step | Why |
|---|---|
| Drop repeats caused by multiple links, then duplicate company-quarters (keep first row) | A company-quarter should appear once. The 628 company-quarters with two *different* rows keep the first in file order. This is an assumption, not an economic rule. |
| Trim to 2025 | Remove anything after the CRSP end date. |
| Drop financials (SIC 6000-6999; ~25% of raw rows) | Their debt is part of their business, so "leverage" means something different and would swamp the high-leverage leg. |
| Require at least one of `dlcq`, `dlttq` | Without any debt item we cannot compute leverage (missing-value rule). |
| Debt = `dlcq` + `dlttq`; a missing piece counts as 0 | If a firm reports one item, the other is plausibly zero. This is an assumption (about 4% of firm-quarters) that we state but have not tested. |
| Non-negative debt | A sanity check (it drops 3 rows). |

### 2b. CRSP cleaning
| Step | Why |
|---|---|
| US common stock (`EQTY`/`COM`/`NS`, US-incorporated) on NYSE, AMEX, NASDAQ | Standard asset-pricing universe; excludes funds, ADRs and foreign firms so Compustat and CRSP data are comparable. |
| Market equity = \|price\| x shares / 1000 ($ millions) | CRSP stores negative prices for bid/ask averages. Shares are in thousands and Compustat debt is in millions, so this puts both in the same units. |
| Drop non-positive market equity | Also removes missing prices. |
| Remove exact duplicate rows | Every duplicated stock-month was an identical row, so removing them is lossless. |
| Count missing `MthRet` | Observations without a return cannot be tested; they drop out when the next-month return is built. |

### Sample window
- The WRDS extracts begin in 1973 (both files), and returns start in January 1974, so the first leverage values come from late 1973 with about 2,200 firms.
- The sample **ends in December 2018** because Compustat's zero-debt share drops from about 20% to 8% in 2019Q1. The firms that jump (Ulta, American Eagle, Urban Outfitters, Five Below) are store-heavy, which suggests lease liabilities (ASC 842) entered reported debt. After 2019 retailers would look highly leveraged because of an accounting change, not risk. This is a pattern we found, not something confirmed against WRDS documentation.

### 2c. Merge and timing
| Step | Why |
|---|---|
| Link valid in that month only; best link P > C > J > N | Uses the correct company over time. No stock-month had more than one valid link in this data, but the rule is there for safety. |
| **Sum market equity across share classes** per company | Leverage = company debt / company equity value. Using one class would overstate leverage. |
| Debt is "available" at `rdq` (else quarter-end + 3 months) | **No look-ahead bias:** an investor could only use numbers that were public. |
| `merge_asof` backward, at most 365 days old | Each month uses the latest public figure, and stale figures (over a year old) are not used. |
| `mkt_lev = debt / (debt + market equity)` | Bounded in [0,1], so no extreme values; it ranks stocks exactly like debt / market cap. |
| `book_lev = debt / assets` (set to missing if assets <= 0) | An alternative definition for the sensitivity test; non-positive assets would create `inf`. |
| `ret_next` taken from CRSP, only if the next row is the next calendar month | The return we explain is **month t+1**, after the sort at the end of month t, so the sort is forward-looking. Taking it from CRSP directly avoids losing a return just because leverage was missing the next month. The calendar check stops a gap from pairing a return with the wrong month. |

## 3. Winsorizing, audit and factor construction (Section 3)
| Choice | Reason |
|---|---|
| Winsorize returns and leverage at 1st/99th percentile **within each month** | The assignment requires winsorizing returns and sorting characteristics. Doing it by month removes extreme observations (one return was +1,577%) without mixing different market conditions. |
| Leverage is clipped even though it cannot change any portfolio | It is bounded and only ranked, so clipping cannot change an assignment. It is clipped anyway so every variable is treated the same, and the changed count is reported. |
| Book leverage clipped at the 99th percentile only | Its maximum is 855, and the lower end is bounded at 0. |
| Audit table | Requirement 4 asks how many observations each step affects. It also confirms zero duplicates and zero missing values remain. |
| **Value-weighted 30/70** baseline | Like Fama-French factors. Value weights stop micro-caps from dominating; equal weights, terciles and quintiles are sensitivity tests. |
| Breakpoints from all listed stocks | Simple and uses the whole universe; NYSE-only breakpoints are a possible refinement, noted as a limitation. |
| `dropna` on the sort variable | A stock with no characteristic must not fall into the lowest bucket (this was a bug in an earlier version). |

## 4. Benchmark factors (Section 4)
Mkt-RF, SMB, HML, UMD and RF are loaded from the local CSV, which matches the Ken French library (differences about 1e-16). A local file means the notebook runs without internet. RF is needed to turn raw returns into excess returns.

## 5. Regressions (Section 5)
| Choice | Reason |
|---|---|
| Premium = average **realized** LEV return, tested against zero | Expected returns cannot be observed; the sample mean over a long period estimates the premium, and the t-stat tells us whether it differs from zero. |
| Newey-West standard errors, 6 lags | Monthly returns have autocorrelation and changing volatility; ordinary standard errors would overstate significance. |
| Hand-written OLS | `statsmodels` does not import in the author's main environment. It was verified against `statsmodels` HAC (agreement to 1e-14). |
| Report adjusted R² and p-values too | Adjusted R² penalizes adding a variable, so a small gain is not mistaken for real explanatory power. |

### 5a. Premium and spanning
LEV is regressed on CAPM, FF3 and FF3+UMD. If the **alpha** is about zero, the existing factors already explain LEV and it is not a new return source. The HML loading and correlation measure overlap with value.

### 5b. Test assets (requirements 5 and 6)
| Choice | Reason |
|---|---|
| **25 size x leverage** portfolios | A rich set of assets that vary in leverage, so LEV can show an effect. It is partly sorted on leverage, so LEV explains it partly by construction. |
| **5 size portfolios, equal-weighted** | Sorted only on size, so independent of leverage. If LEV helps explain these, it captures something it was not built from. |
| Excess returns (minus RF) for test assets, not for LEV | Asset-pricing models explain returns above the risk-free rate. LEV is already a long-minus-short spread. |
| Six models: CAPM, FF3, FF4, each with and without LEV | Holds the benchmark fixed so the change in R² is attributable to LEV. |
| "Significant" means \|t\| > 2 | A simple, consistent rule of thumb. |

## 6. Sensitivity (requirement 7)
Thirteen specifications, each changing one assumption, reporting premium, significance (four-factor alpha) and added explanatory power (R² gain on both sets of test assets):
- **Factor construction:** quintiles, terciles, equal-weighted legs, book leverage.
- **Winsorizing:** none, 1/99 (baseline), 5/95.
- **Sample:** 1974-95 vs 1996-2018, 1981-2018 (the 1970s have fewer firms), excluding the 2007-09 crisis, the **full 1974-2025 sample** and **2019-2025 alone** (these two test whether the conclusion survives the post-2019 debt break; the main sample still ends in 2018).

The grid shows whether any conclusion depends on one arbitrary choice. Thirteen specifications also means one significant result is weak evidence, which the notebook states.

## 7. Bad times (requirement 8 evidence)
- A risk premium should come with poor payoffs in bad times, so we look at LEV and each leg in down markets (Mkt-RF < 0), severe declines (Mkt-RF <= -5%), the worst 10% of months and NBER recessions.
- Stress states are **defined by the market and by NBER dates, not by LEV's own returns**, so they are not chosen after seeing the result.
- Each of the six recessions is shown separately to see whether one episode drives the result.
- Splitting LEV into its two legs shows whether the high-leverage stocks fall more in downturns, which is the mechanism the rationale predicts.

## 8. Charts (Section 8)
Growth of $1 in LEV vs HML and its four-factor loadings show the value overlap visually. The return-by-market-state chart and the leverage-quintile chart show the bad-times pattern and whether returns rise with leverage.

## 9-12. Interpretation
- **Rational vs behavioral:** a rational explanation needs a premium plus losses in bad times; a behavioral one predicts a premium concentrated in small, hard-to-arbitrage stocks. The evidence supports neither.
- **Market efficiency:** leverage uses public accounting and price data, so the test is of **semi-strong** efficiency. A zero abnormal return fits an efficient market, and any small gross effect could be consumed by information and trading costs (Grossman-Stiglitz). Costs are not measured here.
- **Audience:** no premium, heavy overlap with value, an unstable sign, and a negative market beta that is cheaper to get directly, so there is no case for a separate leverage tilt.

## Fixes made while auditing the work
1. **Missing characteristic put in the low bucket:** stocks with missing book leverage were silently ranked as low leverage. They are now excluded.
2. **Link priority:** an alphabetical sort ranked `N` ahead of `P`; links are now ranked P > C > J > N.
3. **Next-month return:** it is now taken from CRSP, which recovered about 670 stock-months.
4. **2019 data break:** originally described as missing data; it is more likely the lease-accounting change.

## Known limitations and unverified items
- **Not verified:** that `MthRet` includes delisting returns.
- **Untested assumption:** treating a missing debt component as 0.
- **Sample:** main results are 1974-2018. 2019-2025 is excluded from them because of the accounting break and appears only in the sensitivity table.
- **Test assets:** the 25 size x leverage portfolios are partly circular; the five size portfolios are independent but few.
- **Costs and out-of-sample:** returns are gross of costs and no out-of-sample period was reserved.
- **Theory references:** the rational-vs-behavioral discussion names theories generically; the group should add the specific ones from class.
