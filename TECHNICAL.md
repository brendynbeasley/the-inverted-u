# Technical notes

This is the technical companion to the [README](README.md). It covers the data, the method, the full set of
test statistics and how to reproduce everything. Every table is in [results/FINDINGS.md](results/FINDINGS.md),
and a review of the original paper's methods is in [METHODS_REVIEW.md](METHODS_REVIEW.md).

## The original study

Philippe Aghion, Nick Bloom, Richard Blundell, Rachel Griffith and Peter Howitt, "Competition and Innovation: An
Inverted-U Relationship," *Quarterly Journal of Economics* 120(2), 2005, pp. 701–728. An unbalanced panel of 354
industry-years (311 London-listed firms, seventeen two-digit SIC industries, 1973–1994). Citation-weighted US
patents per firm are regressed on competition, one minus the industry's average Lerner index, and its square by
Poisson. Preferred estimates (Table I, column 2, year and industry effects): 387.46 (67.74) and −204.55
(36.17), implying a peak at 0.947 against a median competition of 0.95. A control function using UK policy
reforms leaves the estimates almost unchanged (385.13 and −204.83).

## Headline results

| | Industry-years | Linear term | Squared term | Peak | Lind–Mehlum p |
|---|---|---|---|---|---|
| Paper, UK 1973–94, year and industry effects | 354 | 387.46 (67.74) | −204.55 (36.17) | 0.947 | not reported |
| US 2011–2020, year and industry effects | 200 | 1.19 (3.11) | −0.23 (1.14) | outside data | 0.54 |
| US 2011–2020, year effects only | 200 | 19.73 (9.10) | −7.31 (3.47) | 1.35 [1.26, 1.44] | 0.024 |

- Within industries there is no relationship. The joint test on both terms gives χ² = 0.33 (p = 0.85), the
  linear-only slope is 0.56 (1.14), and quintile dummies give relative patent rates of 1.00, 1.04, 1.05, 1.03
  and 1.06.
- Across industries (year effects only) a hump appears, but 94% of industry-years lie left of the peak, and it
  reflects which industries patent, not changes in competition.
- No variant of the competition measure produces a within-industry inverted U. The sales-weighted measure gives
  a significant U (squared term 11.06, s.e. 2.67), and unweighted patent counts fall at high competition.
- Extension: the technology gap rises with competition (0.34, s.e. 0.06, year effects; 0.12, s.e. 0.03, within
  industries with a 90th-percentile frontier), as the model predicts. The interaction of competition with the gap
  runs opposite to the model's fifth proposition.

## Data

- **Accounts:** SEC Financial Statement Data Sets, 58 quarterly zips (2012q1 to 2026q2), from
  `https://www.sec.gov/files/dera/data/financial-statement-data-sets/{quarter}.zip`. 10-K filings only;
  consolidated full-year US-dollar values of us-gaap tags for revenue (largest of five tags), operating income,
  total costs and expenses, pretax income, interest expense, R&D, net property, plant and equipment (two tags) and
  assets. Each filer's SIC code, country and every name it has used come from the filing headers.
- **Patents:** Kogan, Papanikolaou, Seru and Stoffman data extended to 2025 (`KPSS_2025.zip`,
  `Match_patent_permco_permno_2025.zip`, from the KPSS2017 GitHub repository): patent number, filing date, forward
  citations and the owner's CRSP permco.
- **Assignee names:** PatentsView `g_assignee_disambiguated.tsv.zip`, release of December 31, 2024, from the Zenodo
  mirror (record 15783125), CC-BY 4.0.
- **Committed outputs of the build:** `data/processed/firm_years.csv.gz` (74,882 filer-years, fiscal 2010–2024)
  and `data/processed/patent_bridge.csv` (2,869 permco-to-CIK links with the names that made them). Raw files
  (about 6 GB) are downloaded by the build script and ignored by git. Downloaded 2026-11-01.

## Method

Rules fixed before estimation:

- **Sample:** fiscal years 2011–2020 (later filing years are not yet fully granted); US business address; SIC
  2000–3999; revenue of at least $10 million. Operating profit is the operating-income line, or else revenue less
  total costs and expenses (302 firm-years), or else pretax income plus interest (501). An industry-year needs
  five firms. Result: 13,583 firm-years, 200 two-digit industry-years.
- **Lerner index:** as in the paper, with the 8.5% capital charge applied to net plant and equipment (set to zero
  for 371 firm-years without it), winsorized at the pooled 1st and 99th percentiles:

```math
l_{it} = \frac{\pi_{it} - 0.085\,K_{it}}{S_{it}}, \qquad c_{jt} = 1 - \frac{1}{N_{jt}}\sum_{i \in j} l_{it}
```

- **Patents:** each patent weighted by its citations over the mean for its filing year; industry outcome is the
  mean over all sample firms, zeros included.
