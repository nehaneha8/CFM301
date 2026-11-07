"""
One-off helper: extract the data cached inside slide 59's chart of "Ch 9 Bonds.pptx" and save it as data/slide59_cached_series.csv.

A .pptx is a zip file; PowerPoint stores the plotted values of each chart in ppt/charts/chartN.xml. The chart titled
"Baa-Tsy Yield Spreads and Liquidity, Corr = 0.96" holds 46 monthly points (Jan 2006 - Oct 2009) for two series:
  * "Baa-Tsy (LH axis)"                        -> slide_spread_pct   (percent)
  * "On-the-run/Off-the-run (RH axis)"         -> slide_liquidity_bp (basis points)
The notebook reads the CSV only; the pptx is not needed to reproduce the results.

Python 3.9+, standard library only.   Usage:  python extract_slide59.py     (paths are relative to this script's folder)
"""
import csv
import datetime as dt
import pathlib
import re
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
PPTX, OUT = HERE / "Ch 9 Bonds.pptx", HERE / "data" / "slide59_cached_series.csv"
COLS = {"Baa-Tsy (LH axis)": "slide_spread_pct", "On-the-run/Off-the-run (RH axis)": "slide_liquidity_bp"}

with zipfile.ZipFile(PPTX) as z:
    chart = None
    for name in z.namelist():
        if name.startswith("ppt/charts/chart") and name.endswith(".xml"):
            xml = z.read(name).decode("utf8")
            if "Baa-Tsy Yield Spreads and Liquidity" in xml:
                chart = xml
    assert chart is not None, "slide-59 chart not found"

series = {}
for ser in re.findall(r"<c:ser>.*?</c:ser>", chart, re.S):
    label = re.search(r"<c:tx>.*?<c:v>(.*?)</c:v>", ser, re.S).group(1)
    xs = [float(v) for v in re.findall(r"<c:v>(.*?)</c:v>", re.search(r"<c:xVal>(.*?)</c:xVal>", ser, re.S).group(1))]
    ys = [float(v) for v in re.findall(r"<c:v>(.*?)</c:v>", re.search(r"<c:yVal>(.*?)</c:yVal>", ser, re.S).group(1))]
    series[COLS[label]] = dict(zip(xs, ys))

serials = sorted(set.intersection(*[set(s) for s in series.values()]))
with open(OUT, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["month"] + list(COLS.values()))
    for s in serials:                                             # Excel serial date -> calendar month
        d = dt.date(1899, 12, 30) + dt.timedelta(days=int(s))
        w.writerow([d.strftime("%Y-%m")] + [series[c][s] for c in COLS.values()])
print(f"wrote {OUT.relative_to(HERE)}: {len(serials)} months")
