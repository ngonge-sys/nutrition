#!/usr/bin/env python3
import csv
import os
import argparse
from collections import Counter
from statistics import mean, median


def is_number(s):
    try:
        float(s)
        return True
    except Exception:
        return False


def summarize_column(values):
    non_empty = [v for v in values if v != ""]
    n = len(values)
    ne = len(non_empty)
    empty = n - ne
    sample = non_empty[:5]
    uniq = len(set(non_empty))
    numeric_vals = [float(v) for v in non_empty if is_number(v)]
    stats = {}
    stats["count"] = n
    stats["non_empty"] = ne
    stats["empty"] = empty
    stats["unique_non_empty"] = uniq
    stats["sample_non_empty"] = sample
    if numeric_vals:
        stats["is_numeric"] = True
        stats["min"] = min(numeric_vals)
        stats["max"] = max(numeric_vals)
        stats["mean"] = mean(numeric_vals)
        stats["median"] = median(numeric_vals)
    else:
        stats["is_numeric"] = False
        stats["top_values"] = Counter(non_empty).most_common(5)
    return stats


def main():
    p = argparse.ArgumentParser(
        description="Analyze a nutrition CSV (prints column summaries)"
    )
    p.add_argument(
        "--input",
        "-i",
        help="Path to CSV",
        default=os.path.join("PERSONAL", "nutrition.csv"),
    )
    args = p.parse_args()

    CSV_PATH = args.input
    with open(CSV_PATH, newline="") as f:
        # try to sniff delimiter
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample)
        reader = csv.reader(f, dialect)
        rows = list(reader)

    if not rows:
        print("Empty CSV")
        return

    header = rows[0]
    data = rows[1:]
    print("CSV path:", CSV_PATH)
    # show detected delimiter
    det = dialect.delimiter
    print("Detected delimiter:", repr(det))
    # print column count and a short preview of columns
    # show only first few names to avoid very long output lines
    hdr_count = "Columns ({})".format(len(header))
    hdr_preview = str(header[:5])
    print(hdr_count + ":", hdr_preview)
    print("Total rows (excluding header):", len(data))
    print()

    cols = {i: [] for i in range(len(header))}
    for r in data:
        # ensure row has right length
        if len(r) < len(header):
            r = r + [""] * (len(header) - len(r))
        for i, v in enumerate(r[: len(header)]):
            cols[i].append(v.strip())

    for i, col in enumerate(header):
        stats = summarize_column(cols[i])
        print("---")
        print("Column: {} (index {})".format(col, i))
        # split non-empty summary across two smaller pieces
        ne_part = "Non-empty: {}/{}".format(stats["non_empty"], stats["count"])
        uniq_part = "Unique non-empty: {}".format(stats["unique_non_empty"])
        print("  ", ne_part + "  " + uniq_part)
        print("  Sample non-empty values:", stats["sample_non_empty"])
        if stats["is_numeric"]:
            numeric_line_a = "Numeric: min={:.3f}  max={:.3f}".format(
                stats["min"], stats["max"]
            )
            numeric_line_b = "Mean/median: {:.3f} / {:.3f}".format(
                stats["mean"], stats["median"]
            )
            # print numeric stats on two lines to avoid long single-line output
            print(numeric_line_a)
            print(numeric_line_b)
        else:
            print("  Top values:", stats.get("top_values"))


if __name__ == "__main__":
    main()
