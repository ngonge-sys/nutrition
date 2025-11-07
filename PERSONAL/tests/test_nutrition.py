import csv
import os
import sys
from pathlib import Path

# ensure repo root is on sys.path so we can import scripts
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.clean_aggregate_nutrition import (  # noqa: E402
    parse_period,
    to_number,
    main as clean_main,
)


def test_parse_period_examples():
    assert parse_period("23-Jan") == "2023-01"
    assert parse_period("22-Feb") == "2022-02"
    assert parse_period("") == ""
    assert parse_period("2023-05") == "2023-05"


def test_to_number_examples():
    assert to_number("123") == 123
    assert to_number("  45.6 ") == 45.6
    assert to_number("") is None
    assert to_number("1,234") == 1234.0


def test_clean_and_aggregate(tmp_path):
    # Create a small CSV
    csv_content = [
        ["period", "county", "Total Dewormed", "diarrhoea cases"],
        ["23-Jan", "A County", "100", "10"],
        ["23-Feb", "A County", "200", "20"],
        ["23-Jan", "B County", "50", "5"],
        ["", "B County", "", "3"],
    ]
    src = tmp_path / "small.csv"
    with open(src, "w", newline="") as f:
        w = csv.writer(f)
        w.writerows(csv_content)

    outdir = tmp_path / "out"
    os.makedirs(outdir, exist_ok=True)

    # Run the cleaner
    clean_main(input_path=str(src), outdir=str(outdir))

    cleaned = outdir / "cleaned_nutrition.csv"
    assert cleaned.exists()

    agg_county = outdir / "aggregate_by_county.csv"
    agg_period = outdir / "aggregate_by_period.csv"
    assert agg_county.exists()
    assert agg_period.exists()

    # Read county aggregate and check sums
    with open(agg_county, newline="") as f:
        r = csv.reader(f)
        header = next(r)
        rows = list(r)
    # header should be ['county','rows','Total Dewormed','diarrhoea cases']
    assert header[0] == "county"
    by_county = {row[0]: [float(x) for x in row[2:]] for row in rows}
    # A County should have Total Dewormed = 300, diarrhoea cases = 30
    assert by_county["A County"][0] == 300.0
    assert by_county["A County"][1] == 30.0
