# Wealth of Health and Nutrition — Project Plan & Task Board

**Project logic:** We use NHANES data to study how modifiable diet and activity
behaviors relate to metabolic-syndrome risk, while accounting for each
participant's background and access conditions. **Random Forest** finds which
modifiable behaviors matter most, **K-Means** builds context-matched peer groups,
and **Logistic Regression** turns the strongest selected behaviors into an
individual risk probability.

**Current phase:** completing the analysis pipeline *before* recommendations.
Phase 1 (adult dataset + label) is essentially done and documented in
[reports/dataset_report.md](reports/dataset_report.md); we're moving into Phase 2
(lock model inputs + shared split) and Phase 3 (train the three models).

**What comes after:** recommendations + deployment begin **only after validation
passes** — compare a participant with lower-risk people from a similar peer group,
use the validated findings to suggest realistic targets, then a Streamlit demo.

> Work in a personal branch; **do not push directly to `main`.** Everyone imports
> the feature lists from `src/features.py` and loads the same frozen dataset — no
> notebook re-derives its own columns.

**Verified current numbers** (age ≥ 20, HbA1c-primary label, on `nhanes_clean.csv`):
17,057 adults · 6,683 strict-labelled · **12,125 primary-labelled** (4,145 pos /
7,980 neg) · **11,431 core supervised sample** (label + reliable Day-1 diet).

---

## 1. Current status map

| Step | Output | Status | Where |
|------|--------|--------|-------|
| 1 | One usable dataset | ✅ **done** (freeze + column dict pending) | `src/`, `scripts/build_phase1.py`, `reports/` |
| 2 | Shared model inputs | ◐ in progress (feature lists done; split + per-model preprocessing pending) | `src/features.py`, `src/split.py`, `src/preprocess.py` |
| 3 | Three trained models | ☐ not final (baseline run only) | `notebooks/`, `models/`, `outputs/` |
| 4 | Validation | ☐ not started | validation notebook + report |
| 5–6 | Recommendations + demo | ☐ after validation | `recommendation/`, Streamlit app |

---

## 2. Task ownership & dependencies

| ID | Work package | Needs | Owner | Status |
|----|--------------|-------|-------|--------|
| P1-A | Finish data cleaning and audit | – | Munya | ✅ done |
| P1-B | Build and verify the metabolic-syndrome label | P1-A | Bonnie | ✅ done |
| P1-C | Complete the Dataset Report | P1-A, P1-B | — | ◐ report done; column dict + freeze pending |
| P2-A | Finalize feature groups and exclusions | P1-A, P1-B | — | ✅ done (`src/features.py`) |
| P2-B | Build preprocessing and the shared split | P1-B, P2-A | — | ◐ split mechanism done; per-model pipelines + frozen split pending |
| P3-A | Train final Random Forest | P2-B | — | ☐ |
| P3-B | Train and profile K-Means | P2-B | — | ☐ |
| P3-C | Train final Logistic Regression | P2-B, P3-A | — | ☐ |
| P4-A | Validate Random Forest and Logistic Regression | P3-A, P3-C | — | ☐ |
| P4-B | Validate K-Means and complete subgroup checks | P3-B | — | ☐ |
| P4-C | Assemble the Validation Report | P4-A, P4-B | — | ☐ |

*Claim an unowned work package by adding your name.*

---

## Phase 1 — Finish one usable dataset  ✅ (near-complete)

Each row = one adult participant. See [reports/dataset_report.md](reports/dataset_report.md)
for the full audit (sample flow, derivations, verification, limitations).

**Cleaning / deriving** — all in `src/preprocessing.py` + `scripts/build_phase1.py`:
- [x] Merge components within each cycle and stack 2013–14 / 2015–16 / 2017–18 — *Munya*
- [x] Rename raw codes to readable columns + reconcile cycle-specific sleep — *Munya*
- [x] `uid = cycle + SEQN`, verified unique (29,400 → 17,057 adults) — *Munya*
- [x] Filter to adults age ≥ 20
- [x] Normalize the XPT zero artifact (`5.397605e-79` → 0)
- [x] Create `bp_systolic_mean` / `bp_diastolic_mean` (avg of repeated readings)
- [x] Add `potassium_mg` (from `DR1TPOTA`)
- [x] Replace activity yes/no with `moderate_rec_min_week` / `vigorous_rec_min_week`
- [x] Keep `diet_recall_status` / `diet_recall_reliable`
- [x] Audit units, codes, ranges, duplicate rows (extreme HDL/TG verified vs source)
- [ ] **Add `fasting_glucose`** (`GLU_H/I/J`) — *not merged; team chose HbA1c-primary instead (see limitation)*

