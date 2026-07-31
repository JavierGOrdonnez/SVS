"""Parse the SES (Sistema Estadístico de Criminalidad) hate-crime nationality
megatablas — the Interior Ministry's own queryable microdata behind the
"Informe de Delitos de Odio" PDF reports' charts.

Source portal: https://estadisticasdecriminalidad.ses.mir.es (no auth, no
Cloudflare block — unlike the PDF host, interior.gob.es).

Two tables used here (of a 20-table `06001`-`06020` family covering
hechos-conocidos/esclarecidos/victimizaciones/detenciones, each at
CCAA-or-provincia granularity — only the two national-level nationality
tables are used for now, per project scope):

    06019 = Detenciones e investigados x calificacion x comunidades
            autonomas x nacionalidad x periodo x ambito x sexo
    06013 = Victimizaciones (idem, victims instead of detentions)

Coverage is 2021-2024 only — confirmed empirically against a second,
non-nationality table (06001, hechos conocidos) which is *also*
2021-2024-only in this portal, so the cutoff is a portal-wide limitation,
not specific to the nationality tables. Years 2016-2020 remain exclusively
in the PDF reports that `OdioParser` (mir_parser.py) already extracts from;
this module does not touch or duplicate that series.

Both tables use per-country nationality rows (89 countries) x 18 CCAA x 3
sex values x ~13 ambito categories x 4 years -- this module filters to
`Comunidades autonomas == "TOTAL NACIONAL"` at parse time and discards every
other region row (national-level scope only, per project decision), which
also keeps the processed output small even though the raw download is
19-24MB per table.

Validated against hand-checked figures (see data/sources/mir_delitos_odio.md):
2023 detainees, all ambitos, national: 1,161 total / 914 Espana = 78.7%
Spanish (matches the previously prose-only "78.73%" figure). 2023 detainees,
Orientacion sexual e identidad de genero ambito only: 194/269 = 72.1%
Spanish -- a real national OSIG-specific aggressor-nationality figure that
no PDF or press source had previously surfaced.
"""

import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).parent.parent.parent
RAW_DIR = ROOT / "data" / "raw"

SES_BASE = "https://estadisticasdecriminalidad.ses.mir.es/sec/jaxiPx/files/_px/es/csv_bdsc/Datos6/l0/"

TABLES = {
    "detenidos": "06019",
    "victimas": "06013",
}

# The two tables use different labels for the "both/all sexes" aggregate row
# -- 06013 (victims) also breaks out "Persona juridica" (legal-person
# victims, e.g. an association) and "Se desconoce" as their own sex
# categories, which 06019 (detentions) does not have.
TOTAL_SEXO_LABEL = {
    "06019": "Ambos sexos",
    "06013": "TOTAL sexo",
}

NATIONAL_ROW = "TOTAL NACIONAL"

# 2021+ ambito labels not yet in mir_parser.classify_odio_category's
# vocabulary. DISFOBIA is the current label for the disability-hate-crime
# ambito (renamed again, same lineage as DISCAPACIDAD -> DIVERSIDAD
# FUNCIONAL -> PERSONA CON DISCAPACIDAD tracked there); ISLAMOFOBIA is a
# genuinely new category (first broken out in the 2024 report).
NEW_AMBITO_LABELS = {
    "DISFOBIA": "discapacidad",
    "ISLAMOFOBIA": "islamofobia",
}


def fetch_raw(table_id: str) -> str:
    url = SES_BASE + f"{table_id}.px_bdsc"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.content.decode("utf-8-sig")


