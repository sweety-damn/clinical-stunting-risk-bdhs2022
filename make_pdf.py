from pathlib import Path
import html as _html

PROJECT = Path.home() / "clinical-readmission-risk"

CSS = """
@page { size: A4; margin: 2.2cm 2.4cm; }
body { font-family: "Times New Roman", Georgia, serif; font-size: 11.5pt;
       line-height: 1.55; color: #111; max-width: 19cm; margin: 0 auto; }
h1 { font-size: 17pt; line-height: 1.3; margin: 0 0 0.4em 0; text-align: left; }
h2 { font-size: 13pt; margin: 1.6em 0 0.5em 0; border-bottom: 0.6pt solid #999;
     padding-bottom: 0.2em; }
h3 { font-size: 11.5pt; margin: 1.2em 0 0.3em 0; }
p { margin: 0 0 0.7em 0; text-align: justify; }
.meta { font-size: 10.5pt; margin-bottom: 1.4em; }
.abstract { background: #f7f7f7; border-left: 2.5pt solid #555;
            padding: 0.8em 1em; margin: 1.2em 0; font-size: 10.8pt; }
.abstract p { margin-bottom: 0.55em; }
table { border-collapse: collapse; width: 100%; margin: 0.6em 0 1em 0;
        font-size: 9.8pt; page-break-inside: avoid; }
th, td { border: 0.5pt solid #555; padding: 3.5pt 6pt; text-align: left; }
th { background: #e9e9e9; font-weight: bold; }
td.num, th.num { text-align: right; }
.caption { font-size: 9.8pt; font-weight: bold; margin: 1em 0 0.25em 0; }
.refs p { font-size: 10pt; text-indent: -1.4em; padding-left: 1.4em;
          margin-bottom: 0.45em; text-align: left; }
hr { border: none; border-top: 0.5pt solid #bbb; margin: 1.6em 0; }
.small { font-size: 9.8pt; }
"""

HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Calibration and subgroup fairness of a childhood stunting risk model</title>
<style>""" + CSS + """</style></head><body>
"""

PART_1 = """
<h1>Calibration and subgroup fairness of a childhood stunting risk model:
a cross-sectional analysis of the Bangladesh Demographic and Health Survey 2022</h1>

<p class="meta"><b>Sweety Akter</b><br>
BRAC University, Dhaka, Bangladesh<br>
Correspondence: sheikhtanha740@gmail.com</p>

<hr>

<h2>Abstract</h2>
<div class="abstract">
<p><b>Background:</b> Childhood stunting affects roughly one in four children under five in Bangladesh. Machine learning models are increasingly proposed for risk stratification, but published reports typically emphasise discrimination (area under the receiver operating characteristic curve, AUROC) and rarely examine calibration or subgroup performance. This study evaluated a stunting risk model on population health survey data, with calibration and subgroup fairness as primary outcomes rather than secondary considerations.</p>

<p><b>Methods:</b> We conducted a secondary analysis of the 2022 Bangladesh Demographic and Health Survey (BDHS) Kids Recode. The outcome was stunting, defined as a height-for-age z-score below &minus;2 standard deviations using the WHO 2006 growth standards. Of 8,784 child records, 13 had implausible anthropometric measurements and 4,666 had missing outcome data, leaving 4,105 children in 670 enumeration areas (weighted prevalence 23.2%). Thirteen predictors were restricted to information plausibly available before anthropometric assessment. A regularised logistic regression was compared with a gradient-boosted tree model (XGBoost). Models were trained on 3,315 children in 536 enumeration areas and evaluated on 790 children in 134 enumeration areas, with no cluster contributing to both arms. Performance was assessed by AUROC, Brier score with bootstrap 95% confidence intervals, and expected calibration error (ECE) with 10 quantile bins. Subgroup metrics were computed separately by residence, wealth quintile, and sex. A random split was additionally fitted to quantify the cost of ignoring the survey&rsquo;s cluster design.</p>