**Label** — `src/target.py` (the 5 components build `y` only; never predictors):

| Component | Source | Positive when |
|-----------|--------|---------------|
| Central waist | `sex`, `waist_cm` | Male ≥102 cm; Female ≥88 cm |
| Blood pressure | `bp_systolic_mean`, `bp_diastolic_mean` | systolic ≥130 **OR** diastolic ≥85 |
| Triglycerides | `triglycerides` | ≥150 mg/dL |
| Low HDL | `sex`, `hdl` | Male <40; Female <50 mg/dL |
| Blood sugar (**primary**) | `hba1c` | ≥5.7% |

**Labelling rule.** `metabolic_syndrome_strict` = label only when all 5 flags are
observed. `metabolic_syndrome` (primary) starts from strict and adds **deterministic
triglyceride-missing recovery**: with the other four known, 0–1 positive → 0, 3–4 →
1, exactly 2 → unresolved (NaN). Not imputation — labels only where the missing
triglyceride can't change the class. `label_basis` records which path each row took.
- [x] Create five nullable component flags (missing stays missing) — *Bonnie*
- [x] Create `metabolic_component_count_known` + apply the deterministic rule — *Bonnie*
- [x] Document the medication limitation (measurement-based; no medication files)
- [x] Manually verify 10 participants (10/10 matched, 2026-07-22)
- [ ] *(optional)* Build a separate glucose-based `metabolic_syndrome` if `GLU` is ever added — keep proxy separate

**Phase 1 deliverable — Dataset Report** (P1-C):
- [x] Document what went into the dataset (cycles, files, counts, sample flow)
- [x] Missingness table (`missingness_summary.csv` from the build script)
- [x] Every derived field + label process (report §4–6)
- [x] What's excluded from modeling and why (report §8)
- [ ] **Create `column_dictionary.csv`** (readable name, NHANES code, unit, role) — *still open*
- [ ] **Record the final version / team freeze** — *pending approval (report §13)*

**Published:** `nhanes_clean.csv` (Drive), `reports/dataset_report.md`,
`sample_flow.csv`, `missingness_summary.csv`, `src/target.py`.

---

## Phase 2 — Lock model inputs before final training  ◐

The three models do **not** all get the same table. **Order:** freeze Phase-1 data
→ save feature groups → exclude leakage/tracking cols → per-model preprocessing →
one shared 80/20 split → start training.

**Feature groups** — locked in `src/features.py`:
`LABEL_COLUMNS` (build y; excluded from RF/LR) · `RF_FEATURES` (energy, protein,
carbs, sugar, fats, fiber, sodium, potassium, moderate-activity min/wk, sedentary)
· `RF_OPTIONAL_FEATURES` (sleep, vigorous, smoking, alcohol) · `KMEANS_FEATURES`
(age, sex, race/eth, education, income-poverty ratio, food security) ·
`NEVER_FEATURES` (uid/SEQN/cycle, weights, PSU/stratum, BMI/LDL/total chol).
- [x] Auto-check `LABEL_COLUMNS`/`NEVER_FEATURES` never enter `X` (`assert_no_leakage`)
- [x] Auto-check all named features exist before a model runs (`assert_columns_exist`)
- [ ] Select final RF features using **training data only**, then pass to LR *(needs P3-A)*

**Per-algorithm preprocessing (learn from training rows only) — `src/preprocess.py` (to build):**
- [ ] RF: core numeric features; training-median fill; no scaling; drop entirely-missing-diet rows
- [ ] K-Means: impute context gaps, one-hot encode, standardize numerics
- [ ] LR: final RF features; training-set impute; standardize
- [ ] Save each preprocessing pipeline **with** its model

**One shared 80/20 split — `src/split.py` (mechanism ✅, freeze pending):**
- [x] `create_shared_split` + `verify_shared_split` (stratified on label, overlap/coverage checks)
- [ ] Freeze `train_uids.csv` / `test_uids.csv` from the core sample and commit/publish
- [ ] Fit K-Means on training uids only; assign test with `predict()`
- [ ] Split summary (size, label balance, demographics)

---

