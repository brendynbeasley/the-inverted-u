"""Aghion, Bloom, Blundell, Griffith & Howitt (2005) on US manufacturing, 2011-2020.

Replication. For each two-digit SIC manufacturing industry and year, competition is one minus the
average Lerner index of its listed firms, the Lerner index being operating profit net of an 8.5%
financial cost of capital, divided by sales (the paper's equation 1 and footnote 7). Innovation is
the average number of citation-weighted US patents per firm, dated by filing year. Citation-weighted
patent counts are regressed on competition and its square by Poisson quasi-maximum likelihood with
year and industry effects (the paper's Table I, column 2). The peak of the fitted curve and a
Lind-Mehlum test for an inverted U are reported.

Extension (the paper's Table III, and the argument of Hashmi 2013). Each industry-year gets a
technology gap: the average proportional distance of its firms' productivity from the most
productive firm's (the paper's equation 12). The model predicts that the gap rises with competition
and that the inverted U is steeper and peaks later where firms are neck and neck (small gap).

Reads data/processed/firm_years.csv.gz (written by src/build_panel.py). Writes CSVs and PNGs to
results/.

Usage (from the repository root):
    python src/inverted_u.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"

YEARS = range(2011, 2021)        # filing years with near-complete grant coverage in the 2025 KPSS data
SIC_RANGE = (2000, 3999)         # manufacturing, SIC divisions 20-39
COST_OF_CAPITAL = 0.085          # the paper's footnote 7, applied here to net property, plant and equipment
MIN_REVENUE = 10e6               # drops shells and pre-revenue start-ups whose Lerner index is meaningless
WINSOR = (0.01, 0.99)            # pooled percentiles at which firm Lerner and log productivity are capped
MIN_FIRMS = 5                    # firms needed for an industry-year average
PAPER = {"b1": 387.46, "se1": 67.74, "b2": -204.55, "se2": 36.17, "n": 354}   # Table I, column 2
PAPER_TABLE1 = [  # (column, linear, s.e., squared, s.e., observations), QJE 2005 Table I
    ("(1) annual, year effects", 152.80, 55.74, -80.99, 29.61, 354),
    ("(2) annual, year and industry effects", 387.46, 67.74, -204.55, 36.17, 354),
    ("(3) five-year averages", 819.44, 265.63, -434.43, 141.43, 67),
    ("(4) control function", 385.13, 67.56, -204.83, 36.06, 354)]
PAPER_TABLE3 = (424.46, -222.9, 3.82, -3.84, 0.49)   # Table III col. 4 terms; mean gap from Table IV

SIC2 = {20: "Food", 21: "Tobacco", 22: "Textiles", 23: "Apparel", 24: "Lumber and wood", 25: "Furniture",
        26: "Paper", 27: "Printing and publishing", 28: "Chemicals and drugs", 29: "Petroleum refining",
        30: "Rubber and plastics", 31: "Leather", 32: "Stone, clay and glass", 33: "Primary metals",
        34: "Fabricated metal products", 35: "Machinery and computers", 36: "Electronics and electrical",
        37: "Transportation equipment", 38: "Instruments and medical devices", 39: "Other manufacturing"}


def load_firms():
    f = pd.read_csv(ROOT / "data" / "processed" / "firm_years.csv.gz")
    print(f"Loaded {len(f):,} SEC firm-years ({f['cik'].nunique():,} filers)")
    # Operating profit: the operating-income line; failing that, revenue less total costs and expenses;
    # failing that, pretax income plus interest expense
    alt1, alt2 = f["revenue"] - f["costs"], f["pretax"] + f["interest"].fillna(0)
    fallback = np.where(alt1.notna(), "revenue less costs", np.where(alt2.notna(), "pretax plus interest", "none"))
    f["op_source"] = np.where(f["opinc"].notna(), "operating income", fallback)
    f["opinc"] = f["opinc"].fillna(alt1).fillna(alt2)
    steps = [("fiscal years 2011-2020", f["year"].isin(YEARS)),
             ("US business address", f["countryba"].eq("US")),
             ("manufacturing SIC 2000-3999", f["sic"].between(*SIC_RANGE)),
             (f"revenue of at least ${MIN_REVENUE / 1e6:.0f} million", f["revenue"].ge(MIN_REVENUE)),
             ("operating profit available", f["opinc"].notna())]
    counts = []
    for label, keep in steps:
        counts.append((label, int(keep[f.index].sum()), int((~keep[f.index]).sum())))
        f = f[keep[f.index]]
        print(f"  keep {label}: {counts[-1][1]:,} kept, {counts[-1][2]:,} dropped")
    f = f.copy()
    f["ppe_missing"] = f["ppe"].isna()
    counts += [(f"operating profit from {s}", int(n), 0) for s, n in f["op_source"].value_counts().items()]
    counts.append(("net PP&E missing (capital charge set to zero)", int(f["ppe_missing"].sum()), 0))
    print(f"  operating profit sources: {f['op_source'].value_counts().to_dict()}")
    print(f"  net PP&E missing for {f['ppe_missing'].sum():,} firm-years; their capital charge is set to zero")
    f["capital_charge"] = COST_OF_CAPITAL * f["ppe"].fillna(0)
    f["lerner"] = cap((f["opinc"] - f["capital_charge"]) / f["revenue"])
    f["lerner_nocap"] = cap(f["opinc"] / f["revenue"])
    f["rd_int"] = cap(f["rd"].fillna(0) / f["revenue"])
    f["sic2"], f["sic3"] = f["sic"] // 100, f["sic"] // 10
    # Productivity: revenue over a Cobb-Douglas index of operating costs and capital costs
    cost = f["revenue"] - f["opinc"]
    kcost = COST_OF_CAPITAL * f["ppe"]
    ok = (cost > 0) & (kcost > 0)
    share = (cost / (cost + kcost)).where(ok)
    f["s_v"] = share.groupby([f["sic2"], f["year"]]).transform("median")
    f["log_tfp"] = cap(np.log(f["revenue"]) - f["s_v"] * np.log(cost.where(ok))
                       - (1 - f["s_v"]) * np.log(kcost.where(ok)))
    tfp = np.exp(f["log_tfp"])
    frontier = tfp.groupby([f["sic2"], f["year"]]).transform("max")
    f["gap"] = (frontier - tfp) / frontier
    # Robustness: the 90th-percentile firm as the frontier, less sensitive to the number of firms
    p90 = tfp.groupby([f["sic2"], f["year"]]).transform(lambda s: s.quantile(0.9))
    f["gap90"] = ((p90 - tfp) / p90).clip(lower=0)
    return f, counts


def cap(s):
    lo, hi = s.quantile(WINSOR[0]), s.quantile(WINSOR[1])
    return s.clip(lo, hi)


def industry_years(f, ind="sic2", agg="mean"):
    g = f.groupby([ind, "year"])
    d = g.agg(firms=("cik", "size"), lerner=("lerner", agg), lerner_nocap=("lerner_nocap", "mean"),
              cw=("cw_patents", "mean"), pat=("patents", "mean"), rd_int=("rd_int", "mean"),
              gap=("gap", "mean"), gap90=("gap90", "mean"), revenue=("revenue", "sum")).reset_index()
    d["lerner_sw"] = g.apply(lambda x: np.average(x["lerner"], weights=x["revenue"]), include_groups=False).values
    d = d[d["firms"] >= MIN_FIRMS].rename(columns={ind: "ind"})
    for src, dst in [("lerner", "c"), ("lerner_nocap", "c_nocap"), ("lerner_sw", "c_sw")]:
        d[dst] = 1 - d[src]
    return d


def poisson(formula, d, cluster=True):
    model = smf.glm(formula, data=d, family=sm.families.Poisson())
    kw = dict(cov_type="cluster", cov_kwds={"groups": pd.factorize(d["ind"])[0]}) if cluster else {}
    return model.fit(**kw)


def turning_point(res, x="c", lo=None, hi=None):
    """Peak of exp(b1 x + b2 x^2) with a delta-method SE, and the Lind-Mehlum (2010) test."""
    b1, b2 = res.params[x], res.params[f"I({x} ** 2)"]
    V = res.cov_params().loc[[x, f"I({x} ** 2)"], [x, f"I({x} ** 2)"]].values
    peak = -b1 / (2 * b2)
    grad = np.array([-1 / (2 * b2), b1 / (2 * b2 ** 2)])
    se = float(np.sqrt(grad @ V @ grad))
    # Slope b1 + 2 b2 x must be positive at the lowest observed x and negative at the highest
    t_lo = (b1 + 2 * b2 * lo) / np.sqrt(V[0, 0] + 4 * lo ** 2 * V[1, 1] + 4 * lo * V[0, 1])
    t_hi = (b1 + 2 * b2 * hi) / np.sqrt(V[0, 0] + 4 * hi ** 2 * V[1, 1] + 4 * hi * V[0, 1])
    t = min(t_lo, -t_hi)
    return dict(b1=b1, se1=res.bse[x], b2=b2, se2=res.bse[f"I({x} ** 2)"], peak=peak, peak_se=se,
                peak_lo=peak - 1.96 * se, peak_hi=peak + 1.96 * se, slope_lo_t=t_lo, slope_hi_t=t_hi,
                lm_t=t, lm_p=float(stats.norm.sf(t)), x_min=lo, x_max=hi)


def joint_wald(res, names):
    w = res.wald_test(" = 0, ".join(names) + " = 0", scalar=True)
    return float(w.statistic), float(w.pvalue)


def paper_peaks():
    """Peaks implied by the paper's own published coefficients (arithmetic only)."""
    p = pd.DataFrame(PAPER_TABLE1, columns=["column", "b1", "se1", "b2", "se2", "n"])
    p["implied_peak"] = -p["b1"] / (2 * p["b2"])
    b1, b2, g1, g2, gap = PAPER_TABLE3
    for label, m in [("Table III (4) at gap = 0", 0.0), ("Table III (4) at mean gap 0.49", gap)]:
        p.loc[len(p)] = [label, b1 + g1 * m, np.nan, b2 + g2 * m, np.nan, 354, -(b1 + g1 * m) / (2 * (b2 + g2 * m))]
    p.to_csv(OUT / "paper_table1_peaks.csv", index=False, float_format="%.6g")
    return p


