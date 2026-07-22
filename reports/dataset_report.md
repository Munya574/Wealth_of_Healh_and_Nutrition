# Wealth of Health and Nutrition — Phase 1 Dataset Report

**Dataset version:** `nhanes_clean`  
**Build date:** July 22, 2026  
**Population:** NHANES participants age 20 years or older  
**Cycles:** 2013–2014, 2015–2016, and 2017–2018  
**Status:** Updated cleaned dataset pending team verification

## 1. Purpose and scope

This report documents the Phase 1 data product used by the Wealth of Health and Nutrition project. The project studies how modifiable diet and activity behaviors relate to a measurement-based metabolic-syndrome outcome, while using demographic and access variables to form context-matched peer groups.

The purpose of Phase 1 is to create one adult master dataset that is reproducible, auditable, and safe to use in later modeling. The report distinguishes the master adult population from the smaller samples eligible for the supervised models and the core diet-focused Random Forest. A participant is not removed from the master dataset merely because one model cannot use that participant.

This report covers data assembly, adult filtering, correction of import artifacts, derived blood-pressure and activity fields, dietary recall eligibility, metabolic-component flags, target construction, missingness, exclusions, verification, and current limitations. It does not claim that the models are clinically validated or that unweighted project results represent U.S. population prevalence.

## 2. Source data and cycles

The dataset pools three two-year National Health and Nutrition Examination Survey (NHANES) cycles:

| Cycle | Suffix | Participants before adult filter |
|---|---:|---:|
| 2013–2014 | H | Included in pooled total |
| 2015–2016 | I | Included in pooled total |
| 2017–2018 | J | Included in pooled total |
| **Pooled total** | — | **29,400** |

The team’s original merge used the following NHANES component families:

| Component | File family | Main project use |
|---|---|---|
| Demographics | `DEMO_H/I/J` | age, sex, race/ethnicity, education, income, survey fields |
| Day 1 total diet | `DR1TOT_H/I/J` | nutrient intake, potassium, dietary-recall status |
| Body measures | `BMX_H/I/J` | waist circumference and BMI |
| Blood pressure | `BPX_H/I/J` | repeated systolic and diastolic readings |
| Glycohemoglobin | `GHB_H/I/J` | HbA1c |
| HDL cholesterol | `HDL_H/I/J` | HDL component |
| Total cholesterol | `TCHOL_H/I/J` | EDA only in the current plan |
| Triglycerides/LDL | `TRIGLY_H/I/J` | triglyceride component; LDL retained only for EDA |
| Physical activity | `PAQ_H/I/J` | activity days, minutes, and sedentary time |
| Alcohol | `ALQ_H/I/J` | optional sensitivity feature after recoding |
| Smoking | `SMQ_H/I/J` | optional sensitivity feature after recoding |
| Sleep | `SLQ_H/I/J` | optional sensitivity feature |
| Food security | `FSQ_H/I/J` | K-Means context feature |

Within each cycle, component files are joined on `SEQN`. The cycle-specific wide tables are then stacked row-wise. Because `SEQN` is only guaranteed to identify a participant within one cycle, the project identifier is:

```text
uid = cycle + "_" + SEQN
```

The uploaded dataset contained 29,400 unique `uid` values. After the adult filter, all 17,057 retained `uid` values remained unique, with no duplicate rows by `uid`.

## 3. Sample flow

| Stage | Eligibility rule | Participants |
|---|---|---:|
| Uploaded merged dataset | All pooled records | 29,400 |
| Adult master dataset | `age >= 20` | 17,057 |
| Strict five-component label | All five components observed | 6,683 |
| Primary combined label | Strict cases plus mathematically determinable triglyceride-missing cases | 12,125 |
| Primary label = 1 | At least three positive components | 4,145 |
| Primary label = 0 | Fewer than three positive components | 7,980 |
| Reliable Day 1 dietary recall | `DR1DRSTZ == 1` | 14,806 |
| Core supervised diet-model sample | Primary label known and Day 1 recall reliable | 11,431 |

The difference between the earlier discussion estimate of approximately 11,524 and the current 12,125 labeled adults is expected. The current build applies the final `age >= 20` filter, recomputes blood pressure from repeated readings, and reconstructs omitted variables from the source components. The current counts should be treated as the reproducible candidate counts; the earlier numbers were planning estimates based on an older cleaned table.

