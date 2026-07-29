"""Build the sexual_crimes.json dashboard data blob.

Reads the MIR Informe/Anuario/Balance JSON + processed convictions CSV,
returns the dict written to docs/data/sexual_crimes.json.
"""

import csv
import json
from collections import defaultdict

INFORME_JSON = "data/raw/sexual_crimes_mir_2017-2024.json"
ANUARIO_JSON = "data/raw/sexual_crimes_mir_anuario_2016-2023.json"
BALANCE_JSON = "data/raw/sexual_crimes_mir_balance_2019-2025.json"
CONVICTIONS_CSV = "data/processed/ine_condenados_28716_sexual_crimes.csv"

# LO 10/2022 renamed categories mid-series (V24) — pre/post variants unified
# into one continuous series each; every other category name is stable
# across the reform and maps to itself.
CATEGORY_UNIFY = {
    "agresion_sexual": "agresion_sexual_unified",
    "abuso_sexual": "agresion_sexual_unified",
    "agresion_sexual_post_lo10_2022": "agresion_sexual_unified",
    "agresion_sexual_con_penetracion": "agresion_sexual_con_penetracion_unified",
    "abuso_sexual_con_penetracion": "agresion_sexual_con_penetracion_unified",
    "agresion_sexual_con_penetracion_post_lo10_2022": "agresion_sexual_con_penetracion_unified",
}

# MIR's own region labels for nationality by_country rows changed in 2024
# (broader "EUROPA" replacing EU-only "UNION EUROPEA", new APATRIDA/OCEANIA
# buckets) — normalized to one canonical 5-region scale so region lines are
# continuous across the taxonomy change. "Europe" is EU-only 2019-2023 but
# all-Europe-excl-Spain in 2024 (broader) — a real definition break, not a
# bug; documented in the cav-sexual caveat, not silently smoothed over.
REGION_LABEL_MAP = {
    "AFRICA": "Africa",
    "AMERICA": "America",
    "ASIA": "Asia",
    "UNION EUROPEA": "Europe",
    "EUROPA (EXCEPTO ESPANA)": "Europe",
    "RESTO PAISES": "Other",
    "OCEANIA": "Other",
    "APATRIDA": "Other",
    "SIN DATOS SOBRE EL PAIS": "Other",
    "PAIS DESCONOCIDO": "Other",
}
REGIONS = ["Africa", "America", "Asia", "Europe", "Other"]
TOP_N_COUNTRY = 6  # fewer than migration's 7 — only 5 canonical regions here

# Country-name spelling drifts across report editions (typo, Spanish vs
# English spelling, or a name changed between editions) — normalized to one
# canonical spelling per country so e.g. Venezuela isn't split into two
# separate legend entries with each holding half its true count.
COUNTRY_NAME_NORMALIZE = {
    "VENUZUELA": "VENEZUELA",
    "CHINA": "CHINA POPULAR",
    "PAKISTAN": "PAQUISTAN",
    "DOMINICANA": "REPUBLICA DOMINICANA",
    "DOMINICANA REP.": "REPUBLICA DOMINICANA",
    "REP. DOMINICANA": "REPUBLICA DOMINICANA",
    "R. DOMINICANA": "REPUBLICA DOMINICANA",
}
# MIR's own within-region residual rows (not a real country) — excluded
# from the named-country pool; various editions spell this differently.
RESIDUAL_ROW_PREFIXES = ("OTROS", "RESTO")


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def num(x):
    """Parse an int/float cell, tolerating '' and trailing '.0'."""
    if x is None or x == "":
        return None
    try:
        f = float(x)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None