<p><b>Results:</b> Logistic regression achieved AUROC 0.652, Brier score 0.169 (95% CI 0.154&ndash;0.184), and ECE 0.028. XGBoost achieved AUROC 0.651, Brier score 0.171 (0.155&ndash;0.187), and ECE 0.043. Discrimination and calibration were similar for rural and urban children (AUROC 0.648 vs 0.660; ECE 0.033 vs 0.032). Within every wealth quintile the model&rsquo;s Brier score was within 0.005 of the base-rate benchmark, indicating no meaningful improvement over predicting the group mean at that level. Discrimination differed by sex: AUROC 0.609 for boys versus 0.692 for girls, with nearly identical calibration (ECE 0.043 vs 0.045). The random-split comparison inflated AUROC by only 0.002, indicating minimal cluster leakage with these individual and household-level predictors.</p>

<p><b>Conclusions:</b> A regularised logistic regression matched a gradient-boosted model on discrimination and calibrated better. The model performed fairly across residence and wealth, but discriminated stunting risk substantially better for girls than for boys. Prediction studies of childhood undernutrition should report calibration and subgroup analyses alongside AUROC, and should evaluate models on held-out clusters when the underlying survey uses a clustered design.</p>
</div>

<p class="small"><b>Keywords:</b> childhood stunting; Bangladesh; Demographic and Health Survey; calibration; fairness; clinical prediction model; health equity</p>

<hr>

<h2>1. Introduction</h2>

<p>Childhood stunting &mdash; linear growth failure reflected in a height-for-age z-score below &minus;2 standard deviations &mdash; is the most prevalent form of undernutrition globally and is associated with impaired cognitive development, reduced educational attainment, and lower adult productivity [1,2]. In Bangladesh, the 2022 Demographic and Health Survey estimated that approximately 24% of children under five were stunted, a substantial decline from earlier decades but still a burden affecting roughly one in four children [3].</p>

<p>Because stunting is identified through anthropometric measurement, and because measurement requires trained personnel and equipment, there is interest in identifying high-risk children from information collected earlier &mdash; by community health workers, at household visits, or from routine administrative records. Machine learning models trained on nationally representative survey data have been proposed for this purpose, and several studies report AUROC values in the 0.62 to 0.72 range [4]. A recent study extended this work across BDHS rounds with explicit attention to calibration and subgroup fairness, using the 2018 and 2022 rounds as temporal hold-out sets [5].</p>

<p>However, three methodological issues remain under-addressed. First, most reports emphasise discrimination and do not report calibration &mdash; the agreement between predicted probabilities and observed frequencies. Calibration matters more than discrimination when a model&rsquo;s output is used to set a threshold for referral or resource allocation, because a poorly calibrated model will systematically over- or under-estimate risk even when it ranks children correctly [6,7]. Second, the Demographic and Health Surveys use a multistage cluster design; children within an enumeration area are not independent. If train and test sets share enumeration areas, model performance can be inflated by cluster-level memorisation, and the resulting estimate does not reflect how the model would perform in a genuinely new setting [8]. Temporal hold-out, as used in previous work [5], addresses drift between survey rounds but not the correlation between children sampled from the same community. Third, subgroup performance is rarely reported. A model that performs well on average may discriminate or calibrate poorly for specific groups &mdash; by sex, by residence, or by household wealth &mdash; and such disparities are directly relevant to equity in any downstream use [9,10].</p>

<p>This study addresses all three issues in a single analysis. We developed a stunting risk model on the 2022 BDHS Kids Recode using predictors available before anthropometric measurement, evaluated it on held-out enumeration areas, compared a regularised logistic regression with a gradient-boosted tree model, and reported calibration and subgroup performance by residence, wealth quintile, and sex. Our aim was not to maximise predictive accuracy, but to characterise honestly what a simple model can and cannot do with routinely collected survey data, and to identify where its performance is uneven.</p>
"""

PART_2 = """
<h2>2. Methods</h2>

<h3>2.1 Data source and study design</h3>

<p>We conducted a secondary analysis of the 2022 Bangladesh Demographic and Health Survey (BDHS), a nationally representative household survey implemented under the DHS Program [3]. Data were obtained from the Kids Recode (KR) file, which contains one record for each child born in the five years preceding the interview to an interviewed woman, with maternal and household characteristics linked to each child record. The 2022 BDHS used the DHS-VIII recode structure.</p>

