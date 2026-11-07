"""
Documentation-only helper: how the FRED CSVs in data/ were downloaded (needs internet; NOT needed to reproduce the results).

Writes one CSV per series into data/ next to this script. Running it again refreshes the files to FRED's current vintage, so
the numbers in the notebook would then change; the submitted data/ files are the November 2026 vintage the results were produced with.

What is NOT downloaded by this script:
  * data/tnc_qh_pars_1.xls and data/tnc_qh_otrpars.xls: US Treasury "Treasury Nominal Coupon-Issue (TNC) yield curve" monthly average par
    yields (all issues, and on-the-run). Downloaded manually from the Treasury's coupon-issues / yield-curve data page (home.treasury.gov).
  * data/slide59_cached_series.csv: created by extract_slide59.py from the lecture file.

Python 3.9+, standard library only.
Usage:  python 00_fetch_fred.py
"""
import pathlib
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)

SERIES = {
    # corporate yield (Moody's seasoned Baa; maturities of 20 years and above)
    "BAA": "Moody's Baa yield, monthly average, from 1919",
    "DBAA": "Moody's Baa yield, daily, from 1986",
    # Treasury constant-maturity yields
    "GS10": "10-year Treasury, monthly average",
    "DGS10": "10-year Treasury, daily",
    "DGS20": "20-year Treasury, daily (no data Jan 1987 - Sep 1993)",
    "DGS30": "30-year Treasury, daily",
    # volatility (default-risk / stress proxy) and funding-liquidity proxy
    "VIXCLS": "VIX, daily, from 1990",
    "VXOCLS": "VXO (old VIX), daily, 1986 to Sep 2021",
    "TEDRATE": "TED spread, daily, 1986 to Jan 2022",
}

for sid, desc in SERIES.items():
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
    dest = OUT / f"{sid}.csv"
    with urllib.request.urlopen(url, timeout=60) as r:
        dest.write_bytes(r.read())
    print(f"{sid:8s} -> {dest.relative_to(OUT.parent)}  ({desc})")
