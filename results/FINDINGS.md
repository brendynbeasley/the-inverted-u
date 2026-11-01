# Aghion, Bloom, Blundell, Griffith & Howitt (2005) on US manufacturing: findings

## In plain English

In 2005 five economists showed that British industries invented most when competition was middling, neither so
weak that firms could coast nor so strong that catching up did not pay. This study reruns their test on American
listed manufacturers from 2011 to 2020.

- **Within American industries there is no hump.** When an industry such as computers (IBM, Apple, HP) or
  vehicles (Ford, Boeing, General Motors) became more or less competitive, its patenting did not change in any
  systematic way.
- **Across industries a hump appears, but it reflects industry type.** The big patenting industries, computers,
  electronics (Intel, Qualcomm, GE) and medical instruments (3M, Boston Scientific), have average margins near
  zero, while food (Coca-Cola, PepsiCo), apparel (Levi Strauss) and lumber (Louisiana-Pacific) earn steady margins
  and patent very little.
- **The competition measure strains under modern listings.** A third of listed manufacturer-years show operating
  losses, and in chemicals and drugs (Procter & Gamble, Merck, Monsanto, plus many loss-making drug developers)
  the average margin is −67%. No version of the measure produces a within-industry inverted U.
- **The neck-and-neck prediction fails.** More competitive industries do show wider productivity gaps between
  their firms, as the model predicts, but the hump does not get steeper where firms are close together.

A friendlier tour is in the [README](../README.md). The rest of this page is the detail.

**Key to the labels below:** *c* = competition, one minus the industry's average Lerner index. *Lerner* =
(operating profit − 8.5% × net plant and equipment) / sales. *cw* = citation-weighted patents per firm, each
patent weighted by its citations over the average for its filing year. *pat* = unweighted patents per firm.
*gap* = average proportional distance of an industry's firms from its most productive firm. *b1*, *b2* =
coefficients on c and c² in a Poisson regression; *peak* = −b1/(2·b2), a maximum when b2 < 0 and a minimum
when b2 > 0. *Lind–Mehlum p* tests that the slope is positive at the lowest c and negative at the highest.
Standard errors are clustered by industry unless the row says otherwise.

## Sample

Build (`build_counts.csv`):

| Step | Kept | Dropped |
|---|---|---|
| SEC firm-years with revenue, fiscal 2010–2024 | 74,882 | 36,054 |
| KPSS patents filed 2008–2022 (of all years) | 1,482,341 | 2,349,567 |
| Permco-CIK links by exact name (≥ 3 patents or 10%) | 2,717 | 69 |
| Permco-CIK links by leading words (≥ 10 patents and 25%) | 152 | 165 |
| Patents in linked firm-years whose assignee name matched the filer | 746,215 | 113,020 |
| KPSS patents filed 2008–2022 attributed to an SEC filer | 746,215 | 736,126 |
| KPSS patents filed 2011–2020 attributed to an SEC filer | 624,478 | 437,235 |

Analysis sample (`sample_counts.csv`):

| Step | Kept | Dropped |
|---|---|---|
| Fiscal years 2011–2020 | 51,257 | 23,625 |
| US business address | 47,666 | 3,591 |
| Manufacturing, SIC 2000–3999 | 19,080 | 28,586 |
| Revenue of at least $10 million | 13,859 | 5,221 |
| Operating profit available | 13,583 | 276 |
| of which from the operating-income line | 12,780 | |
| of which from pretax income plus interest | 501 | |
| of which from revenue less total costs | 302 | |
| Net PP&E missing (capital charge set to zero) | 371 | |
| Two-digit industry-years with ≥ 5 firms | 200 | 0 |
| Three-digit industry-years with ≥ 5 firms | 604 | 540 |

Industry-year variables (`descriptive.csv`):

| Variable | Mean | s.d. | Min | Median | Max |
|---|---|---|---|---|---|
| cw | 14.95 | 21.42 | 0 | 6.03 | 102.89 |
| pat | 16.71 | 27.14 | 0 | 4.93 | 122.41 |
| c | 1.042 | 0.186 | 0.786 | 0.991 | 2.070 |
| gap | 0.247 | 0.135 | 0.037 | 0.198 | 0.565 |
| Firms per industry-year | 67.9 | 85.0 | 6 | 24 | 364 |

## The paper's own numbers

Peaks implied by the published coefficients (`paper_table1_peaks.csv`):