<p>The DHS Program grants access to registered users under a data use agreement that prohibits redistribution of microdata and requires that no attempt be made to identify individual respondents. All analyses were conducted on de-identified data on a personal computer. Only derived code and aggregate results are publicly shared.</p>

<h3>2.2 Cohort construction</h3>

<p>The KR file contained 8,784 child records. We excluded 13 records in which the height-for-age z-score was recorded as a special code indicating an implausible measurement (codes 9996, 9997, or 9998, reflecting height out of plausible range, age in days out of plausible range, or a flagged case). We further excluded 4,666 records with a missing height-for-age z-score, typically because the child was not present or not measured. The final analysable cohort comprised <b>4,105 children in 670 enumeration areas</b>.</p>

<p>Missingness was not concentrated in any subgroup: the proportion of children without a valid z-score was 52.4% in rural and 54.5% in urban areas, and ranged from 52.6% to 54.3% across wealth quintiles. This flat pattern suggests that the analysable sample is demographically representative of the full KR file, which is relevant to the interpretation of the subgroup results.</p>

<h3>2.3 Outcome</h3>

<p>The primary outcome was stunting, defined as a height-for-age z-score below &minus;2 standard deviations relative to the WHO 2006 Child Growth Standards [2], corresponding to the recoded variable <span class="small"><code>hw70 &lt; &minus;200</code></span>. The unweighted prevalence in the analysable cohort was 23.5%; the prevalence weighted by the child sampling weight (<span class="small"><code>v005</code></span>) was 23.2%, closely matching the official BDHS-2022 estimate of approximately 24% [3]. This agreement was used as a validation check on file selection, outcome definition, and weight handling.</p>

<h3>2.4 Predictors</h3>

<p>Thirteen predictors were selected, restricted to information plausibly available before anthropometric measurement:</p>

<ul>
<li><b>Child:</b> age in months, sex, birth order, preceding birth interval with a firstborn indicator.</li>
<li><b>Maternal:</b> education level, body mass index with a missing indicator.</li>
<li><b>Household:</b> wealth quintile, urban or rural residence, source of drinking water, type of toilet facility.</li>
<li><b>Region:</b> administrative region.</li>
</ul>

<p>Antenatal care visits were excluded from the primary model. In this dataset, missingness for this variable was deterministically age-dependent: 1.0% missing among children under 12 months, 2.8% at 12&ndash;24 months, 20.9% at 24&ndash;36 months, and 100% among children aged 36 months or older. This pattern reflects the DHS-8 maternity-care module, which collects antenatal information only for births within a three-year recall window. Any missingness indicator would therefore have encoded child age directly, introducing a form of leakage from the questionnaire design rather than from biology. Excluding the variable was the conservative choice.</p>

<p>The preceding birth interval is structurally missing for firstborn children. Rather than imputing a biologically implausible value, we set the interval to zero and added a binary firstborn indicator, so that the model can distinguish &ldquo;no preceding birth&rdquo; from &ldquo;a very short interval.&rdquo; Maternal BMI was missing for only two children (0.05%); we retained these children, imputing the median and adding a binary missing indicator.</p>

<h3>2.5 Model development</h3>

<p>Two models were fitted. The first was a logistic regression with L2 regularisation on standardised continuous predictors and one-hot encoded categorical predictors. The second was a gradient-boosted tree model (XGBoost) with 300 trees, maximum depth 4, learning rate 0.05, and row and column subsampling at 0.8. Both models used identical predictor sets and identical preprocessing within a scikit-learn pipeline.</p>

<h3>2.6 Train/test split</h3>

<p>Because the DHS uses a multistage cluster design, children within the same enumeration area share household and community context and are not independent observations. We therefore split the cohort by enumeration area using grouped random sampling, assigning 80% of clusters to training and 20% to testing. This produced <b>3,315 children in 536 clusters for training and 790 children in 134 clusters for testing, with zero clusters appearing in both arms</b>. Prevalence was similar across arms (23.6% training, 23.2% testing).</p>

