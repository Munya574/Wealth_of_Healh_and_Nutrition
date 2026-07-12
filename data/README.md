# Data

> **Raw data is NOT committed to git.** The `data/raw/` and `data/processed/`
> folders are gitignored. Each teammate downloads the raw files locally.

## Cycles used

This project pools **three NHANES cycles, 2013–2018**:

| Cycle | Years     | File suffix |
|-------|-----------|-------------|
| H     | 2013–2014 | `_H`        |
| I     | 2015–2016 | `_I`        |
| J     | 2017–2018 | `_J`        |

When pooling cycles, concatenate the matching component across years (e.g.,
`DEMO_H`, `DEMO_I`, `DEMO_J`) and account for the survey design / weights per the
[NHANES analytic guidelines](https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx).

## Where the data comes from

Canonical source is the CDC NHANES portal:

**https://wwwn.cdc.gov/nchs/nhanes/Default.aspx**

### Team access (start here)

The compiled 2013–2018 datasets are in our shared Google Drive folder:

**https://drive.google.com/drive/folders/1ajcnnocEQEbuDb61FQ4zF_e1NeFUYVpD**

To get set up:

1. Open the folder above. If you can't access it, ask a teammate to share it with
   your Google account.
2. Download the NHANES component files (`.xpt`).
3. Place them in your local `data/raw/` folder, organized by cycle (see layout
   below). This folder is gitignored, so the files stay on your machine only —
   never commit them.

If a file is missing from the Drive, it can also be re-downloaded from the CDC
portal linked above.

Cleaned and merged output produced by the `src/` pipeline is written to:

```
data/processed/
```

Both folders stay on your machine only.

## Local layout

Files are organized into one subfolder per cycle:

```
data/raw/
├── 2013-2014/   # *_H.xpt
├── 2015-2016/   # *_I.xpt
└── 2017-2018/   # *_J.xpt
```

## Component files

We merge NHANES components on the respondent sequence number **`SEQN`**. The
following 13 components are present in **each** cycle (`_H` / `_I` / `_J` suffix):

| Component     | File code | Group         | Key variables (notes)                              |
|---------------|-----------|---------------|----------------------------------------------------|
| Demographics  | `DEMO`    | Demographics  | age, sex, race/ethnicity, income, survey weights   |
| Dietary       | `DR1TOT`  | Dietary       | day-1 total nutrient intake                        |
| Body measures | `BMX`     | Examination   | BMI, **waist circumference** (`BMXWAIST`)          |
| Blood pressure| `BPX`     | Examination   | systolic / diastolic BP                            |
| HbA1c         | `GHB`     | Laboratory    | glycohemoglobin (glycemic marker)                  |
| HDL           | `HDL`     | Laboratory    | HDL cholesterol                                    |
| Total chol.   | `TCHOL`   | Laboratory    | total cholesterol                                  |
| Triglycerides | `TRIGLY`  | Laboratory    | triglycerides (+ LDL)                              |
| Phys. activity| `PAQ`     | Questionnaire | physical activity                                  |
| Alcohol       | `ALQ`     | Questionnaire | alcohol use                                        |
| Smoking       | `SMQ`     | Questionnaire | smoking status                                     |
| Sleep         | `SLQ`     | Questionnaire | sleep duration / disorders                         |
| Food security | `FSQ`     | Questionnaire | household food security                            |

### Notes for the metabolic-composite target

The panel supports a metabolic-syndrome-style composite from: **waist** (`BMX`),
**triglycerides** & **HDL** (`TRIGLY`, `HDL`), **blood pressure** (`BPX`), and a
**glycemic marker** (`GHB` / HbA1c). Note there is **no fasting glucose (`GLU`) or
insulin (`INS`) file** — HbA1c stands in as the glycemic component. Only day-1
dietary (`DR1TOT`) is included (no `DR2TOT`).
