"""Tier-1 official CCAA budget parser (SPEC.md T10).

Pulls, per CCAA x year x {presupuestado, liquidado}, the "Clasificación
Funcional por capítulos" report from Ministerio de Hacienda's two SGCIEF
portals:

  - PublicacionPresupuestos (initial/approved budget, `presupuestado`)
  - PublicacionLiquidaciones (executed budget, `liquidado`)

Both portals are ASP.NET WebForms apps with no documented API: the
"Descargas en Excel" option is a same-page POST (year + CCAA code + report
type + VIEWSTATE/EVENTVALIDATION tokens scraped from a fresh GET of the
form) that returns a real .xlsx directly — confirmed by hand before writing
this script, see SPEC.md T10.

This is NOT wildfire-specific — it's the finest cross-CCAA-comparable
breakdown this consolidated source offers (~20 functional "políticas de
gasto" categories, e.g. "41. Agricultura, Pesca y Alimentación", which
*contains* wildfire spend along with everything else agriculture/fisheries/
food-related). Two columns are extracted per row: the CCAA's grand total
("Total Gastos") and the 41-code subtotal, both clearly labeled as what
they are — an authoritative denominator upgrade and a coarse sanity-check
ceiling, not a wildfire figure. See wildfire-funding/parsers/README.md for
how this composes with the per-CCAA Tier-2 wildfire-specific parsers.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "wff_total_budget_timeseries.csv"

PORTALS = {
    "presupuestado": {
        "base": "https://serviciostelematicosext.hacienda.gob.es/SGCIEF/PublicacionPresupuestos/aspx/",
        "entry": "inicio.aspx",
        "field": "tipoDescarga",
        "years": range(2013, 2025),  # 2025/2026 are proyecto-stage in this portal, skip for now
    },
    "liquidado": {
        "base": "https://serviciostelematicosext.hacienda.gob.es/SGCIEF/PublicacionLiquidaciones/aspx/",
        "entry": "menuInicio.aspx",
        "field": "tipoConsulta",
        "years": range(2013, 2025),
    },
}

REPORT = "../aspx/DescargaFuncionalCapDC.aspx?cdcdad="

CCAA_CODES = {
    "01": "Andalucía",
    "02": "Aragón",
    "03": "Principado de Asturias",
    "17": "Comunidad Valenciana",
    "05": "Canarias",
    "06": "Cantabria",
    "07": "Castilla y León",
    "08": "Castilla-La Mancha",
    "09": "Cataluña",
    "10": "Extremadura",
    "11": "Galicia",
    "04": "Islas Baleares",
    "12": "Comunidad de Madrid",
    "13": "Región de Murcia",
    "14": "Comunidad Foral de Navarra",
    "15": "País Vasco",
    "16": "La Rioja",
    # 18 Ceuta, 19 Melilla intentionally excluded — not tracked elsewhere in this project
}

HIDDEN_RE = re.compile(r'id="(__VIEWSTATE|__VIEWSTATEGENERATOR|__EVENTVALIDATION)" value="([^"]*)"')


def fetch_tokens(session: requests.Session, base: str, entry: str) -> dict[str, str]:
    session.get(base + entry, timeout=30)
    resp = session.get(base + "SelDescargaDC.aspx", timeout=30, headers={"Referer": base + entry})
    return dict(HIDDEN_RE.findall(resp.text))


def download_one(session: requests.Session, base: str, field: str, tokens: dict, year: int, ccaa_code: str) -> bytes | None:
    data = {
        "__VIEWSTATE": tokens.get("__VIEWSTATE", ""),
        "__VIEWSTATEGENERATOR": tokens.get("__VIEWSTATEGENERATOR", ""),
        "__EVENTVALIDATION": tokens.get("__EVENTVALIDATION", ""),
        "ctl00$MainContent$ano": str(year),
        "ctl00$MainContent$autonomia": ccaa_code,
        f"ctl00$MainContent${field}": REPORT,
        "ctl00$MainContent$botonAceptar.x": "10",
        "ctl00$MainContent$botonAceptar.y": "10",
    }
    resp = session.post(
        base + "SelDescargaDC.aspx",
        data=data,
        timeout=30,
        headers={"Referer": base + "SelDescargaDC.aspx"},
    )
    ctype = resp.headers.get("Content-Type", "")
    if "spreadsheet" not in ctype:
        return None  # empty year/CCAA combo (e.g. CCAA didn't exist yet, or no data published) -> server returns an HTML page instead
    return resp.content


def parse_xlsx(content: bytes) -> tuple[float | None, float | None]:
    """Returns (total_gastos_eur, func41_agricultura_pesca_eur), both in EUR (source is in thousands)."""
    import io

    df = pd.read_excel(io.BytesIO(content), header=None)
    total = None
    func41 = None
    for _, row in df.iterrows():
        label = str(row[0]) if pd.notna(row[0]) else ""
        last = row.iloc[-1]
        if label.strip().lower().startswith("total gastos") and pd.notna(last):
            total = float(last) * 1000
        if label.strip().startswith("41.") and pd.notna(last):
            func41 = float(last) * 1000
    return total, func41


def main() -> None:
    rows = []
    for spend_type, cfg in PORTALS.items():
        session = requests.Session()
        for year in cfg["years"]:
            # Refresh tokens once per year (cheap) rather than once per (year, ccaa) —
            # if a CCAA-level POST ever 419s / gets a session-expired page, this loop
            # re-fetches tokens for the next CCAA rather than silently emitting nulls.
            tokens = fetch_tokens(session, cfg["base"], cfg["entry"])
            for code, ccaa in CCAA_CODES.items():
                try:
                    content = download_one(session, cfg["base"], cfg["field"], tokens, year, code)
                except requests.RequestException as e:
                    print(f"  ! {spend_type} {year} {ccaa}: request failed ({e})", file=sys.stderr)
                    continue
                if content is None:
                    continue
                try:
                    total, func41 = parse_xlsx(content)
                except Exception as e:
                    print(f"  ! {spend_type} {year} {ccaa}: parse failed ({e})", file=sys.stderr)
                    continue
                if total is None:
                    continue
                rows.append(
                    {
                        "ccaa": ccaa,
                        "year": year,
                        "spend_type": spend_type,
                        "total_gastos_eur": total,
                        "func41_agricultura_pesca_alimentacion_eur": func41,
                        "source_ref": f"{cfg['base']}DescargaFuncionalCapDC.aspx?cdcdad={code}&ano={year}",
                    }
                )
                time.sleep(0.3)  # be polite to a public-sector server, not rate-limit-evading
            print(f"{spend_type} {year}: {sum(1 for r in rows if r['year'] == year and r['spend_type'] == spend_type)}/{len(CCAA_CODES)} CCAAs", file=sys.stderr)

    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({len(out)} rows)")


if __name__ == "__main__":
    main()