<p>To quantify the consequence of ignoring the cluster structure, we additionally fitted the same logistic model on a conventional random split of children, in which approximately 450 of the 670 clusters appeared in both arms. The difference in AUROC between the random and grouped splits is reported as the leakage cost.</p>

<h3>2.7 Evaluation</h3>

<p>Discrimination was assessed by AUROC. Probabilistic accuracy was assessed by the Brier score, with 95% confidence intervals obtained from 1,000 bootstrap resamples of the test set. Calibration was assessed by expected calibration error (ECE) using 10 quantile bins, and by reliability diagrams plotting mean predicted probability against observed prevalence within each bin. Quantile binning was used rather than equal-width binning because predicted probabilities from imbalanced classifiers are concentrated near the base rate, and equal-width bins would place most predictions in a single bin and conceal miscalibration.</p>

<h3>2.8 Subgroup fairness analysis</h3>

<p>All three metrics &mdash; AUROC, Brier score, and ECE &mdash; were computed separately for subgroups defined by residence (rural, urban), wealth quintile (1 = poorest to 5 = richest), and sex. For wealth quintiles we additionally computed the base-rate Brier score (the score obtained by predicting the constant group prevalence for every child), because Brier score is not directly comparable across groups with different outcome prevalence. Subgroup differences are reported as the maximum minus the minimum across groups.</p>

<h3>2.9 Software</h3>

<p>Analyses were conducted in Python 3 using pandas, scikit-learn, XGBoost, and matplotlib. Calibration functions were implemented in a reusable module and are available in the project repository. Reporting follows the TRIPOD+AI guidance for prediction models [11].</p>
"""

PART_3 = """
<h2>3. Results</h2>

<h3>3.1 Overall model performance</h3>

<p>On the held-out set of 134 enumeration areas (n = 790, prevalence 23.2%), logistic regression achieved AUROC 0.652, Brier score 0.169 (95% CI 0.154&ndash;0.184), and ECE 0.028. XGBoost achieved AUROC 0.651, Brier score 0.171 (0.155&ndash;0.187), and ECE 0.043 (Table 1).</p>

<p class="caption">Table 1. Overall performance on the grouped test set (n = 790).</p>
<table>
<thead><tr><th>Model</th><th class="num">AUROC</th><th class="num">Brier (95% CI)</th><th class="num">ECE</th></tr></thead>
<tbody>
<tr><td>Logistic regression</td><td class="num">0.652</td><td class="num">0.169 (0.154&ndash;0.184)</td><td class="num">0.028</td></tr>
<tr><td>XGBoost</td><td class="num">0.651</td><td class="num">0.171 (0.155&ndash;0.187)</td><td class="num">0.043</td></tr>
</tbody></table>

<p>The two models were indistinguishable on discrimination (difference in AUROC = &minus;0.001) and their Brier confidence intervals overlapped substantially. However, ECE was 52% higher for XGBoost (0.043 vs 0.028), indicating meaningfully worse calibration despite equivalent ranking ability.</p>

<h3>3.2 Leakage cost</h3>

<p>The same logistic model fitted on a conventional random split achieved AUROC 0.653, compared with 0.651 on the grouped split &mdash; a difference of +0.002 (Table 2). This small gap is consistent with the nature of the predictors: all are measured at the individual, maternal, or household level, and none encodes enumeration-area identity. With a small average cluster size (approximately six children), cluster-level memorisation has little opportunity to operate. The grouped split nonetheless remains the methodologically correct choice, because the near-zero cost is an empirical property of this predictor set rather than a general property of DHS prediction problems.</p>

<p class="caption">Table 2. Leakage cost of a conventional random split versus the grouped split.</p>
<table>
<thead><tr><th>Split</th><th class="num">AUROC</th><th class="num">Difference vs grouped</th></tr></thead>
<tbody>
<tr><td>Grouped by enumeration area</td><td class="num">0.651</td><td class="num">&mdash;</td></tr>
<tr><td>Random split of children</td><td class="num">0.653</td><td class="num">+0.002</td></tr>
</tbody></table>

<h3>3.3 Subgroup performance</h3>

