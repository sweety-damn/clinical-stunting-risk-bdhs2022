# survey_prevalence.R
# Cross-check of survey-weighted stunting prevalence using R's survey package.
# Run with: Rscript survey_prevalence.R

library(haven)
library(survey)
library(dplyr)

# ---- Paths (Windows-safe, no backslash escaping needed) ----
home      <- Sys.getenv("USERPROFILE")
data_path <- file.path(home, "clinical-readmission-risk", "data", "raw", "BDKR81FL.DTA")
out_path  <- file.path(home, "clinical-readmission-risk", "r-analysis", "prevalence_output.txt")

cat("Loading:", data_path, "\n")
dhs <- read_dta(data_path)

# ---- Clean outcome: stunting ----
dhs <- dhs %>%
  mutate(
    hw70_num   = as.numeric(hw70),
    hw70_clean = if_else(hw70_num %in% c(9996, 9997, 9998, 9999) | is.na(hw70_num),
                         NA_real_, hw70_num),
    stunted    = if_else(hw70_clean < -200, 1, 0)
  ) %>%
  filter(!is.na(hw70_clean))

# ---- Readable factor labels ----
dhs$residence <- factor(dhs$v025, levels = c(1, 2), labels = c("Urban", "Rural"))
dhs$wealth    <- factor(dhs$v190, levels = 1:5,
                        labels = c("Q1 (poorest)", "Q2", "Q3", "Q4", "Q5 (richest)"))
dhs$sex       <- factor(dhs$b4, levels = c(1, 2), labels = c("Male", "Female"))

cat("Analysable records:", nrow(dhs), "\n")
cat("Unique clusters (v001):", length(unique(dhs$v001)), "\n\n")

# ---- Survey design ----
design <- svydesign(ids = ~v001, weights = ~v005, data = dhs)

# ---- Write results to file ----
sink(out_path)

cat("=== R survey-weighted prevalence (BDHS-2022, KR file) ===\n\n")

overall <- svymean(~stunted, design)
cat(sprintf("Overall weighted prevalence: %.4f (%.2f%%)\n",
            coef(overall)[1], coef(overall)[1] * 100))
cat(sprintf("Standard error:             %.4f\n\n", SE(overall)[1]))

cat("By residence:\n")
print(round(coef(svyby(~stunted, ~residence, design, svymean)), 4))
cat("\n")

cat("By wealth quintile:\n")
print(round(coef(svyby(~stunted, ~wealth, design, svymean)), 4))
cat("\n")

cat("By sex:\n")
print(round(coef(svyby(~stunted, ~sex, design, svymean)), 4))
cat("\n")

cat("Comparison with Python:\n")
cat("  Python weighted prevalence (full cohort): 0.232\n")
cat("  R survey-weighted prevalence (full cohort): see above\n")
cat("  Expected: agreement to within 0.005\n")

sink()

cat("Output written to:", out_path, "\n")