| Paper, Table I column | b1 (s.e.) | b2 (s.e.) | N | Implied peak |
|---|---|---|---|---|
| (1) annual, year effects | 152.80 (55.74) | −80.99 (29.61) | 354 | 0.9433 |
| (2) annual, year and industry effects | 387.46 (67.74) | −204.55 (36.17) | 354 | 0.9471 |
| (3) five-year averages | 819.44 (265.63) | −434.43 (141.43) | 67 | 0.9431 |
| (4) control function | 385.13 (67.56) | −204.83 (36.06) | 354 | 0.9401 |
| Table III (4) at gap = 0 | 424.46 | −222.90 | 354 | 0.9521 |
| Table III (4) at mean gap 0.49 | 426.33 | −224.78 | 354 | 0.9483 |

## Replication of Table I

`table1_replication.csv`:

| Specification | N | b1 (s.e.) | b2 (s.e.) | Joint χ² (p) | Peak (s.e.) | Lind–Mehlum p | Share left of peak | Shape |
|---|---|---|---|---|---|---|---|---|
| (1) year effects | 200 | 19.73 (9.10) | −7.31 (3.47) | 5.33 (0.070) | 1.349 (0.047) | 0.024 | 0.94 | inverted U |
| (2) year and industry effects | 200 | 1.19 (3.11) | −0.23 (1.14) | 0.33 (0.849) | 2.54 (6.56) | 0.542 | 1.00 | rising over the data (flat) |
| (2) conventional Poisson errors | 200 | 1.19 (1.18) | −0.23 (0.43) | 6.10 (0.047) | 2.54 (2.26) | 0.629 | 1.00 | rising over the data |
| Patent counts, not citation-weighted | 200 | 0.37 (1.69) | −0.48 (0.54) | 23.18 (< 0.001) | 0.39 (1.34) | 0.672 | 0.00 | falling over the data |
| No capital charge | 200 | 1.60 (3.26) | −0.39 (1.13) | 0.36 (0.836) | 2.06 (2.51) | 0.504 | 1.00 | rising over the data (flat) |
| Sales-weighted Lerner | 200 | −20.92 (6.09) | 11.07 (2.67) | 57.96 (< 0.001) | 0.945 (0.054) | 1.000 | | U |
| Three-digit SIC | 604 | −1.22 (1.45) | 0.18 (0.41) | 4.66 (0.097) | 3.47 (4.04) | 0.866 | | falling over the data |
| R&D / sales as outcome | 200 | 10.48 (5.89) | −2.81 (1.68) | 6.42 (0.040) | 1.863 (0.088) | 0.148 | 0.98 | inverted U (fails endpoint test) |
| Median Lerner | 200 | −15.02 (12.09) | 7.18 (6.62) | 3.50 (0.174) | 1.046 (0.156) | 0.962 | | U |
| Profitable firms only | 198 | −5.91 (24.74) | 3.14 (15.48) | 0.64 (0.728) | 0.94 (0.73) | 0.725 | | U |
| Revenue ≥ $100 million | 199 | −13.93 (15.88) | 6.55 (8.14) | 1.67 (0.434) | 1.063 (0.144) | 0.859 | | U |
| Excluding SIC 283 | 200 | −14.87 (7.88) | 6.66 (3.57) | 3.83 (0.147) | 1.117 (0.027) | 0.973 | | U |
| Linear only, year and industry effects | 200 | 0.56 (1.14) | | 0.25 (0.620) | | | | linear |
| Paper, UK 1973–94, Table I (2) | 354 | 387.46 (67.74) | −204.55 (36.17) | | 0.947 | | | inverted U |

Shape is the script's label: "inverted U" or "U" when the turning point lies inside the observed range of c,
and "rising over the data" or "falling over the data" when it lies outside, so the fitted curve is monotone where
there are observations. "(flat)" is added here where the two terms are also jointly insignificant at 10%. The
unweighted-patent fit declines throughout, with an endpoint slope t of −2.59 at the competitive end.

Competition quintiles with year and industry effects (`competition_quintiles.csv`):

| Quintile | c range | Median c | Industry-years | Patents relative to lowest quintile | s.e. (log) |
|---|---|---|---|---|---|
| 1 (least competitive) | 0.786–0.954 | 0.938 | 40 | 1.000 | |
| 2 | 0.955–0.975 | 0.967 | 40 | 1.038 | 0.083 |
| 3 | 0.975–1.009 | 0.991 | 40 | 1.053 | 0.147 |
| 4 | 1.009–1.059 | 1.029 | 40 | 1.034 | 0.125 |
| 5 (most competitive) | 1.061–2.070 | 1.174 | 40 | 1.062 | 0.167 |

See [inverted_u.png](inverted_u.png).

## Industries

Averages over 2011–2020 (`industries.csv`; top patentees by patents filed 2011–2020):

