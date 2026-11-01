"""Build the firm-year panel: accounts from SEC filings, patents from the USPTO, joined by firm.

Two public sources are combined.

  Accounts. The SEC's Financial Statement Data Sets (FSDS), one zip per calendar quarter, hold every
  number tagged in every XBRL filing. All 58 quarters from 2012q1 to 2026q2 are read; 10-K filings
  only, consolidated full-year US-dollar values of standard us-gaap tags. A year ending July-December
  belongs to that calendar year, one ending January-June to the year before (the SEC "frames" rule).
  When a fiscal year appears in two filings, the filing in which it is the current year wins.

  Patents. Kogan, Papanikolaou, Seru & Stoffman (KPSS, 2017; data extended to 2025) match every US
  patent owned by a stock-market-listed firm to that firm's CRSP identifier (permco), with filing date
  and forward citations. CRSP identifiers are not public, so each permco is bridged to an SEC filer
  (CIK) by name: the patents' disambiguated assignee names from PatentsView (USPTO, 12/31/2024 release)
  are normalized and matched to every name the filer has used on a 10-K, including former names
  (Google LLC matches Alphabet's former name, Google Inc.). In each year a permco's patents go to the
  matched filer that filed accounts for that year, which handles holding-company reorganizations that
  create a new CIK. A patent counts only if its own assignee name is tied to that filer (see bridge()).

Raw files (about 6 GB) are not committed. Missing ones are downloaded into data/raw/. Outputs are
committed so the analysis runs offline:
    data/processed/firm_years.csv.gz   one row per filer and fiscal year, 2010-2024
    data/processed/patent_bridge.csv   permco -> CIK links, with the names that made them
    results/build_counts.csv           what was loaded, kept and dropped at each step

Usage (from the repository root):
    python src/build_panel.py
"""

import re
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "results"

YEARS = range(2010, 2025)                     # fiscal years covered by 10-Ks filed 2012q1-2026q2
QUARTERS = [f"{y}q{q}" for y in range(2012, 2027) for q in (1, 2, 3, 4)][:-2]
PATENT_YEARS = range(2008, 2023)              # filing years used to build the name bridge
FSDS = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{q}.zip"
KPSS = ("https://raw.githubusercontent.com/KPSS2017/"
        "Technological-Innovation-Resource-Allocation-and-Growth-Extended-Data/master/{f}")
PV = "https://zenodo.org/api/records/15783125/files/{f}/content"   # PatentsView 12/31/2024, CC-BY 4.0
HEADERS = {"User-Agent": "Brendyn Beasley research 83249437+brendynbeasley@users.noreply.github.com"}

DURATION = {  # tag -> measure, full-year (qtrs = 4) values
    "Revenues": "revenue", "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue",
    "RevenueFromContractWithCustomerIncludingAssessedTax": "revenue", "SalesRevenueNet": "revenue",
    "SalesRevenueGoodsNet": "revenue", "OperatingIncomeLoss": "opinc",
    "ResearchAndDevelopmentExpense": "rd",
    "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost": "rd",
    # Fallbacks for filers that tag no operating-income line (ExxonMobil, Pfizer, GE)
    "CostsAndExpenses": "costs", "InterestExpense": "interest",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "pretax",
}
INSTANT = {  # tag -> measure, balance-sheet (qtrs = 0) values
    "PropertyPlantAndEquipmentNet": "ppe",
    "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization": "ppe",
    "Assets": "assets",
}
# Legal-form words dropped from the end of names before matching (judgment list)
SUFFIXES = {"INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "LLC", "LP",
            "PLC", "NV", "SA", "AG", "SE", "AB", "ASA", "HOLDINGS", "HOLDING", "GROUP", "THE"}
