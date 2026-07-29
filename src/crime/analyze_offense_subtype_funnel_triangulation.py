"""T78 -- exploratory funnel triangulation: does INE's convicted-offense-
subtype mix for the "Africa" nationality group (region-level, the finest
nationality granularity 28716 offers) skew toward a particular sexual-crime
subtype (e.g. violacion vs agresion_sexual sin penetracion) relative to
other regions, and does MIR's country-level data suggest Morocco or Algeria
specifically drives Africa's share of cases?

This directly answers the user's question ("can we cross-check convicted
vs. investigated data, even though they show two different things, to infer
whether a crime subtype is more likely in a population") -- but the honest
answer is: only as an EXPLORATORY, heavily-caveated signal, not a resolved
joint distribution. Two real limitations, neither fixable with data
currently in this repo:

  1. FUNNEL-STAGE MISMATCH: INE table 28716 counts CONVICTED persons;
     MIR's by_country data counts INVESTIGATED/IDENTIFIED persons. These
     are different stages of denuncia -> investigacion -> imputacion ->
     condena, each with its own attrition (case strength, evidentiary
     standards, plea patterns, charge bargaining between subtypes,
     investigation-practice differences) that need not be uniform across
     nationality or subtype. A subtype's SHARE among convictions can differ
     from its share among investigations even with identical underlying
     offending, purely from differential attrition.
  2. GRANULARITY MISMATCH: INE's nationality axis stops at "Africa" (this
     table has no Morocco/Algeria-specific row); MIR's stops at named
     countries plus "AFRICA" region totals. Africa's convicted-subtype mix
     cannot be attributed to Morocco vs Algeria specifically from 28716
     alone -- only MIR's within-Africa country shares (perpetrator counts,
     not subtype-specific) can approximate how much of "Africa" each
     country represents, which is then combined with 28716's Africa-wide
     subtype mix as a (weak) proxy, NOT a real Morocco/Algeria subtype
     breakdown.

Association only (V9). Present as a signal to investigate further if a
country-level subtype x nationality source is ever found (see T76's INE
28857/28709 catalogue check for why finer sources weren't available),
never as resolving the offense-subtype question.

Data sources:
  data/processed/ine_condenados_28716_sexual_crimes.csv  -- convicted, by
      offense subtype x nationality-region x year
  data/raw/sexual_crimes_mir_2019-2024.json               -- investigated/
      identified, by country x year (incl. AFRICA region total)

Output:
  data/processed/offense_subtype_funnel_triangulation.csv
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
INE_CSV = ROOT / "data" / "processed" / "ine_condenados_28716_sexual_crimes.csv"
MIR_JSON = ROOT / "data" / "raw" / "sexual_crimes_mir_2019-2024.json"
OUT_CSV = ROOT / "data" / "processed" / "offense_subtype_funnel_triangulation.csv"

# Subtypes to compare (excludes cap8_total and abusos_agresiones_menores16,
# which is an LO10/2022-era merged category not comparable pre/post reform
# per SPEC.md C3/B6 -- kept out of this ratio to avoid conflating the
# definition break with a real regional signal).
SUBTYPES = ["violacion", "agresion_sexual", "agresiones_sexuales", "abusos_sexuales", "acoso_sexual", "exhibicionismo"]
REGIONS_OF_INTEREST = ["africa", "europa_no_ue", "america"]  # comparison set, not exhaustive


def load_ine_subtype_shares():
    """{year: {region: {subtype: pct_of_that_region's_cap8_total}}}"""
    rows = list(csv.DictReader(open(INE_CSV, encoding="utf-8")))
    by_year_region_subtype = {}
    cap8_by_year_region = {}
    for r in rows:
        year, label, nat, count = int(r["year"]), r["crime_label"], r["nationality_label"], float(r["count"])
        # INE reclassified EU27<->EU28 mid-series (post-Brexit) -- normalize
        # both "europa_no_ue27"/"europa_no_ue28" to one key so the
        # non-Africa comparison set doesn't silently drop years.
        if nat in ("europa_no_ue27", "europa_no_ue28"):
            nat = "europa_no_ue"
        if label == "cap8_total":
            cap8_by_year_region.setdefault(year, {})[nat] = count
        elif label in SUBTYPES:
            by_year_region_subtype.setdefault(year, {}).setdefault(nat, {})[label] = count

    result = {}
    for year, region_subtypes in by_year_region_subtype.items():
        result[year] = {}
        for region in REGIONS_OF_INTEREST:
            cap8_total = cap8_by_year_region.get(year, {}).get(region)
            if not cap8_total:
                continue
            subtype_counts = region_subtypes.get(region, {})
            result[year][region] = {
                s: round(subtype_counts.get(s, 0) / cap8_total * 100, 1) for s in SUBTYPES
            }
    return result


def load_mir_africa_country_shares():
    """{year: {country_name: pct of AFRICA region's total perpetrators}}"""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for report in data["reports"]:
        year = report["year"]
        by_country = report["nationality"]["perpetrators"]["by_country"]
        africa_total = next(
            (e["total"] for e in by_country if e.get("is_region_total") and e.get("region") == "AFRICA"), None)
        if not africa_total:
            continue
        result[year] = {
            e["name"]: round(e["total"] / africa_total * 100, 1)
            for e in by_country
            if not e.get("is_region_total") and e.get("region") == "AFRICA" and e["name"] in ("MARRUECOS", "ARGELIA")
        }
    return result


def main():
    ine_shares = load_ine_subtype_shares()
    mir_africa_shares = load_mir_africa_country_shares()

    rows = []
    for year in sorted(set(ine_shares) & set(mir_africa_shares)):
        africa_mix = ine_shares[year].get("africa", {})
        other_mix = {s: (ine_shares[year].get("europa_no_ue", {}).get(s, 0) +
                          ine_shares[year].get("america", {}).get(s, 0)) / 2 for s in SUBTYPES}
        ma_share = mir_africa_shares[year].get("MARRUECOS")
        dz_share = mir_africa_shares[year].get("ARGELIA")
        for subtype in SUBTYPES:
            rows.append({
                "year": year, "subtype": subtype,
                "africa_convicted_pct_of_africa_cap8": africa_mix.get(subtype),
                "other_regions_avg_convicted_pct": round(other_mix.get(subtype, 0), 1),
                "morocco_pct_of_mir_africa_perpetrators": ma_share,
                "algeria_pct_of_mir_africa_perpetrators": dz_share,
            })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")

    print("\n=== EXPLORATORY, heavily caveated (see module docstring) ===")
    print("Does 'Africa' region's CONVICTED offense-subtype mix (INE 28716) differ from other regions'?")
    for year in sorted(ine_shares):
        if "africa" not in ine_shares[year]:
            continue
        print(f"\n  {year}:")
        for s in SUBTYPES:
            africa_pct = ine_shares[year]["africa"].get(s, 0)
            print(f"    {s:22} Africa={africa_pct:5.1f}%")
        if year in mir_africa_shares:
            print(f"    MIR within-Africa perpetrator share: Marruecos={mir_africa_shares[year].get('MARRUECOS', 'n/a')}%  "
                  f"Argelia={mir_africa_shares[year].get('ARGELIA', 'n/a')}%")


if __name__ == "__main__":
    main()
