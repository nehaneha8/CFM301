"""Optional source preparation; the analysis notebook needs no network or this script.

Default: reconstruct financial_highlights_raw.csv from the included original table
snapshots. Online flags refresh selected extracts to a separate output directory.
Use a new directory to preserve the submitted, checksum-verified data vintage.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from io import StringIO, BytesIO
import json
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
SOURCE_DATA = ROOT / 'data'
HEADERS = {'User-Agent': 'CFM301 university coursework public-data research research@example.com'}


def normalize(value):
    return re.sub(r'\s+', ' ', str(value)).strip()


def fetch(url):
    for attempt in range(3):
        response = requests.get(url, headers=HEADERS, timeout=60)
        if response.ok:
            time.sleep(.25)
            return response.content
        time.sleep(2 * (attempt + 1))
    response.raise_for_status()


def rebuild_highlights(output):
    """No hand-entered expense histories: parse the original selected table rows."""
    snapshots = json.loads((SOURCE_DATA / 'financial_highlights_sources.json').read_text())
    funds = pd.read_csv(SOURCE_DATA / 'funds.csv').set_index('ticker')
    records = []
    percent_pattern = r'\(?\s*-?(?:\d+(?:\.\d+)?|\.\d+)\s*\)?\s*%'
    for source in snapshots:
        ticker = source['ticker']
        text = normalize(source['table_text'])
        if str(source['file']).startswith(('80257_', '902259_')):
            years = [2000 + int(y) for y in re.findall(r'12/31/(\d\d)', text[:250])]
        else:
            years = [int(y) for y in re.findall(r'\b20\d{2}\b', text[:250])]
        years = list(dict.fromkeys(years))
        if len(years) != 5:
            raise ValueError(f'Inspect year headers: {source["source_id"]}')
        rowmap = {}
        for row in source['rows']:
            cells = [normalize(c) for c in row.split('|')]
            if cells and cells[0]:
                rowmap[cells[0]] = ' '.join(c for c in cells[1:] if c)

        def row_containing(*terms):
            return next(((label, values) for label, values in rowmap.items()
                         if all(term.lower() in label.lower() for term in terms)), ('', ''))

        expense = row_containing('net of all reductions')
        if not expense[0]:
            expense = row_containing('Net expenses after waivers')
        if not expense[0]:
            expense = row_containing('Ratio of Total Expenses')
        turnover = row_containing('turnover')
        returns = row_containing('total return')
        assets = row_containing('net assets', 'end of period')

        def percentages(value):
            value = value.replace('–', '-').replace('−', '-').replace('—', '-')
            return re.findall(percent_pattern, value)

        expense_values = percentages(expense[1])
        return_values = percentages(returns[1])
        turnover_values = percentages(turnover[1])
        asset_values = re.findall(r'\d[\d,]*(?:\.\d+)?', assets[1])
        if not all(len(values) == 5 for values in [expense_values, return_values, asset_values]):
            raise ValueError(f'Inspect numeric row structure: {source["source_id"]}')
        if len(turnover_values) != 5:
            turnover_values = [''] * 5
        asset_label = assets[0].lower()
        multiplier = (1e6 if 'million' in asset_label else
                      1e3 if 'thousand' in asset_label or '000 omitted' in asset_label else 1.)
        for i, year in enumerate(years):
            if year < 2016:
                continue
            records.append(dict(ticker=ticker, fiscal_year=year,
                fiscal_month=int(funds.loc[ticker, 'fiscal_month']),
                expense_raw=expense_values[i], turnover_raw=turnover_values[i],
                reported_return_raw=return_values[i], assets_raw=asset_values[i],
                assets_multiplier=multiplier, source_id=source['source_id'],
                filing_date=source['filing_date']))
    frame = pd.DataFrame(records)
    frame.to_csv(output / 'financial_highlights_raw.csv', index=False)
    original = pd.read_csv(SOURCE_DATA / 'financial_highlights_raw.csv', keep_default_na=False)
    pd.testing.assert_frame_equal(frame.fillna(''), original, check_dtype=False)
    print(f'Rebuilt {len(frame)} financial-highlight rows; identical to submitted raw extract.')


def refresh_market(output):
    funds = pd.read_csv(SOURCE_DATA / 'funds.csv')

    def get_fund(ticker):
        request = requests.Request('GET', f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}',
            params={'period1': 1417392000, 'period2': 1767225600,
                    'interval': '1d', 'events': 'div,splits,capitalGains'}).prepare()
        chart = json.loads(fetch(request.url))['chart']
        if not chart.get('result'):
            raise ValueError(f'Yahoo returned no usable data for {ticker}: {chart.get("error")}')
        result = chart['result'][0]
        dates = (pd.to_datetime(result['timestamp'], unit='s', utc=True)
                 .tz_convert('America/New_York').tz_localize(None).normalize())
        navs = result['indicators']['quote'][0]['close']
        adjusted = result['indicators']['adjclose'][0]['adjclose']
        daily = [dict(ticker=ticker, date=str(date.date()), nav=navs[i], adj_close=adjusted[i])
                 for i, date in enumerate(dates) if str(date.date()) >= '2014-12-31']
        events = []
        for kind, values in result.get('events', {}).items():
            for event in values.values():
                date = (pd.to_datetime(event['date'], unit='s', utc=True)
                        .tz_convert('America/New_York').date())
                if str(date) < '2015-01-01':
                    continue
                events.append(dict(ticker=ticker, date=str(date), event=kind,
                    amount=event.get('amount'), numerator=event.get('numerator'),
                    denominator=event.get('denominator')))
        return daily, events

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(get_fund, funds.ticker))
    pd.DataFrame([row for daily, _ in results for row in daily]).to_csv(output/'yahoo_daily.csv', index=False)
    pd.DataFrame([row for _, events in results for row in events]).to_csv(output/'yahoo_actions.csv', index=False)
    print('Refreshed Yahoo extracts. Revalidate returns before adopting a new vintage.')


def refresh_factors(output):
    source = json.loads((SOURCE_DATA/'sources.json').read_text())['factors']

    def read_factor(url, columns):
        with ZipFile(BytesIO(fetch(url))) as archive:
            lines = archive.read(archive.namelist()[0]).decode('utf-8-sig').splitlines()
        rows = [row for row in lines if re.match(r'^\d{6},', row)]
        frame = pd.read_csv(StringIO('\n'.join(rows)), header=None,
                            names=['month']+columns, dtype={'month': str})
        return frame.loc[frame.month.between('201601', '202512')]

    ff = read_factor(source['ff3'], ['Mkt_RF', 'SMB', 'HML', 'RF'])
    mom = read_factor(source['momentum'], ['Mom'])
    ff.merge(mom, on='month', validate='one_to_one').to_csv(output/'factors_percent.csv', index=False)
    print('Refreshed factor extracts; the live library vintage may differ from the submission.')


def refresh_flows(output):
    seed = pd.read_csv(SOURCE_DATA/'sec_quarterly_series_assets.csv')
    funds = pd.read_csv(SOURCE_DATA/'funds.csv').set_index('ticker')
    flows, assets, returns = [], [], []

    def get_filing(row):
        return row, ET.fromstring(fetch(row.source_url))

    with ThreadPoolExecutor(max_workers=2) as pool:
        filings = list(pool.map(get_filing, seed.itertuples()))
    for row, root in filings:
        def find(tag):
            return next(n for n in root.iter() if n.tag.split('}')[-1] == tag)
        assert find('seriesId').text == funds.loc[row.ticker, 'series_id']
        end = pd.Period(find('repPdDate').text, freq='M')
        assets.append(dict(ticker=row.ticker, series_id=row.series_id,
            date=str(end.to_timestamp('M').date()), net_assets_usd=float(find('netAssets').text),
            source_url=row.source_url))
        for i, tag in enumerate(['mon1Flow', 'mon2Flow', 'mon3Flow']):
            node = find(tag)
            flows.append(dict(ticker=row.ticker, series_id=row.series_id, month=str(end-2+i),
                quarter_end=str(end), sales_usd=node.attrib['sales'], redemptions_usd=node.attrib['redemption'],
                reinvestment_usd=node.attrib['reinvestment'], source_url=row.source_url))
        for node in root.iter():
            if node.tag.split('}')[-1] == 'monthlyTotReturn' and node.attrib.get('classId') == funds.loc[row.ticker, 'class_id']:
                for i, key in enumerate(['rtn1', 'rtn2', 'rtn3']):
                    returns.append(dict(ticker=row.ticker, class_id=node.attrib.get('classId'),
                        month=str(end-2+i), reported_return_pct=node.attrib[key], source_url=row.source_url))
    pd.DataFrame(flows).to_csv(output/'sec_reported_monthly_flows.csv', index=False)
    pd.DataFrame(assets).to_csv(output/'sec_quarterly_series_assets.csv', index=False)
    pd.DataFrame(returns).to_csv(output/'sec_monthly_class_returns.csv', index=False)
    print('Refreshed the fixed set of N-PORT extracts; preserve raw redemption signs for the notebook audit.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'source_rebuild')
    parser.add_argument('--refresh-market', action='store_true')
    parser.add_argument('--refresh-factors', action='store_true')
    parser.add_argument('--refresh-flows', action='store_true')
    args = parser.parse_args()
    if args.output_dir.resolve() == SOURCE_DATA.resolve():
        parser.error('Choose a separate output directory to preserve the submitted data vintage.')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rebuild_highlights(args.output_dir)
    if args.refresh_market:
        refresh_market(args.output_dir)
    if args.refresh_factors:
        refresh_factors(args.output_dir)
    if args.refresh_flows:
        refresh_flows(args.output_dir)
    print('Output:', args.output_dir)


if __name__ == '__main__':
    main()
