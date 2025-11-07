#!/usr/bin/env python3
"""Clean and aggregate PERSONAL/nutrition.csv.

Writes cleaned_nutrition.csv and two aggregate CSVs under PERSONAL/work/.
This script is non-destructive.
"""
import csv
import os
import argparse
from collections import defaultdict
from datetime import datetime

# keep defaults short and relative to repository root
ROOT = "PERSONAL"


def parse_args():
    p = argparse.ArgumentParser(description="Clean and aggregate a CSV")
    p.add_argument(
        "--input",
        "-i",
        help="Path to input CSV",
        default=os.path.join(ROOT, "nutrition.csv"),
    )
    p.add_argument(
        "--outdir",
        "-o",
        help="Output directory",
        default=os.path.join(ROOT, "work"),
    )
    return p.parse_args()


def normalize_header(header):
    # remove BOM and trim
    out = []
    for h in header:
        # decode/strip in two steps to avoid a very long source line
        tmp = h.encode("utf-8").decode("utf-8")
        v = tmp.strip().lstrip("\ufeff")
        out.append(v)
    return out


def parse_period(token):
    # token examples: '23-Jan', '22-Feb'
    token = token.strip()
    if not token:
        return ""
    # assume tokens like '23-Jan' or '22-Jan' map to 2023/2022
    parts = token.split("-")
    if len(parts) != 2:
        # try to parse with datetime as fallback
        for fmt in ("%Y-%m-%d", "%Y-%m", "%d/%m/%Y"):
            try:
                return datetime.strptime(token, fmt).strftime("%Y-%m")
            except Exception:
                pass
        return token
    yy, mon = parts
    # normalize year and month to numbers
    try:
        # if yy is 4-digit year, use directly
        if len(yy) == 4:
            year_full = int(yy)
        else:
            year = int(yy)
            year_full = 2000 + year
    except Exception:
        return token

    # month can be short name (Jan) or numeric '05'
    month_num = None
    if mon.isdigit():
        try:
            month_num = int(mon)
        except Exception:
            month_num = None
    else:
        try:
            mon_dt = datetime.strptime(mon, "%b")
            month_num = mon_dt.month
        except Exception:
            try:
                mon_dt = datetime.strptime(mon, "%B")
                month_num = mon_dt.month
            except Exception:
                month_num = None

    if month_num is None:
        return f"{year_full}-{mon}"
    return f"{year_full}-{month_num:02d}"


def to_number(s):
    s = s.strip()
    if s == "":
        return None
    try:
        # handle floats like '1299.3'
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        try:
            return float(s.replace(",", ""))
        except Exception:
            return None


def main(input_path=None, outdir=None):
    # Allow callers (tests) to pass input_path and outdir directly.
    if input_path is None or outdir is None:
        args = parse_args()
        input_path = input_path or args.input
        outdir = outdir or args.outdir

    SRC = input_path
    OUT_DIR = outdir
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(SRC, newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample)
        reader = csv.reader(f, dialect)
        rows = list(reader)

    header = normalize_header(rows[0])
    data = rows[1:]

    # prepare outputs
    cleaned_path = os.path.join(OUT_DIR, "cleaned_nutrition.csv")
    agg_county_path = os.path.join(OUT_DIR, "aggregate_by_county.csv")
    agg_period_path = os.path.join(OUT_DIR, "aggregate_by_period.csv")

    numeric_idx = []
    for i, h in enumerate(header):
        if h.lower() in ("period", "county"):
            continue
        numeric_idx.append(i)

    # Write cleaned CSV with normalized period
    with open(cleaned_path, "w", newline="") as outf:
        w = csv.writer(outf)
        w.writerow(header)
        for r in data:
            if len(r) < len(header):
                r = r + [""] * (len(header) - len(r))
            row = list(r[: len(header)])
            # normalize period
            row[0] = parse_period(row[0])
            # trim county
            row[1] = row[1].strip()
            w.writerow(row)

    # Aggregate by county and period
    agg_county = defaultdict(lambda: [0.0] * len(numeric_idx))
    agg_period = defaultdict(lambda: [0.0] * len(numeric_idx))
    counts_county = defaultdict(int)
    counts_period = defaultdict(int)

    with open(cleaned_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        for r in reader:
            period = r[0]
            county = r[1]
            for j, col_idx in enumerate(numeric_idx):
                val = to_number(r[col_idx])
                if val is not None:
                    agg_county[county][j] += val
                    agg_period[period][j] += val
            counts_county[county] += 1
            counts_period[period] += 1

    # write aggregated files
    numeric_headers = [header[i] for i in numeric_idx]
    with open(agg_county_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["county", "rows"] + numeric_headers)
        for county, sums in sorted(agg_county.items()):
            w.writerow([county, counts_county[county]] + sums)

    with open(agg_period_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["period", "rows"] + numeric_headers)
        for period, sums in sorted(agg_period.items()):
            w.writerow([period, counts_period[period]] + sums)

    print("Wrote cleaned CSV ->", cleaned_path)
    print("Wrote aggregation by county ->", agg_county_path)
    print("Wrote aggregation by period ->", agg_period_path)


if __name__ == "__main__":
    main()
