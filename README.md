\# Calibration and subgroup fairness audit of a childhood stunting risk model



\*\*Clinical question:\*\* Which children under five in Bangladesh are at high risk of

stunting, and does the model that predicts this risk perform equally well for

girls and boys, for rural and urban children, and across household wealth

quintiles?



\---



\## Project summary



I fitted a regularised logistic regression and an XGBoost model to predict

stunting (height-for-age z-score < −2 SD, WHO 2006 growth standards) using the

Bangladesh Demographic and Health Survey 2022 Kids Recode. On a held-out set of

enumeration areas, the logistic model achieved \*\*AUROC 0.652, Brier 0.169,

ECE 0.028\*\*, and the XGBoost model achieved no improvement in discrimination

(AUROC 0.651) and slightly worse calibration (ECE 0.043). A subgroup fairness

audit found \*\*excellent calibration fairness across residence\*\*, \*\*no meaningful

discrimination advantage in any wealth quintile beyond predicting the group

mean\*\*, and a \*\*substantive sex disparity in discrimination\*\* (AUROC 0.609 male

vs 0.692 female) despite near-identical calibration.



The project was built to demonstrate rigorous health data science on

population-level survey data — specifically calibration, subgroup fairness,

and leakage-aware evaluation — in preparation for postgraduate study in Health

Data Science.



\---



\## Data



\- \*\*Source:\*\* Bangladesh Demographic and Health Survey (BDHS) 2022, Kids Recode

&#x20; (`BDKR81FL.DTA`), obtained via the DHS Program under a registered research

&#x20; project. The DHS terms of use prohibit redistribution of microdata, so the

&#x20; raw and processed data files are \*\*not included in this repository\*\*.

\- \*\*Cohort construction:\*\*

&#x20; - 8,784 KR records total.

&#x20; - Excluded 13 records with `hw70` special codes {9996, 9997, 9998} (implausible

&#x20;   anthropometric measurement).

&#x20; - Excluded 4,666 records with missing `hw70`.

&#x20; - \*\*Analysable cohort: 4,105 children in 670 enumeration areas.\*\*

\- \*\*Outcome:\*\* stunted = 1 if `hw70 < -200`, else 0.