## 4. Cleaning and derivation decisions

### 4.1 Adult population

Only participants age 20 years or older are retained. Pediatric metabolic-syndrome definitions differ from the adult criteria used in this project.

### 4.2 SAS XPORT zero artifact

Some true zeros imported from SAS XPORT files appeared as approximately `5.397605e-79`. Values with absolute magnitude below `1e-70` were normalized to exactly zero before range checks. This correction was applied only to the known near-zero representation; legitimate small values and genuine extreme values were not automatically removed.

### 4.3 Repeated blood-pressure measurements

The previous cleaned CSV retained only the first blood-pressure reading. The updated dataset uses all available valid readings:

```text
bp_systolic_mean  = mean(BPXSY1, BPXSY2, BPXSY3, BPXSY4)
bp_diastolic_mean = mean(BPXDI1, BPXDI2, BPXDI3, BPXDI4)
```

`bp_valid_reading_count` records the number of valid systolic readings contributing to the mean. A blood-pressure component is positive if either mean crosses its threshold. A negative component requires both the systolic and diastolic means to be observed and below threshold; one observed low value does not make a missing counterpart negative.

### 4.4 Dietary variables and reliability

`potassium_mg` was recovered from `DR1TPOTA`. Day 1 dietary values are considered eligible for the core diet model only when `DR1DRSTZ == 1`, recorded as `diet_recall_reliable = True`.

Participants with missing or unreliable Day 1 recalls remain in the adult master dataset. The project does not impute an entire missing dietary record with typical intake values. These participants are excluded only from the core diet-focused Random Forest sample.

### 4.5 Activity minutes

The yes/no recreational-activity fields are retained as source information, but practical model inputs are expressed in minutes per week:

```text
vigorous_rec_min_week = PAQ655 × PAD660 when PAQ650 == 1
moderate_rec_min_week = PAQ670 × PAD675 when PAQ665 == 1
```

If the participant explicitly reported no activity (`PAQ650 == 2` or `PAQ665 == 2`), the corresponding weekly minutes equal zero. Refused, unknown, or structurally unavailable responses remain missing. Known sentinel values such as `77`, `99`, `7777`, and `9999` are treated as missing rather than literal days or minutes.

### 4.6 Range and extreme-value policy

The build checks units and plausible ranges but does not automatically delete an extreme value solely for being extreme. For example, the cleaned data include one HDL value above 200 mg/dL and one triglyceride value above 3,000 mg/dL. These records are flagged for source verification rather than silently winsorized or removed.

## 5. Metabolic-syndrome components

The target is measurement-based and uses five nullable component flags. Missing measurements remain missing.

| Component | Source fields | Positive when |
|---|---|---|
| Central waist | `sex`, `waist_cm` | male ≥102 cm; female ≥88 cm |
| Blood pressure | `bp_systolic_mean`, `bp_diastolic_mean` | systolic ≥130 or diastolic ≥85 mmHg |
| Triglycerides | `triglycerides` | ≥150 mg/dL |
| Low HDL | `sex`, `hdl` | male <40; female <50 mg/dL |
| Blood sugar proxy | `hba1c` | HbA1c ≥5.7% |

The corresponding fields are:

```text
waist_flag
bp_flag
triglycerides_flag
hdl_flag
hba1c_flag
```

Each flag is `1`, `0`, or missing. `metabolic_component_count_known` is the sum of observed positive flags and must always be interpreted together with `metabolic_component_known_n`, the number of known flags.

## 6. Target construction

### 6.1 Strict audit label

`metabolic_syndrome_strict` is assigned only when all five component flags are observed:

```text
1 if five components are observed and positive count >= 3
0 if five components are observed and positive count <= 2
missing otherwise
```

This strict complete-case label is available for sensitivity analysis and auditing. It is known for 6,683 adults.

### 6.2 Primary combined label

The primary `metabolic_syndrome` label implements the team’s final deterministic-recovery decision. It begins with the strict label and additionally considers participants for whom triglycerides alone are missing while waist, blood pressure, HDL, and HbA1c are all known:

