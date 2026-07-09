# Wealth of Health and Nutrition

A machine-learning project studying **which nutrition and exercise factors
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

## Running on Google Colab

Colab is convenient because our data already lives in Google Drive — you can mount
it and skip local downloads. Start from [notebooks/00_colab_setup.ipynb](notebooks/00_colab_setup.ipynb),
or run these cells at the top of any notebook:

```python
# 1. Clone the repo (or `git pull` if already cloned)
!git clone https://github.com/<your-org>/Wealth_of_Healh_and_Nutrition.git
%cd Wealth_of_Healh_and_Nutrition

# 2. Install dependencies
!pip install -r requirements.txt

# 3. Mount Google Drive (where the NHANES files live)
from google.colab import drive
drive.mount('/content/drive')

# 4. Point the loaders at the Drive data folder (no download needed)
import os
os.environ["NHANES_RAW_DIR"] = "/content/drive/MyDrive/<path-to-nhanes-folder>"

# 5. Import the project modules
from src import data_loading, preprocessing, target, features
```

Update the clone URL and the Drive path once the repo and shared folder are set.
`src/data_loading.py` reads `NHANES_RAW_DIR` if set, so no code changes are needed
to switch between local and Colab runs.

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
