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

## Data pipeline

Two processed files are produced from the raw NHANES data. **Both are gitignored**
— get them from the shared Google Drive, or regenerate locally:

```bash
python -m src.data_loading    # -> data/processed/nhanes_merged.csv
python -m src.preprocessing   # -> data/processed/nhanes_clean.csv
```

| File | What it is | Use |
|------|-----------|-----|
| `nhanes_merged.csv` | Full raw union of all 13 components across the 3 cycles (29,400 × 502) | source of truth / backup |
| **`nhanes_clean.csv`** | Curated 36-col table: readable names, sleep reconciled across cycles, sentinel codes → blank | **use this for EDA & modeling** |

Key things to know:
- **`uid` is the row key** (`cycle` + `SEQN`). `SEQN` alone is *not* unique across
  cycles, so always key on `uid`.
- **Treat `nhanes_clean.csv` as the frozen shared input.** Don't rebuild the
  pipeline inside each notebook — everyone loads the *same* file so results are
  comparable. If the clean file needs a fix, change it once in `src/` and
  regenerate.
- **~16,500 rows** have all core metabolic markers (waist, HbA1c, HDL, systolic
  BP) — that's the realistic modeling sample. Blank cells elsewhere are expected
  (NHANES doesn't run every test on every person), not errors.

## Running on Google Colab

Colab is convenient because our data already lives in Google Drive — you can mount
it and skip local downloads. Start from [notebooks/00_colab_setup.ipynb](notebooks/00_colab_setup.ipynb),
or run these cells at the top of any notebook:

```python
# 1. Clone the repo (or `git pull` if already cloned)
!git clone https://github.com/Munya574/Wealth_of_Healh_and_Nutrition.git
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

## Notebook workflow

Notebooks live in `notebooks/`. **One notebook per analysis/model** (e.g. a
separate notebook for KNN, LR, RF) so people don't edit the same file and hit
merge conflicts.

**Colab ↔ GitHub:**
- **Open from GitHub:** in Colab, `File → Open notebook → GitHub tab`, pick the repo
  and branch.
- **Save to GitHub:** `File → Save a copy in GitHub` → choose **your feature
  branch** and write a commit message. **Never save to `main`.**
- **Clear outputs before saving/committing** (`Edit → Clear all outputs`) — keeps
  git diffs small and the repo light.

**Every model notebook should:**
1. Load `data/processed/nhanes_clean.csv` (from Drive on Colab).
2. Build the target and train/test split the **same way** (shared setup — see
   `src/target.py`).
3. Differ **only** in the model, so KNN / LR / RF are compared on identical data.

**Adding a notebook you downloaded (not via Colab's GitHub save):**
```bash
git checkout feature-modeling        # your feature branch
# put the .ipynb in notebooks/
git add notebooks/
git commit -m "Add <name> notebook"
git push -u origin feature-modeling
# then open a Pull Request into main on GitHub
```
