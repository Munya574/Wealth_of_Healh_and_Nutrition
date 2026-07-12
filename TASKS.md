# Task Board — pick what you want to work on

**Our goal for this milestone:** get one full version of the project working end to
end — a "healthy vs. at-risk" tag for each person, our three models running on the
same clean data, and a first attempt at giving personalized food/exercise tips.

**How to claim a task:** put your name in the **Owner** column (or just call it in
the group chat). New to machine learning? Totally fine — each task has an
**experience level** below, and several are great starting points. Ask questions
anytime.

---

## The big picture (how the tasks connect)

Think of it like an assembly line:

```
                        ┌─> Random Forest ─(its top 5 findings)─> Logistic Regression ─┐
clean data ─> LABEL ────┤   (finds what matters)                  (turns it into a %)   │
 (the health           │                                                                ├─> TIPS FOR
  "at-risk" tag)       └─> (the label also tells us who counts as "healthy")            │    THE USER
                                                                                         │
clean data ────────────────> K-Means (sorts people into similar-background groups) ──────┘

            Meanwhile: exploring/charting the data (EDA) happens all along
```

**Most important:** the **LABEL** (Task 1) has to be built first, because the models
can't run without it. K-Means and the data-exploration task don't need the label, so
they can start right away.

---

## Tasks — one person each (7 people, 7 tasks)

| # | Task | Where you'll work | Needs | Level | Owner |
|---|------|-------------------|-------|-------|-------|
| 1 | **The data + the health label** (do first!) | `src/target.py` | – | Intermediate | — |
| 2 | Pick the inputs + split the data | `src/features.py` | 1 | Intermediate | — |
| 3 | Random Forest model | `RandomForest.ipynb` | 1, 2 | Beginner-friendly | — |
| 4 | Logistic Regression model | `LogisticRegression.ipynb` | 3 | Beginner-friendly | — |
| 5 | K-Means groups | `K_MeansClustering.ipynb` | 1 | Beginner-friendly | — |
| 6 | The recommendation / tips engine | `recommendation` branch | 3, 4, 5 | Intermediate | — |
| 7 | Explore the data + slides / organizing | `eda` branch | 1 | Beginner-friendly | — |

*If you finish early, hop over and help on Task 1 or Task 6 — those are the biggest.*

---

## What each task actually means

### 1 . The data + the health label  ⟵ start here, everything depends on it
Two connected jobs:
- **Prepare the dataset:** narrow it to the people we'll actually study;
  **adults (18+)** who have the blood-test results we need (about 7,000–8,000 people).
- **Build the health label:** our target. We use a standard
  medical definition of **metabolic syndrome**... 5 warning signs (big
  waist, high blood pressure, high triglycerides, low "good" cholesterol, high blood
  sugar). If a person has **3 or more**, we tag them `1` = at-risk; otherwise
  `0` = healthy.

*requires familiarity with spreadsheets / pandas. This sets up everyone
else, so must be completed first.*

### 2 . Pick the inputs + split the data
Choose the 15 **things people can change**; diet and exercise info like fiber,
sugar, sodium, calories, protein, and activity minutes. **Split the data:** suggested 80% - 20% train-test split
>  Don't include the blood-test numbers we used to *make* the label to avoid leaking.

### 3 . Random Forest model
A model that looks at everyone's diet/exercise habits and learns which ones matter
most for being at-risk. Produce a ranked list of the **top 5 habits** that affect risk the most (that list feeds Tasks 4 and 6).

### 4 . Logistic Regression model
Takes the **top 5 habits** from Task 3 and turns them into a simple **risk score
from 0–100%**

### 5 . K-Means groups  (start anytime)
Groups people by **demographics**: age, income level, background.

### 6 . The recommendation / tips engine
For a given person: look at the **healthy people in their peer group**, see what
they eat and do differently, and turn that into **realistic, affordable
suggestions**...plus show their risk score vs. the healthy target. You can start
sketching the idea now; the build waits on Tasks 3–5.

### 7 . Explore the data + slides / organizing  (start anytime)
Make charts to understand the data (what's typical, what's missing, how groups
differ)...keep the shared code
tidy and pull everyone's results into a **slide deck**.

---

## A few things everyone should know

- Load `nhanes_clean.csv` (in the Drive / repo).
  Don't re-clean or re-merge the raw files. Any fixes must go through Task 1 owner so we all stay in sync.
- Use the `uid` column as the ID (not `SEQN`, which can
  repeat across years).
- **Blood-sugar signal:** the medical definition normally uses a
  *fasting glucose* blood test, which we don't have...so we're using **HbA1c**
  instead (a blood-sugar test already in our data). The Task 1 owner flags high
  blood sugar when **HbA1c ≥ 5.7%**.
- Lots of empty cells are expected. NHANES doesn't run every
  test on every person. Not a bug.
