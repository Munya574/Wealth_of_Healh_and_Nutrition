# Wealth of Health and Nutrition

A team machine-learning project studying **which nutrition and exercise factors
predict metabolic health**, using [NHANES](https://wwwn.cdc.gov/nchs/nhanes/Default.aspx)
(National Health and Nutrition Examination Survey) data from the CDC.

Rather than predicting BMI, we model a **metabolic-health composite target** built
from multiple clinical markers (e.g., glucose/HbA1c, blood pressure, lipids, waist
circumference). The goal is to identify the dietary and physical-activity factors
that most strongly relate to metabolic health.

## Project structure

```
data/
  raw/          # original NHANES .XPT/.csv files (gitignored, download locally)
  processed/    # cleaned/merged output (gitignored)
notebooks/      # Jupyter notebooks for EDA and modeling
src/            # reusable Python modules
  data_loading.py   # load and merge NHANES files on SEQN
  preprocessing.py  # cleaning, column decoding, missing-value handling
  target.py         # build the metabolic-health composite target
  features.py       # feature selection / engineering
```

See [data/README.md](data/README.md) for how to obtain the raw data.

## Setup

1. Create and activate a virtual environment:

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download the raw NHANES files into `data/raw/` (see [data/README.md](data/README.md)).
   The `data/raw/` and `data/processed/` folders are gitignored, so data stays local.

4. Launch Jupyter:
   ```bash
   jupyter notebook
   ```

## Branch workflow

- `main` is **protected** — do not commit directly to it.
- All work happens on **feature branches** created off `main`.
- Open a **pull request** to merge a feature branch back into `main`; get a review before merging.

Suggested starting branches:

```bash
git checkout main && git pull
git checkout -b data-cleaning
git checkout -b feature-modeling
git checkout -b recommendation
git checkout -b eda
```