def _merge_totals(informe, anuario, balance):
    """Reported-totals timeline: Anuario backfills 2016-2018 (Informe's
    2017/2018 editions have no reliably-parseable headline typology table —
    see mir_parser.py InformeParser._extract_typology docstring — so their
    total_count is None despite those years now contributing nationality
    data elsewhere); Balance extends one year past Informe's latest (2025,
    not yet in Informe/Anuario) and is also carried in full as a separate
    `balance_total` overlay — Balance's own totals diverge 7-9% from
    Anuario/Informe in 2022+ (B24, self-flagged "pending consolidation" in
    the source), a real cross-publication discrepancy worth showing rather
    than hiding behind a single merged number."""
    by_year = {}
    for r in anuario:
        if r["year"] < 2019:
            by_year[r["year"]] = {
                "total": r["total_count"], "clearance_rate": r.get("clearance_rate"),
                "perp_male_pct": r.get("perp_male_pct"), "source": "anuario",
            }
    for r in informe:
        if r["total_count"] is None:
            # 2017/2018: nationality data is real (see below) but this
            # edition's own headline total isn't parseable — keep the
            # Anuario-sourced total already set above rather than clobbering
            # it with None.
            continue
        by_year[r["year"]] = {
            "total": r["total_count"], "clearance_rate": r.get("clearance_rate"),
            "perp_male_pct": r.get("perp_male_pct"), "source": "informe",
        }
    balance_by_year = {r["year"]: r["total_count"] for r in balance}
    for y, tot in balance_by_year.items():
        if y not in by_year:
            by_year[y] = {"total": tot, "clearance_rate": None, "perp_male_pct": None, "source": "balance"}

    years = sorted(by_year)
    return {
        "years": years,
        "total": [by_year[y]["total"] for y in years],
        "source": [by_year[y]["source"] for y in years],
        "clearance_rate": [by_year[y]["clearance_rate"] for y in years],
        "perp_male_pct": [by_year[y]["perp_male_pct"] for y in years],
        "balance_total": [balance_by_year.get(y) for y in years],
    }


def _unified_categories(informe):
    """All categories the Informe reports (2019-2024), pre/post-LO10/2022
    variants unified (V24). Read directly from the JSON rather than
    data/processed/sexual_crime_evolution.csv, whose category section is
    missing 2020 entirely despite the raw JSON having full 2020 data."""
    years = sorted(r["year"] for r in informe)
    per_year = {}
    for r in informe:
        agg = defaultdict(int)
        for c in r["categories"]:
            key = CATEGORY_UNIFY.get(c["category"], c["category"])
            agg[key] += c.get("count") or 0
        per_year[r["year"]] = agg
    all_keys = sorted({k for agg in per_year.values() for k in agg})
    return {
        "years": years,
        # None (not 0) for a category absent from that year's report — some
        # categories were introduced partway through the series (e.g.
        # promocion_prostitucion_nuevas_tecnologias, "categoria nueva,
        # introducida en el informe de 2023" per the source's own notes);
        # 0 would misrepresent "didn't exist yet" as "zero cases occurred".
        "series": {k: [per_year[y].get(k) for y in years] for k in all_keys},
    }


# B38: the 2020 Informe's victim-nationality table (page 19 of
# MIR_Informe_DelitosSexuales2020.pdf) prints TOTAL=429 (310 Spanish + 119
# foreign) for a report titled "Año 2020" — ~31x smaller than that year's
# 13,174 headline crime count, and wildly inconsistent with every other
# year's equivalent table (2019's prints 15,706, within 2.5% of its 15,319
# headline). The 2020 perpetrator-nationality table on the same report is
# fine (7,959, a plausible annual figure). Confirmed via direct PDF text
# dump, not a parser bug — pdfplumber extracts exactly what the page prints.
# Treated as a source-document defect: nulled here rather than plotted as a
# fake ~97%-of-year dip in every region's line.
BAD_NATIONALITY_YEARS = {"victims": {2020}, "perpetrators": set()}


