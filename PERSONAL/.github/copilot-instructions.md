## Copilot instructions for this workspace

This repository is not a traditional code project. It's a personal documents workspace (images, scanned PDFs, IDs, and a few data files). These instructions tell an AI agent how to be useful and safe here.

Key facts discovered
- Root folder: `PERSONAL/` — contains many images, PDFs, and a small CSV: `nutrition.csv`.
- Subfolders of interest: `ID-BACK/`, `ID-FRONT/`, `Pictures/`, `Saved Pictures/` — these contain scanned IDs and many photos.
- Sensitive files: many personal IDs and certificates (e.g., files with names containing `ID`, `passport`, `birth cert`, `death cert`, `signature`). Treat these as sensitive.

What agents should do first (read-only discovery)
- Run a filename search for keywords: `ID`, `passport`, `birth`, `death`, `certificate`, `signature`, `nutrition.csv` and inspect file metadata only.
- Open `nutrition.csv` for schema inspection (it's located at `PERSONAL/nutrition.csv`). Prefer read-only operations and propose changes before editing.
- When encountering PDFs or images, prefer to extract text via OCR only after asking the user for permission.

Safe defaults and hard constraints
- Never upload or exfiltrate any file contents to external services without explicit user approval.
- Do not modify or move original files unless the user explicitly asks. For proposed edits, create copies under a `work/` or `staging/` folder and explain the changes.
- Assume files named with `ID`, `passport`, `birth`, `death`, `signature` are highly sensitive. Ask before any processing that could expose contents.

Patterns and conventions found (examples)
- Scanned front/back IDs grouped into `ID-FRONT/` and `ID-BACK/` folders. Example: `ID FRONT_page-0001.jpg` and `ID BACK_page-0001.jpg`.
- Multiple image collections are grouped under `Pictures/` and `Saved Pictures/` with subfolders like `bouncing baby boy-seth(davdee)/`.
- Document filenames often include descriptive words (e.g., `faith death cert.pdf`, `EPP1-ERTO8JAQ-Passport Application Form.pdf`, `signature.jpg`) — rely on these tokens for search and classification.

No build/test/deploy workflows detected
- This workspace contains no package manifests, build scripts, or test runners. There are no obvious commands to build or run code. If you need to add scripts, propose them and ask where to place them.

How to handle common tasks (concise examples)
- Inspect `nutrition.csv`: open read-only, infer delimiter and columns, and report a sample (first 10 rows) and inferred schema.
- Searching: prefer filename token searches (grep-style) over full-content scans for large binaries. Example tokens: `passport|birth|death|ID|signature|nutrition`.
- Converting PDFs/images: recommend lossless, non-destructive workflows. Example: create `work/ocr/` and place OCR outputs there, do not overwrite originals.

When to ask the user (must-ask situations)
- Any action that reads, transcribes, or shares content from sensitive files.
- Any file modification, deletion, or bulk rename.
- Uploading files to cloud services or third-party OCR APIs.

Reference files (examples to inspect)
- `PERSONAL/nutrition.csv` — small data file, safe to analyze with user approval.
- `ID-FRONT/ID FRONT_page-0001.jpg` and `ID-BACK/ID BACK_page-0001.jpg` — represent scanned IDs; treat as sensitive.
- `passport.JPG`, `faith death cert.pdf`, `signature.jpg` — more sensitive documents referenced by filename.

If you add automation (recommended minimal rules)
- Create a top-level `work/` folder for intermediate outputs and keep originals immutable.
- Add a short `README.md` describing any added scripts and their expected inputs/outputs.

Scripts & workflows (what to run and why)
- `scripts/analyze_nutrition.py` — quick read-only inspector. Use to infer delimiter, list columns, show sample rows and simple numeric summaries. Runs without writing files. Example:
	- `python3 scripts/analyze_nutrition.py --input PERSONAL/nutrition.csv`
- `scripts/clean_aggregate_nutrition.py` — cleans `period` tokens (e.g., `23-Jan` → `2023-01`), strips BOM from header, and writes non-destructive outputs to an output folder (default: `PERSONAL/work`). Outputs:
	- `cleaned_nutrition.csv` (normalized CSV)
	- `aggregate_by_county.csv` (sums per county)
	- `aggregate_by_period.csv` (sums per normalized period)
	Example:
	- `python3 scripts/clean_aggregate_nutrition.py --input PERSONAL/nutrition.csv --outdir PERSONAL/work`
- `scripts/plot_nutrition.py` — reads `work/cleaned_nutrition.csv` and produces simple PNG plots under `work/plots/` (time series for a county and top-10 counties bar chart). Requires `matplotlib`.
	Example:
	- `python3 scripts/plot_nutrition.py --cleaned PERSONAL/work/cleaned_nutrition.csv --outdir PERSONAL/work/plots --county "Nairobi County" --col "Total Dewormed"`

-Notes:
- All scripts are CLI-first and non-destructive. They accept `--input`/`--outdir` (or short flags) so you can run them on copies or different folders.
- Sensitive-file rule still applies: scripts operate on CSVs only; do not run any OCR or image-processing scripts on scanned IDs without explicit approval.

Script reference (detailed)
- `scripts/analyze_nutrition.py`
	- Purpose: quick, read-only inspection of a CSV to infer delimiter, list columns, sample rows, and simple numeric summaries.
	- Flags: `--input` / `-i` (path to CSV). Default: `PERSONAL/nutrition.csv`.
	- Writes: none (prints to stdout).
	- Example: `python3 scripts/analyze_nutrition.py -i PERSONAL/nutrition.csv`

- `scripts/clean_aggregate_nutrition.py`
	- Purpose: normalize header (remove BOM), normalize `period` tokens like `23-Jan` → `2023-01`, and produce CSV aggregates.
	- Flags: `--input` / `-i` (input CSV), `--outdir` / `-o` (output directory). Defaults: `PERSONAL/nutrition.csv`, `PERSONAL/work`.
	- Writes (to outdir): `cleaned_nutrition.csv`, `aggregate_by_county.csv`, `aggregate_by_period.csv`.
	- Notes: sums numeric columns and records row counts. Empty cells are treated as missing (ignored in sums).
	- Example: `python3 scripts/clean_aggregate_nutrition.py -i PERSONAL/nutrition.csv -o PERSONAL/work`

- `scripts/plot_nutrition.py`
	- Purpose: generate quick PNG plots from `work/cleaned_nutrition.csv` (time series for a single county and top-10 counties bar chart).
	- Flags: `--cleaned` / `-c` (path to cleaned CSV), `--outdir` / `-o` (plot output dir), `--county` (county name), `--col` (numeric column). Defaults target `Total Dewormed` and `Nairobi County`.
	- Writes (to outdir): `time_series_{county}_{col}.png`, `top_counties_{col}.png`.
	- Requirements: `matplotlib` must be installed. Install with `python3 -m pip install matplotlib` or use the environment's package manager.
		- Example: `python3 scripts/plot_nutrition.py -c PERSONAL/work/cleaned_nutrition.csv -o PERSONAL/work/plots --county "Nairobi County" --col "Total Dewormed"`

Safety and reproducibility notes
- Scripts are intentionally simple and use CSV summation. They do not access images or PDFs and will not upload data externally.
- For reproducible runs, consider creating a virtual environment and recording the dependency (`matplotlib`) in a `requirements.txt` if you intend to share scripts.

Questions for maintainers
- Do you want automated OCR or transcript extraction for the PDFs/images, or should everything be manual/approval-based?
- Would you like scripts for CSV analysis (e.g., `scripts/analyze_nutrition.py`) placed in the repo?

If something here looks incorrect or you want more automation, reply with what operations you'd like automated and I'll propose a safe implementation.