def replication(f, d, d3):
    rows, fits = [], {}
    # Checks added after the first results, on the composition of the firms behind the average
    extra = [("Median rather than mean Lerner index", industry_years(f, agg="median")),
             ("Profitable firms only", industry_years(f[f["opinc"] > 0])),
             ("Revenue of $100 million or more", industry_years(f[f["revenue"] >= 100e6])),
             ("Excluding drugs (SIC 283)", industry_years(f[~f["sic"].between(2830, 2839)]))]
    specs = [("(1) year effects", "cw ~ c + I(c ** 2) + C(year)", d, "c"),
             ("(2) year and industry effects", "cw ~ c + I(c ** 2) + C(year) + C(ind)", d, "c"),
             ("(2) with conventional Poisson errors", "cw ~ c + I(c ** 2) + C(year) + C(ind)", d, "c"),
             ("Patent counts, not citation-weighted", "pat ~ c + I(c ** 2) + C(year) + C(ind)", d, "c"),
             ("No capital charge in the Lerner index", "cw ~ c_nocap + I(c_nocap ** 2) + C(year) + C(ind)", d, "c_nocap"),
             ("Sales-weighted Lerner index", "cw ~ c_sw + I(c_sw ** 2) + C(year) + C(ind)", d, "c_sw"),
             ("Three-digit SIC industries", "cw ~ c + I(c ** 2) + C(year) + C(ind)", d3, "c"),
             ("R&D / sales as the outcome", "rd_int ~ c + I(c ** 2) + C(year) + C(ind)", d, "c")]
    specs += [(label, "cw ~ c + I(c ** 2) + C(year) + C(ind)", data, "c") for label, data in extra]
    for label, formula, data, x in specs:
        res = poisson(formula, data, cluster="conventional" not in label)
        r = turning_point(res, x, data[x].min(), data[x].max())
        r["share_left_of_peak"] = float((data[x] < r["peak"]).mean()) if r["b2"] < 0 else np.nan
        w, p = joint_wald(res, [x, f"I({x} ** 2)"])
        rows.append(dict(spec=label, n=len(data), industries=data["ind"].nunique(), c_median=data[x].median(),
                         wald=w, wald_p=p, **r))
        fits[label] = res
    lin = poisson("cw ~ c + C(year) + C(ind)", d)
    rows.append(dict(spec="Linear only, year and industry effects", n=len(d), industries=d["ind"].nunique(),
                     b1=lin.params["c"], se1=lin.bse["c"], wald=float(lin.tvalues["c"] ** 2),
                     wald_p=float(lin.pvalues["c"])))
    rows.append(dict(spec="Paper, Table I column (2): UK 1973-94", n=PAPER["n"], industries=17, b1=PAPER["b1"],
                     se1=PAPER["se1"], b2=PAPER["b2"], se2=PAPER["se2"],
                     peak=-PAPER["b1"] / (2 * PAPER["b2"])))
    t = pd.DataFrame(rows)
    # 'peak' is a maximum only when the squared term is negative; otherwise the curve is a U and it is a minimum.
    # A turning point outside the observed range means the fitted curve is monotone over the data.
    inside = (t["peak"] > t["x_min"]) & (t["peak"] < t["x_max"])
    up, down = t["b2"] < 0, t["b2"] > 0
    above, below = t["peak"] >= t["x_max"], t["peak"] <= t["x_min"]
    t["shape"] = np.select(
        [t["b2"].isna(), t["x_min"].isna(), inside & up, inside & down,
         (up & above) | (down & below), (up & below) | (down & above)],
        ["linear", "inverted U", "inverted U", "U", "rising over the data", "falling over the data"], "")
    t.to_csv(OUT / "table1_replication.csv", index=False, float_format="%.6g")
    return t, fits