- **Patent attribution:** a KPSS permco is linked to an SEC filer when at least 3 patents (or 10%) carry an
  assignee name equal to one of the filer's normalized names; failing that, when the filer's name is the leading
  words of assignee names covering at least 10 patents and 25% of the permco's. A patent counts only if its own
  assignee name matched the filer, led with the filer's name, or shares the first word of one of the filer's
  names. KPSS groups some unrelated assignees under one permco (Robert Bosch and BMW patents sit with
  Parker-Hannifin's), and this rule drops them. Eight aliases for patent-holding subsidiaries of large
  manufacturers are listed in the script.
- **Estimation:** Poisson quasi-maximum likelihood, standard errors clustered by industry (20 clusters, few
  enough that the clustered errors are approximate; the conventional ones are reported alongside):

```math
\mathbb{E}\left[y_{jt} \mid c_{jt}\right] = \exp\left(\beta_1 c_{jt} + \beta_2 c_{jt}^2 + \alpha_j + \tau_t\right)
```

- **Inverted-U test:** Lind and Mehlum (2010). The slope must be positive at the lowest observed competition and
  negative at the highest; the reported p-value is the larger of the two one-sided p-values. The peak's standard
  error is by the delta method.
- **Technology gap:** productivity is revenue over a Cobb–Douglas index of operating costs and capital costs,
  with the industry-year median cost share as the weight; the gap is the mean proportional distance from the
  most productive firm (the paper's equation 12), and alternatively from the 90th-percentile firm.

Checks added after the first results, on the composition of firms behind the average Lerner index: the median
instead of the mean, profitable firms only, revenue of $100 million or more, and excluding drugs (SIC 283).

## Full test statistics

| Specification | N | Linear (s.e.) | Squared (s.e.) | Joint χ² (p) | Lind–Mehlum p |
|---|---|---|---|---|---|
| (1) Year effects | 200 | 19.73 (9.10) | −7.31 (3.47) | 5.33 (0.070) | 0.024 |
| (2) Year and industry effects | 200 | 1.19 (3.11) | −0.23 (1.14) | 0.33 (0.85) | 0.54 |
| (2) with conventional Poisson errors | 200 | 1.19 (1.18) | −0.23 (0.43) | 6.10 (0.047) | 0.63 |
| Patent counts, unweighted | 200 | 0.37 (1.69) | −0.48 (0.54) | 23.18 (< 0.001) | 0.67 |
| No capital charge | 200 | 1.60 (3.26) | −0.39 (1.13) | 0.36 (0.84) | 0.50 |
| Sales-weighted Lerner | 200 | −20.92 (6.09) | 11.06 (2.67) | 57.96 (< 0.001) | 1.00 |
| Three-digit SIC | 604 | −1.22 (1.45) | 0.18 (0.41) | 4.66 (0.097) | 0.87 |
| R&D / sales as outcome | 200 | 10.48 (5.89) | −2.81 (1.68) | 6.42 (0.040) | 0.15 |
| Median Lerner | 200 | −15.02 (12.09) | 7.18 (6.62) | 3.50 (0.17) | 0.96 |
| Profitable firms only | 198 | −5.91 (24.74) | 3.14 (15.48) | 0.64 (0.73) | 0.73 |
| Revenue ≥ $100 million | 199 | −13.93 (15.88) | 6.55 (8.14) | 1.67 (0.43) | 0.86 |
| Excluding SIC 283 | 200 | −14.87 (7.88) | 6.66 (3.57) | 3.83 (0.15) | 0.97 |

The R&D-intensity row (the paper's alternative outcome) peaks at 1.86, with 98% of industry-years to the left,
and fails the endpoint test.

Extension (year and industry effects unless stated):

| Test | Frontier = best firm | Frontier = 90th percentile |
|---|---|---|
| Gap on competition, year effects | 0.338 (0.063) | 0.288 (0.032) |
| Gap on competition, year and industry effects | 0.067 (0.064) | 0.117 (0.026) |
| Competition × gap | 12.31 (2.98) | 20.45 (5.38) |
| Competition² × gap | −11.43 (2.71) | −18.61 (4.73) |
| Joint χ² on interactions | 17.8 | 15.5 |
| Implied squared term at gap p25 / p75 | 7.86 / 5.13 | 9.54 / 8.21 |
| Neck-and-neck half: peak or trough, Lind–Mehlum p | trough at 1.10, 1.00 | peak at 0.99, 0.35 |
| Correlation of gap with firm count | 0.78 | 0.68 |

## Reproducing the results

```bash
pip install -r requirements.txt
python src/build_panel.py    # optional: downloads about 6 GB and rebuilds data/processed/ (10-20 minutes)
python src/inverted_u.py     # runs offline from data/processed/ and writes results/
```

## Repository layout

| Path | What it is |
|---|---|
| [src/build_panel.py](src/build_panel.py) | SEC accounts, KPSS patents, the name bridge |
| [src/inverted_u.py](src/inverted_u.py) | Replication, robustness, neck-and-neck extension, figures |
| `data/processed/` | Firm-year panel and patent bridge (committed) |
| `results/` | CSVs, figures and [FINDINGS.md](results/FINDINGS.md) |

## References

- Aghion, P., Bloom, N., Blundell, R., Griffith, R. & Howitt, P. (2005). Competition and innovation: an inverted-U
  relationship. *QJE* 120(2).
- Aghion, P. & Howitt, P. (1992). A model of growth through creative destruction. *Econometrica* 60.
- Hashmi, A. (2013). Competition and innovation: the inverted-U relationship revisited. *Review of Economics and
  Statistics* 95(5).
- Kogan, L., Papanikolaou, D., Seru, A. & Stoffman, N. (2017). Technological innovation, resource allocation, and
  growth. *QJE* 132(2).
- Lind, J. T. & Mehlum, H. (2010). With or without U? The appropriate test for a U-shaped relationship. *Oxford
  Bulletin of Economics and Statistics* 72(1).
- Shapiro, C. (2012). Competition and innovation: did Arrow hit the bull's eye? In Lerner & Stern (eds.), *The Rate
  and Direction of Inventive Activity Revisited*. University of Chicago Press.
