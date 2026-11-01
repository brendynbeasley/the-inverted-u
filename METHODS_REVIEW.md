# Methods review: Aghion, Bloom, Blundell, Griffith & Howitt (2005)

- **Paper:** Philippe Aghion, Nick Bloom, Richard Blundell, Rachel Griffith and Peter Howitt, "Competition and
  Innovation: An Inverted-U Relationship," *Quarterly Journal of Economics* 120(2), May 2005, pp. 701–728.
  doi:10.1162/0033553053970214.
- **Statistical focus:** the exponential quadratic Poisson estimates of citation-weighted patents on competition
  (one minus the Lerner index) in Table I, column (2), with the implied peak near the median competition of 0.95;
  and the neck-and-neck interaction estimates in Table III that support the model's fifth proposition.
- **Review standard:** current AEA Data and Code Availability Policy; standard reporting of estimates,
  uncertainty, inference choices and sample construction; for the theory section, internal consistency of the
  formal results, explicit assumptions and the testability of the predictions.
- **What was read:** the full published article (the copy openly posted in Harvard University's DASH repository,
  handle 1/4481507), including Tables I–IV, Figures I–III and Appendix 1. The October 2002 NBER working paper
  (w9269) was skimmed for its abstract. The 2004 UCL working paper the article cites for details of the
  instruments was not read, and neither was Bloom and Van Reenen (2002), which it cites for the data cleaning.

## Methods summary

**Research design.** An observational industry-year panel combined with a theoretical model. The empirical part
estimates the shape of the relationship between product market competition and innovation, first by Poisson
regression with year and industry effects, then with a control function that uses policy reforms as instruments
for competition. The theory part is a step-by-step innovation model with duopolists in a continuum of sectors,
solved in closed form for the case where the technology gap is at most one step.

**Sampling strategy.** Firms listed on the London Stock Exchange (accounts from Datastream) matched to the NBER
patent database of US patents. The patent sample is all listed firms whose names begin with "A" to "L" plus all
large R&D firms (p. 704). Firms involved in large mergers or acquisitions, firms with missing data and firms
with fewer than three consecutive years of data were removed (pp. 704 and 727). The Lerner index and technology
gap are computed from the entire population of listed firms in each industry, not only the patent subsample
(pp. 705 and 727).

**Sample size.** 311 firms in seventeen two-digit SIC industries, 1973–1994, giving an unbalanced panel of 354
industry-year observations (67 in the five-year-average version).

**Inclusion and exclusion criteria.** As above. The rule for when an industry-year has "a sufficient number of
firms" to enter the panel is not stated (p. 704).

**Independent and dependent variables.** Dependent: the average across a two-digit industry's sample firms of
citation-weighted patents, dated by application year. Main regressor: competition
c_jt = 1 − (1/N_jt) Σ l_it, where l_it is operating profit net of depreciation, provisions and a financial cost
of capital (8.5% of a perpetual-inventory capital stock), divided by sales (equation 1, footnote 7). Extension
variable: the technology gap m_jt, the industry average of (TFP_F − TFP_i)/TFP_F (equation 12).

**Statistical methods.** Poisson quasi-maximum-likelihood on the first moment E[p | c, x] = exp(g(c) + x′β),
with g quadratic (the "exponential quadratic") and, as a check, a spline estimated following Ai and Chen (2003).
Endogeneity is handled by a control function: a reduced form for competition on policy instruments (Single
Market Program, Monopolies and Mergers Commission remedies, privatizations; Table II) and other instruments,
whose residual enters the Poisson moment (equations 5 and 6). The technology-gap predictions are tested by a
linear regression of the gap on competition and by interacting competition and its square with the gap.

**Missing data treatment.** Firms with missing data were dropped before the panel was built. Industry-years with
too few firms are absent, which makes the panel unbalanced. R&D was not a mandatory reporting item in the UK
before 1990 (footnote 10), so the R&D check uses a much smaller sample. No imputation is described.