def bins(d):
    """Competition quintile dummies with the same effects: a check that does not impose a parabola."""
    d = d.copy()
    d["q"] = pd.qcut(d["c"], 5, labels=False)
    r = poisson("cw ~ C(q) + C(year) + C(ind)", d)
    out = d.groupby("q")["c"].agg(["min", "median", "max", "size"]).reset_index()
    out["relative_patents"] = [1.0] + [float(np.exp(r.params[f"C(q)[T.{q}]"])) for q in range(1, 5)]
    out["se_log"] = [0.0] + [float(r.bse[f"C(q)[T.{q}]"]) for q in range(1, 5)]
    out.to_csv(OUT / "competition_quintiles.csv", index=False, float_format="%.6g")
    return out


def extension(d):
    rows, split = [], {}
    groups = pd.factorize(d["ind"])[0]
    for g, tag in [("gap", "frontier = best firm"), ("gap90", "frontier = 90th percentile")]:
        for label, fe in [("year effects", "C(year)"), ("year and industry effects", "C(year) + C(ind)")]:
            r = smf.ols(f"{g} ~ c + {fe}", data=d).fit(cov_type="cluster", cov_kwds={"groups": groups})
            rows.append(dict(spec=f"Gap on competition, {label}", gap=tag, n=len(d), coef_c=r.params["c"],
                             se_c=r.bse["c"], p=r.pvalues["c"]))
        for label, fe in [("year effects", "C(year)"), ("year and industry effects", "C(year) + C(ind)")]:
            r = poisson(f"cw ~ c + I(c ** 2) + c:{g} + I(c ** 2):{g} + {fe}", d)
            w, p = joint_wald(r, [f"c:{g}", f"I(c ** 2):{g}"])
            rows.append(dict(spec=f"Interactions, {label}", gap=tag, n=len(d), coef_c=r.params["c"], se_c=r.bse["c"],
                             coef_c2=r.params["I(c ** 2)"], se_c2=r.bse["I(c ** 2)"], coef_c_gap=r.params[f"c:{g}"],
                             se_c_gap=r.bse[f"c:{g}"], coef_c2_gap=r.params[f"I(c ** 2):{g}"],
                             se_c2_gap=r.bse[f"I(c ** 2):{g}"], wald=w, p=p))
            if fe != "C(year)":   # curvature implied at the gap's quartiles: negative means an inverted U
                for q in (0.25, 0.75):
                    m = d[g].quantile(q)
                    rows.append(dict(spec=f"Implied squared-term coefficient at gap p{int(q * 100)}", gap=tag,
                                     n=len(d), median_gap=m,
                                     coef_c2=r.params["I(c ** 2)"] + r.params[f"I(c ** 2):{g}"] * m))
        med = d[g].median()
        for label, sub in [("Neck and neck (gap below median)", d[d[g] < med]),
                           ("Unleveled (gap above median)", d[d[g] >= med])]:
            r = poisson("cw ~ c + I(c ** 2) + C(year) + C(ind)", sub)
            tp = turning_point(r, "c", sub["c"].min(), sub["c"].max())
            rows.append(dict(spec=label, gap=tag, n=len(sub), industries=sub["ind"].nunique(), coef_c=tp["b1"],
                             se_c=tp["se1"], coef_c2=tp["b2"], se_c2=tp["se2"], peak=tp["peak"],
                             peak_se=tp["peak_se"], lm_t=tp["lm_t"], lm_p=tp["lm_p"], median_gap=med,
                             mean_cw=sub["cw"].mean(), mean_firms=sub["firms"].mean()))
            if g == "gap":
                split[label] = (sub, r)
    rows.append(dict(spec="Correlation of gap with firms per industry-year", gap="frontier = best firm", n=len(d),
                     coef_c=d["gap"].corr(d["firms"])))
    rows.append(dict(spec="Correlation of gap with firms per industry-year", gap="frontier = 90th percentile",
                     n=len(d), coef_c=d["gap90"].corr(d["firms"])))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "table3_neck_and_neck.csv", index=False, float_format="%.6g")
    return t, split