| Positive count among the four known components | Effect of unknown triglycerides | Primary label |
|---:|---|---:|
| 0–1 | Even a positive triglyceride flag cannot reach three | 0 |
| 2 | Triglycerides determines whether the total is two or three | missing |
| 3–4 | The participant already has at least three positive components | 1 |

This procedure does not impute or guess a triglyceride measurement. It labels a record only when either possible triglyceride result leads to the same final class. `label_basis` records whether each result came from all five observed components, deterministic triglyceride-missing recovery, or remains unresolved because triglycerides is required.

## 7. Missing-data policy

The project uses different missing-data rules for label construction and predictors:

1. The five target components are never statistically imputed.
2. Missing triglycerides may be bypassed only through the deterministic logic described above.
3. An unreliable Day 1 recall excludes a participant from the core diet model but not from the master dataset.
4. Predictor imputation occurs only after the train/test split.
5. Imputation values must be learned from the training set and then applied unchanged to the held-out test set.
6. K-Means context features may use training-set median or most-frequent imputation as part of a saved preprocessing pipeline.

The complete per-column counts and percentages are stored in `missingness_summary.csv`. Important structural sources of missingness include the fasting laboratory subsample for triglycerides, skipped or unreliable dietary interviews, examination nonparticipation, and demographic nonresponse.

## 8. Column roles and leakage controls

### 8.1 Label-construction fields

The following fields construct or directly reveal the supervised target and must not enter Random Forest or Logistic Regression predictors:

```text
waist_cm
bp_systolic_mean
bp_diastolic_mean
triglycerides
hdl
hba1c
waist_flag
bp_flag
triglycerides_flag
hdl_flag
hba1c_flag
metabolic_component_count_known
metabolic_component_known_n
metabolic_syndrome_strict
metabolic_syndrome
label_basis
```

### 8.2 Core modifiable Random Forest fields

```text
energy_kcal
protein_g
carb_g
sugar_g
fat_total_g
fat_sat_g
fiber_g
sodium_mg
potassium_mg
moderate_rec_min_week
sedentary_min
```

Vigorous activity, sleep, smoking, and alcohol belong in separately identified sensitivity analyses rather than silently changing the core feature set.

### 8.3 K-Means context fields

```text
age
sex
race_eth
education
income_poverty_ratio
food_security_adult
```

K-Means must not use the metabolic label, clinical markers, diet targets, activity targets, survey fields, or identifiers to create peer groups.

### 8.4 Tracking and excluded fields

`uid`, `SEQN`, and `cycle` are tracking fields, never predictors. Survey weights, PSU, and strata are excluded from the model-ready CSV and from all X matrices. BMI, LDL, total cholesterol, and other unused clinical outputs may be retained for audit or EDA but are not current supervised predictors.

Because survey weights are excluded from model training, reported percentages and metrics describe the project sample. They must not be described as nationally representative U.S. prevalence or population performance.

## 9. Dataset products

| File | Purpose | Recommended location |
|---|---|---|
| `nhanes_clean.csv` | cleaned adult dataset | Google Drive `Datasets/Processed/` |
| `sample_flow.csv` | row counts at each eligibility stage | Drive and/or GitHub report support |
| `missingness_summary.csv` | missing count and percentage by field | Drive and/or GitHub report support |
| `column_dictionary.csv` | field definitions, derivations, roles, and dtypes | Drive and GitHub documentation |
| `manual_label_check_10.csv` | ten-record human verification worksheet | Drive and GitHub documentation |
| `dataset_report.md` | methods and decisions | GitHub `reports/` |

The large model-ready CSV and raw XPT data should remain in Google Drive and should not be committed to GitHub. Code, tests, feature lists, and this report belong in GitHub.

## 10. Verification performed

The local cleaning build passed the following automated checks:

- 17,057 adult records retained.
- Minimum retained age is 20.
- Adult `uid` values are unique.
- No train/test UID overlap in the baseline split.
- Strict labels agree with the independently recomputed five-flag total.
- Deterministically recovered labels agree with the four-known-component rule.
- Near-zero XPORT artifacts were normalized to zero.
- Required derived fields exist in the output.
- Survey design fields are absent from the model-ready output.

