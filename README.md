# Nutrition data tools

![CI](https://github.com/ngonge-sys/nutrition/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2C3.10%2C3.11-blue)

Small personal project to analyze and plot nutrition CSV data found under `PERSONAL/nutrition.csv`.

## What is included

- `PERSONAL/scripts/analyze_nutrition.py` — quick CSV inspector (prints column summaries).
- `PERSONAL/scripts/clean_aggregate_nutrition.py` — cleans the CSV (normalizes `period`), writes `PERSONAL/work/cleaned_nutrition.csv` and aggregates by county/period.
- `PERSONAL/scripts/plot_nutrition.py` — generates PNG plots in `PERSONAL/work/plots/` (time series and top counties).
- `tests/test_nutrition.py` — small pytest suite covering parsing and aggregation.
- `.github/workflows/ci.yml` — CI that runs black, flake8, and pytest.

## Quick usage

All scripts accept `--input`/`--outdir` style flags. Examples:

```bash
python3 PERSONAL/scripts/clean_aggregate_nutrition.py \
  --input PERSONAL/nutrition.csv --outdir PERSONAL/work

python3 PERSONAL/scripts/plot_nutrition.py \
  --cleaned PERSONAL/work/cleaned_nutrition.csv --outdir PERSONAL/work/plots
```

Run the tests:

```bash
python3 -m pytest -q
```

## Notes

- Non-destructive: outputs are written into `PERSONAL/work/` by default.
- The repository includes formatting and linting (black + flake8) in CI.

## Contributing

Open a pull request against `fix/linting-ci` or the main branch.