<p><b>Residence.</b> Performance was similar for rural (n = 501) and urban (n = 289) children. AUROC was 0.648 and 0.660 respectively (difference 0.013), Brier score 0.173 and 0.163 (difference 0.010), and ECE 0.033 and 0.032 (difference 0.001) (Table 3).</p>

<p class="caption">Table 3. Subgroup performance by residence.</p>
<table>
<thead><tr><th>Group</th><th class="num">n</th><th class="num">Events</th><th class="num">AUROC</th><th class="num">Brier</th><th class="num">ECE</th></tr></thead>
<tbody>
<tr><td>Rural</td><td class="num">501</td><td class="num">119</td><td class="num">0.648</td><td class="num">0.173</td><td class="num">0.033</td></tr>
<tr><td>Urban</td><td class="num">289</td><td class="num">64</td><td class="num">0.660</td><td class="num">0.163</td><td class="num">0.032</td></tr>
<tr><td>Maximum minus minimum</td><td class="num"></td><td class="num"></td><td class="num">0.013</td><td class="num">0.010</td><td class="num">0.001</td></tr>
</tbody></table>

<p><b>Wealth quintile.</b> Observed prevalence fell steeply from 36.0% in the poorest quintile to 8.5% in the richest, so Brier scores are not comparable across quintiles in absolute terms. The base-rate Brier score &mdash; the score obtained by predicting the constant group prevalence for every child &mdash; fell from 0.230 in quintile 1 to 0.078 in quintile 5. In every quintile, the fitted model&rsquo;s Brier score was within 0.005 of this benchmark (Table 4). In other words, at the level of wealth quintiles, the model added essentially no information beyond the group mean.</p>

<p>AUROC, which is prevalence-invariant, ranged from 0.548 in quintile 3 to 0.673 in quintile 5 (difference 0.125). The quintile 5 estimate, however, rests on only 13 events and should be regarded as unstable.</p>

<p class="caption">Table 4. Subgroup performance by wealth quintile.</p>
<table>
<thead><tr><th>Quintile</th><th class="num">n</th><th class="num">Events</th><th class="num">Prevalence</th><th class="num">Base-rate Brier</th><th class="num">Model Brier</th><th class="num">AUROC</th><th class="num">ECE</th></tr></thead>
<tbody>
<tr><td>Q1 (poorest)</td><td class="num">150</td><td class="num">54</td><td class="num">0.360</td><td class="num">0.230</td><td class="num">0.230</td><td class="num">0.576</td><td class="num">0.074</td></tr>
<tr><td>Q2</td><td class="num">147</td><td class="num">41</td><td class="num">0.279</td><td class="num">0.201</td><td class="num">0.197</td><td class="num">0.596</td><td class="num">0.069</td></tr>
<tr><td>Q3</td><td class="num">147</td><td class="num">36</td><td class="num">0.245</td><td class="num">0.185</td><td class="num">0.185</td><td class="num">0.548</td><td class="num">0.094</td></tr>
<tr><td>Q4</td><td class="num">193</td><td class="num">39</td><td class="num">0.202</td><td class="num">0.161</td><td class="num">0.161</td><td class="num">0.582</td><td class="num">0.070</td></tr>
<tr><td>Q5 (richest)</td><td class="num">153</td><td class="num">13</td><td class="num">0.085</td><td class="num">0.078</td><td class="num">0.079</td><td class="num">0.673</td><td class="num">0.066</td></tr>
</tbody></table>

<p><b>Sex.</b> Calibration was nearly identical for boys (n = 408, ECE 0.043) and girls (n = 382, ECE 0.045), and Brier scores differed by only 0.005. Discrimination, however, differed substantially: AUROC was 0.609 for boys and 0.692 for girls, a gap of 0.083 (Table 5).</p>

