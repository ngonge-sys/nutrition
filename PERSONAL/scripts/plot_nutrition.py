#!/usr/bin/env python3
"""Plot cleaned nutrition CSV into PNGs under work/plots/.

Generates a time-series per-county and a top-counties bar chart.
"""
import csv
import os
import argparse
from collections import defaultdict
from datetime import datetime

ROOT = "PERSONAL"
DEFAULT_CLEANED = os.path.join(ROOT, "work", "cleaned_nutrition.csv")
DEFAULT_PLOTS = os.path.join(ROOT, "work", "plots")


def parse_args():
    p = argparse.ArgumentParser(description="Plot cleaned nutrition CSV")
    p.add_argument(
        "--cleaned", "-c", default=DEFAULT_CLEANED, help="Path to cleaned CSV"
    )
    p.add_argument(
        "--outdir", "-o", default=DEFAULT_PLOTS, help="Output plot directory"
    )
    p.add_argument(
        "--county",
        default="Nairobi County",
        help="County to time-series (default: Nairobi County)",
    )
    p.add_argument(
        "--col",
        default="Total Dewormed",
        help="Numeric column to plot (default: Total Dewormed)",
    )
    return p.parse_args()


def to_number(s):
    s = s.strip()
    if s == "":
        return None
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        try:
            return float(s.replace(",", ""))
        except Exception:
            return None


def read_cleaned(path):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader]
    return header, rows


def aggregate_for_county(header, rows, county, colname):
    # returns list of (period_datetime, value)
    idx_period = header.index("period")
    idx_county = header.index("county")
    try:
        idx_col = header.index(colname)
    except ValueError:
        raise

    by_period = defaultdict(list)
    for r in rows:
        p = r[idx_period]
        c = r[idx_county]
        if c != county:
            continue
        v = to_number(r[idx_col])
        if v is None:
            continue
        # parse YYYY-MM
        try:
            dt = datetime.strptime(p, "%Y-%m")
        except Exception:
            # skip unparsable
            continue
        by_period[dt].append(v)

    # average per period
    out = []
    for dt in sorted(by_period.keys()):
        vals = by_period[dt]
        out.append((dt, sum(vals)))
    return out


def aggregate_by_county(header, rows, colname):
    idx_county = header.index("county")
    idx_col = header.index(colname)
    sums = defaultdict(float)
    for r in rows:
        c = r[idx_county]
        v = to_number(r[idx_col])
        if v is None:
            continue
        sums[c] += v
    return sums


def make_plots(cleaned, outdir, county, colname):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print(
            "Matplotlib not available. Please install matplotlib and re-run: "
            "pip install matplotlib"
        )
        raise

    header, rows = read_cleaned(cleaned)
    # Ensure outdir
    os.makedirs(outdir, exist_ok=True)

    # Time series for county
    series = aggregate_for_county(header, rows, county, colname)
    if series:
        xs = [d for d, v in series]
        ys = [v for d, v in series]
        plt.figure(figsize=(10, 4))
        plt.plot(xs, ys, marker="o")
        plt.title(f"{colname} over time — {county}")
        plt.xlabel("Period")
        plt.ylabel(colname)
        plt.grid(True)
        fname = (
            f"time_series_{county.replace(' ', '_')}_"
            f"{colname.replace(' ', '_')}.png"
        )
        out_path = os.path.join(outdir, fname)
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
        print("Wrote", out_path)
    else:
        print("No data for county", county)

    # Top counties bar chart
    sums = aggregate_by_county(header, rows, colname)
    # sort top 10
    items = sorted(sums.items(), key=lambda x: x[1], reverse=True)[:10]
    if items:
        names = [n for n, v in items]
        vals = [v for n, v in items]
        plt.figure(figsize=(10, 6))
        plt.barh(names[::-1], vals[::-1])
        plt.title(f"Top 10 counties by {colname}")
        plt.xlabel(colname)
        fname = f"top_counties_{colname.replace(' ', '_')}.png"
        out_path = os.path.join(outdir, fname)
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
        print("Wrote", out_path)
    else:
        print("No county aggregates found")


def main():
    args = parse_args()
    make_plots(args.cleaned, args.outdir, args.county, args.col)


if __name__ == "__main__":
    main()