def _nationality_breakdown(informe, side):
    """T-sx-nat: region totals + top-N-country-plus-Other drill-down for
    `side` ('victims' or 'perpetrators'), mirroring migration's T68/T72
    stock_by_region/by_country shape. "Other" is always computed as
    region_total minus the named top countries (not a source-provided
    figure) so it reconciles exactly even in years with a genuine country-
    level breakdown gap (e.g. perpetrators in most years lack a sex split
    but still carry country totals)."""
    excluded = BAD_NATIONALITY_YEARS[side]
    years = sorted(r["year"] for r in informe)
    region_totals = defaultdict(lambda: defaultdict(int))       # region -> year -> total
    country_totals = defaultdict(lambda: defaultdict(int))      # (region, name) -> year -> total
    for r in informe:
        y = r["year"]
        if y in excluded:
            continue
        for row in r["nationality"][side].get("by_country", []):
            region = REGION_LABEL_MAP.get(row["region"], row["region"])
            if region not in REGIONS:
                continue
            if row["is_region_total"]:
                region_totals[region][y] += row.get("total") or 0
            elif not row["name"].upper().startswith(RESIDUAL_ROW_PREFIXES):
                # MIR's own within-region residual row is excluded from the
                # named-country pool — its value falls through into our own
                # subtraction-based "Other" bucket below instead of
                # duplicating it as a second, redundant "other" entry.
                name = COUNTRY_NAME_NORMALIZE.get(row["name"].upper(), row["name"].upper())
                country_totals[(region, name.title())][y] += row.get("total") or 0

    latest = years[-1]
    codes_by_region = defaultdict(list)
    for (region, name) in country_totals:
        codes_by_region[region].append(name)

    def val(d, y):
        return None if y in excluded else d.get(y, 0)

    by_country = {}
    for region in REGIONS:
        names = codes_by_region[region]
        ranked = sorted(names, key=lambda n: country_totals[(region, n)].get(latest, 0), reverse=True)
        top = ranked[:TOP_N_COUNTRY]
        series = {n: [val(country_totals[(region, n)], y) for y in years] for n in top}
        named_sum = [sum(country_totals[(region, n)].get(y, 0) for n in top) for y in years]
        series["Other"] = [
            None if y in excluded else max(0, region_totals[region].get(y, 0) - named_sum[i])
            for i, y in enumerate(years)
        ]
        by_country[region] = {"countries": list(series.keys()), "series": series}

    return {
        "years": years,
        "regions": REGIONS,
        "series": {region: [val(region_totals[region], y) for y in years] for region in REGIONS},
        "by_country": by_country,
    }


def build():
    informe = read_json(INFORME_JSON)["reports"]
    informe.sort(key=lambda r: r["year"])
    anuario = read_json(ANUARIO_JSON)["reports"]
    balance = read_json(BALANCE_JSON)["reports"]

    totals = _merge_totals(informe, anuario, balance)
    categories = _unified_categories(informe)
    nationality_victims = _nationality_breakdown(informe, "victims")
    nationality_perpetrators = _nationality_breakdown(informe, "perpetrators")

    # Convictions by nationality group (INE table 28716), aggregated across
    # sexual-crime categories per (year, nationality).
    conv_rows = read_csv(CONVICTIONS_CSV)
    conv = defaultdict(lambda: defaultdict(float))
    for r in conv_rows:
        conv[num(r["year"])][r["nationality_label"]] += num(r["count"]) or 0
    conv_years = sorted(conv)
    conv_groups = sorted({g for y in conv.values() for g in y})
    convictions = {
        "years": conv_years,
        "groups": conv_groups,
        "series": {g: [round(conv[y].get(g, 0)) for y in conv_years] for g in conv_groups},
    }

    return {
        "source": "Ministerio del Interior — Informe/Anuario/Balance sobre delitos contra la libertad sexual; INE Estadística de Condenados (t.28716)",
        "source_url": "https://estadisticasdecriminalidad.ses.mir.es/",
        "confidence": "high",
        "definition_breaks": {2022: "LO 10/2022 (‘Solo sí es sí’) narrowed the rape definition", 2023: "further reform"},
        "totals": totals,
        "categories": categories,
        "nationality_victims": nationality_victims,
        "nationality_perpetrators": nationality_perpetrators,
        "convictions": convictions,
    }


def main():
    print(json.dumps(build(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