# Single words too generic to identify a filer when matched as the leading word of an assignee name
GENERIC = {"AMERICAN", "AMERICA", "CHINA", "GENERAL", "GLOBAL", "INTERNATIONAL", "NATIONAL", "UNITED", "UNIVERSAL",
           "ADVANCED", "FIRST", "PACIFIC", "ATLANTIC", "NORTH", "SOUTH", "WESTERN", "EASTERN", "STANDARD", "APPLIED"}
# Patent-holding subsidiaries of large manufacturers whose names share no leading words with the parent's
# 10-K name (normalized assignee name -> normalized SEC name); each checked against the filers' 10-Ks
ALIASES = {"EXXONMOBIL CHEMICAL PATENTS": "EXXON MOBIL", "EXXONMOBIL RESEARCH AND ENGINEERING": "EXXON MOBIL",
           "EXXONMOBIL UPSTREAM RESEARCH": "EXXON MOBIL", "SEMICONDUCTOR COMPONENTS INDUSTRIES": "ON SEMICONDUCTOR",
           "DOW GLOBAL TECHNOLOGIES": "DOW CHEMICAL", "E I DU PONT DE NEMOURS": "DUPONT E I DE NEMOURS",
           "FREEESCALE SEMICONDUCTOR": "FREESCALE SEMICONDUCTOR", "GM GLOBAL TECHNOLOGY OPERATIONS": "GENERAL MOTORS"}


def fetch(url, path):
    """Return path, downloading url there first (via a temporary name) if it is missing."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"  downloading {path.name} ...")
        time.sleep(0.3)
        r = requests.get(url, headers=HEADERS, timeout=3600)
        if r.status_code != 200 or not r.content.startswith(b"PK"):
            raise SystemExit(f"download failed ({r.status_code}): {url}")
        tmp = path.with_suffix(".part")
        tmp.write_bytes(r.content)
        tmp.rename(path)
    return path


def normalize(name):
    """Upper case, no punctuation, no trailing legal-form words: 'Apple Inc.' -> 'APPLE'."""
    if not isinstance(name, str):
        return ""
    s = name.upper().split(" /")[0]
    s = re.sub(r"[/\\][A-Z]{1,4}[/\\]?\s*$", "", s).replace("&", " AND ")   # 'QUALCOMM INC/DE', 'CORP \\PA\\'
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    words = s.split()
    while words and (words[-1] in SUFFIXES or words[-1] == "AND"):
        words.pop()
    if words and words[0] == "THE":
        words = words[1:]
    return " ".join(words)


def read_quarter(q):
    """10-K headers and the tagged values this study uses, from one FSDS quarter."""
    with zipfile.ZipFile(fetch(FSDS.format(q=q), RAW / "sec" / f"{q}.zip")) as z:
        sub = pd.read_csv(z.open("sub.txt"), sep="\t", dtype=str, usecols=[
            "adsh", "cik", "name", "former", "sic", "countryba", "form", "period", "filed"])
        sub = sub[sub["form"] == "10-K"]
        header = z.open("num.txt").readline().decode().strip().split("\t")
        cols = ["adsh", "tag", "version", "ddate", "qtrs", "uom", "coreg", "value"]
        cols += ["segments"] if "segments" in header else []
        parts = []
        for c in pd.read_csv(z.open("num.txt"), sep="\t", dtype=str, usecols=cols,
                             chunksize=2_000_000, quoting=3, on_bad_lines="skip"):
            dur = c["tag"].isin(DURATION) & (c["qtrs"] == "4")
            ins = c["tag"].isin(INSTANT) & (c["qtrs"] == "0")
            c = c[(dur | ins) & (c["uom"] == "USD") & c["coreg"].isna()
                  & c["version"].str.startswith("us-gaap") & c["adsh"].isin(set(sub["adsh"]))]
            if "segments" in c:
                c = c[c["segments"].isna()]
            parts.append(c[["adsh", "tag", "ddate", "value"]])
    num = pd.concat(parts).merge(sub[["adsh", "cik", "period", "filed"]], on="adsh")
    print(f"  {q}: {len(sub):,} 10-K filings, {len(num):,} values kept")
    return sub, num


def sec_accounts(counts):
    """Firm-year accounts, each filer's latest SIC code and country, and every name it has used."""
    subs, nums = zip(*[read_quarter(q) for q in QUARTERS])
    sub, d = pd.concat(subs), pd.concat(nums, ignore_index=True)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    end = pd.to_datetime(d["ddate"], format="%Y%m%d", errors="coerce")
    period = pd.to_datetime(d["period"], format="%Y%m%d", errors="coerce")
    d["year"] = end.dt.year - (end.dt.month <= 6).astype(int)
    d["current"] = ((end - period).abs().dt.days <= 31).astype(int)
    d["measure"] = d["tag"].map(DURATION | INSTANT)
    # Largest value among a measure's tags within a filing, then the preferred filing per firm-year
    per = d.groupby(["cik", "year", "measure", "adsh", "current", "filed", "ddate"])["value"].max().reset_index()
    best = per.sort_values(["current", "ddate", "filed"]).drop_duplicates(["cik", "year", "measure"], keep="last")
    panel = best.pivot_table(index=["cik", "year"], columns="measure", values="value").reset_index()
    n0 = len(panel)
    panel = panel[panel["year"].isin(YEARS) & panel["revenue"].notna()]
    counts.append(("SEC firm-years with revenue, fiscal 2010-2024", len(panel), n0 - len(panel)))
    info = sub.sort_values("filed").drop_duplicates("cik", keep="last")[["cik", "name", "sic", "countryba"]]
    panel = panel.merge(info, on="cik", how="left")
    names = pd.concat([sub[["cik", "name"]], sub[["cik", "former"]].rename(columns={"former": "name"})])
    names["key"] = names["name"].map(normalize)
    names = names[names["key"].str.len() >= 2].drop_duplicates(["cik", "key"])
    print(f"SEC: {len(panel):,} firm-years, {panel['cik'].nunique():,} filers, {len(names):,} distinct name keys")
    return panel, names