**Stated limitations.** The authors note the mutual endogeneity of competition and innovation (Section II.D),
the small R&D sample (footnote 10), and that the standard errors in column (4) of Table I and columns (3) and (4)
of Table III are not corrected for the estimated control function (table notes).

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Competition, Poisson, year effects | 152.80 (s.e. 55.74), log points per unit of competition | Table I, col. (1) | Linear term of the exponential quadratic, no industry effects | A causal effect; it mixes permanent cross-industry differences with within-industry variation |
| Competition squared, same column | −80.99 (29.61) | Table I, col. (1) | Curvature | That the turning point lies inside the data without a test at the endpoints |
| Competition, year and industry effects (preferred) | 387.46 (67.74) | Table I, col. (2) | Linear term identified from within-industry variation over time | Causality; standard errors are not described as robust or clustered |
| Competition squared, preferred | −204.55 (36.17) | Table I, col. (2) | Curvature; with col. (2)'s linear term implies a peak at c = 0.947 (computed from the reported coefficients) | The precision of the peak; no confidence interval for it is reported |
| Joint significance, preferred | 38.34, p = 0.00 | Table I, col. (2) | Likelihood-ratio statistic for both competition terms | That the relationship is inverted-U rather than monotone over the observed range (a joint test cannot distinguish them) |
| Five-year averages | 819.44 (265.63) and −434.43 (141.43), 9.97 (p = 0.01), N = 67 | Table I, col. (3) | Same specification on period averages | Robustness to the period boundaries, which are uneven (first period seven years, footnote 9) |
| Control-function estimates | 385.13 (67.56) and −204.83 (36.06) | Table I, col. (4) | Exponential quadratic with the reduced-form residual included | Correct inference; standard errors not corrected for the generated regressor |
| Policy instruments in reduced form | 10.11, p = 0.002 | Table I, col. (4) | Joint significance of the policy instruments for competition | Instrument strength in the modern sense, or exclusion (that the reforms affected patenting only through margins) |
| Control function coefficient | 4.38 (4.04) | Table I, col. (4) | Coefficient on the reduced-form residual | Absence of endogeneity; the test has low power at this precision |
| Reduced-form R² | 0.801 | Table I, col. (4) | Fit of competition on instruments and fixed effects | Explanatory power of the excluded instruments alone (the fixed effects are included) |
| Median competition | 0.95 | Section II.C, p. 707; Table IV | Where the typical industry-year sits; the text says the peak lies near it | How many observations lie on each side of the peak (not reported) |
| Technology gap on competition | 2.858 (0.400); with industry effects 0.942 (0.419) | Table III, cols. (1)–(2) | Proposition 4: the gap rises with competition | A model-specific mechanism; TFP spread can rise with competition for other reasons |
| Interactions with the gap, year and industry effects | c × gap 3.82 (2.66); c² × gap −3.84 (2.78); joint 7.93, p = 0.02 | Table III, col. (4) | Proposition 5: the shape differs with neck-and-neckness | The size of the difference; each term is individually insignificant and small next to the main terms (424.46 and −222.9) |
| Citation-weighted patents | mean 6.65, s.d. 8.43, median 3.35, range 0–45 | Table IV | Scale and skew of the dependent variable | Firm-level innovation; it is an industry average |
| One minus Lerner | mean 0.95, s.d. 0.023, range 0.87–0.99 | Table IV | Variation in the regressor | That 0.87–0.99 spans enough of the theoretical range to see both arms of the U |
| Technology gap | mean 0.49, s.d. 0.155, range 0.080–0.81 | Table IV | Average distance to the TFP frontier | Comparability with gap measures built from other productivity estimates |
| Lerner index | averages 4%; 13% in office and computing machinery (1973) to below 1% in motor vehicles (1982) | Appendix 2, p. 727 | The spread of margins across industry-years | Market power in the price-over-marginal-cost sense; it is an accounting margin |

## Interpretation notes

- **What carries the result.** The inverted U is identified from movements in industry margins over 22 years
  within seventeen industries. The regressor varies over a narrow band (standard deviation 0.023), so the
  quadratic is fitted across margins between about 1% and 13%.
- **The peak is not given with an interval.** The coefficients in column (2) imply a peak at a competition value
  of about 0.947, very close to the median of 0.95, which is what the text describes. The paper does not report a
  standard error for this point or a test that the slope changes sign inside the observed range (the test later
  formalized by Lind and Mehlum, 2010). The joint likelihood-ratio statistic shows curvature, not that both arms of
  the U are present.
