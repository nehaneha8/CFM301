# Project 5: Do active mutual fund fees survive better benchmarks?

**Question:** Does an active mutual fund's fee remain justified when performance is evaluated against progressively more demanding benchmarks?

**Audience:** Retail investors and financial advisors evaluating active US growth management. Five historical case studies, January 2016–December 2025: FBGRX, FDGRX, FOCPX, PRGFX and TRBCX. The index-fund benchmark uses VFIAX, VIGAX, VVIAX and VSMAX. These are availability-selected surviving funds, not a representative or survivor-bias-free sample. Some active funds restrict new investors.

## Run the analysis

Tested with Python 3.11.4 on macOS. Use Python 3.11 and the versions in `requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --sys-prefix --name python3 --display-name "Python 3"
python -m jupyter nbconvert --to notebook --execute --inplace Project5_Mutual_Fund_Fees.ipynb
```

Or open `Project5_Mutual_Fund_Fees.ipynb`, select this environment, and **Restart Kernel and Run All**. Run from this folder. The normal analysis reads only `data/`, writes tables/figures to `output/`, and requires no internet, CRSP, Bloomberg or credentials. Outputs are also displayed inline. The first plotting run may take longer while fonts are cached.

The notebook follows Projects 2–4: numbered Markdown sections, explanations after code cells, a cleaning log, displayed statistical evidence, economic interpretation, sensitivity, source notes and a requirements checklist. All analysis is in the notebook; `prepare_free_data.py` is optional source preparation, not an analysis dependency.

## Files

| File/folder | Purpose |
|---|---|
| `Project5_Mutual_Fund_Fees.ipynb` | Full analysis, results, all 12 requirements and explicit data limitations |
| `data/` | Only numerical/source inputs required by the notebook |
| `output/` | Generated CSV tables, PNG figures and `results_summary.json` |
| `requirements.txt` | Pinned direct execution/source-preparation dependencies |
| `prepare_free_data.py` | Rebuild the raw financial-highlight CSV from included source-table snapshots; optional online refresh of market/factor/flow extracts |

## Data and conventions

* `yahoo_daily.csv` holds split-adjusted daily NAV and adjusted close; `yahoo_actions.csv` holds distributions and split metadata for the same nine classes. The source query covers December 2014–December 2025; the submitted extract retains the December 31, 2014 prior NAV and then 2015–2025, with 2015 supplying lagged returns. Daily total returns are `(NAV + cash distribution) / previous NAV - 1`, compounded monthly. Yahoo already adjusts historical prices/distributions for splits; 2018 split events are audited and never applied a second time. Do not add cash distributions to adjusted-close returns.
* `financial_highlights_raw.csv` preserves original percent strings, fiscal years, filing dates, expense/turnover/return fields and asset-unit multipliers. `financial_highlights_sources.json` preserves the selected table text/rows, headings and exact source links. Repeated years are resolved inside the notebook by retaining the latest filed description. Fees are after waivers/reductions; gross returns add the annual ratio divided by 12. Fiscal rates are spread across their fiscal months, not substituted with today's fee. FDGRX December 2025 uses the last completed fiscal ratio for one month, explicitly counted and tested.
* The fiscal-year return-validation table reports source differences. Calendar-year pilot agreement did not guarantee exact fiscal agreement. The notebook retains original values, displays discrepancies above 10 bp, and tests the adjusted-close alternative. It does not silently alter NAVs to match an annual report.
* `factors_percent.csv` is the US FF3 and momentum monthly data from the Ken French library, both September 2026 vintage, restricted to 2016–2025. Inputs remain in percent and are converted once to decimals in the notebook. No factors are mixed with the older Project Two vintage.
* `ici_fee_distribution.csv` contains the two relevant 2025 rows of ICI Figure 2 (equity funds and growth funds). Quantiles equally weight share classes; the asset-weighted mean describes dollars. Only published percentile bands are inferred. The broad US-registered equity universe includes international/world funds.
* `sec_reported_monthly_flows.csv`, `sec_quarterly_series_assets.csv` and `sec_monthly_class_returns.csv` are extracts of individual N-PORT filings for PRGFX/TRBCX. Links are retained on each row. Cash flows cover all share classes in each series; class returns are separately identified. No portfolio holdings or unused fields are included.
* `sources.json` records definitions, data vintage and SHA256 hashes. The notebook checks these hashes. Do not edit source files to make an assertion pass.

## What requirement 9 can and cannot support

No complete monthly share-class TNA series was established from the free sources. The notebook implements the requested formula and audits whether consecutive monthly class asset pairs exist (zero). It then provides:

1. Half-sample Carhart alpha/rank persistence for all five funds.
2. Inferred **annual** class flows from observed annual TNA and matching compounded fiscal returns, related to the preceding fiscal year's returns.
3. Actual reported **monthly series** external flows for two funds: sales minus the absolute redemption withdrawal amount, excluding reinvestments. The legacy 2019–2023 source fields use negative redemptions while 2024–2025 uses positive withdrawal amounts; original fields are preserved and normalization counts are logged. Flows are scaled by the **previous quarter-end** series TNA and related to lagged retail-class 12-month returns as a disclosed performance proxy.
4. A joint Berk–Green interpretation with the gross/net evidence, without asserting that flows caused alpha decay.

Annual residual flows and reported series flows are not relabelled as exact monthly class flows. The original monthly-TNA part of requirement 9 remains a documented limitation under the instructor's clarification that paid data are not expected. Neither annual nor quarterly assets are interpolated. Other limitations include survivorship/incubation, family concentration, model choice, fee timing, uncertain alphas and non-causal fee/flow comparisons.

## Main outputs

* `table_factor_regressions.csv`: CAPM, FF3 and Carhart alpha, alpha t, residual tracking error, annual appraisal ratio and R² for each fund.
* `table_gross_factor_results.csv`, `table_final_fee_verdict.csv`: gross/net comparisons, average fees, investable-benchmark alpha/cost, uncertainty and per-fund verdicts.
* `table_index_weights.csv`, `table_index_holdout.csv`: non-negative fully invested weights and a 2016–2020-trained / 2021–2025 evaluation check.
* `table_persistence.csv`, `table_annual_flow_summary.csv`, `table_reported_flow_regressions.csv`: persistence and the disclosed flow analyses.
* `table_sensitivity.csv`: recent/early samples, 1/99 winsorization, adjusted-close returns, exclusion of the fee-approximation month and lagged-filed expense sensitivity. The notebook also checks the index set and rolling 36-month alphas.

Point-estimate fee justification is separate from confidence intervals and five-fund BH q-values. Tracking error is the sample standard deviation of **regression residuals**, annualized by √12. Alpha is annualized by ×12. Index weights and an intercept are fitted jointly; benchmark fees are not subtracted twice.

## Source preparation (optional)

This is not required to run or grade the notebook. To independently rebuild the financial-highlight extract from the included snapshots without network access:

```bash
python prepare_free_data.py --output-dir /tmp/project5_source_check
```

The script also offers `--refresh-market`, `--refresh-factors` and `--refresh-flows` for optional public-source re-acquisition. Use a separate `--output-dir` to preserve the submitted vintage; live sources can be revised. Original acquisition was November 20, 2026. ICI rows, fund metadata and the fixed selected-table snapshots are included explicitly. A source refresh is not needed for reproducibility of this submission.

