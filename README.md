# PNAD — Tableau-ready Export

This repository contains `pnad_analysis.py`, a small script that downloads Brazilian PNAD (trimestral) data, applies English labels and mappings, and produces a CSV file ready for use in BI tools such as Tableau.

## What the script does
- Downloads PNAD trimestral microdata for a given year and quarter (using the `pnadium` package) if a cleaned CSV does not already exist.
- Renames selected variables to English, maps categorical codes to human-readable labels, and filters invalid observations.
- Exports a Tableau-ready CSV with comma delimiters and UTF-8 encoding.

## Requirements
- Python 3.8+
- Packages: `pnadium`, `pandas`, `numpy`

Install dependencies with:

```bash
pip install pnadium pandas numpy
```

## Configuration
Open `pnad_analysis.py` and edit the top-level constants if needed:
- `ANO` — year (default: 2025)
- `TRIMESTRE` — quarter (1..4)
- `NOME_ARQUIVO_CSV` — output CSV filename (script sets a default based on year/quarter)

The script contains a column mapping `MAPA_COLUNAS_EN` that selects and renames PNAD variables to English column names used in the final CSV.

## Usage
From the repository root run:

```bash
python pnad_analysis.py
```

Behavior:
- If the target CSV (`NOME_ARQUIVO_CSV`) does not exist, the script downloads the selected PNAD variables, processes them, and writes the cleaned CSV.
- If the CSV exists, the script loads it and prints a small sample and data types.

## Output (final CSV columns)
The resulting CSV contains these columns (Tableau-friendly):

- `State_Name`: Brazilian state name (English-mapped)
- `State_Code`: numeric IBGE state code
- `Gender`: `Male` / `Female`
- `Age`: age in years
- `Labor_Force_Status`: `Employed` / `Unemployed` / `Out of Labor Force`
- `Employment_Type`: human-readable employment category
- `Economic_Sector`: mapped economic sector description
- `Education_Level`: mapped education attainment
- `Weekly_Hours_Worked`: weekly hours variable (renamed)
- `Monthly_Income`: effective income (renamed)
- `Sampling_Weight`: person sampling weight

## Notes & Troubleshooting
- The CSV is written with `sep=','` and `encoding='utf-8'` for universal Tableau compatibility.
- If you encounter a critical error stating the loaded DataFrame is empty, delete the existing CSV and re-run the script to force a fresh download.
- Network or `pnadium` errors during download will be printed; ensure you have internet access and the `pnadium` package is functional.

## Contact
This README was generated from the contents of `pnad_analysis.py`.