| SIC | Industry | Firms a year | c | Mean Lerner % | Median Lerner % | Loss share | gap | cw per firm | Patents | Top patentees |
|---|---|---|---|---|---|---|---|---|---|---|
| 35 | Machinery and computers | 160.5 | 1.02 | −2.20 | 4.82 | 0.31 | 0.38 | 77.23 | 156,450 | IBM (71,639); Apple (21,223); HP (11,702) |
| 37 | Transportation equipment | 85.5 | 0.99 | 0.62 | 5.49 | 0.17 | 0.35 | 46.73 | 58,189 | Ford (14,385); Boeing (10,505); General Motors (9,567) |
| 36 | Electronics and electrical | 225.2 | 1.03 | −3.06 | 2.44 | 0.37 | 0.44 | 44.72 | 135,732 | Intel (26,675); Qualcomm (22,280); General Electric (14,408) |
| 38 | Instruments and medical devices | 207.5 | 1.15 | −14.73 | 2.56 | 0.43 | 0.43 | 41.52 | 38,734 | 3M (4,685); Boston Scientific (4,020); Raytheon (2,112) |
| 21 | Tobacco | 7.1 | 1.07 | −7.06 | 13.72 | 0.27 | 0.30 | 13.80 | 907 | Altria (887); 22nd Century Group (20) |
| 29 | Petroleum refining | 17.3 | 1.03 | −2.84 | 1.82 | 0.22 | 0.22 | 13.01 | 3,354 | Chevron (1,730); ExxonMobil (1,055); ConocoPhillips (389) |
| 33 | Primary metals | 38.8 | 1.00 | −0.55 | 1.87 | 0.24 | 0.16 | 12.53 | 5,131 | Corning (4,316); Mueller Industries (315); Howmet Aerospace (115) |
| 25 | Furniture | 18.3 | 0.98 | 2.15 | 4.46 | 0.14 | 0.09 | 11.42 | 854 | Steelcase (317); Johnson Controls (205); Sleep Number (99) |
| 39 | Other manufacturing | 25.3 | 0.99 | 1.21 | 3.88 | 0.28 | 0.21 | 9.24 | 1,179 | Callaway Golf (518); Mattel (273); Hasbro (86) |
| 28 | Chemicals and drugs | 304.8 | 1.67 | −67.12 | −1.66 | 0.48 | 0.50 | 8.22 | 30,556 | Procter & Gamble (4,175); Merck (2,723); Monsanto (2,237) |
| 30 | Rubber and plastics | 25.2 | 1.00 | 0.06 | 4.61 | 0.19 | 0.16 | 6.31 | 2,060 | Nike (758); Goodyear (547); Entegris (362) |
| 32 | Stone, clay and glass | 14.1 | 1.13 | −12.87 | 2.76 | 0.23 | 0.15 | 5.57 | 135 | View (79); Carbo Ceramics (32); Apogee Enterprises (9) |
| 26 | Paper | 20.5 | 0.99 | 0.60 | 3.04 | 0.16 | 0.14 | 3.68 | 1,090 | Kimberly-Clark (929); MeadWestvaco (48); Bemis (36) |
| 34 | Fabricated metal products | 51.5 | 0.97 | 3.42 | 6.23 | 0.15 | 0.20 | 2.84 | 1,938 | Parker-Hannifin (472); Snap-on (338); Stanley Black & Decker (168) |
| 20 | Food | 76.6 | 0.97 | 3.19 | 5.78 | 0.20 | 0.33 | 0.63 | 1,110 | Coca-Cola (280); PepsiCo (215); General Mills (175) |
| 23 | Apparel | 20.0 | 0.97 | 3.28 | 6.84 | 0.20 | 0.23 | 0.43 | 91 | Levi Strauss (46); Under Armour (21); Columbia Sportswear (15) |
| 22 | Textiles | 10.1 | 0.97 | 2.92 | 4.21 | 0.18 | 0.11 | 0.43 | 15 | Mohawk Industries (13); Interface (2) |
| 27 | Printing and publishing | 24.5 | 1.00 | −0.52 | 2.40 | 0.29 | 0.18 | 0.24 | 165 | Acco Brands (106); Quad/Graphics (16); American Greetings (13) |
| 24 | Lumber and wood | 15.5 | 0.96 | 4.41 | 4.58 | 0.14 | 0.14 | 0.23 | 57 | Louisiana-Pacific (18); Jeld-Wen (17); Trex (9) |
| 31 | Leather | 10.0 | 0.95 | 4.58 | 7.42 | 0.15 | 0.23 | 0.15 | 16 | Tumi (9); Wolverine World Wide (4); Rocky Brands (3) |
| | All manufacturing (firm-years) | | 1.18 | −18.21 | 3.46 | 0.34 | | 28.52 | 437,763 | |