def names_table(f, d):
    rows = []
    for ind, g in d.groupby("ind"):
        firms = f[f["sic2"] == ind]
        top = (firms.groupby("name")["patents"].sum().sort_values(ascending=False).head(3))
        rows.append(dict(sic2=ind, industry=SIC2.get(ind, str(ind)), years=len(g), firms_per_year=g["firms"].mean(),
                         competition=g["c"].mean(), lerner_pct=100 * g["lerner"].mean(),
                         median_lerner_pct=100 * firms["lerner"].median(), loss_share=(firms["opinc"] < 0).mean(),
                         gap=g["gap"].mean(), cw_patents_per_firm=g["cw"].mean(), patents_total=firms["patents"].sum(),
                         top_patentees="; ".join(f"{n.title()} ({int(p):,})" for n, p in top.items() if p > 0)))
    t = pd.DataFrame(rows).sort_values("cw_patents_per_firm", ascending=False)
    t.loc[len(t)] = dict(sic2=0, industry="All manufacturing (firm-years)", years=len(d), firms_per_year=np.nan,
                         competition=1 - f["lerner"].mean(), lerner_pct=100 * f["lerner"].mean(),
                         median_lerner_pct=100 * f["lerner"].median(), loss_share=(f["opinc"] < 0).mean(),
                         gap=np.nan, cw_patents_per_firm=f["cw_patents"].mean(), patents_total=f["patents"].sum(),
                         top_patentees="")
    t.to_csv(OUT / "industries.csv", index=False, float_format="%.4g")
    return t