def patents(counts):
    """KPSS patents with filing year, forward citations, permco and first assignee's name."""
    k = pd.read_csv(fetch(KPSS.format(f="KPSS_2025.zip"), RAW / "patents" / "KPSS_2025.zip"),
                    usecols=["patent_num", "filing_date", "cites"])
    k["fyear"] = k["filing_date"] // 10000
    n0 = len(k)
    k = k[k["fyear"].isin(PATENT_YEARS)]
    counts.append(("KPSS patents filed 2008-2022 (of all years)", len(k), n0 - len(k)))
    n0 = len(k)
    m = pd.read_csv(fetch(KPSS.format(f="Match_patent_permco_permno_2025.zip"),
                          RAW / "patents" / "Match_patent_permco_permno_2025.zip"),
                    usecols=["patent_num", "permco"]).drop_duplicates("patent_num")
    k = k.merge(m, on="patent_num", how="inner")
    counts.append(("KPSS patents filed 2008-2022 with a permco", len(k), n0 - len(k)))
    path = fetch(PV.format(f="g_assignee_disambiguated.tsv.zip"), RAW / "patents" / "g_assignee_disambiguated.tsv.zip")
    a = pd.read_csv(path, sep="\t", dtype=str, usecols=["patent_id", "assignee_sequence",
                                                        "disambig_assignee_organization"])
    a = a[a["assignee_sequence"] == "0"]
    a["patent_num"] = pd.to_numeric(a["patent_id"], errors="coerce")
    a = a.dropna(subset=["patent_num"]).astype({"patent_num": "int64"})
    k = k.merge(a[["patent_num", "disambig_assignee_organization"]], on="patent_num", how="left")
    k["key"] = k["disambig_assignee_organization"].map(normalize).replace(ALIASES)
    print(f"KPSS: {len(k):,} patents filed {PATENT_YEARS[0]}-{PATENT_YEARS[-1]} at {k['permco'].nunique():,} "
          f"listed firms; {k['key'].str.len().gt(0).mean():.1%} have an assignee name")
    return k


