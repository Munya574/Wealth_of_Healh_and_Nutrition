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
2. Download the NHANES component files (`.XPT`, or `.csv` if converted).
3. Place them in your local `data/raw/` folder (this folder is gitignored, so the
   files stay on your machine only — never commit them).

If a file is missing from the Drive, it can also be re-downloaded from the CDC
portal linked above.

Cleaned and merged output produced by the `src/` pipeline is written to:

```
data/processed/
```

Both folders stay on your machine only.

## Component files needed

<!-- PLACEHOLDER — confirm exact NHANES file codes against the Drive folder. -->
<!-- Base names below are the standard NHANES codes; each exists per cycle with -->
<!-- the _H / _I / _J suffix (e.g. DEMO_H, DEMO_I, DEMO_J). VERIFY before use. -->

We merge NHANES components on the respondent sequence number **`SEQN`**. Base file
codes below are the standard NHANES names — each should exist once per cycle with
the `_H` / `_I` / `_J` suffix. **Verify these against the actual Drive contents and
tick them off:**

| Component     | Base file code(s)                                  | Cycles      | Key variables (notes)                        |
|---------------|----------------------------------------------------|-------------|----------------------------------------------|
| Demographics  | `DEMO`                                              | H / I / J   | age, sex, race/ethnicity, income, weights    |
| Dietary       | `DR1TOT`, `DR2TOT`                                  | H / I / J   | nutrient intake (day 1 / day 2)              |
| Examination   | `BMX`, `BPX`                                        | H / I / J   | body measures, waist circ., blood pressure   |
| Laboratory    | `GLU`, `GHB`, `TCHOL`, `HDL`, `TRIGLY`, `INS`      | H / I / J   | glucose, HbA1c, lipids, insulin              |
| Questionnaire | `PAQ`, `DBQ`, `SMQ`, `ALQ`                          | H / I / J   | physical activity, diet behavior, smoking, alcohol |

<!-- TODO: after confirming against the Drive, replace this comment with the
     exact filenames present, e.g.:
     - DEMO_H.XPT, DEMO_I.XPT, DEMO_J.XPT
     - DR1TOT_H.XPT, ...
-->
