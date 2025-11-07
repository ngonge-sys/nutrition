This folder contains outputs produced by the nutrition scripts.

Files produced by `scripts/clean_aggregate_nutrition.py`:

- `cleaned_nutrition.csv` — cleaned, normalized CSV. Header normalized, `period` column converted to `YYYY-MM` where possible.
- `aggregate_by_county.csv` — sums of numeric columns per county, plus `rows` (number of source rows aggregated).
- `aggregate_by_period.csv` — sums of numeric columns per period (YYYY-MM), plus `rows`.

How to run (CLI examples):

```bash
# analyze CSV (prints summary)
python3 scripts/analyze_nutrition.py --input PERSONAL/nutrition.csv

# clean and aggregate to the default work/ folder
python3 scripts/clean_aggregate_nutrition.py --input PERSONAL/nutrition.csv --outdir PERSONAL/work

# specify custom paths
python3 scripts/clean_aggregate_nutrition.py -i PERSONAL/nutrition.csv -o PERSONAL/my_work
```

Notes:
- Scripts are non-destructive and will create the output folder if it does not exist.
- Period parsing assumes two-digit year tokens map to 2000+ (e.g., `23-Jan` → `2023-01`). If you need different logic, update the script or ask for changes.