<p class="caption">Table 5. Subgroup performance by sex.</p>
<table>
<thead><tr><th>Group</th><th class="num">n</th><th class="num">Events</th><th class="num">AUROC</th><th class="num">Brier</th><th class="num">ECE</th></tr></thead>
<tbody>
<tr><td>Male</td><td class="num">408</td><td class="num">89</td><td class="num">0.609</td><td class="num">0.167</td><td class="num">0.043</td></tr>
<tr><td>Female</td><td class="num">382</td><td class="num">94</td><td class="num">0.692</td><td class="num">0.172</td><td class="num">0.045</td></tr>
<tr><td>Maximum minus minimum</td><td class="num"></td><td class="num"></td><td class="num">0.083</td><td class="num">0.005</td><td class="num">0.003</td></tr>
</tbody></table>

<p>This is the study&rsquo;s principal fairness finding: the model ranks stunting risk among girls considerably better than among boys, while remaining equally well calibrated for both.</p>
"""

PART_4 = """
<h2>4. Discussion</h2>

<p>In a cohort of 4,105 children from the 2022 Bangladesh DHS, a regularised logistic regression using thirteen routinely collected predictors achieved modest discrimination (AUROC 0.652) and good calibration (ECE 0.028) on a held-out set of enumeration areas. A gradient-boosted model of considerably greater complexity matched this performance on discrimination but calibrated worse. Subgroup analysis found no meaningful disparity by residence and no advantage over the group mean at the level of wealth quintiles, but a substantial disparity by sex in discrimination, with no corresponding disparity in calibration.</p>

<p>The comparison between the two models is consistent with a growing body of evidence that complex models do not automatically outperform simple, well-specified ones on tabular clinical and survey data [12]. The practical implication is straightforward: when a logistic model achieves equivalent discrimination and better calibration, it should be preferred, both because it is more interpretable and because its probability estimates are more trustworthy. The ECE difference observed here (0.028 vs 0.043) is not trivial if a model&rsquo;s output is used to set a referral threshold.</p>

<p>The near-zero leakage cost deserves comment. We expected a grouped split to reduce apparent performance relative to a random split, because clustered survey data violate the independence assumption underlying standard cross-validation. In this analysis, the difference was only 0.002 in AUROC. The most plausible explanation is that the predictors carry no cluster-level information: they are individual, maternal, and household variables, and the coarsest of them &mdash; administrative region &mdash; has eight levels, far fewer than the 670 clusters. Cluster identity therefore has little to memorise. This is reassuring for this specific model, but it should not be generalised. Studies that include cluster-level covariates such as distance to a health facility, community wealth, or area-level food access would likely see a larger gap, and the grouped split should remain the default practice regardless of the observed cost.</p>

<p>The sex disparity in discrimination is the finding most in need of cautious interpretation. The model ranks risk among girls substantially better than among boys (AUROC 0.692 vs 0.609), while calibration is nearly identical. Two explanations are worth considering, and this dataset cannot distinguish between them.</p>

<p>The first is that the predictor set captures girls&rsquo; risk pathways more completely than boys&rsquo;. If, for example, maternal education and household wealth translate more consistently into feeding and care practices for girls than for boys in this population, then the same covariates would predict girls&rsquo; outcomes more accurately. The second explanation is statistical: with 89 and 94 events in the two groups, an AUROC difference of 0.083 is approximately two standard errors from zero. It is unlikely to be pure noise, but it is not so precisely estimated that it should be treated as a firm effect size. A larger test set, or replication in another survey round, would be needed to confirm the direction and magnitude.</p>

<p>Either way, the practical implication is the same. A model intended for screening should not be deployed without a subgroup evaluation that includes sex, because average performance can conceal a group for whom the model is substantially less useful. This is the argument that has been made forcefully in the algorithmic fairness literature [9,10], and it applies with equal force to models built on survey data as to those built on electronic health records.</p>

<p>The wealth-quintile results require careful reading. The apparent Brier-score gap between quintile 1 (0.230) and quintile 5 (0.079) is entirely a consequence of the prevalence gradient, not of differential model quality: predicting the constant group prevalence already yields those scores. The relevant comparison is between the model&rsquo;s Brier score and the base-rate benchmark within each quintile, and by that comparison the model adds almost nothing at the quintile level. This does not mean the model is useless &mdash; it discriminates within the cohort as a whole at AUROC 0.652 &mdash; but it does mean that the model&rsquo;s probabilities should not be interpreted as reflecting something more than the wealth gradient that the quintile variable already encodes. Reporting the base-rate benchmark alongside the Brier score, as we have done here, is a simple practice that prevents this misunderstanding.</p>