def parse_raw(text: str) -> pd.DataFrame:
    """Parse the SES CSV (semicolon-delimited, Spanish number format) and
    filter to national-level rows only.

    Column layout differs slightly by table: 06019 (detenciones) carries an
    extra leading "Calificacion" column that 06013 (victimizaciones) does
    not -- detect by column count rather than hardcoding one layout.
    """
    df = pd.read_csv(
        StringIO(text),
        sep=";",
        thousands=".",
        decimal=",",
        encoding="utf-8-sig",
    )
    if len(df.columns) == 7:
        df.columns = ["calificacion", "ccaa", "nacionalidad", "anyo", "ambito", "sexo", "total"]
        df = df.drop(columns=["calificacion"])
    elif len(df.columns) == 6:
        df.columns = ["ccaa", "nacionalidad", "anyo", "ambito", "sexo", "total"]
    else:
        raise ValueError(f"Unexpected column count {len(df.columns)}: {list(df.columns)}")
    df["total"] = pd.to_numeric(df["total"], errors="coerce")

    national = df[df["ccaa"] == NATIONAL_ROW].copy()
    national = national.drop(columns=["ccaa"])
    national = national.sort_values(["anyo", "ambito", "nacionalidad", "sexo"]).reset_index(drop=True)
    return national


def validate(df: pd.DataFrame, total_sexo_label: str) -> list[str]:
    """Check per-country nationality rows reconcile with the 'TOTAL
    nacionalidad' row, and per-ambito rows reconcile with 'TOTAL ambito'."""
    errors = []
    both = df[df["sexo"] == total_sexo_label]
    for year in sorted(both["anyo"].unique()):
        for ambito in both["ambito"].unique():
            slice_ = both[(both["anyo"] == year) & (both["ambito"] == ambito)]
            total_row = slice_[slice_["nacionalidad"] == "TOTAL nacionalidad"]
            sub_rows = slice_[slice_["nacionalidad"] != "TOTAL nacionalidad"]
            if total_row.empty or sub_rows.empty:
                continue
            expected = float(total_row["total"].iloc[0])
            actual = float(sub_rows["total"].sum())
            if abs(actual - expected) > 2:
                errors.append(
                    f"{year}/{ambito}: nationality sub-totals {actual:.0f} != "
                    f"TOTAL nacionalidad {expected:.0f}"
                )
    return errors


def summarize_spanish_share(df: pd.DataFrame, total_sexo_label: str) -> pd.DataFrame:
    """Per (year, ambito): Espana count, total count, foreign count, % Spanish."""
    both = df[df["sexo"] == total_sexo_label]
    espana = both[both["nacionalidad"] == "ESPAÑA"][["anyo", "ambito", "total"]].rename(
        columns={"total": "espana"}
    )
    total = both[both["nacionalidad"] == "TOTAL nacionalidad"][["anyo", "ambito", "total"]].rename(
        columns={"total": "total_nacionalidad"}
    )
    summary = total.merge(espana, on=["anyo", "ambito"], how="left")
    summary["foreign"] = summary["total_nacionalidad"] - summary["espana"]
    summary["pct_spanish"] = (summary["espana"] / summary["total_nacionalidad"] * 100).round(1)
    return summary.sort_values(["anyo", "ambito"]).reset_index(drop=True)


def fetch_and_process(table_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    total_sexo_label = TOTAL_SEXO_LABEL[table_id]
    text = fetch_raw(table_id)
    df = parse_raw(text)
    errors = validate(df, total_sexo_label)
    if errors:
        print(f"  VALIDATION WARNINGS ({table_id}):", file=sys.stderr)
        for e in errors:
            print(f"    ⚠ {e}", file=sys.stderr)
    else:
        print(f"  ✓ validation passed ({table_id})")
    return df, summarize_spanish_share(df, total_sexo_label)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, table_id in TABLES.items():
        print(f"Fetching SES table {table_id} ({name})...")
        df, summary = fetch_and_process(table_id)
        years = sorted(df["anyo"].unique())
        print(f"  {len(df)} national-level rows; years {years}")

        out_raw = RAW_DIR / f"hate_crimes_ses_nacionalidad_{name}_2021-2024.csv"
        out_summary = RAW_DIR / f"hate_crimes_ses_nacionalidad_{name}_summary_2021-2024.csv"
        df.to_csv(out_raw, index=False)
        summary.to_csv(out_summary, index=False)
        print(f"  Saved → {out_raw.name} ({len(df)} rows), {out_summary.name} ({len(summary)} rows)")

        print(f"\n  === % Spanish by ambito, {name} ===")
        pivot = summary.pivot_table(values="pct_spanish", index="ambito", columns="anyo", aggfunc="sum")
        print(pivot.to_string())
        print()


if __name__ == "__main__":
    main()