def vote(hits, total, method):
    """Patents per (permco, CIK) pair among name matches."""
    v = (hits.groupby(["permco", "cik"]).agg(matched=("patent_num", "nunique"),
                                             assignee=("disambig_assignee_organization", "first"),
                                             sec_name=("name", "first")).reset_index())
    v = v.join(total, on="permco")
    v["method"] = method
    return v


def bridge(k, names, panel, counts):
    """Link each permco to SEC filers by name; return the links and the assignee names behind them."""
    total = k.groupby("permco")["patent_num"].nunique().rename("permco_patents")
    hits = k.merge(names[["cik", "key", "name"]], on="key", how="inner")
    exact = vote(hits, total, "exact")
    n0 = len(exact)
    # An exact-name link needs at least 3 patents or 10% of the permco's patents
    exact = exact[(exact["matched"] >= 3) | (exact["matched"] >= 0.1 * exact["permco_patents"])]
    counts.append(("permco-CIK links by exact name (>= 3 patents or 10%)", len(exact), n0 - len(exact)))
    # Leading words: the filer's name opens the assignee's ("ORACLE" in "ORACLE INTERNATIONAL");
    # the longest such filer name wins. These names join an existing exact link, or, for a permco with
    # none, form a link if they cover at least 10 patents and 25% of the permco's patents.
    keys = k.loc[k["key"].str.contains(" "), ["key"]].drop_duplicates()
    keys["prefix"] = keys["key"].str.split().map(lambda w: [" ".join(w[:i]) for i in range(len(w) - 1, 0, -1)])
    keys = keys.explode("prefix")
    usable = (keys["prefix"].str.len() >= 5) | keys["prefix"].str.contains(r"\d", na=False)   # '3M' counts
    keys = keys[usable & ~keys["prefix"].isin(GENERIC)].merge(
        names[["key", "cik", "name"]].rename(columns={"key": "prefix"}), on="prefix")
    keys["words"] = keys["prefix"].str.count(" ")
    keys = keys[keys["words"] == keys.groupby("key")["words"].transform("max")]
    phits = k.merge(keys[["key", "cik", "name"]], on="key")
    pairs = set(zip(exact["permco"], exact["cik"]))
    joins = phits[[pc in pairs for pc in zip(phits["permco"], phits["cik"])]]
    prefix = vote(phits[~phits["permco"].isin(exact["permco"])], total, "leading words")
    n0 = len(prefix)
    prefix = prefix[(prefix["matched"] >= 10) & (prefix["matched"] >= 0.25 * prefix["permco_patents"])]
    counts.append(("permco-CIK links by leading words (>= 10 patents and 25%)", len(prefix), n0 - len(prefix)))
    votes = pd.concat([exact, prefix], ignore_index=True)
    pairs |= set(zip(prefix["permco"], prefix["cik"]))
    # Within a linked permco, a subsidiary whose name starts with the same word as one of the filer's
    # names also counts ("FORD GLOBAL TECHNOLOGIES" for Ford Motor, "CISCO TECHNOLOGY" for Cisco Systems)
    first = names[["cik", "key"]].assign(w=names["key"].str.split().str[0]).drop(columns="key").drop_duplicates()
    first = first[(first["w"].str.len() >= 3) & ~first["w"].isin(GENERIC)]
    same = (k.assign(w=k["key"].str.split().str[0]).merge(votes[["permco", "cik"]], on="permco")
            .merge(first, on=["cik", "w"]))
    names_used = pd.concat([hits, joins, phits, same])[["permco", "cik", "key"]].drop_duplicates()
    names_used = names_used[[pc in pairs for pc in zip(names_used["permco"], names_used["cik"])]]
    # Year by year: the linked filer with accounts that year; ties go to the one with more matches
    py = k[["permco", "fyear"]].drop_duplicates().merge(votes[["permco", "cik", "matched"]], on="permco")
    have = panel[["cik", "year", "revenue"]].rename(columns={"year": "fyear"})
    py = py.merge(have, on=["cik", "fyear"], how="inner")
    py = py.sort_values(["matched", "revenue"]).drop_duplicates(["permco", "fyear"], keep="last")
    print(f"Bridge: {votes['permco'].nunique():,} permcos linked to {votes['cik'].nunique():,} SEC filers "
          f"({prefix['permco'].nunique():,} by leading words); {len(names_used):,} assignee names in use")
    return votes, py[["permco", "fyear", "cik"]], names_used