<h3>4.1 Implications for practice and future work</h3>

<p>Three implications follow. First, stunting risk models built from cross-sectional survey data should be evaluated with grouped splitting by enumeration area, and the leakage cost should be reported rather than assumed. Second, calibration should be reported alongside discrimination, with the base-rate benchmark made explicit for subgroup comparisons. Third, subgroup performance by sex should be a standard component of evaluation, not an optional extension.</p>

<p>Future work should extend the analysis in three directions. A sensitivity analysis restricted to children under 36 months, where antenatal care is available, would allow the contribution of maternity-care variables to be assessed without the age-based leakage that forced their exclusion here. External validation in a different BDHS survey round, or in a different country&rsquo;s DHS, would test whether the sex disparity replicates. And a decision-curve analysis would quantify the clinical utility of the model at plausible referral thresholds, which the present study did not address.</p>

<h2>5. Limitations</h2>

<p>Several limitations should be considered.</p>

<p>First, the analysis is cross-sectional and restricted to a single survey round. The model predicts association with stunting, not the effect of any intervention, and the results do not establish temporal or external validity.</p>

<p>Second, discrimination is modest. AUROC 0.652 is within the range reported by published BDHS stunting models, but it is not sufficient for individual-level clinical decision-making. The model cannot reliably identify children at substantially elevated risk, and should be regarded as a demonstration of methodology rather than a deployable screening tool.</p>

<p>Third, good calibration partly reflects prediction compression. Predicted probabilities span only approximately 0.10 to 0.42 around a base rate of 0.23. A model whose predictions cluster near the base rate will be trivially well calibrated. The ECE of 0.028 should be interpreted in that light: it indicates that the model is not badly miscalibrated, not that its probabilities carry substantial individual-level information.</p>

<p>Fourth, the wealth-quintile Brier scores are not comparable across quintiles because of the prevalence gradient, and the quintile 5 AUROC rests on only 13 events and is unstable.</p>

<p>Fifth, the sex disparity in AUROC is documented but not resolved. This study cannot distinguish between a genuine difference in how well the predictors capture boys&rsquo; risk pathways and a chance finding in a modest test set.</p>

<p>Sixth, antenatal care was excluded because its missingness was structurally age-dependent, which removes a clinically plausible predictor from the model.</p>

<p>Seventh, the model has not been externally validated in a separate population and should not be used in any real health setting without prospective validation.</p>

<h2>6. Conclusion</h2>

<p>A regularised logistic regression matched a gradient-boosted model on discrimination and calibrated better when predicting childhood stunting from 2022 Bangladesh DHS data evaluated on held-out enumeration areas. Calibration and discrimination were fair across residence, the model added no information beyond the group mean at the level of wealth quintiles, and discrimination was substantially better for girls than for boys despite equivalent calibration. These findings support three reporting practices for prediction models built on clustered survey data: grouped splitting by cluster, calibration with an explicit base-rate benchmark, and subgroup metrics reported as a standard component of evaluation.</p>

<h2>Statements</h2>

<p><b>Ethics approval.</b> This study is a secondary analysis of de-identified survey data obtained under a registered DHS Program data use agreement. No individual or household can be identified. Ethical approval was not required for secondary analysis of de-identified public data.</p>