## Phase 3 — Train the three models  ☐

**Workflow:** RF core behaviors → stable top features → LR probability. K-Means
context → peer-group assignment. *(A baseline run exists only to confirm the
pipeline end-to-end — RF/LR ROC-AUC ≈ 0.57/0.58, not a validation pass.)*

### 3A — Random Forest (`RandomForest.ipynb`)
- [ ] Load frozen dataset + shared uids; import `RF_FEATURES`; assert no leakage
- [ ] Fit preprocessing + `RandomForestClassifier` on training rows only
- [ ] Tune with CV inside training data (small, documented)
- [ ] Export impurity + permutation importance; prefer features stable across folds/seeds
- [ ] Select final top features for LR (after ranking is stable)
- [ ] Save RF pipeline, importance CSV, selected-feature list, test probabilities

### 3B — K-Means (`K_MeansClustering.ipynb`)
- [ ] Load frozen data + uids; `KMEANS_FEATURES` only (no label/marker/ID/survey)
- [ ] Impute context gaps, one-hot encode, standardize
- [ ] Compare `k` (elbow, silhouette, size, interpretability)
- [ ] Fit on training uids; assign test with `predict()`
- [ ] Profile clusters in original units (don't label healthy/unhealthy)
- [ ] Save pipeline, assignments, profiles, elbow + silhouette figures

### 3C — Logistic Regression (`LogisticRegression.ipynb`)
- [ ] Wait for final RF selected features (don't pick a different set)
- [ ] Same train/test uids as RF; fit impute+scale on training only, regularized LR
- [ ] Choose regularization with training-only CV
- [ ] Export probabilities, coefficients, odds ratios (association, not causation)
- [ ] Save pipeline + outputs

**Deliverables:** 3 notebooks rerun on frozen data + shared split, `models/` (3
pipelines), `outputs/` (importance, selected features, clusters, LR probabilities,
figures), a run log (dataset version, commit, seed, feature-list version, owner).

---

## Phase 4 — Validate before recommendations  ☐

**Open the final test set only after Phases 1–3 are frozen.**
- **4A Protect:** no train/test overlap; preprocessing from training only; final feature-exclusion check; freeze RF/LR features + K-Means `k`; `DummyClassifier` baseline.
- **4B RF:** held-out predictions; confusion matrix, precision, recall, F1, ROC-AUC, PR-AUC; feature-ranking stability; permutation importance; core vs optional kept separate.
- **4C LR:** same held-out uids; same metrics vs baseline + RF; **calibration** (curve + Brier); calibrate in training folds only; review coefficient direction.
- **4D K-Means:** choose `k` from training; stability across seeds; flag tiny clusters; profile in original units; use label only *after* clustering to find lower-risk peers.
- **4E Subgroups/sensitivity:** metrics by sex/age/race/income (+ sample sizes); flag gaps; **strict vs primary label** sensitivity run (also 6,683 strict vs 12,125 recovered); review notable FN/FP; describe results as *project-sample*, not U.S. prevalence.
- **4F Decide pass:** no leakage; RF+LR beat baseline; LR calibration honest; RF findings stable; K-Means stable/large-enough; limitations documented; team approves.

**Files:** `validation/Validation.ipynb`, `outputs/test_predictions.csv`, `outputs/metrics_summary.csv`, `outputs/rf_feature_stability.csv`, `outputs/kmeans_validation.csv`, `outputs/logistic_calibration.png`, `validation_report.md`.

---

## Phases 5–6 — Recommendations & demo (after validation passes)  ☐

Compare a participant with lower-risk people from a similar peer group, use the
validated findings to suggest realistic behavior targets, present via a **Streamlit**
demo. Work in `recommendation/`.

---

## Materials & references
- **Week 3** clean/select features (Phases 1–2) · **Weeks 4–5** model roles (Phase 3) · **Week 8** train/test/evaluate (Phase 4)
- Alberti et al. (2009), *Harmonizing the Metabolic Syndrome* — https://doi.org/10.1161/CIRCULATIONAHA.109.192644
- CDC NHANES 2013–2018 component docs — https://wwwn.cdc.gov/nchs/nhanes/
- NIDDK A1C guidance — https://www.niddk.nih.gov/health-information/diagnostic-tests/a1c-test

**The loop:** clean data → build the label → lock model inputs → train models →
validate on unseen participants → approve artifacts → begin recommendations.
