# Calibration and subgroup fairness audit of a childhood stunting risk model

**Clinical question:** Which children under five in Bangladesh are at high risk of stunting, and does the model perform equally well for girls and boys, for rural and urban children, and across wealth quintiles?

## Project summary

I fitted a regularised logistic regression and an XGBoost model to predict stunting (height-for-age z-score < -2 SD) using BDHS 2022 Kids Recode. On a held-out set of enumeration areas, the logistic model achieved **AUROC 0.652, Brier 0.169, ECE 0.028**. XGBoost matched discrimination (AUROC 0.651) but was worse on calibration (ECE 0.043). Fairness audit: excellent calibration fairness across residence, no meaningful discrimination advantage in any wealth quintile beyond predicting the group mean, and a substantive sex disparity in discrimination (AUROC 0.609 male vs 0.692 female) with near-identical calibration.

## Data

- **Source:** BDHS 2022 Kids Recode (BDKR81FL.DTA). DHS terms of use prohibit redistribution, so microdata is not included.
- **Cohort:** 8,784 KR records, minus 13 implausible measurements, minus 4,666 missing outcomes, leaving **4,105 children in 670 enumeration areas**.
- **Outcome:** stunted = 1 if hw70 < -200.
- **Prevalence:** 23.5% unweighted, **23.2% weighted** (matches BDHS-2022 official ~24%).

## Predictors

Thirteen features: b19 age, female, bord birth order, b11_filled preceding interval, firstborn, v106 maternal education, v445_filled BMI, v445_missing, v190 wealth, urban, v113 water, v116 toilet, v024 region.

Antenatal care (m14) excluded because missingness was age-dependent (1% under 12 months, 100% over 36 months).

## Evaluation

**Grouped split by enumeration area (v001):** train 3,315 children in 536 clusters, test 790 children in 134 clusters, **zero overlap**.

**Metrics:** AUROC, Brier with bootstrap 95% CI, ECE (10 quantile bins), reliability diagrams, subgroup versions by residence, wealth quintile, and sex.

## Results

### Overall performance (n=790)

| Model | AUROC | Brier [95% CI] | ECE |
|---|---|---|---|
| **Logistic** | **0.6518** | **0.1691** [0.154, 0.184] | **0.0281** |
| XGBoost | 0.6510 | 0.1713 [0.155, 0.187] | 0.0428 |

XGBoost matched discrimination (change = -0.0008) but was **52% worse on ECE**. A simple model done properly matched a complex one.

### Leakage cost

| Split | AUROC |
|---|---|
| Grouped by v001 | 0.6510 |
| Random | 0.6528 |

Difference: +0.0018. Small, because predictors are individual/household level, not cluster level.
### Fairness audit (logistic model, test set)

**Residence - fair.**

| Group | n | Events | AUROC | Brier | ECE |
|---|---|---|---|---|---|
| Rural | 501 | 119 | 0.6477 | 0.1730 | 0.0330 |
| Urban | 289 | 64 | 0.6604 | 0.1632 | 0.0324 |
| **max-min** | | | **0.0127** | **0.0098** | **0.0006** |

**Wealth quintile - Brier gap is prevalence artefact, AUROC gap is real.**

| Group | n | Events | Prev. | Base Brier | Model Brier | AUROC | ECE |
|---|---|---|---|---|---|---|---|
| Q1 | 150 | 54 | 0.360 | 0.2304 | 0.2302 | 0.5762 | 0.0737 |
| Q2 | 147 | 41 | 0.279 | 0.2011 | 0.1970 | 0.5957 | 0.0690 |
| Q3 | 147 | 36 | 0.245 | 0.1849 | 0.1853 | 0.5478 | 0.0936 |
| Q4 | 193 | 39 | 0.202 | 0.1613 | 0.1608 | 0.5816 | 0.0696 |
| Q5 | 153 | **13** | 0.085 | 0.0778 | 0.0788 | 0.6725 | 0.0655 |

Model Brier is within 0.005 of base-rate Brier in every quintile, meaning the model adds no meaningful improvement over predicting the group mean at the quintile level. Q5's AUROC rests on only 13 events.

**Sex - substantive discrimination disparity, calibration fair.**

| Group | n | Events | AUROC | Brier | ECE |
|---|---|---|---|---|---|
| Male | 408 | 89 | 0.6090 | 0.1671 | 0.0428 |
| Female | 382 | 94 | 0.6919 | 0.1719 | 0.0453 |
| **max-min** | | | **0.0829** | **0.0048** | **0.0025** |

The model is calibrated equally well for boys and girls but discriminates stunting risk **substantially better for girls**. This is the project's main fairness finding.

## Limitations

- Single-survey, cross-sectional.
- Modest discrimination (AUROC 0.65, in line with published BDHS stunting models).
- Calibration partly reflects prediction compression (probabilities span 0.10 to 0.42).
- Q5 AUROC rests on 13 events.
- Sex disparity documented but not resolved.
- Antenatal care excluded due to age-dependent missingness.
- Not externally validated.

## Reproducibility

Register at https://dhsprogram.com/data/, download BDKR81DT.ZIP, place .DTA in data/raw/, pip install -r requirements.txt, run notebooks, run python src/fairness_audit.py.

## Citation

Sweety Akter (2026). Calibration and subgroup fairness audit of a childhood stunting risk model using BDHS-2022 Kids Recode data. GitHub repository.