\- \*\*Prevalence:\*\* 23.5% unweighted, \*\*23.2% weighted\*\* (matches official BDHS-2022

&#x20; estimate of \~24%, confirming correct file choice, outcome definition, and

&#x20; weight handling).



\## Predictors



Thirteen features, all available at a community-health-worker visit before

anthropometric measurement:



| Category | Variables |

|---|---|

| Child | `b19` age in months, `female` (b4==2), `bord` birth order, `b11\_filled` preceding birth interval, `firstborn` indicator |

| Maternal | `v106` education, `v445\_filled` BMI (÷100), `v445\_missing` indicator |

| Household | `v190` wealth quintile, `urban` (v025==1), `v113` water source, `v116` toilet type |

| Region | `v024` |



\*\*Antenatal care visits (`m14`) were excluded from the primary model.\*\* Missingness

was deterministically age-dependent (1% missing for children under 12 months,

100% for children over 36 months) because the DHS-8 maternity-care module has a

3-year recall window. Any missingness indicator would have encoded child age

and introduced leakage. A sensitivity analysis restricted to children under

36 months is noted as future work.



\## Evaluation design



\*\*Grouped train/test split by enumeration area (`v001`).\*\* Train: 3,315 children

in 536 clusters. Test: 790 children in 134 clusters. \*\*Zero clusters overlap

between train and test.\*\* Random splits would place \~450 of 670 clusters in both

arms, allowing cluster-level context to be memorised. The grouped split is the

correct choice for DHS's complex survey design.



\*\*Metrics:\*\* AUROC (discrimination), Brier score with bootstrap 95% CI

(probabilistic accuracy), expected calibration error (ECE) with 10 quantile bins,

reliability diagrams, and subgroup versions of all three metrics by residence,

wealth quintile, and sex.



\## Results



\### Overall model performance (grouped test set, n=790)



| Model | AUROC | Brier \[95% CI] | ECE |

|---|---|---|---|

| \*\*Logistic (elastic-net, scaled)\*\* | \*\*0.6518\*\* | \*\*0.1691\*\* \[0.154, 0.184] | \*\*0.0281\*\* |

| XGBoost (300 trees, depth 4) | 0.6510 | 0.1713 \[0.155, 0.187] | 0.0428 |



XGBoost matched logistic on discrimination (ΔAUROC = −0.0008) but was \*\*52%

worse on calibration error\*\* (ECE 0.043 vs 0.028). The Brier confidence intervals

overlap. A simple model done properly matched a complex one, and calibrated better.



\### Leakage cost (grouped vs random split)



| Split | AUROC | Δ vs grouped |

|---|---|---|

| Grouped by `v001` | 0.6510 | — |

| Random | 0.6528 | +0.0018 |



The leakage cost was small, reflecting the individual and household-level nature

of the predictors and the small average cluster size (\~6 children). The grouped

split remains the methodologically correct choice; the near-zero gap demonstrates

the result is robust to split choice, a finding that cannot be assumed in DHS

prediction studies where cluster-level covariates are included.



\### Subgroup fairness audit (logistic model, test set)



\*\*Residence — fair.\*\*



| Group | n | Events | AUROC | Brier | ECE |

|---|---|---|---|---|---|

| Rural | 501 | 119 | 0.6477 | 0.1730 | 0.0330 |

| Urban | 289 | 64 | 0.6604 | 0.1632 | 0.0324 |

| \*\*max−min\*\* | | | \*\*0.0127\*\* | \*\*0.0098\*\* | \*\*0.0006\*\* |



\*\*Wealth quintile — apparent Brier gap is a prevalence artefact; AUROC gap is real.\*\*



| Group | n | Events | Prev. | Base-rate Brier | Model Brier | AUROC | ECE |

|---|---|---|---|---|---|---|---|

| Q1 (poorest) | 150 | 54 | 0.360 | 0.2304 | 0.2302 | 0.5762 | 0.0737 |

| Q2 | 147 | 41 | 0.279 | 0.2011 | 0.1970 | 0.5957 | 0.0690 |

| Q3 | 147 | 36 | 0.245 | 0.1849 | 0.1853 | 0.5478 | 0.0936 |

| Q4 | 193 | 39 | 0.202 | 0.1613 | 0.1608 | 0.5816 | 0.0696 |

| Q5 (richest) | 153 | \*\*13\*\* | 0.085 | 0.0778 | 0.0788 | 0.6725 | 0.0655 |



Brier score is not comparable across groups with different prevalence; the

base-rate benchmark (predicting the constant `p`) varies from 0.078 in Q5 to 0.230

in Q1. In \*\*every quintile\*\*, the model's Brier is within 0.005 of that benchmark,

meaning the model adds no meaningful improvement over predicting the group mean

at the quintile level. The AUROC gap (0.548 to 0.673) is prevalence-invariant

and therefore the more meaningful comparison, but Q5's high AUROC is based on only

13 events and is unstable.



\*\*Sex — substantive discrimination disparity, calibration fair.\*\*



| Group | n | Events | AUROC | Brier | ECE |

|---|---|---|---|---|---|

| Male | 408 | 89 | 0.6090 | 0.1671 | 0.0428 |

| Female | 382 | 94 | 0.6919 | 0.1719 | 0.0453 |

| \*\*max−min\*\* | | | \*\*0.0829\*\* | \*\*0.0048\*\* | \*\*0.0025\*\* |



The model is calibrated equally well for boys and girls, but \*\*discriminates

stunting risk substantially better for girls\*\* (AUROC gap 0.083). With n≈400

per group, this gap is roughly two standard errors from zero. This is the

project's main fairness finding and would warrant investigation in a full study

— candidate explanations include differences in how well the predictor set captures

boys' specific risk pathways, or residual confounding by unmeasured household

characteristics.



\## Limitations



\- \*\*Single-survey, cross-sectional.\*\* Results reflect BDHS-2022 only and do not

&#x20; establish temporal or external validity. The model predicts \*association with\*

&#x20; stunting, not the effect of any intervention.

\- \*\*Modest discrimination.\*\* AUROC 0.65 is in line with published BDHS stunting

&#x20; models (0.62–0.72) but is not sufficient for individual-level clinical use.

&#x20; The model cannot identify children at substantially elevated risk.

\- \*\*Calibration partly reflects prediction compression.\*\* Predicted probabilities

&#x20; span only 0.10 to 0.42 around a base rate of 0.23, so good calibration is

&#x20; partly a consequence of predicting near the group mean. This is honest and

&#x20; expected from a small predictor set, but it means the model's clinical utility

&#x20; is limited.

\- \*\*Wealth-quintile Brier scores are not comparable.\*\* The apparent Brier gap

&#x20; between Q1 and Q5 is fully explained by the prevalence gradient.

\- \*\*Q5's AUROC is based on 13 events\*\* and should not be over-interpreted.

\- \*\*The sex disparity in AUROC is not resolved.\*\* The audit documents it; it does

&#x20; not explain or correct it.

\- \*\*Antenatal care was excluded\*\* due to structurally age-dependent missingness.

&#x20; A sensitivity analysis restricted to children under 36 months is future work.

\- \*\*Not externally validated.\*\* The model should not be used in any real health

&#x20; setting without prospective validation in a separate population.



\## Reproducibility



1\. Register for DHS data access at https://dhsprogram.com/data/ and download the

&#x20;  Bangladesh 2022 Kids Recode (`BDKR81DT.ZIP`).

2\. Place the extracted `.DTA` file in `data/raw/`.

3\. Install dependencies: `pip install -r requirements.txt`.

4\. Run the notebook sequence in `notebooks/` (`00\_setup\_and\_intake.ipynb`

&#x20;  through the analysis notebook).

5\. Run `python src/fairness\_audit.py` for the subgroup tables.



The repository does not include the DHS microdata, any derived row-level data

(`data/processed/\*.parquet`), or the prediction `.npz` files. Only code, aggregate

results, and figures are tracked.



\## Repository structure

.md