def main():
    OUT.mkdir(exist_ok=True)
    PROC.mkdir(parents=True, exist_ok=True)
    counts = []
    panel, names = sec_accounts(counts)
    k = patents(counts)
    votes, link, names_used = bridge(k, names, panel, counts)

    # Citation weight: forward citations relative to the mean for patents filed the same year
    k["weight"] = k["cites"] / k.groupby("fyear")["cites"].transform("mean")
    k = k.merge(link, on=["permco", "fyear"], how="left")
    # A patent counts only if its own assignee name is one that matched that filer: KPSS groups some
    # unrelated assignees under one permco (Robert Bosch and BMW patents sit with Parker-Hannifin's)
    ok = k.merge(names_used.assign(ok=True), on=["permco", "cik", "key"], how="left")["ok"]
    ok = ok.fillna(False).astype(bool).values
    counts.append(("patents in linked firm-years whose assignee name matched the filer", int(ok.sum()),
                   int((k["cik"].notna() & ~ok).sum())))
    k.loc[~ok, "cik"] = np.nan
    for y0, y1 in [(2008, 2022), (2011, 2020)]:
        w = k[k["fyear"].between(y0, y1)]
        counts.append((f"KPSS patents filed {y0}-{y1} attributed to an SEC filer", int(w["cik"].notna().sum()),
                       int(w["cik"].isna().sum())))
    print(f"Patents attributed to an SEC filer: {k['cik'].notna().mean():.1%} of KPSS patents filed "
          f"{PATENT_YEARS[0]}-{PATENT_YEARS[-1]}")
    fp = (k.dropna(subset=["cik"]).groupby(["cik", "fyear"])
          .agg(patents=("patent_num", "size"), cw_patents=("weight", "sum"), cites=("cites", "sum"))
          .reset_index().rename(columns={"fyear": "year"}))
    panel = panel.merge(fp, on=["cik", "year"], how="left")
    for c in ["patents", "cw_patents", "cites"]:
        panel[c] = panel[c].fillna(0)
    linked = set(votes["cik"])
    panel["patent_linked"] = panel["cik"].isin(linked).astype(int)

    cols = ["cik", "year", "name", "sic", "countryba", "revenue", "opinc", "costs", "pretax", "interest", "ppe",
            "assets", "rd",
            "patents", "cw_patents", "cites", "patent_linked"]
    panel[cols].sort_values(["cik", "year"]).to_csv(PROC / "firm_years.csv.gz", index=False,
                                                    compression="gzip", float_format="%.6g")
    votes.sort_values("matched", ascending=False).to_csv(PROC / "patent_bridge.csv", index=False)
    pd.DataFrame(counts, columns=["step", "kept", "dropped"]).to_csv(OUT / "build_counts.csv", index=False)
    print(pd.DataFrame(counts, columns=["step", "kept", "dropped"]).to_string(index=False))
    print(f"Wrote data/processed/firm_years.csv.gz ({len(panel):,} rows) and data/processed/patent_bridge.csv "
          f"({len(votes):,} links)")


if __name__ == "__main__":
    main()