- **Inference choices are not described.** The tables call the numbers in brackets standard errors without saying
  whether they are the conventional Poisson ones, robust ones, or clustered by industry. With seventeen industries
  and annual data, serial correlation within an industry is likely, and the conventional standard errors would
  then be too small. This is a reporting gap, not a demonstrated error.
- **Labelling.** The text on p. 719 refers to "columns 3 and 4 of Table II" for the neck-and-neck results, which
  appear in Table III. The notes to Tables I and III describe "likelihood ratio test-statistics and P-value from
  the F-test," which combines two different tests. The note to Table III mentions a control function for columns
  (3) and (4) that the text does not otherwise describe.
- **Proposition 5 in the data.** Figure III shows a higher and steeper curve for the below-median-gap subsample.
  The continuous interactions in Table III, column (4), are jointly significant, but taken at face value they
  shift the implied peak only slightly (from about 0.952 at a zero gap to about 0.948 at the mean gap of 0.49,
  computed from the reported coefficients) and make the curve slightly more, not less, curved as the gap rises.
  The figure and the table may summarize different specifications.
- **Sample selection.** The "A" to "L" plus large-R&D design is not random with respect to innovation, and
  removing firms involved in large mergers removes some of the events that change both competition and
  innovation. The direction of any bias is not discussed.
- **Measurement.** The Lerner index is an accounting margin net of an assumed 8.5% cost of capital. The authors
  report that the shape survives dropping the capital charge (footnote 7). Patents are counted at the US patent
  office for UK firms, which captures their internationally important inventions and may miss domestic ones.
- **Data and code availability.** No replication package is described. This was common for the period and is a
  gap against today's standard, not a criticism of the authors' conduct.
- **Published reassessments.** Aamir Hashmi, "Competition and Innovation: The Inverted-U Relationship Revisited,"
  *Review of Economics and Statistics* 95(5), 2013, pp. 1653–1668, finds a mildly negative relationship in US
  publicly traded manufacturing firms using an exchange-rate instrument, and reconciles it with this paper by
  arguing that UK industries are more neck and neck than US ones (from the published abstract). Juan A. Correa,
  "Innovation and competition: An unstable relationship," *Journal of Applied Econometrics* 27(1), 2012,
  pp. 160–166, re-examines the stability of the result; its content was not read here. Neither is a documented
  correction of an analytical error.
- **How this repository relates.** The rerun here applies the same definitions to US listed manufacturers in
  2011–2020 with public data. It is a new test of the same hypothesis, not a reproduction of the paper's numbers.
  It finds no inverted U within industries; a hump appears only when industries are compared with one another.

## Unanswered questions

- How many of the 354 industry-years lie above and below the implied peak, and how precisely is the peak located?
- Are the reported standard errors robust to within-industry serial correlation?
- What minimum number of firms qualified an industry-year for the panel, and how many industry-years did that rule
  remove?
- How large is the first stage of the policy instruments alone, excluding the "other instruments" (US and French
  industry variables), and do the results hold with the policy instruments alone?
- Does the inverted U survive when the five or so industries with the most patents are dropped one at a time? The
  paper reports that each of the top four innovating industries shows part or all of an inverted U (citing the
  2004 working paper), which is a weaker statement.
- How was TFP estimated for the technology gap (production function, input shares, deflators)?

## Items requiring expert verification

- Whether the bracketed numbers in Tables I and III are conventional Poisson standard errors, and how clustering
  by industry would change the joint tests.
- Whether the interaction signs in Table III, column (4), match the steeper-curve pattern drawn in Figure III, or
  whether the figure comes from a separate subsample regression not reported in the table.
- The construction and timing of the Single Market Program instrument (the Cecchini ranking of three-digit
  industries mapped to two-digit industries), described only in the 2004 working paper.
- Whether the structural-break argument in Correa (2012), which was not read for this review, affects the
  preferred specification.
- The equivalence of the Ai and Chen (2003) spline estimator used for Figure II with the exponential quadratic in
  the region where data are sparse (the tails of the 0.87–0.99 range).