<p><b>Data availability.</b> The DHS microdata are available to registered users from the DHS Program (https://dhsprogram.com/data/) under a data use agreement that prohibits redistribution. The microdata are therefore not included in the project repository.</p>

<p><b>Code availability.</b> Analysis code, aggregate results, and figures are available at https://github.com/sweety-damn/clinical-stunting-risk-bdhs2022 under an MIT license.</p>

<p><b>Conflicts of interest.</b> The author declares no competing interests.</p>

<p><b>Funding.</b> This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.</p>

<h2>References</h2>
<div class="refs">
<p>1. Black RE, Victora CG, Walker SP, Bhutta ZA, Christian P, de Onis M, Ezzati M, Grantham-McGregor S, Katz J, Martorell R, Uauy R; Maternal and Child Nutrition Study Group. Maternal and child undernutrition and overweight in low-income and middle-income countries. <i>Lancet</i>. 2013;382(9890):427&ndash;451. doi:10.1016/S0140-6736(13)60937-X</p>

<p>2. de Onis M, Onyango AW, Borghi E, Siyam A, Nishida C, Siekmann J. Development of a WHO growth reference for school-aged children and adolescents. <i>Bull World Health Organ</i>. 2007;85(9):660&ndash;667. doi:10.2471/BLT.07.043497</p>

<p>3. National Institute of Population Research and Training (NIPORT) and ICF. <i>Bangladesh Demographic and Health Survey 2022: Final Report</i>. Dhaka, Bangladesh, and Rockville, Maryland, USA: NIPORT and ICF; 2024. Available from: https://dhsprogram.com/pubs/pdf/FR386/FR386.pdf</p>

<p>4. Talukder A, Ahammed B. Machine learning algorithms for predicting malnutrition among under-five children in Bangladesh. <i>Nutrition</i>. 2020;78:110861. doi:10.1016/j.nut.2020.110861</p>

<p>5. Haque MA, Kabir MA. Machine learning-based prediction of childhood stunting in Bangladesh: fairness and temporal robustness assessment. arXiv:2609.24386 [cs.LG]. 2026. doi:10.48550/arXiv.2609.24386</p>

<p>6. Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW; Topic Group &lsquo;Evaluating diagnostic tests and prediction models&rsquo; of the STRATOS initiative. Calibration: the Achilles heel of predictive analytics. <i>BMC Med</i>. 2019;17(1):230. doi:10.1186/s12916-019-1466-7</p>

<p>7. Steyerberg EW, Vickers AJ, Cook NR, Gerds T, Gonen M, Obuchowski N, Pencina MJ, Kattan MW. Assessing the performance of prediction models: a framework for traditional and novel measures. <i>Epidemiology</i>. 2010;21(1):128&ndash;138. doi:10.1097/EDE.0b013e3181c30fb2</p>

<p>8. Heeringa SG, West BT, Berglund PA. <i>Applied Survey Data Analysis</i>. 2nd ed. Boca Raton, FL: Chapman and Hall/CRC; 2017.</p>

<p>9. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. <i>Science</i>. 2019;366(6464):447&ndash;453. doi:10.1126/science.aax2342</p>

<p>10. Seyyed-Kalantari L, Zhang H, McDermott MBA, Chen IY, Ghassemi M. Underdiagnosis bias of artificial intelligence algorithms applied to chest radiographs in under-served patient populations. <i>Nat Med</i>. 2021;27(12):2176&ndash;2182. doi:10.1038/s41591-021-01595-0</p>

<p>11. Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. <i>BMJ</i>. 2024;385:e078378. doi:10.1136/bmj-2023-078378</p>

<p>12. Christodoulou E, Ma J, Collins GS, Steyerberg EW, Verbakel JY, Van Calster B. A systematic review shows no performance benefit of machine learning over logistic regression for clinical prediction models. <i>J Clin Epidemiol</i>. 2019;110:12&ndash;22. doi:10.1016/j.jclinepi.2019.02.004</p>
</div>

</body></html>
"""

full_html = HEAD + PART_1 + PART_2 + PART_3 + PART_4

out_html = PROJECT / "manuscript_print.html"
out_html.write_text(full_html, encoding="utf-8")

print("Written:", out_html)
print("Size:", len(full_html), "characters")
checks = {
    "title": "Calibration and subgroup fairness" in full_html,
    "abstract": "Abstract" in full_html,
    "table1": "0.169 (0.154" in full_html,
    "table5": "0.083" in full_html,
    "ref12": "jclinepi.2019.02.004" in full_html,
    "ref5_replaced": "2609.24386" in full_html,
    "no_placeholder": "Islam MM" not in full_html,
    "closing_html": full_html.rstrip().endswith("</html>"),
}
for k, v in checks.items():
    print(("  OK   " if v else "  FAIL ") + k)