Firms are placed in industries by the SIC code on their latest 10-K, so Corning (SIC 3357, fiber and wire) sits
in primary metals, Johnson Controls in furniture and Nike in rubber and plastics.

## The neck-and-neck extension

`table3_neck_and_neck.csv`, best-firm frontier (the paper's definition) and 90th-percentile frontier:

| Test | Best-firm frontier | 90th-percentile frontier |
|---|---|---|
| Gap on c, year effects (OLS) | 0.338 (0.063) | 0.288 (0.032) |
| Gap on c, year and industry effects (OLS) | 0.067 (0.064), p = 0.29 | 0.117 (0.026) |
| Interactions, year effects: c × gap, c² × gap | 19.01 (3.82), −11.91 (2.57) | 17.97 (6.45), −11.75 (4.22) |
| Joint χ² on interactions, year effects | 34.0 | 7.8 |
| Interactions, year and industry effects: c, c² | −17.45 (4.44), 9.36 (2.36) | −20.85 (5.79), 11.07 (3.01) |
| Interactions, year and industry effects: c × gap, c² × gap | 12.31 (2.98), −11.43 (2.71) | 20.45 (5.38), −18.61 (4.73) |
| Joint χ² on interactions, year and industry effects | 17.8 | 15.5 |
| Implied c² coefficient at gap p25 (gap value) | 7.86 (0.131) | 9.54 (0.082) |
| Implied c² coefficient at gap p75 (gap value) | 5.13 (0.369) | 8.21 (0.154) |
| Neck-and-neck half: b1, b2 | −40.92 (5.97), 18.61 (2.38) | 30.39 (63.67), −15.32 (31.17) |
| Neck-and-neck half: turning point, Lind–Mehlum p | 1.100 (minimum), 1.000 | 0.992 (maximum), 0.345 |
| Neck-and-neck half: cw per firm, firms per industry-year | 4.99, 20.5 | 7.03, 26.5 |
| Unleveled half: b1, b2 | −0.95 (1.04), 0.09 (0.29) | −0.99 (1.20), 0.09 (0.32) |
| Unleveled half: cw per firm, firms per industry-year | 24.90, 115.3 | 22.87, 109.3 |
| Correlation of gap with firms per industry-year | 0.779 | 0.680 |

Proposition 4 (the gap rises with competition) holds across industries under both frontiers and within
industries under the 90th-percentile frontier. Proposition 5 (a steeper hump in neck-and-neck industries) is not
supported. The c² coefficient is positive throughout the interquartile range of the gap and falls toward zero as
the gap widens, which is the reverse of the prediction. The paper's neck-and-neck industries patented more than
the others; here they patent less, plausibly because the gap rises with the number of firms and the biggest
patenting industries have the most firms. The paper's own Table III, column 4, has interaction terms with the
same signs as here (3.82 and −3.84), each individually insignificant. See [neck_and_neck.png](neck_and_neck.png).

## Worked examples

`worked_examples.csv`, fiscal 2019 (dollar amounts in billions):

| | Revenue | Operating income | Net PP&E | Capital charge | Lerner | 1 − Lerner | Patents | cw patents |
|---|---|---|---|---|---|---|---|---|
| Apple | 260.174 | 63.930 | 37.378 | 3.177 | 0.2335 | 0.7665 | 2,530 | 4,539.8 |
| Intel | 71.965 | 22.035 | 55.386 | 4.708 | 0.2408 | 0.7592 | 2,417 | 1,811.9 |
| Boeing | 76.559 | −1.975 | 12.502 | 1.063 | −0.0397 | 1.0397 | 1,320 | 581.3 |
| SIC 36, average of 200 firms | | | | | −0.0485 | 1.0485 | 69.6 | 71.9 |

The full industry-year panel is in `industry_years.csv`.

## How to read this

**What it does say:** among US-listed manufacturers in 2011–2020, changes in an industry's average margin were
not associated with changes in its citation-weighted patenting, under the paper's definitions and every variant
tried. The inverted U that appears across industries comes from which industries patent, which the paper's
industry effects were designed to remove.

**What it does not say:** that competition has no effect on innovation. There is no instrument here, the
competition measure moves little within most industries over ten years, accounting margins in loss-heavy
industries are a noisy proxy for competition, and the patent match misses some subsidiaries and all private
firms. A modest hump could exist and go undetected.

Data: SEC Financial Statement Data Sets (2012q1–2026q2); Kogan, Papanikolaou, Seru & Stoffman patent data
extended to 2025; USPTO PatentsView assignees (December 31, 2024 release). Accessed 2026-11-01.
