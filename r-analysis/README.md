# R cross-check of survey-weighted estimates

The BDHS uses a multistage cluster sample. Weighted prevalence and subgroup
prevalences were computed independently in R using the `survey` package and
compared with the Python implementation.

Run: `"C:\Program Files\R\R-4.6.0\bin\Rscript.exe" survey_prevalence.R`

Result: R survey-weighted prevalence **0.2322 (SE 0.0084)**, Python **0.232**.
Agreement within 0.0002.

Wealth-quintile prevalences (R): Q1 0.3424, Q2 0.2675, Q3 0.2176,
Q4 0.1701, Q5 0.1529.