A ten-record worksheet containing five label-0 and five label-1 participants was independently recalculated on July 22, 2026. The review recomputed each waist, blood-pressure, triglycerides, HDL, and HbA1c flag directly from the displayed measurements and then recomputed the final label. All 10 independently calculated flag sets and labels matched the stored results (10/10 passed).

Two extreme laboratory records were also checked directly against the original XPT source files rather than against the cleaned CSV. In `HDL_I.xpt`, `SEQN 84166` has `LBDHDD = 226 mg/dL`. In `TRIGLY_H.xpt`, `SEQN 80169` has `LBXTR = 4233 mg/dL`. Both cleaned values match their source records and are retained rather than silently deleted or winsorized.

## 11. Preliminary pipeline run

A local baseline run was performed only to confirm that the cleaned dataset, shared UID split, and feature boundaries work end to end. Among 11,431 participants with a primary label and reliable Day 1 recall, 9,144 were assigned to training and 2,287 to the held-out test set using a stratified 80/20 split with random seed 42.

The baseline Random Forest and Logistic Regression produced ROC-AUC values of approximately 0.572 and 0.584, respectively. These results are weak and are not a validation pass. They should not replace the team’s existing Random Forest notebook. The next action is to connect the existing notebook to the updated nhanes_clean.csv and shared UIDs, then perform training-only cross-validation, stable feature selection, and a single final held-out evaluation.

## 12. Limitations

1. The current primary label uses HbA1c ≥5.7% as the blood-sugar component rather than fasting glucose.
2. Medication treatment for hypertension, dyslipidemia, or elevated glucose is not incorporated; the target is measurement-based.
3. Triglycerides is structurally missing for many participants because it was measured in a fasting subsample.
4. Deterministic recovery increases the labeled sample but does not recover participants whose four known components contain exactly two positives.
5. Dietary intake is based on Day 1 recall and is subject to recall and day-to-day variability.
6. Survey weights and design variables are not used in the models; conclusions apply to the analytic sample.
7. The ten-record independent recalculation was performed with Codex assistance rather than signed by a named teammate; the team may add a human reviewer if required by the course rubric.
8. Model performance, stability, calibration, and subgroup behavior remain to be validated.

## 13. Freeze and approval checklist

`nhanes_clean.csv` should replace the shared processed copy only after the team confirms all items below:

- [x] Independently recalculate the ten sampled labels (10/10 matched on July 22, 2026).
- [x] Check the HDL and triglyceride extreme records against `HDL_I.xpt` and `TRIGLY_H.xpt`.
- [ ] `column_dictionary.csv` is reviewed for final descriptions and units.
- [x] Record the team decision to use HbA1c as the primary blood-sugar component.
- [x] Record deterministic triglyceride-missing recovery as the primary label strategy.
- [x] Add automated checks preventing label-construction fields from entering the approved supervised feature lists.
- [ ] The existing Random Forest notebook successfully reads the updated `nhanes_clean.csv` and shared train/test UIDs.
- [x] Record the final filename and Drive location (`Datasets/Processed/nhanes_clean.csv`).
- [ ] The Git commit and random seed are recorded in the run log.

## 14. Reproducibility record

For every final run, record:

| Item | Candidate value |
|---|---|
| Dataset filename | `nhanes_clean.csv` |
| Build date | 2026-07-22 |
| Adult cutoff | age ≥20 |
| Primary blood-sugar component | HbA1c ≥5.7% |
| Primary label | strict plus deterministic triglyceride-missing recovery |
| Random split seed | 42 |
| Core supervised sample | primary label known + reliable Day 1 recall |
| Git branch | `phase1-data-cleaning` |
| Independent label verification | 10/10 matched, 2026-07-22 |
| Team approval date | to be filled |

## 15. References

- Alberti KGMM et al. (2009). *Harmonizing the Metabolic Syndrome*. Circulation. https://doi.org/10.1161/CIRCULATIONAHA.109.192644
- CDC National Center for Health Statistics. NHANES 2013–2018 documentation. https://wwwn.cdc.gov/nchs/nhanes/
- National Institute of Diabetes and Digestive and Kidney Diseases. A1C test information. https://www.niddk.nih.gov/health-information/diagnostic-tests/a1c-test