def worked_examples(f, d):
    """The arithmetic behind the measures, for three firms and one industry, fiscal 2019."""
    rows = []
    for cik in [320193, 50863, 12927]:   # Apple, Intel, Boeing
        r = f[(f["cik"] == cik) & (f["year"] == 2019)].iloc[0]
        rows.append(dict(item=r["name"].title(), sic=r["sic"], revenue_bn=r["revenue"] / 1e9,
                         operating_income_bn=r["opinc"] / 1e9, ppe_bn=r["ppe"] / 1e9,
                         capital_charge_bn=r["capital_charge"] / 1e9, lerner=r["lerner"], one_minus_lerner=1 - r["lerner"],
                         patents=r["patents"], cw_patents=r["cw_patents"]))
    s = d[(d["ind"] == 36) & (d["year"] == 2019)].iloc[0]
    rows.append(dict(item="SIC 36 electronics, industry average", sic=36, lerner=s["lerner"], one_minus_lerner=s["c"],
                     patents=s["pat"], cw_patents=s["cw"], firms=s["firms"]))
    pd.DataFrame(rows).to_csv(OUT / "worked_examples.csv", index=False, float_format="%.6g")


def plot_curve(d, res, path):
    """Patents relative to the industry and year baseline against competition, US fit and the paper's UK fit."""
    b1, b2 = res.params["c"], res.params["I(c ** 2)"]
    ref = -PAPER["b1"] / (2 * PAPER["b2"])      # both curves set to 1 at the paper's peak
    base = np.exp(res.predict(d, which="linear") - b1 * d["c"] - b2 * d["c"] ** 2)
    rel = d["cw"] / base / np.exp(b1 * ref + b2 * ref ** 2)
    grid = np.linspace(d["c"].min(), min(d["c"].max(), 1.4), 300)
    uk = np.linspace(0.87, 0.99, 100)           # the paper's observed range (Table IV)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    keep = d["c"] <= 1.4
    ax.scatter(d.loc[keep, "c"], rel[keep], s=14, alpha=0.45, color="#4C72B0", label="US industry-years, 2011-2020")
    ax.plot(grid, np.exp(b1 * (grid - ref) + b2 * (grid ** 2 - ref ** 2)), color="#4C72B0", lw=2.2,
            label="US fit, year and industry effects")
    ax.plot(uk, np.exp(PAPER["b1"] * (uk - ref) + PAPER["b2"] * (uk ** 2 - ref ** 2)), color="#C44E52", lw=2.2,
            label="Paper's UK fit, 1973-94 (Table I, col. 2)")
    ax.set_yscale("log")
    ax.set_xlabel("Competition = 1 - average Lerner index")
    ax.set_ylabel("Citation-weighted patents per firm\n(relative to industry and year effects)")
    ax.set_title(f"No inverted U in US manufacturing ({(~keep).sum()} points above 1.4 not shown)")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_split(split, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for (label, (sub, r)), col in zip(split.items(), ["#55A868", "#8172B2"]):
        grid = np.linspace(sub["c"].quantile(0.02), sub["c"].quantile(0.98), 200)
        level = np.exp(r.predict(sub, which="linear") - r.params["c"] * sub["c"]
                       - r.params["I(c ** 2)"] * sub["c"] ** 2).mean()
        ax.plot(grid, level * np.exp(r.params["c"] * grid + r.params["I(c ** 2)"] * grid ** 2), lw=2.2,
                color=col, label=label)
    ax.set_xlabel("Competition = 1 - average Lerner index")
    ax.set_ylabel("Fitted citation-weighted patents per firm")
    ax.set_title("The neck-and-neck split, US manufacturing 2011-2020")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    f, counts = load_firms()
    d, d3 = industry_years(f, "sic2"), industry_years(f, "sic3")
    n2, n3 = f.groupby(["sic2", "year"]).ngroups, f.groupby(["sic3", "year"]).ngroups
    counts += [("two-digit industry-years with >= 5 firms", len(d), n2 - len(d)),
               ("three-digit industry-years with >= 5 firms", len(d3), n3 - len(d3))]
    pd.DataFrame(counts, columns=["step", "kept", "dropped"]).to_csv(OUT / "sample_counts.csv", index=False)
    d.to_csv(OUT / "industry_years.csv", index=False, float_format="%.6g")
    print(f"Industry-years: {len(d)} (two-digit, {d['ind'].nunique()} industries), {len(d3)} (three-digit, "
          f"{d3['ind'].nunique()} industries); firms per industry-year median {d['firms'].median():.0f}")
    desc = d[["cw", "pat", "c", "gap", "firms"]].describe(percentiles=[0.5]).T
    desc.to_csv(OUT / "descriptive.csv", float_format="%.6g")
    print(desc.round(3).to_string())

    print("\nPeaks implied by the paper's coefficients\n" + paper_peaks().round(4).to_string(index=False))
    t1, fits = replication(f, d, d3)
    print("\nTable I replication\n" + t1[["spec", "n", "b1", "se1", "b2", "se2", "peak", "lm_t", "lm_p"]]
          .round(3).to_string(index=False))
    q = bins(d)
    print("\nCompetition quintiles\n" + q.round(3).to_string(index=False))
    t3, split = extension(d)
    print("\nNeck-and-neck extension\n" + t3.round(3).to_string(index=False))
    names = names_table(f, d)
    print("\nIndustries\n" + names.round(3).to_string(index=False))
    worked_examples(f, d)
    plot_curve(d, fits["(2) year and industry effects"], OUT / "inverted_u.png")
    plot_split(split, OUT / "neck_and_neck.png")
    print("\nWrote results/*.csv, results/inverted_u.png and results/neck_and_neck.png")


if __name__ == "__main__":
    main()
