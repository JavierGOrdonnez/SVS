"""Build the sexual_crimes.json dashboard data blob.

Reads the MIR Informe/Anuario/Balance JSON + processed convictions CSV,
returns the dict written to docs/data/sexual_crimes.json.
"""

import csv
import json
from collections import defaultdict

INFORME_JSON = "data/raw/sexual_crimes_mir_2019-2024.json"
ANUARIO_JSON = "data/raw/sexual_crimes_mir_anuario_2016-2023.json"
BALANCE_JSON = "data/raw/sexual_crimes_mir_balance_2019-2025.json"
CONVICTIONS_CSV = "data/processed/ine_condenados_28716_sexual_crimes.csv"
MIGRATION_CSV = "data/raw/migration_spain.csv"

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
    earliest year is 2019); Balance extends one year past Informe's latest
    (2025, not yet in Informe/Anuario) and is also carried in full as a
    separate `balance_total` overlay — Balance's own totals diverge 7-9%
    from Anuario/Informe in 2022+ (B24, self-flagged "pending consolidation"
    in the source), a real cross-publication discrepancy worth showing
    rather than hiding behind a single merged number."""
    by_year = {}
    for r in anuario:
        if r["year"] < 2019:
            by_year[r["year"]] = {
                "total": r["total_count"], "clearance_rate": r.get("clearance_rate"),
                "perp_male_pct": r.get("perp_male_pct"), "source": "anuario",
            }
    for r in informe:
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


def _compute_spania(informe, side):
    """Derive Spain victim/perpetrator counts from spanish_pct and foreign total.

    MIR nationality tables only list foreign countries/regions; Spain (domestic)
    is given only as `spanish_pct`. We compute Spain's absolute count as:

        total = region_sum / (foreign_pct / 100)
        spain = total * spanish_pct / 100

    2020 is nulled on the victims side (B38)."""
    excluded = BAD_NATIONALITY_YEARS[side]
    years = sorted(r["year"] for r in informe)
    spain_data = {}
    for r in informe:
        y = r["year"]
        if y in excluded:
            spain_data[y] = None
            continue
        nat = r["nationality"][side]
        sp = nat.get("spanish_pct")
        fp = nat.get("foreign_pct")
        if sp is None or fp is None or fp == 0:
            spain_data[y] = None
            continue
        region_sum = sum(
            c.get("total") or 0 for c in nat.get("by_country", [])
            if c.get("is_region_total")
        )
        total = region_sum / (fp / 100)
        spain_data[y] = round(total * sp / 100)
    return [spain_data.get(y) for y in years]


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
    region_totals = defaultdict(lambda: defaultdict(int))
    country_totals = defaultdict(lambda: defaultdict(int))
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

    spain_series = _compute_spania(informe, side)

    return {
        "years": years,
        "regions": REGIONS,
        "series": {region: [val(region_totals[region], y) for y in years] for region in REGIONS},
        "by_country": by_country,
        "spain": spain_series,
    }


# MIR country names → ISO 3166-1 alpha-2 codes for migration population join
MIR_COUNTRY_ISO = {
    "ALEMANIA": "DE", "ARGELIA": "DZ", "ARGENTINA": "AR", "BELGICA": "BE",
    "BOLIVIA": "BO", "BRASIL": "BR", "BULGARIA": "BG",
    "CHINA": "CN", "CHINA POPULAR": "CN",
    "COLOMBIA": "CO",
    "DOMINICANA": "DO", "DOMINICANA REP.": "DO", "R. DOMINICANA": "DO",
    "REP. DOMINICANA": "DO", "REPUBLICA DOMINICANA": "DO",
    "ECUADOR": "EC",
    "FILIPINAS": "PH", "FRANCIA": "FR",
    "GEORGIA": "GE", "GUINEA ECUATORIAL": "GQ",
    "HOLANDA": "NL", "HONDURAS": "HN",
    "INDIA": "IN", "IRLANDA": "IE", "ITALIA": "IT",
    "MARRUECOS": "MA",
    "NICARAGUA": "NI", "NIGERIA": "NG",
    "PAKISTAN": "PK", "PAQUISTAN": "PK", "PARAGUAY": "PY", "PERU": "PE",
    "POLONIA": "PL", "PORTUGAL": "PT",
    "REINO UNIDO": "UK", "RUMANIA": "RO", "RUSIA": "RU",
    "SENEGAL": "SN", "SUECIA": "SE",
    "UCRANIA": "UA",
    "VENEZUELA": "VE", "VENUZUELA": "VE",
}

PELIGROSITY_AGE_BANDS = ("15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59")


def _peligrosity(informe, migration_rows):
    """Per-100k male 15-59 perpetrator rates by nationality (identified
    perpetrators from MIR Informe, denominator from migration_spain.csv
    stock_nationality + total population).

    Returns {years, groups: [countries], series: {country: [rate, ...]}}
    where the first group is always 'España' (derived from spanish_pct).
    """
    # Build denominator: male 15-59 population by nationality code × year
    pop = defaultdict(lambda: defaultdict(int))  # iso_code -> year -> pop
    total_male_15_59 = defaultdict(int)           # year -> total male 15-59
    for r in migration_rows:
        if r["age_group"] not in PELIGROSITY_AGE_BANDS:
            continue
        if r["sex"] != "male":
            continue
        code = r["nationality"]
        val = int(r["value"]) if r["value"] else 0
        pop[code][int(r["year"])] += val
        total_male_15_59[int(r["year"])] += val

    # Spanish male 15-59 population = total male 15-59 (from all nationalities
    # in stock_nationality) — the foreign stock dataset only covers 50
    # nationalities (~86% of INE ECP foreign stock); the residual ~14% of
    # foreign population (small nationalities not in the top-50) is a known
    # coverage gap. This means Spanish-denominator counts are slightly
    # *over*stated (since the foreign denominator is understated), making
    # Spain's peligrosity rate a slight *under*estimate and foreign rates
    # a slight *over*estimate.
    TOTAL_POP_CSV = "data/processed/population_spain_midyear_5yr.csv"
    with open(TOTAL_POP_CSV, encoding="utf-8") as f:
        total_rows = list(csv.DictReader(f))
    total_male_15_59_all = defaultdict(int)
    for r in total_rows:
        if r["age_group"] not in PELIGROSITY_AGE_BANDS:
            continue
        if r["sex"] != "male":
            continue
        total_male_15_59_all[int(r["year"])] += int(r["population_july1"]) if r["population_july1"] else 0

    for y in total_male_15_59:
        es_pop = total_male_15_59_all.get(y, 0) - total_male_15_59.get(y, 0)
        if es_pop > 0:
            pop["ES"][y] = es_pop

    years = sorted(r["year"] for r in informe)
    # Build per-year per-country numerator from MIR perpetrator data
    # First compute Spain as a derived entry
    spain_by_year = dict(zip(years, _compute_spania(informe, "perpetrators")))

    perp_by_country = defaultdict(lambda: defaultdict(int))  # name -> year -> count
    for r in informe:
        y = r["year"]
        for row in r["nationality"]["perpetrators"].get("by_country", []):
            if row.get("is_region_total") or row["name"].upper().startswith(RESIDUAL_ROW_PREFIXES):
                continue
            name = COUNTRY_NAME_NORMALIZE.get(row["name"].upper(), row["name"].upper())
            iso = MIR_COUNTRY_ISO.get(name)
            if iso:
                perp_by_country[iso][y] += row.get("total") or 0

    # Pick groups: Spain + top foreign groups by latest-year perp count
    latest = years[-1]
    foreign_counts = [(iso, perp_by_country[iso].get(latest, 0)) for iso in perp_by_country]
    foreign_counts.sort(key=lambda x: -x[1])
    top_foreign = [iso for iso, _ in foreign_counts[:7]]

    all_groups = ["ES"] + top_foreign

    def rate(iso, y):
        num = None
        if iso == "ES":
            num = spain_by_year.get(y)
        else:
            num = perp_by_country[iso].get(y)
        if num is None or num == 0:
            return None
        den = pop[iso].get(y)
        if den is None or den == 0:
            return None
        return round(num / den * 100000, 2)

    group_label = {
        "ES": "España", "MA": "Marruecos", "RO": "Rumanía", "CO": "Colombia",
        "VE": "Venezuela", "EC": "Ecuador", "DZ": "Argelia", "PE": "Perú",
        "BO": "Bolivia", "DO": "Rep. Dominicana", "BR": "Brasil", "HN": "Honduras",
        "PK": "Pakistán", "BG": "Bulgaria", "IT": "Italia", "FR": "Francia",
        "DE": "Alemania", "PT": "Portugal", "PL": "Polonia", "CN": "China",
        "PH": "Filipinas", "NG": "Nigeria", "PY": "Paraguay", "GB": "Reino Unido",
        "AR": "Argentina", "BE": "Bélgica", "NL": "Holanda", "RU": "Rusia",
        "UA": "Ucrania", "SN": "Senegal", "NI": "Nicaragua", "GE": "Georgia",
        "GQ": "Guinea Ecuatorial", "IN": "India", "IE": "Irlanda", "SE": "Suecia",
    }

    series = {}
    for iso in all_groups:
        label = group_label.get(iso, iso)
        series[label] = [rate(iso, y) for y in years]

    return {
        "years": years,
        "groups": [group_label.get(iso, iso) for iso in all_groups],
        "series": series,
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

    # Peligrosity: per-100k male 15-59 perpetrator rates by nationality
    migration_rows = read_csv(MIGRATION_CSV)
    peligrosidad = _peligrosity(informe, migration_rows)

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
        "peligrosidad": peligrosidad,
    }


def main():
    print(json.dumps(build(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
