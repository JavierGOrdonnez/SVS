"""MIR Sexual Violence Report Parser (T21).

Parses two PDF series from Ministerio del Interior:
  1. "Informe sobre Delitos contra la Libertad e Indemnidad Sexual en España"
     (dedicated annual reports, 2019–present; most consistent table format)
  2. "Anuario Estadístico del Ministerio del Interior"
     (chapters on crimes, 2000–2021; broader document, variable format)

Usage:
    python src/parsers/mir_parser.py --mode informe --pdf-dir /path/to/informes/
    python src/parsers/mir_parser.py --mode anuario --pdf-dir /path/to/anuarios/
    python src/parsers/mir_parser.py --mode informe --pdf /path/to/single.pdf --year 2023

The PDFs must be downloaded manually (interior.gob.es returns 403 for automated fetches):
  Informes index: https://www.interior.gob.es/opencms/es/archivos-y-documentacion/
      publicaciones/.../informe-sobre-delitos-contra-la-libertad-e-indemnidad-sexual-en-espana/
  Anuarios index: https://www.interior.gob.es/opencms/es/archivos-y-documentacion/
      publicaciones/.../anuario-estadistico-del-ministerio-del-interior/

Output: one consolidated data/raw/sexual_crimes_mir_{min_year}-{max_year}.json
per --mode run (informe mode keeps the bare filename; anuario mode gets an
`_anuario` tag, since the two are independently-sourced series, not one
dataset -- see B6/V13). Nested, Pydantic-validated MIRDataset -> MIRReport
(one per year) -> categories: [CategorySexBreakdown] for category x sex,
nationality: {victims, perpetrators} for nationality x sex at report-total
level -- see the MIRReport/MIRDataset models below for the full schema.

Validation gate (V12): sum(crime subcategories) must equal headline total.
"""

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import pdfplumber
    import pandas as pd
    from pydantic import BaseModel
except ImportError:
    sys.exit("Install: pip install pdfplumber pandas pydantic")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import parse_es_number

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "data" / "raw"


# ──────────────────────────────────────────────────────────────
# Data model
# ──────────────────────────────────────────────────────────────

@dataclass
class MIRRecord:
    year: int
    crime_category: str        # e.g. 'violacion', 'agresion_sin_penetracion', 'total'
    legal_article: str         # e.g. 'Art.179', 'Art.181', 'all'
    count: int | None
    victims_female: int | None = None
    victims_male: int | None = None
    victims_unknown: int | None = None
    victims_minor_pct: float | None = None
    victims_spanish_pct: float | None = None
    victims_foreign_pct: float | None = None
    victims_by_country: list | None = None
    perp_female: int | None = None
    perp_male: int | None = None
    perp_male_pct: float | None = None
    perp_spanish_pct: float | None = None
    perp_foreign_pct: float | None = None
    perp_by_country: list | None = None
    clearance_rate: float | None = None
    source_document: str = ""
    source_table: str = ""
    source_page: int | None = None
    confidence: str = "medium"
    notes: str = ""


# ──────────────────────────────────────────────────────────────
# Number parsing utilities
# ──────────────────────────────────────────────────────────────

def parse_pct(s: str) -> float | None:
    v = parse_es_number(s.replace("%", ""))
    return v


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# ──────────────────────────────────────────────────────────────
# Crime-category classification
#
# LO 10/2022 ("solo sí es sí", effective ~Oct 2022) eliminated the distinct
# "abuso sexual" category, merging it into "agresión sexual" (and likewise
# "abuso sexual con penetración" into "agresión sexual con penetración").
# Reports from 2022 onward use the merged definition even when the label text
# itself doesn't say "y abuso" (e.g. the 2024 report just says "Agresión
# sexual", per its own footnote that this includes former abuso cases).
# We give the merged post-reform categories distinct keys so they are never
# silently summed/compared against the pre-reform series of the same name.
# ──────────────────────────────────────────────────────────────

REFORM_NOTE = (
    'Categoria redefinida por LO 10/2022 ("solo si es si"), vigente desde oct-2022: '
    'incluye los delitos anteriormente tipificados como "abuso sexual". '
    "No comparable directamente con años anteriores a 2022."
)


def classify_category(raw_label: str, merged_categories: bool) -> tuple[str, str, str] | None:
    """Map a (possibly noisy) Spanish category label to (key, legal_article, note)."""
    norm = strip_accents(raw_label).upper()
    has_penetracion = "PENETRACION" in norm
    has_abuso = "ABUSO" in norm
    has_agresion = "AGRESION" in norm

    # Checked first: legend-text recovery for garbled tables sometimes glues a
    # stray "AGRESIONES" chart-annotation word onto this category's label, so
    # it must be classified before the AGRESION/ABUSO checks below.
    if "CONTACTO" in norm and ("TECNOLOG" in norm or "GROOMING" in norm or "16 A" in norm):
        return ("contacto_tecnologico_menor_16", "Art.183 bis", "")

    if has_agresion and "SEXUAL" in norm and (has_abuso or merged_categories):
        if has_penetracion:
            return ("agresion_sexual_con_penetracion_post_lo10_2022", "Art.179 (LO 10/2022)", REFORM_NOTE)
        return ("agresion_sexual_post_lo10_2022", "Art.178-179 (LO 10/2022)", REFORM_NOTE)
    if has_agresion and "SEXUAL" in norm:
        return (("agresion_sexual_con_penetracion" if has_penetracion else "agresion_sexual"),
                ("Art.179" if has_penetracion else "Art.178"), "")
    if has_abuso and "SEXUAL" in norm:
        return (("abuso_sexual_con_penetracion" if has_penetracion else "abuso_sexual"),
                ("Art.182" if has_penetracion else "Art.181"), "")
    if "EXHIBICIONISMO" in norm:
        return ("exhibicionismo", "Art.185", "")
    if "PORNOGRAF" in norm:
        return ("pornografia_menores", "Art.189", "")
    if "PROSTITU" in norm and (
        "PROMOCION" in norm or "PROMUEV" in norm or "TECNOLOG" in norm or "DIGITAL" in norm
    ):
        return ("promocion_prostitucion_nuevas_tecnologias", "Art.187-189", "Categoria nueva, introducida en el informe de 2023.")
    if "PROSTITU" in norm:
        return ("delitos_relativos_prostitucion", "Art.187", "")
    if "ACOSO" in norm:
        return ("acoso_sexual", "Art.184", "")
    if "CORRUPCION" in norm or "DISCAPAC" in norm:
        return ("corrupcion_menores_discapacitados", "Art.181", "")
    if "PROVOCACION" in norm:
        return ("provocacion_sexual", "Art.186", "")
    if norm.strip() in ("TOTAL", "TOTAL GENERAL") or (
        "TOTAL" in norm and (
            len(norm.strip()) < 16
            or "VICTIMIZACION" in norm
            or "DETEN" in norm
            or "INVESTIGAD" in norm
        )
    ):
        return ("total_sexual_crimes", "all", "")
    return None


_LEGEND_PAIR_RE = re.compile(r"([A-ZÁÉÍÓÚÑÜ0-9()/.,\s-]{3,120}?)(\d{1,2},\d)\s*%")


def extract_legend_pcts(text: str) -> dict[float, str]:
    """Recover clean (pct -> label) pairs from a chart-legend text block.

    Chart-annotation numbers (axis ticks, pie-slice group totals) in these
    reports are always whole percentages (e.g. "83%"), while true per-category
    percentages always carry one decimal (e.g. "3,1%"); requiring a comma
    lets the regex skip over annotation clutter automatically.
    """
    out: dict[float, str] = {}
    for label, pct in _LEGEND_PAIR_RE.findall(text):
        v = parse_pct(pct)
        if v is not None:
            out[round(v, 1)] = label.strip()
    return out


# ──────────────────────────────────────────────────────────────
# "Tipología penal" table extraction
#
# Every "Informe sobre Delitos..." (2019+) report has one multi-year crime
# typology table ("Hechos conocidos registrados. Tipologías penales") and
# one parallel clearance table ("Hechos esclarecidos ... Tipologías
# penales"). Two cell layouts are observed:
#   - Format A (2019, 2021, 2022, 2023): one big table row where the label
#     column and each year column are each a single '\n'-joined blob with
#     the same item count (pdfplumber merges multi-line chart labels into
#     one cell). In the 2022/2023 reports this label blob is additionally
#     corrupted by an overlapping text layer (leftover chart template
#     artifact from the LO 10/2022 category merge); the numeric cells stay
#     clean. We recover the true labels by matching the table's own
#     (clean) per-category percentage column against a clean legend text
#     block found elsewhere in the same table ("Año YYYY\nLABEL X,Y%...").
#   - Format B (2024): one table row per category, cells already separated.
# In both formats we only need the report's own (rightmost) year column,
# since the CLI already writes one CSV per report year.
# ──────────────────────────────────────────────────────────────

def _locate_typology_table(pdf, keywords: list[str], merged_categories: bool, start: int = 0):
    """Find the first page (from `start`) whose text contains all `keywords`
    and, among its tables, the one that actually parses into >=2 crime
    categories (some report years put the "TIPOLOGIA PENAL" section title in
    a separate text object above the table rather than gluing it into a
    table cell, so a literal substring match on table content is unreliable)."""
    for i in range(start, len(pdf.pages)):
        page = pdf.pages[i]
        text = strip_accents(page.extract_text() or "").upper()
        if not all(kw in text for kw in keywords):
            continue
        best_table, best_score = None, 0
        for table in page.extract_tables():
            if not table:
                continue
            results = parse_typology_table(table, merged_categories)
            score = sum(1 for k in results if k != "total_sexual_crimes")
            if score > best_score:
                best_table, best_score = table, score
        if best_score >= 2:
            return i, best_table
    return None, None


def parse_typology_table(table: list[list[str]], merged_categories: bool) -> dict[str, tuple[int, str, str]]:
    """Extract {category_key: (count, legal_article, note)} for the report's own year."""
    results: dict[str, tuple[int, str, str]] = {}

    # --- Format B: one row per category, already clean ---
    # (Require >=2 distinct non-total categories; a lone TOTAL row can also
    # look like a valid single-row match and must not short-circuit format A.)
    non_total_hits = 0
    for row in table:
        cells = [c.strip() for c in row if c not in (None, "") and str(c).strip() != ""]
        if len(cells) < 3:
            continue
        label = cells[0]
        if "TIPOLOG" in strip_accents(label).upper():
            continue
        # Format-A's glued content row packs an entire category list into a
        # single 3-cell row (label/values/pcts each newline-joined); Format-B
        # rows have one cell per year and can *also* wrap a long label across
        # several lines, so only treat this as a glued row when cell count is
        # small too (a genuine per-year row here has 8+ cells).
        if len(cells) <= 3 and label.count("\n") >= 3:
            continue  # format-A glued row, handled below
        year_cells = cells[1:]
        numeric = [parse_pct(c) if "%" in c else parse_es_number(c) for c in year_cells]
        if len(numeric) < 2 or any(v is None for v in numeric[:-1]):
            continue
        clean_label = label.replace("\n", " ").strip()
        cls = classify_category(clean_label, merged_categories)
        if not cls:
            continue
        key, article, note = cls
        # Last cell is typically an aggregate share (e.g. "TOTALES"), not a year value.
        value = numeric[-2] if "%" in year_cells[-1] else numeric[-1]
        if value is not None:
            results[key] = (int(round(value)), article, note)
            if key != "total_sexual_crimes":
                non_total_hits += 1
    if non_total_hits >= 2:
        return _with_fallback_total(results)
    results = {}

    # --- Format A: single glued-cell content row (+ separate TOTAL row) ---
    for row in table:
        cells = [c for c in row if c not in (None, "") and str(c).strip() != ""]
        if len(cells) < 2:
            continue
        label_cell = cells[0]

        # Plain single-value TOTAL row (no '\n' glut, one number per year column).
        if label_cell.count("\n") == 0:
            cls = classify_category(label_cell, merged_categories)
            if cls and cls[0] == "total_sexual_crimes":
                value = parse_es_number(cells[-1])
                if value is not None:
                    results["total_sexual_crimes"] = (int(round(value)), "all", "")
            continue

        if label_cell.count("\n") < 3 or len(cells) < 3:
            continue  # not the glued content row

        value_cell, pct_cell = cells[-2], cells[-1]
        values = [parse_es_number(v) for v in value_cell.split("\n")]
        if not values or any(v is None for v in values):
            continue
        n = len(values)
        label_lines = label_cell.split("\n")[:n]
        pct_lines = [parse_pct(p) for p in pct_cell.split("\n")[:n]]

        direct_ok = (
            len(label_lines) == n
            and classify_category(label_lines[0], merged_categories) is not None
        )
        if direct_ok:
            for lbl, val in zip(label_lines, values):
                cls = classify_category(lbl, merged_categories)
                if cls and val is not None:
                    key, article, note = cls
                    results[key] = (int(round(val)), article, note)
        else:
            # Labels are corrupted: recover them via the clean legend block
            # ("Año YYYY\nLABEL X,Y%...") elsewhere in the same table.
            legend_text = "\n".join(
                str(c) for r2 in table for c in r2
                if c and "ANO " in strip_accents(str(c)).upper() and "%" in str(c)
            )
            legend = extract_legend_pcts(legend_text)
            for pct, val in zip(pct_lines, values):
                if pct is None or val is None:
                    continue
                lbl = legend.get(round(pct, 1))
                if not lbl:
                    continue
                cls = classify_category(lbl, merged_categories)
                if cls:
                    key, article, note = cls
                    results[key] = (int(round(val)), article, note)
    return _with_fallback_total(results)


def _with_fallback_total(
    results: dict[str, tuple[int, str, str]],
) -> dict[str, tuple[int, str, str]]:
    """Some report years' typology table has no explicit "Total general" row
    (e.g. 2024's "hechos conocidos" table) -- fall back to summing the
    subcategories we did find."""
    if "total_sexual_crimes" not in results:
        sub_counts = [v[0] for k, v in results.items() if k != "total_sexual_crimes"]
        if len(sub_counts) >= 2:
            results["total_sexual_crimes"] = (sum(sub_counts), "all", "")
    return results


def parse_clearance_rate(table: list[list[str]] | None) -> float | None:
    """Extract the overall '% de esclarecidos sobre hechos conocidos' for the
    report's own year, if the table has an explicit row for it (2022+)."""
    if not table:
        return None
    for row in table:
        cells = [c for c in row if c not in (None, "") and str(c).strip() != ""]
        if len(cells) < 2:
            continue
        label = strip_accents(cells[0]).upper()
        if "ESCLARECID" in label and "CONOCID" in label:
            return parse_pct(cells[-1])
    return None


# ──────────────────────────────────────────────────────────────
# Per-category "sexo" breakdown table extraction
#
# Both the victims section ("Victimizaciones registradas según sexo") and
# the perpetrators section ("Detenciones/investigados según sexo") have one
# such table per report. Column order (Masculino/Femenino[/Desconocido]/
# Total) is NOT fixed across years -- 2024 reverses Femenino before
# Masculino and drops the "Desconocido"/Total columns for perpetrators --
# so it must be detected per table rather than hardcoded by position.
# Three cell layouts are observed:
#   - parallel columns: one glued, '\n'-joined label cell plus one glued
#     value cell per sex column, in the same row (victims table, 2019/2021/
#     2022/2023). A leading row-numbering cell ('1\n2\n...\n11') sometimes
#     precedes the label cell and must be stripped.
#   - single glued cell: 'LABEL NUM NUM NUM' repeated one per line inside a
#     single cell, no separate value columns at all (perpetrators table,
#     2019/2021/2022/2023).
#   - clean one-row-per-category (2024, both victims and perpetrators); its
#     header lives in page text rather than the table object itself, so the
#     caller must supply `col_order_hint` from `_detect_sex_col_order_from_text`.
# ──────────────────────────────────────────────────────────────

_SEX_KEYWORDS = {"MASCULINO": "male", "FEMENINO": "female", "TOTAL": "total"}
_COLUMNA_RE = re.compile(r"^COLUMNA\d*$", re.I)
_SEX_KW_RE = re.compile(r"MASCULINO|FEMENINO|NO\s*CONSTA|DESCONOCIDO|TOTAL")
_LEADING_NUM_RE = re.compile(r"^[\d.\-‐]+\s*")


def _normalize_sex_col(cell: str) -> str | None:
    norm = strip_accents(cell).upper().strip()
    if norm in _SEX_KEYWORDS:
        return _SEX_KEYWORDS[norm]
    if norm == "DESCONOCIDO" or re.fullmatch(r"NO\s*CONSTA", norm):
        return "unknown"
    return None


def _compact_cells(row) -> list[str]:
    """Drop None/empty cells and spreadsheet-template bleed-through cells
    ('Columna1', 'Columna17', ...) seen in the 2022/2023 reports."""
    out = []
    for c in row:
        if c in (None, ""):
            continue
        s = str(c).strip()
        if not s or _COLUMNA_RE.match(strip_accents(s).upper()):
            continue
        out.append(s)
    return out


def _is_numbering_col(cell: str) -> bool:
    lines = cell.split("\n")
    return len(lines) > 1 and lines[0].strip() == "1" and all(l.strip().isdigit() for l in lines)


def _dedupe_glued_number(s: str) -> str:
    """2022/2023 spreadsheet-template corruption sometimes glues a value's
    text twice ('699 699') and/or prefixes an Excel '###' column-overflow
    marker before the real value ('### 11.000'). Strip '#'-only tokens and
    collapse an exact duplicate down to a single value before parsing."""
    tokens = [t for t in s.split() if not re.fullmatch(r"#+", t)]
    if len(tokens) == 2 and tokens[0] == tokens[1]:
        tokens = tokens[:1]
    return " ".join(tokens) if tokens else s


def _detect_sex_col_order_from_text(text: str) -> list[str] | None:
    """Recover column order for a per-category sex table whose header is a
    separate page-text line rather than part of the pdfplumber table object
    (2024 report)."""
    norm = strip_accents(text).upper()
    for line in norm.split("\n"):
        found = [f for f in (_normalize_sex_col(m.group(0)) for m in _SEX_KW_RE.finditer(line)) if f]
        if len(found) >= 2 and "male" in found and "female" in found:
            return found
    return None


def _store_sex_result(results: dict, key: str, col_order: list[str], nums: list[float | None]):
    entry = results.setdefault(key, {})
    for colname, v in zip(col_order, nums):
        if v is not None:
            entry[colname] = int(round(v))


def parse_category_sex_table(
    table: list[list[str]], merged_categories: bool, col_order_hint: list[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Extract {category_key: {'male'/'female'/'unknown'/'total': count}} from
    a per-crime-category sex-breakdown table."""
    col_order = None
    for row in table:
        cells = _compact_cells(row)
        cols = [c for c in (_normalize_sex_col(c) for c in cells) if c]
        if len(cols) >= 2 and "male" in cols and "female" in cols:
            col_order = cols
            break
    if col_order is None:
        col_order = col_order_hint
    if not col_order:
        return {}
    k = len(col_order)

    results: dict[str, dict[str, int]] = {}
    for row in table:
        cells = _compact_cells(row)
        if not cells:
            continue
        if _is_numbering_col(cells[0]) and len(cells) >= 2:
            cells = cells[1:]
        if not cells:
            continue
        label_cell, rest = cells[0], cells[1:]
        if rest and all(_normalize_sex_col(c) for c in rest):
            continue  # header row, already consumed above
        if len(rest) == k + 1 and "%" in rest[-1]:
            rest = rest[:-1]  # trailing '% sobre total' / '% por tipologia' column

        n = label_cell.count("\n") + 1
        if len(rest) == k and all(r.count("\n") == 0 for r in rest):
            # single category row; label may still word-wrap across lines
            # (e.g. a long category name), but the values don't.
            cls = classify_category(label_cell.replace("\n", " "), merged_categories)
            if not cls:
                continue
            nums = [parse_es_number(_dedupe_glued_number(v)) for v in rest]
            if any(v is None for v in nums):
                continue
            _store_sex_result(results, cls[0], col_order, nums)
            continue

        label_lines = label_cell.split("\n")
        if len(rest) == k and all(len(r.split("\n")) == n for r in rest):
            # parallel value columns, aligned by line index
            value_cols = [r.split("\n") for r in rest]
            for i, lbl in enumerate(label_lines):
                cls = classify_category(lbl, merged_categories)
                if not cls:
                    continue
                nums = [parse_es_number(_dedupe_glued_number(vc[i])) for vc in value_cols]
                if any(v is None for v in nums):
                    continue
                _store_sex_result(results, cls[0], col_order, nums)
        elif not rest:
            # single glued cell: 'LABEL NUM NUM ... NUM' per line
            num_pat = r"\s+([\d.,]+)" * k
            line_re = re.compile(r"^(.*?)" + num_pat + r"\s*$")
            for line in label_lines:
                m = line_re.match(line.strip())
                if not m:
                    continue
                cls = classify_category(m.group(1).strip(), merged_categories)
                if not cls:
                    continue
                nums = [parse_es_number(g) for g in m.groups()[1:]]
                if any(v is None for v in nums):
                    continue
                _store_sex_result(results, cls[0], col_order, nums)
    return results


def _locate_category_sex_table(pdf, keywords: list[str], merged_categories: bool, start: int = 0):
    """Find the first page (from `start`) whose text contains all `keywords`
    and, among its tables, the one that parses into >=2 crime categories."""
    for i in range(start, len(pdf.pages)):
        page = pdf.pages[i]
        raw_text = page.extract_text() or ""
        text = strip_accents(raw_text).upper()
        if not all(kw in text for kw in keywords):
            continue
        col_order_hint = _detect_sex_col_order_from_text(raw_text)
        best_table, best_score = None, 0
        for table in page.extract_tables():
            if not table:
                continue
            results = parse_category_sex_table(table, merged_categories, col_order_hint)
            score = sum(1 for k in results if k != "total_sexual_crimes")
            if score > best_score:
                best_table, best_score = table, score
        if best_score >= 2:
            return i, best_table, col_order_hint
    return None, None, None


# ──────────────────────────────────────────────────────────────
# Total-level "nacionalidad" breakdown table extraction
#
# Nationality is only ever reported at the report-total level (crossed with
# sex, never with individual crime category), in one row per nationality
# group ("N.- ESPAÑOLES" / "N.- EXTRANJEROS", plus continent/country
# sub-rows we don't need). Unlike the typology/sex tables, these rows are
# never glued multi-category blobs, so a simple per-row scan suffices.
# ──────────────────────────────────────────────────────────────

def parse_nationality_table(table: list[list[str]]) -> tuple[float | None, float | None]:
    """Return (spanish_pct, foreign_pct) from a total-level nationality
    breakdown table, reading its own '% sobre total' / '%' column."""
    spanish = foreign = None
    for row in table:
        cells = _compact_cells(row)
        if len(cells) < 2:
            continue
        label = _LEADING_NUM_RE.sub("", strip_accents(cells[0]).upper()).strip()
        value_cells = cells[1:]
        if not label and len(cells) >= 2:
            # Numbering ("1.") sits in its own cell, label in the next one
            # (2024 report layout), rather than glued together (2019-2023).
            label = strip_accents(cells[1]).upper().strip()
            value_cells = cells[2:]
        is_spanish = label.startswith("ESPANOL")
        is_foreign = label.startswith("EXTRANJER")
        if not (is_spanish or is_foreign):
            continue
        pct = None
        for c in value_cells:
            if "%" in c:
                # 2022/2023 sometimes glue the percentage twice into one cell
                # ("64,2% 64,2%") — take only the first occurrence.
                m = re.search(r"[\d.,]+\s*%", c)
                pct = parse_pct(m.group(0)) if m else None
                break
        if pct is None:
            continue
        if is_spanish:
            spanish = pct
        else:
            foreign = pct
    return spanish, foreign


def _locate_nationality_table(pdf, keywords: list[str], start: int = 0):
    """Find the first page (from `start`) whose text contains all `keywords`
    and, among its tables, the one that yields both a spanish_pct and a
    foreign_pct value."""
    for i in range(start, len(pdf.pages)):
        page = pdf.pages[i]
        text = strip_accents(page.extract_text() or "").upper()
        if not all(kw in text for kw in keywords):
            continue
        for table in page.extract_tables():
            if not table:
                continue
            spanish, foreign = parse_nationality_table(table)
            if spanish is not None and foreign is not None:
                return i, spanish, foreign
    return None, None, None


# ──────────────────────────────────────────────────────────────
# Per-country nationality breakdown table extraction (T26)
#
# Below the Spanish/foreign aggregate, the same table breaks foreigners down
# by continent region ("2.1.- ÁFRICA") and then by country within each
# region (2019/2021/2022/2023: countries newline-blocked into one cell per
# region; 2024: one flat row per country). The 2024 perpetrators table has
# no sex breakdown at all (total + % only) -- col_order is then None and
# every entry carries only total/pct.
# ──────────────────────────────────────────────────────────────

class CountryBreakdown(BaseModel):
    name: str
    region: str
    is_region_total: bool = False
    male: int | None = None
    female: int | None = None
    unknown: int | None = None
    total: int | None = None
    pct: float | None = None


_NUM_PREFIX_RE = re.compile(r"^(\d+)\.(\d*)\.?[-‐]?\s*(.*)$")


def _classify_label_row(cells: list[str]) -> tuple[int | None, str | None, list[str]]:
    """Classify a compacted row by its label cell: 0 = top-level (ESPAÑOLES/
    EXTRANJEROS/TOTAL, already handled by parse_nationality_table), 1 =
    region header, None = country-level row (candidate)."""
    if not cells:
        return None, None, []
    m = _NUM_PREFIX_RE.match(cells[0].strip())
    if m:
        minor, rest_label = m.group(2), m.group(3).strip()
        if rest_label:
            return (1 if minor else 0), rest_label, cells[1:]
        if len(cells) < 2:
            return None, None, []
        return (1 if minor else 0), cells[1].strip(), cells[2:]
    if "TOTAL" in strip_accents(cells[0]).upper():
        return 0, cells[0].strip(), cells[1:]
    return None, cells[0], cells[1:]


def _build_country_entry(
    name: str, region: str, value_cells: list[str], col_order: list[str] | None,
    is_region_total: bool,
) -> CountryBreakdown | None:
    k = len(col_order) if col_order else 0
    n = max(k, 1)
    if len(value_cells) < n:
        return None
    pct = None
    for c in value_cells[n:]:
        if "%" in c:
            m = re.search(r"[\d.,]+\s*%", c)
            pct = parse_pct(m.group(0)) if m else None
            break
    if k == 0:
        total = parse_es_number(_dedupe_glued_number(value_cells[0]))
        if total is None:
            return None
        return CountryBreakdown(name=name, region=region, is_region_total=is_region_total,
                                 total=int(round(total)), pct=pct)
    nums = [parse_es_number(_dedupe_glued_number(v)) for v in value_cells[:k]]
    if any(v is None for v in nums):
        return None
    sexes = {colname: int(round(v)) for colname, v in zip(col_order, nums)}
    return CountryBreakdown(
        name=name, region=region, is_region_total=is_region_total,
        male=sexes.get("male"), female=sexes.get("female"),
        unknown=sexes.get("unknown"), total=sexes.get("total"), pct=pct,
    )


def parse_country_breakdown_table(
    rows: list[list[str]], col_order_hint: list[str] | None = None,
) -> list[CountryBreakdown]:
    """Extract every region/country row from a nationality breakdown table
    (all tables on the page, already flattened by the caller)."""
    col_order = None
    for row in rows:
        cells = _compact_cells(row)
        cols = [c for c in (_normalize_sex_col(c) for c in cells) if c]
        if len(cols) >= 2 and "male" in cols and "female" in cols:
            col_order = cols
            break
    if col_order is None:
        col_order = col_order_hint

    entries: list[CountryBreakdown] = []
    current_region: str | None = None
    for row in rows:
        cells = _compact_cells(row)
        if not cells:
            continue
        level, label, value_cells = _classify_label_row(cells)
        if level == 0 or label is None:
            continue
        if level == 1:
            region_name = strip_accents(label).upper().strip()
            current_region = region_name
            entry = _build_country_entry(region_name, region_name, value_cells, col_order, True)
            if entry:
                entries.append(entry)
            continue
        if current_region is None:
            continue
        if "\n" in label:
            names = label.split("\n")
            n = len(names)
            per_index_cells = []
            for i in range(n):
                row_vals = []
                for v in value_cells:
                    parts = v.split("\n")
                    row_vals.append(parts[i] if i < len(parts) else (parts[-1] if parts else v))
                per_index_cells.append(row_vals)
            for nm, vc in zip(names, per_index_cells):
                entry = _build_country_entry(
                    strip_accents(nm).upper().strip(), current_region, vc, col_order, False,
                )
                if entry:
                    entries.append(entry)
        else:
            entry = _build_country_entry(
                strip_accents(label).upper().strip(), current_region, value_cells, col_order, False,
            )
            if entry:
                entries.append(entry)
    return entries


# ──────────────────────────────────────────────────────────────
# Table detection helpers
# ──────────────────────────────────────────────────────────────

_TOTAL_CRIMES_PATTERNS = [
    re.compile(r"(total|delitos? sexuales?|libertad sexual)", re.I),
]
_RAPE_PATTERNS = [
    re.compile(r"(violaci[oó]n|agres[iío]n.{0,30}penetraci[oó]n|art\.?\s*179)", re.I),
]
_NO_PEN_PATTERNS = [
    re.compile(r"(sin penetraci[oó]n|agres[iío]n sexual sin)", re.I),
]
_VICTIM_SEX_PATTERNS = [
    re.compile(r"(v[ií]ctimas?.{0,20}(mujer|femenin|mujer))", re.I),
]
_PERP_NAT_PATTERNS = [
    re.compile(r"(nacionalidad|espa[ñn]ol.{0,20}extranjero|agresor.{0,30}nacionalidad)", re.I),
]


def header_matches(text: str, patterns: list) -> bool:
    return any(p.search(text) for p in patterns)


# ──────────────────────────────────────────────────────────────
# Informe parser (2019–2024 format)
# ──────────────────────────────────────────────────────────────

class InformeParser:
    """
    The MIR "Informe sobre Delitos contra la Libertad Sexual" (2019–2024)
    has a consistent structure:
      - Section 1: total crimes by category (table with violaciones, agresiones, etc.)
      - Section 2: victims (by sex, age, nationality)
      - Section 3: perpetrators (by sex, nationality, multiple perpetrators)
      - Section 4: clearance rates

    Table detection: we look for tables whose first-column text matches
    known category labels.
    """

    def __init__(self, pdf_path: Path, year: int):
        self.pdf_path = pdf_path
        self.year = year
        self.source = pdf_path.name
        self.records: list[MIRRecord] = []
        self._headline_total: int | None = None

    def parse(self) -> list[MIRRecord]:
        # Always seed a 'total_sexual_crimes' placeholder first (count=None)
        # so `_extract_sex_breakdown`/`_extract_nationality`'s `_update_field`
        # calls have a record to attach to even when `_extract_typology` finds
        # nothing (2017/2018's older layout, see below) -- otherwise their
        # results are silently dropped rather than shipped as a partial record.
        self._upsert("total_sexual_crimes", "all", None, None)
        with pdfplumber.open(self.pdf_path) as pdf:
            self._extract_typology(pdf)
            self._extract_sex_breakdown(pdf)
            self._extract_nationality(pdf)
        self._validate()
        return self.records

    def _extract_typology(self, pdf):
        """Extract the crime-typology and clearance-rate tables (the report's
        headline multi-year 'Tipología penal' tables), which are far more
        reliable than scanning every page for scattered category mentions.

        2017/2018 editions use an older layout this table-locator does not
        handle reliably: 2017 finds nothing at all, and 2018 was observed to
        match the wrong table and produce an internally-inconsistent total
        (81 vs a 703 subcategory sum -- off by ~9x). Rather than risk shipping
        a wrong headline count for those two years, skip typology extraction
        for year < 2019 entirely; `total_sexual_crimes.count` stays None and
        a note points at the independently-parsed, cross-validated Anuario
        series (`sexual_crimes_mir_anuario_2016-2023.json`) for the real
        total. Sex-breakdown and nationality data (this method's siblings)
        use a different, reliably-parseable table on these same editions and
        are unaffected by this skip."""
        if self.year < 2019:
            self._update_field(
                "total_sexual_crimes", "notes",
                "Headline 'hechos conocidos' typology table not reliably parseable in this "
                "edition's older layout (see mir_parser.py InformeParser._extract_typology "
                "docstring) -- total_count left unset rather than risking a wrong figure. "
                "See sexual_crimes_mir_anuario_2016-2023.json for this year's cross-validated "
                "total. Nationality/sex breakdown below is from a different, unaffected table.",
            )
            return
        merged_categories = self.year >= 2022

        known_page, known_table = _locate_typology_table(
            pdf, ["TIPOLOGIA PENAL", "HECHOS CONOCIDOS"], merged_categories
        )
        if known_table is None:
            print(f"  ⚠ {self.year}: could not locate 'hechos conocidos' typology table", file=sys.stderr)
            return
        cleared_start = (known_page + 1) if known_page is not None else 0
        cleared_page, cleared_table = _locate_typology_table(
            pdf, ["TIPOLOGIA PENAL", "HECHOS ESCLARECIDOS"], merged_categories, start=cleared_start
        )

        results = parse_typology_table(known_table, merged_categories)
        for key, (count, article, note) in results.items():
            self._upsert(key, article, count, known_page + 1 if known_page is not None else None, note)
            if key == "total_sexual_crimes":
                self._headline_total = count

        clearance_rate = parse_clearance_rate(cleared_table)
        if clearance_rate is None and cleared_table is not None:
            cleared_results = parse_typology_table(cleared_table, merged_categories)
            cleared_total = cleared_results.get("total_sexual_crimes")
            if cleared_total and self._headline_total:
                clearance_rate = round(cleared_total[0] / self._headline_total * 100, 1)
        if clearance_rate is not None:
            self._update_field("total_sexual_crimes", "clearance_rate", clearance_rate)

    def _extract_sex_breakdown(self, pdf):
        """Per-crime-category sex breakdown, for both victims and
        perpetrators ('... según sexo' tables), at report-total level."""
        merged_categories = self.year >= 2022

        v_page, v_table, v_hint = _locate_category_sex_table(
            pdf, ["TIPOLOG", "SEXO", "VICTIM"], merged_categories
        )
        if v_table is not None:
            for key, sexes in parse_category_sex_table(v_table, merged_categories, v_hint).items():
                if "female" in sexes:
                    self._update_field(key, "victims_female", sexes["female"])
                if "male" in sexes:
                    self._update_field(key, "victims_male", sexes["male"])
                if "unknown" in sexes:
                    self._update_field(key, "victims_unknown", sexes["unknown"])
        else:
            print(f"  ⚠ {self.year}: could not locate victim sex-breakdown table", file=sys.stderr)

        p_page, p_table, p_hint = _locate_category_sex_table(
            pdf, ["TIPOLOG", "SEXO", "DETEN"], merged_categories
        )
        if p_table is not None:
            p_results = parse_category_sex_table(p_table, merged_categories, p_hint)
            for key, sexes in p_results.items():
                if "female" in sexes:
                    self._update_field(key, "perp_female", sexes["female"])
                if "male" in sexes:
                    self._update_field(key, "perp_male", sexes["male"])
            total = p_results.get("total_sexual_crimes")
            if total and "male" in total:
                grand = total.get("total") or (
                    total.get("male", 0) + total.get("female", 0) + total.get("unknown", 0)
                )
                if grand:
                    self._update_field("total_sexual_crimes", "perp_male_pct",
                                        round(total["male"] / grand * 100, 1))
        else:
            print(f"  ⚠ {self.year}: could not locate perpetrator sex-breakdown table", file=sys.stderr)

    def _extract_nationality(self, pdf):
        """Total-level nationality breakdown (Spanish vs. foreign), plus the
        per-region/per-country rows on the same page (T26), for both victims
        and perpetrators."""
        v_page, v_spanish, v_foreign = _locate_nationality_table(pdf, ["NACIONALIDAD", "VICTIM"])
        if v_spanish is not None:
            self._update_field("total_sexual_crimes", "victims_spanish_pct", v_spanish)
        if v_foreign is not None:
            self._update_field("total_sexual_crimes", "victims_foreign_pct", v_foreign)
        if v_page is not None:
            v_countries = self._extract_country_rows(pdf, v_page)
            if v_countries:
                self._update_field("total_sexual_crimes", "victims_by_country", v_countries)

        p_page, p_spanish, p_foreign = _locate_nationality_table(pdf, ["NACIONALIDAD", "DETEN"])
        if p_spanish is not None:
            self._update_field("total_sexual_crimes", "perp_spanish_pct", p_spanish)
        if p_foreign is not None:
            self._update_field("total_sexual_crimes", "perp_foreign_pct", p_foreign)
        if p_page is not None:
            p_countries = self._extract_country_rows(pdf, p_page)
            if p_countries:
                self._update_field("total_sexual_crimes", "perp_by_country", p_countries)

        if v_spanish is None or p_spanish is None:
            print(f"  ⚠ {self.year}: could not locate nationality table(s) "
                  f"(victims={'ok' if v_spanish is not None else 'MISSING'}, "
                  f"perp={'ok' if p_spanish is not None else 'MISSING'})", file=sys.stderr)

    @staticmethod
    def _extract_country_rows(pdf, page_index: int) -> list[CountryBreakdown]:
        page = pdf.pages[page_index]
        rows = [row for table in page.extract_tables() for row in table]
        col_order_hint = _detect_sex_col_order_from_text(page.extract_text() or "")
        return parse_country_breakdown_table(rows, col_order_hint)

    def _upsert(self, category: str, article: str, count: int | None, page_no: int | None, note: str = ""):
        for r in self.records:
            if r.crime_category == category:
                if count:
                    r.count = count
                if page_no:
                    r.source_page = page_no
                if note:
                    r.notes = note
                return
        self.records.append(MIRRecord(
            year=self.year,
            crime_category=category,
            legal_article=article,
            count=count,
            source_document=self.source,
            source_table="tipologia_penal_table",
            source_page=page_no,
            notes=note,
        ))

    def _update_field(self, category: str, field_name: str, value):
        for r in self.records:
            if r.crime_category == category:
                setattr(r, field_name, value)
                return

    def _validate(self):
        total_rec = next((r for r in self.records if r.crime_category == "total_sexual_crimes"), None)
        if total_rec is None or total_rec.count is None:
            return
        total = total_rec.count
        sub_cats = [r.crime_category for r in self.records if r.crime_category != "total_sexual_crimes"]
        sub_sum = sum(r.count for r in self.records if r.crime_category in sub_cats and r.count)
        if sub_sum > 0 and abs(sub_sum - total) / total > 0.05:
            note = f"VALIDATION: sub-cat sum {sub_sum} vs headline {total} (diff {sub_sum-total})"
            total_rec.notes = (total_rec.notes + " " + note).strip()
            print(f"  ⚠ {self.year}: {note}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────
# Anuario parser (2000–2021 format)
# ──────────────────────────────────────────────────────────────

class AnuarioParser:
    """
    Sexual crimes in the MIR "Anuario Estadístico" do NOT live in a dedicated
    chapter with per-category tables (that was the original, untested
    assumption -- see B9). They live as one row ("III. Libertad sexual", or
    "III. Contra la libertad sexual" pre-2020) plus 4-5 numbered sub-rows
    inside the "Hechos conocidos por tipología penal" and "Hechos
    esclarecidos..." tables, each a single dense page covering ALL crime
    types with a 5-year "evolución"/"serie histórica" column window, in the
    "Seguridad Ciudadana" chapter. The table has no ruling lines --
    pdfplumber's extract_tables() finds nothing; text must be parsed directly.

    The table's printed number is NOT stable across editions (2016: TABLA
    3-1-1; 2017-2019: TABLA 3-1-2; 2020-2023: TABLA 3-1-5) and in at least
    one edition (2019) the string "TABLA 3-1-5" is reused for a completely
    different, unrelated table -- so the table is located by content (its
    "HECHOS CONOCIDOS"/"HECHOS ESCLARECIDOS" title plus the presence of the
    "III. libertad sexual" row) rather than by its printed number.

    Sub-category count varies by publication date (LO 10/2022 reform):
    - Pre-reform editions (e.g. the 2021 Anuario): 4 sub-rows. "Agresión
      sexual con penetración" = Art.179 alone (the violación-equivalent
      series, comparable to Informe's Art.179-only figures).
    - Post-reform editions (2022 Anuario onward) RETROACTIVELY restate prior
      years using the new merged scheme: 5 sub-rows, "Agresión sexual" +
      "Agresión sexual con penetración" are each agresión+abuso MERGED (see
      footnote "se computan agresiones sexuales... y abusos sexuales...").
      Consequence: the same year's headline sub-count differs by edition --
      e.g. 2021's "con penetración" count is 2.143 in the 2021 edition (old
      scheme) but 3.795 in the 2022/2023 editions (new scheme, retroactively
      restated) -- a genuine ~1.8x discrepancy from recategorization, not a
      parsing error. See B9/§B6.
    """

    # Table numbering is NOT stable across editions: 2016 uses TABLA 3-1-1,
    # 2017-2019 use TABLA 3-1-2, 2020-2023 use TABLA 3-1-5 -- and the 2019
    # edition's own "TABLA 3-1-5" is a *different*, unrelated table (regional
    # breakdown). So the table is located by content (a "HECHOS
    # CONOCIDOS"/"HECHOS ESCLARECIDOS" page that also contains the "III./3.
    # (Contra la) libertad sexual" row) rather than by its printed number.
    CONOCIDOS_RE = re.compile(r"HECHOS CONOCIDOS", re.I)
    ESCLARECIDOS_RE = re.compile(r"HECHOS ESCLARECIDOS", re.I)
    # "Tipología penal 2016 2017 ..." (2020+ editions) or
    # "Enero-diciembre 2015 2016 ..." (pre-2020 editions).
    YEAR_HEADER_RE = re.compile(r"(?:Tipolog.a penal|Enero-[Dd]iciembre)\s+((?:\d{4}\s*){2,6})", re.I)
    # "III. Libertad sexual" (2020+) or "III. Contra la libertad sexual" (pre-2020).
    TOTAL_ROW_RE = re.compile(r"^(iii\.|3\.)\s*(contra la )?libertad sexual\b")
    SECTION_END_RE = re.compile(r"^(iv\.|4\.)\s*relaciones familiares\b")
    NUM_RE = re.compile(r"\d{1,3}(?:\.\d{3})*(?:,\d+)?")

    def __init__(self, pdf_path: Path, year: int):
        self.pdf_path = pdf_path
        self.year = year
        self.source = pdf_path.name
        self.records: list[MIRRecord] = []

    def parse(self) -> list[MIRRecord]:
        page5 = page6 = None
        page5_no = page6_no = None
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                # Only accept a "HECHOS CONOCIDOS/ESCLARECIDOS" page as the
                # crime-typology table if it actually contains the "III.
                # (Contra la) libertad sexual" row -- some editions have
                # other tables with the same title phrase (e.g. an
                # aggregated summary table) that lack the per-category rows.
                has_row = any(self.TOTAL_ROW_RE.match(l.strip().lower()) for l in text.splitlines())
                if page5 is None and self.CONOCIDOS_RE.search(text) and has_row:
                    page5, page5_no = text, i + 1
                elif page6 is None and self.ESCLARECIDOS_RE.search(text) and has_row:
                    page6, page6_no = text, i + 1
                if page5 is not None and page6 is not None:
                    break
        if page5 is None:
            print(f"  ⚠ {self.year}: crime-typology table (hechos conocidos) not found in {self.source}", file=sys.stderr)
            return []
        self._extract(page5, page6, page5_no, page6_no)
        self._validate()
        return self.records

    def _year_columns(self, text: str) -> list[int]:
        m = self.YEAR_HEADER_RE.search(text)
        return [int(y) for y in m.group(1).split()] if m else []

    def _row_values(self, text: str, predicate, n_cols: int) -> list[float | None] | None:
        """Last n_cols numeric tokens of the first line matching predicate(line_lower)."""
        for line in text.splitlines():
            if predicate(line.lower()) and len(self.NUM_RE.findall(line)) >= n_cols:
                nums = self.NUM_RE.findall(line)[-n_cols:]
                return [parse_es_number(t) for t in nums]
        return None

    def _libertad_sexual_section(self, text: str) -> str:
        lines, started, out = text.splitlines(), False, []
        for line in lines:
            if not started and self.TOTAL_ROW_RE.match(line.strip().lower()):
                started = True
            if started:
                out.append(line)
                if self.SECTION_END_RE.match(line.strip().lower()) and len(out) > 1:
                    break
        return "\n".join(out)

    def _add_category(self, category: str, article: str, count: float | None, page_no: int, note: str):
        self.records.append(MIRRecord(
            year=self.year, crime_category=category, legal_article=article,
            count=int(count) if count is not None else None,
            source_document=self.source,
            # Table number varies by edition (3-1-1 in 2016, 3-1-2 in
            # 2017-2019, 3-1-5 in 2020-2023); identified by content, not number.
            source_table="Hechos conocidos por tipología penal (Seguridad Ciudadana)",
            source_page=page_no,
            confidence="high" if self.year >= 2012 else "medium",
            notes=note,
        ))

    def _extract(self, page5: str, page6: str | None, page5_no: int | None, page6_no: int | None):
        years5 = self._year_columns(page5)
        if self.year not in years5:
            print(f"  ⚠ {self.year}: not in crime-typology table column range {years5} of {self.source}", file=sys.stderr)
            return
        idx, n = years5.index(self.year), len(years5)

        total_row = self._row_values(page5, lambda l: self.TOTAL_ROW_RE.match(l) is not None, n)
        if total_row is None:
            print(f"  ⚠ {self.year}: 'III. (Contra la) libertad sexual' row not found in crime-typology table", file=sys.stderr)
            return
        total = total_row[idx]

        clearance = None
        if page6:
            years6 = self._year_columns(page6)
            if self.year in years6:
                esclar_row = self._row_values(page6, lambda l: self.TOTAL_ROW_RE.match(l) is not None, len(years6))
                if esclar_row is not None:
                    esclar = esclar_row[years6.index(self.year)]
                    if esclar is not None and total:
                        clearance = round(esclar / total * 100, 1)

        territorial_note = ""
        if self.year <= 2011:
            territorial_note = "TERRITORIAL LIMITATION: excludes Cataluña/PaísVasco/Navarra (~25-30% population). Multiply by ~1.3-1.5 for national estimate."

        self.records.append(MIRRecord(
            year=self.year, crime_category="total_sexual_crimes", legal_article="all",
            count=int(total) if total is not None else None,
            clearance_rate=clearance,
            source_document=self.source,
            source_table="Hechos conocidos/esclarecidos por tipología penal (Seguridad Ciudadana)",
            source_page=page5_no,
            confidence="high" if self.year >= 2012 else "medium",
            notes=territorial_note,
        ))

        section = self._libertad_sexual_section(page5)
        agresion_penetracion = self._row_values(section, lambda l: "sexual con penetraci" in l, n)
        agresion_sin_penetracion = self._row_values(
            section, lambda l: "agresi" in l and "sexual" in l and "penetraci" not in l, n)
        corrupcion = self._row_values(section, lambda l: "corrupci" in l and "menor" in l, n)
        pornografia = self._row_values(section, lambda l: "pornograf" in l and "menor" in l, n)
        # "4. Otras infracciones contra la libertad/indemnidad sexual" (2020+)
        # or "4. Otros contra la libertad/indemnidad sexual" (pre-2020).
        otras = self._row_values(
            section, lambda l: re.match(r"^\d\.\s*otr", l) and ("libertad" in l or "indemnidad" in l), n)

        merged_scheme = agresion_sin_penetracion is not None

        if agresion_penetracion is not None:
            if merged_scheme:
                self._add_category("agresion_sexual_con_penetracion_post_lo10_2022",
                                    "Art.179 (LO 10/2022)", agresion_penetracion[idx], page5_no, REFORM_NOTE)
            else:
                self._add_category("agresion_sexual_con_penetracion",
                                    "Art.179", agresion_penetracion[idx], page5_no, "")

        if agresion_sin_penetracion is not None:
            self._add_category("agresion_sexual_post_lo10_2022", "Art.178-179 (LO 10/2022)",
                                agresion_sin_penetracion[idx], page5_no, REFORM_NOTE)

        if corrupcion is not None:
            self._add_category("corrupcion_menores_discapacitados", "Art.181", corrupcion[idx], page5_no, "")

        if pornografia is not None:
            self._add_category("pornografia_menores", "Art.189", pornografia[idx], page5_no, "")

        if otras is not None:
            note = ("Aggregates remaining Art.178/181/183/185/187 etc. not broken out separately "
                    "in this Anuario table; not directly comparable to Informe's per-article categories.")
            self._add_category("otras_libertad_indemnidad_sexual", "various", otras[idx], page5_no, note)

    def _validate(self):
        total_rec = next((r for r in self.records if r.crime_category == "total_sexual_crimes"), None)
        if total_rec is None or total_rec.count is None:
            return
        total = total_rec.count
        sub_sum = sum(r.count for r in self.records
                      if r.crime_category != "total_sexual_crimes" and r.count)
        if sub_sum > 0 and abs(sub_sum - total) / max(total, 1) > 0.05:
            note = f"VALIDATION: sub-cat sum {sub_sum} vs headline {total}"
            total_rec.notes = (total_rec.notes + " " + note).strip()
            print(f"  ⚠ {self.year}: {note}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────
# Balance de Criminalidad parser (T55, quarterly format)
# ──────────────────────────────────────────────────────────────

class BalanceParser:
    """
    MIR "Balance de Criminalidad" quarterly reports contain one national
    aggregate table ("NACIONAL ... Acumulado enero a {mes}") among hundreds
    of per-region/province pages -- its page location is NOT fixed (front
    page in some editions, last page in others; verified to vary even
    between quarters of the same year). We scan a front+back window of pages
    for a line starting "NACIONAL" to find it robustly.

    CRITICAL: these are CUMULATIVE year-to-date figures, not per-quarter
    increments -- "Q2" already includes Q1's crimes, Q4 ("enero a
    diciembre") IS the full calendar year. Summing four quarters' cumulative
    values massively over-counts (~2.4-2.5x for the sexual-crimes total --
    see B24). The correct annual total per year is the Q4 report's own
    figure, not a sum.

    Only 2 sexual-crime subcategories are broken out (row 5.1 "con
    penetración" and row 5.2 "resto", a residual bucket combining
    everything else) -- coarser than Anuario/Informe's 4-7 subcategories.
    Row 5.2 is NOT directly comparable to Anuario's
    "otras_libertad_indemnidad_sexual" (that key excludes the
    sin-penetración "agresión sexual" category, which Balance's "resto"
    bucket includes) -- kept under its own key to avoid a false equivalence.

    Some editions carry an explicit "(tipificación previa a LO 10/22)"
    footnote on row 5.1 (e.g. 2022 Q3): they report the PRE-reform
    (narrower) definition even mid-way through the reform year. Each year's
    Q4 edition (published after the full year, without that footnote)
    already uses the merged post-reform definition -- same year >= 2022
    convention used elsewhere in this file.

    Header year columns are NOT fixed at 2 -- some editions (2022 Q3/Q4)
    compare against a 3-year window (e.g. 2019/2021/2022, skipping the
    pandemic-distorted 2020) instead of just prior-year/current-year. The
    target column must be located by matching the inferred year against the
    header's own year list, not by a fixed index. Row text can also contain
    spurious digit-like tokens from footnote text (e.g. "LO 10/22"), so
    count tokens are taken from the right-hand end of the line (immediately
    before the comma-bearing Var.% columns), not the left.
    """

    NATIONAL_RE = re.compile(r"^NACIONAL\b")
    TIPOLOGIA_RE = re.compile(r"^TIPOLOG", re.I)
    YEAR_RE = re.compile(r"(20\d{2})")
    NUM_RE = re.compile(r"-?\d{1,3}(?:\.\d{3})*(?:,\d+)?")
    PREFIX_RE = re.compile(r"^\s*\d+(?:\.\d+)?\.?-?\s*")
    TOTAL_ROW_RE = re.compile(r"^5\.-?\s*Delitos contra la libertad", re.I)
    PEN_ROW_RE = re.compile(r"^5\.1\.-?\s*Agresi.n sexual con penetraci", re.I)
    RESTO_ROW_RE = re.compile(r"^5\.2\.-?\s*Resto de delitos contra la libertad", re.I)
    WINDOW = 6  # pages scanned from front and from back to locate NACIONAL

    def __init__(self, pdf_path: Path, year: int, quarter: str):
        self.pdf_path = pdf_path
        self.year = year
        self.quarter = quarter
        self.source = pdf_path.name
        self.records: list[MIRRecord] = []
        self.period_label: str = ""

    def parse(self) -> list[MIRRecord]:
        with pdfplumber.open(self.pdf_path) as pdf:
            page_no, text = self._find_national_page(pdf)
        if text is None:
            print(f"  ⚠ {self.year} {self.quarter}: NACIONAL table not found in {self.source}", file=sys.stderr)
            return []
        self._extract(text, page_no)
        self._validate()
        return self.records

    def _find_national_page(self, pdf) -> tuple[int | None, str | None]:
        n = len(pdf.pages)
        candidates = sorted(set(range(0, min(self.WINDOW, n))) | set(range(max(0, n - self.WINDOW), n)))
        for i in candidates:
            text = pdf.pages[i].extract_text() or ""
            for line in text.splitlines():
                if self.NATIONAL_RE.match(line.strip()):
                    return i + 1, text
        return None, None

    def _header_years(self, text: str) -> list[str]:
        for line in text.splitlines():
            if self.TIPOLOGIA_RE.match(line.strip()):
                return self.YEAR_RE.findall(line)
        return []

    def _row_counts(self, text: str, label_re, n_year_cols: int) -> list[str] | None:
        """Last n_year_cols count-like tokens (no comma -- Var.% columns
        always carry a decimal comma) of the first line matching label_re."""
        for line in text.splitlines():
            s = line.strip()
            if label_re.match(s):
                rest = self.PREFIX_RE.sub("", s)
                nums = self.NUM_RE.findall(rest)
                count_tokens = [t for t in nums if "," not in t]
                if len(count_tokens) < n_year_cols:
                    return None
                return count_tokens[-n_year_cols:]
        return None

    def _extract(self, text: str, page_no: int | None):
        period_line = next((l for l in text.splitlines() if l.strip().startswith("NACIONAL")), "")
        self.period_label = period_line.strip()
        note_period = f"{self.period_label} ({self.quarter})."

        years = self._header_years(text)
        if str(self.year) not in years:
            print(f"  ⚠ {self.year} {self.quarter}: year not found in header columns {years} of {self.source}", file=sys.stderr)
            return
        idx, n = years.index(str(self.year)), len(years)

        total = self._row_counts(text, self.TOTAL_ROW_RE, n)
        pen = self._row_counts(text, self.PEN_ROW_RE, n)
        resto = self._row_counts(text, self.RESTO_ROW_RE, n)
        if total is None:
            print(f"  ⚠ {self.year} {self.quarter}: row 5 (total) not found", file=sys.stderr)
            return

        merged = self.year >= 2022

        self.records.append(MIRRecord(
            year=self.year, crime_category="total_sexual_crimes", legal_article="all",
            count=int(parse_es_number(total[idx])),
            source_document=self.source, source_table="NACIONAL (Balance de Criminalidad)",
            source_page=page_no, notes=note_period,
        ))
        if pen is not None:
            key, art, note = (
                ("agresion_sexual_con_penetracion_post_lo10_2022", "Art.179 (LO 10/2022)", REFORM_NOTE)
                if merged else ("agresion_sexual_con_penetracion", "Art.179", "")
            )
            self.records.append(MIRRecord(
                year=self.year, crime_category=key, legal_article=art,
                count=int(parse_es_number(pen[idx])),
                source_document=self.source, source_table="NACIONAL (Balance de Criminalidad)",
                source_page=page_no, notes=(note + " " + note_period).strip(),
            ))
        if resto is not None:
            note = ("Bucket residual del Balance: agrupa TODOS los delitos contra la libertad sexual "
                    "salvo 'agresion con penetracion' (incluye agresion/abuso sin penetracion, "
                    "corrupcion de menores, pornografia, etc. sin desglosar). No equivale a "
                    "'otras_libertad_indemnidad_sexual' del Anuario (esa clave excluye 'agresion sin "
                    "penetracion', que aqui si esta incluida).")
            self.records.append(MIRRecord(
                year=self.year, crime_category="resto_libertad_sexual_balance", legal_article="various",
                count=int(parse_es_number(resto[idx])),
                source_document=self.source, source_table="NACIONAL (Balance de Criminalidad)",
                source_page=page_no, notes=(note + " " + note_period).strip(),
            ))

    def _validate(self):
        total_rec = next((r for r in self.records if r.crime_category == "total_sexual_crimes"), None)
        pen_rec = next((r for r in self.records if r.crime_category.startswith("agresion_sexual_con_penetracion")), None)
        resto_rec = next((r for r in self.records if r.crime_category == "resto_libertad_sexual_balance"), None)
        if not (total_rec and pen_rec and resto_rec):
            return
        sub_sum = pen_rec.count + resto_rec.count
        if abs(sub_sum - total_rec.count) > 1:
            note = f"VALIDATION: 5.1+5.2={sub_sum} vs row-5 total={total_rec.count}"
            total_rec.notes = (total_rec.notes + " " + note).strip()
            print(f"  ⚠ {self.year} {self.quarter}: {note}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────
# "Delitos de Odio" (hate crime) ámbito classification
#
# The ámbito ("scope"/ground) list is NOT stable across years -- both
# renames (methodology breaks, not real trend changes) and genuine new
# ámbitos being added over time. We map every observed label variant to one
# stable internal key so category counts can be compared/summed across
# years without silently conflating a rename with a real change.
#   DISCAPACIDAD (2016) -> DIVERSIDAD FUNCIONAL (2017, explicit "nueva
#     metodologia de computo" in the report itself; causes an artefactual
#     -91.2% single-year drop, 262->23, that is NOT a real decline) ->
#     PERSONA CON DISCAPACIDAD (2018-2020) -> DELITOS DE ODIO CONTRA
#     PERSONAS CON DISCAPACIDAD (2021, 2023) -- all map to "discapacidad".
#   ANTIGITANISMO: new ámbito, introduced in the 2019 report ("nuevo
#     ambito", explicit in the report's own prose).
#   DISCRIMINACION GENERACIONAL (ageism) and DISCRIMINACION POR RAZON DE
#     ENFERMEDAD: both new in the 2018 report (absent in 2016/2017).
# ──────────────────────────────────────────────────────────────

ODIO_DISCAPACIDAD_NOTE = (
    'Ambito historicamente inestable: "DISCAPACIDAD" (2016) fue renombrado '
    '"DIVERSIDAD FUNCIONAL" en el informe de 2017 con una nueva metodologia '
    "de computo explicitamente senalada en el propio informe (la caida de "
    "262 a 23, -91,2%, es un artefacto metodologico, no un descenso real); "
    'paso a llamarse "PERSONA CON DISCAPACIDAD" desde 2018. Tratar '
    "comparaciones que crucen 2016/2017/2018+ con cautela."
)
ODIO_ANTIGITANISMO_NOTE = "Nuevo ambito introducido en el informe de 2019 (no desglosado en anos anteriores)."


def classify_odio_category(raw_label: str) -> str | None:
    """Map a (possibly noisy) Spanish hate-crime ámbito label to a stable
    internal key. Order matters: more specific checks (ANTIGITANISMO,
    ORIENTAC.) must run before generic substring checks that could
    otherwise misfire (e.g. DISCRIMINACION+SEXO+GENERO also appearing,
    coincidentally, inside an ORIENTACION SEXUAL label)."""
    norm = strip_accents(raw_label).upper()
    letters_only = re.sub(r"[^A-Z]", "", norm)

    if "ANTIGITANISMO" in norm:
        return "antigitanismo"
    if "ANTISEMITISMO" in norm:
        return "antisemitismo"
    if "APOROFOBIA" in norm:
        return "aporofobia"
    if "CREENCIAS" in norm and ("RELIGIOS" in norm or "PRACTICAS" in norm):
        return "creencias_practicas_religiosas"
    if "DIVERSIDAD" in norm and "FUNCIONAL" in norm:
        return "discapacidad"
    if "DISCAPACIDAD" in norm:
        return "discapacidad"
    if "DISFOBIA" in norm:
        return "discapacidad"
    if "ISLAMOFOBIA" in norm:
        return "islamofobia"
    if "ORIENTAC" in norm and ("SEXUAL" in norm or "IDENTIDAD" in norm or "IDENT" in norm):
        return "orientacion_identidad_sexual_genero"
    if "RACISMO" in norm or "XENOFOB" in norm:
        return "racismo_xenofobia"
    if "IDEOLOG" in norm:
        return "ideologia"
    if "DISCRIMINACION" in norm and "GENERAC" in norm:
        return "discriminacion_generacional"
    if "DISCRIMINACION" in norm and "ENFERM" in norm:
        return "discriminacion_enfermedad"
    if "DISCRIMINACION" in norm and "SEXO" in norm and "GENERO" in norm:
        return "discriminacion_sexo_genero"
    if "INFRAC" in norm and ("ADM" in norm or "RESTO" in norm):
        return "infracciones_administrativas"
    if "TOTAL" in norm and "DELITOS" in norm and "INCIDENTES" in norm:
        return "total_con_incidentes"
    if "TOTAL" in norm and "DELITOS" in norm:
        return "total_delitos"
    if letters_only == "TOTAL":
        return "total_delitos"
    return None


class OdioParser:
    """
    MIR "Informe sobre la evolucion de los delitos de odio en España"
    (annual, 2016-2021 + 2023; no PDF published/available for 2022 -- see
    below). Locate the target page by CONTENT ("HECHOS CONOCIDOS
    REGISTRADOS" + "RACISMO" both present), not a fixed page number: the
    table's page varies by year (2016:p14, 2017:p12, 2018:p11, 2019:p10,
    2020:p17, 2021:p14, 2023:p12).

    This table is rendered as an infographic/chart, not a ruled table:
    both `pdftotext -layout` (scrambles reading order) and pdfplumber's
    `extract_tables()` (relies on ruling lines, none exist here) fail on
    it. The only reliable extraction is `page.extract_words()` (word
    bounding boxes) reconstructed into rows by Y-POSITION CLUSTERING, not
    exact-`top` grouping: the same logical row's label and its numeric
    columns are sometimes rendered as two word-clusters only ~1-2pt apart
    (and, in some rows e.g. 2023's "TOTAL DELITOS", the numbers-cluster can
    appear ABOVE the label-cluster in raw top order), while distinct
    ámbito rows are always >=10pt apart in every year inspected -- so a
    small top-proximity tolerance (ROW_TOL, 3pt) safely re-joins a split
    row without ever merging two different ámbitos.

    Numeric columns are read LEFT-TO-RIGHT (opposite of BalanceParser's
    right-to-left `_row_counts`, which dodges footnote pollution at the
    END of a line): the first N purely-integer tokens (N = number of year
    columns, detected per-block from the header row's own "20XX" tokens,
    NOT hardcoded -- it is 2 for 2016-2020 and 3 for 2021/2023, which also
    add a third, older, comparison year) in x-order are the real values;
    any stray split-off digit (e.g. "0" split from "0,00%", or a bare
    footnote-marker digit like the "1" trailing 2016's TOTAL row) always
    renders AFTER the N real columns, so it's naturally dropped once N
    values are collected. Total counts are inconsistently formatted with
    or without a thousands-separator dot even within the same table (e.g.
    2019's TOTAL DELITOS row: "1476" then "1.598" a few tokens later) --
    INT_TOKEN_RE accepts both.

    Table shape has evolved: 2016-2018 have ONE "TOTAL" row equal to the
    ámbito sum. 2019+ introduces a 3-tier total: TOTAL DELITOS (= sum of
    ~11 ámbitos) + INFRAC. ADM. Y RESTO DE INCIDENTES (administrative
    infractions/incidents, NOT counted as an ámbito) = TOTAL DELITOS E
    INCIDENTES DE ODIO (the report's own headline figure, "total_hate_
    crimes" here). Both relationships verified EXACT (not approximate) for
    every year checked.

    KNOWN retroactive-restatement gotcha (parallel to, but distinct from,
    the Anuario's B9 pattern): a later report's own backward-looking
    comparison column for a prior year can disagree with that prior year's
    OWN dedicated report (e.g. the 2018 report's own 2018 column says
    RACISMO/XENOFOBIA=531, ANTISEMITISMO=9; the 2019 report's "2018"
    comparison column says 426 and 8 respectively). We therefore ALWAYS
    parse each year from its own dedicated report, never from a later
    report's prior-year comparison column.

    2022 GAP: no dedicated PDF for 2022 was published/is available, so no
    2022 MIRReport is emitted. The 2023 report's own table happens to
    retroactively include a full 2022 column (TOTAL DELITOS=1796, TOTAL
    DELITOS E INCIDENTES=1869) purely as its own prior-year comparison --
    this is NOT synthesized into a 2022 record here (would conflate a
    primary-sourced year with a secondary-sourced one); it is documented
    as a footnote only (see data/sources/mir_delitos_odio.md).

    Zero-record guard (B25-class, mirrors run_balance_batch): if the table
    can't be located or extraction yields no ámbito rows, `parse()`
    returns an empty list rather than emitting an empty/wrong MIRReport;
    the caller (`run_odio_batch`) skips that year and logs it.
    """

    LOCATE_KEYWORDS = ["HECHOS CONOCIDOS REGISTRADOS", "RACISMO"]
    ROW_TOL = 3  # pt; top-position clustering tolerance (see docstring)
    INT_TOKEN_RE = re.compile(r"^-?\d+$|^-?\d{1,3}(?:\.\d{3})+$")
    YEAR_TOKEN_RE = re.compile(r"^20\d{2}$")
    SOURCE_TABLE = "Hechos conocidos registrados (delitos de odio)"

    def __init__(self, pdf_path: Path, year: int):
        self.pdf_path = pdf_path
        self.year = year
        self.source = pdf_path.name
        self.records: list[MIRRecord] = []

    def parse(self) -> list[MIRRecord]:
        with pdfplumber.open(self.pdf_path) as pdf:
            page_no, page = self._locate_page(pdf)
            if page is None:
                print(f"  ⚠ {self.year}: hate-crime typology table not found in {self.source}", file=sys.stderr)
                return []
            rows = self._cluster_rows(page.extract_words())
        known_idx = self._find_marker(rows, {"HECHOS", "CONOCIDOS"}, 0)
        if known_idx is None:
            print(f"  ⚠ {self.year}: 'Hechos conocidos' section not found on p.{page_no} of {self.source}", file=sys.stderr)
            return []
        cleared_idx = self._find_marker(rows, {"HECHOS", "ESCLARECIDOS"}, known_idx + 1)
        known = self._extract_block(rows, known_idx)
        cleared = self._extract_block(rows, cleared_idx) if cleared_idx is not None else {}
        self._build_records(known, cleared, page_no)
        self._validate()
        return self.records

    def _locate_page(self, pdf):
        for i, page in enumerate(pdf.pages):
            text = strip_accents(page.extract_text() or "").upper()
            if all(kw in text for kw in self.LOCATE_KEYWORDS):
                return i + 1, page
        return None, None

    @classmethod
    def _cluster_rows(cls, words) -> list[list[dict]]:
        """Group words into logical rows by Y-proximity (see docstring),
        each row sorted left-to-right by x0."""
        ws = sorted(words, key=lambda w: w["top"])
        rows, cur, prev_top = [], [], None
        for w in ws:
            if cur and w["top"] - prev_top > cls.ROW_TOL:
                rows.append(cur)
                cur = []
            cur.append(w)
            prev_top = w["top"]
        if cur:
            rows.append(cur)
        return [sorted(r, key=lambda w: w["x0"]) for r in rows]

    @staticmethod
    def _find_marker(rows, marker_words: set[str], start: int) -> int | None:
        for i in range(start, len(rows)):
            text = strip_accents(" ".join(w["text"] for w in rows[i])).upper()
            if all(mw in text for mw in marker_words):
                return i
        return None

    def _detect_n_cols(self, rows, start_idx: int) -> int:
        best = 0
        for row in rows[start_idx:start_idx + 6]:
            n = sum(1 for w in row if self.YEAR_TOKEN_RE.match(w["text"]))
            best = max(best, n)
        return best or 2

    def _extract_block(self, rows, start_idx: int) -> dict[str, list[float]]:
        n_cols = self._detect_n_cols(rows, start_idx)
        out: dict[str, list[float]] = {}
        hit_total = False
        for row in rows[start_idx + 1:start_idx + 40]:
            label = " ".join(w["text"] for w in row if not self.INT_TOKEN_RE.match(w["text"]) and "%" not in w["text"])
            key = classify_odio_category(label)
            if key is None:
                if hit_total:
                    break
                continue
            count_tokens = [w["text"] for w in row if self.INT_TOKEN_RE.match(w["text"])]
            if len(count_tokens) < n_cols:
                continue
            out[key] = [parse_es_number(t) for t in count_tokens[:n_cols]]
            if key in ("total_delitos", "total_con_incidentes"):
                hit_total = True
        return out

    def _category_note(self, key: str) -> str:
        if key == "discapacidad" and self.year >= 2017:
            return ODIO_DISCAPACIDAD_NOTE
        if key == "antigitanismo" and self.year == 2019:
            return ODIO_ANTIGITANISMO_NOTE
        return ""

    def _build_records(self, known: dict, cleared: dict, page_no: int | None):
        if not known:
            return
        total_con_incidentes = known.get("total_con_incidentes")
        total_delitos = known.get("total_delitos")
        headline = total_con_incidentes if total_con_incidentes is not None else total_delitos
        if headline is None:
            return
        headline_count = int(round(headline[-1]))

        cleared_total = None
        if cleared:
            c = cleared.get("total_con_incidentes")
            if c is None:
                c = cleared.get("total_delitos")
            if c is not None:
                cleared_total = c[-1]
        clearance_rate = round(cleared_total / headline_count * 100, 1) if cleared_total and headline_count else None

        self.records.append(MIRRecord(
            year=self.year, crime_category="total_hate_crimes", legal_article="Art.22.4 CP (agravante)",
            count=headline_count, clearance_rate=clearance_rate,
            source_document=self.source, source_table=self.SOURCE_TABLE, source_page=page_no,
        ))
        if total_delitos is not None:
            note = ("Subtotal: solo delitos (excluye infracciones administrativas y resto de incidentes)."
                    if total_con_incidentes is not None else "")
            self.records.append(MIRRecord(
                year=self.year, crime_category="total_delitos", legal_article="Art.22.4 CP (agravante)",
                count=int(round(total_delitos[-1])),
                source_document=self.source, source_table=self.SOURCE_TABLE, source_page=page_no, notes=note,
            ))
        infrac = known.get("infracciones_administrativas")
        if infrac is not None:
            note = "Infracciones administrativas y resto de incidentes de odio, no tipificados como delito."
            self.records.append(MIRRecord(
                year=self.year, crime_category="infracciones_administrativas", legal_article="n/a",
                count=int(round(infrac[-1])),
                source_document=self.source, source_table=self.SOURCE_TABLE, source_page=page_no, notes=note,
            ))
        for key, values in known.items():
            if key in ("total_delitos", "total_con_incidentes", "infracciones_administrativas"):
                continue
            self.records.append(MIRRecord(
                year=self.year, crime_category=key, legal_article="Art.22.4 CP (agravante)",
                count=int(round(values[-1])),
                source_document=self.source, source_table=self.SOURCE_TABLE, source_page=page_no,
                notes=self._category_note(key),
            ))

    def _validate(self):
        total_rec = next((r for r in self.records if r.crime_category == "total_hate_crimes"), None)
        delitos_rec = next((r for r in self.records if r.crime_category == "total_delitos"), None)
        infrac_rec = next((r for r in self.records if r.crime_category == "infracciones_administrativas"), None)
        ambito_recs = [
            r for r in self.records
            if r.crime_category not in ("total_hate_crimes", "total_delitos", "infracciones_administrativas")
        ]
        if delitos_rec and delitos_rec.count is not None:
            sub_sum = sum(r.count for r in ambito_recs if r.count is not None)
            if sub_sum and abs(sub_sum - delitos_rec.count) > 1:
                note = f"VALIDATION: sum(ambitos)={sub_sum} vs TOTAL DELITOS={delitos_rec.count}"
                delitos_rec.notes = (delitos_rec.notes + " " + note).strip()
                print(f"  ⚠ {self.year}: {note}", file=sys.stderr)
        if total_rec and delitos_rec and total_rec.count is not None and delitos_rec.count is not None:
            infrac = infrac_rec.count if infrac_rec and infrac_rec.count is not None else 0
            if abs(delitos_rec.count + infrac - total_rec.count) > 1:
                note = f"VALIDATION: TOTAL DELITOS+INFRAC={delitos_rec.count + infrac} vs headline={total_rec.count}"
                total_rec.notes = (total_rec.notes + " " + note).strip()
                print(f"  ⚠ {self.year}: {note}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────
# Output schema (nested per-report JSON, Pydantic-validated)
#
# One MIRReport per year: category×sex breakdown as a list (one entry per
# crime category, excluding the report-total row), plus report-total-level
# fields (headline count, clearance rate, nationality×sex) pulled out of the
# "total_sexual_crimes" MIRRecord -- this avoids repeating those totals on
# every category row the way the old flat CSV did. `source_page`, `source_
# table` and `verified` also live at report level, not per category: every
# category's count comes from the same typology-table page/table within a
# given report, so per-category copies would just be silent duplicates
# (V20). `verified` starts False; a human flips it to True after visually
# checking the report's numbers against the source PDF -- it is not
# something the parser can infer.
# ──────────────────────────────────────────────────────────────

class SexCounts(BaseModel):
    female: int | None = None
    male: int | None = None
    unknown: int | None = None


class NationalityBreakdown(BaseModel):
    spanish_pct: float | None = None
    foreign_pct: float | None = None
    by_country: list[CountryBreakdown] = []


class NationalitySplit(BaseModel):
    victims: NationalityBreakdown = NationalityBreakdown()
    perpetrators: NationalityBreakdown = NationalityBreakdown()


class CategorySexBreakdown(BaseModel):
    category: str
    legal_article: str
    count: int | None = None
    victims: SexCounts = SexCounts()
    perpetrators: SexCounts = SexCounts()
    notes: str = ""


class MIRReport(BaseModel):
    year: int
    total_count: int | None = None
    clearance_rate: float | None = None
    victims_minor_pct: float | None = None
    perp_male_pct: float | None = None
    categories: list[CategorySexBreakdown] = []
    nationality: NationalitySplit = NationalitySplit()
    source_document: str
    source_table: str = ""
    source_page: int | None = None
    verified: bool = False
    notes: str = ""


class MIRDataset(BaseModel):
    reports: list[MIRReport]


def records_to_report(records: list[MIRRecord], year: int, source_document: str, total_key: str = "total_sexual_crimes") -> MIRReport:
    total_rec = next((r for r in records if r.crime_category == total_key), None)
    categories = [
        CategorySexBreakdown(
            category=r.crime_category,
            legal_article=r.legal_article,
            count=r.count,
            victims=SexCounts(female=r.victims_female, male=r.victims_male, unknown=r.victims_unknown),
            perpetrators=SexCounts(female=r.perp_female, male=r.perp_male),
            notes=r.notes,
        )
        for r in records if r.crime_category != total_key
    ]
    nationality = NationalitySplit(
        victims=NationalityBreakdown(
            spanish_pct=total_rec.victims_spanish_pct if total_rec else None,
            foreign_pct=total_rec.victims_foreign_pct if total_rec else None,
            by_country=total_rec.victims_by_country if total_rec and total_rec.victims_by_country else [],
        ),
        perpetrators=NationalityBreakdown(
            spanish_pct=total_rec.perp_spanish_pct if total_rec else None,
            foreign_pct=total_rec.perp_foreign_pct if total_rec else None,
            by_country=total_rec.perp_by_country if total_rec and total_rec.perp_by_country else [],
        ),
    )
    return MIRReport(
        year=year,
        total_count=total_rec.count if total_rec else None,
        clearance_rate=total_rec.clearance_rate if total_rec else None,
        victims_minor_pct=total_rec.victims_minor_pct if total_rec else None,
        perp_male_pct=total_rec.perp_male_pct if total_rec else None,
        categories=categories,
        nationality=nationality,
        source_document=source_document,
        source_table=total_rec.source_table if total_rec else "",
        source_page=total_rec.source_page if total_rec else None,
        notes=total_rec.notes if total_rec else "",
    )


def write_dataset(dataset: MIRDataset, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(dataset.model_dump_json(indent=2), encoding="utf-8")
    print(f"  -> {out_path} ({len(dataset.reports)} report(s))")


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def infer_year(pdf_path: Path) -> int | None:
    m = re.search(r"(20\d{2})", pdf_path.stem)
    return int(m.group(1)) if m else None


def infer_quarter(pdf_path: Path) -> str | None:
    m = re.search(r"Q([1-4])", pdf_path.stem)
    return f"Q{m.group(1)}" if m else None


def run_informe(pdf_path: Path, year: int) -> list[MIRRecord]:
    print(f"  Parsing Informe {year}: {pdf_path.name}")
    parser = InformeParser(pdf_path, year)
    return parser.parse()


def run_anuario(pdf_path: Path, year: int) -> list[MIRRecord]:
    print(f"  Parsing Anuario {year}: {pdf_path.name}")
    parser = AnuarioParser(pdf_path, year)
    return parser.parse()


def run_odio(pdf_path: Path, year: int) -> list[MIRRecord]:
    print(f"  Parsing Odio {year}: {pdf_path.name}")
    parser = OdioParser(pdf_path, year)
    return parser.parse()


def run_batch(pdf_year_pairs: list[tuple[Path, int]], parse_fn, out_dir: Path, filename_tag: str = "") -> Path:
    """Parse each (pdf, year) pair and write exactly one MIRDataset JSON file
    (V21) -- named by the actual year range, or the single year if there's
    only one report -- instead of one file per input plus a redundant
    consolidated copy of the same data.

    `filename_tag` disambiguates the Anuario series from the Informe series
    when their year ranges could otherwise collide/be confused (they are two
    independently-sourced, cross-validated series per B6/V13, not one
    dataset) -- left empty for informe mode to avoid renaming the existing,
    already-referenced `sexual_crimes_mir_{range}.json` file."""
    by_year: dict[int, list[str]] = {}
    for pdf, year in pdf_year_pairs:
        by_year.setdefault(year, []).append(pdf.name)
    collisions = {y: names for y, names in by_year.items() if len(names) > 1}
    if collisions:
        detail = "; ".join(f"{y}: {names}" for y, names in sorted(collisions.items()))
        raise ValueError(
            f"run_batch: multiple PDFs infer to the same year (V22) -- {detail}. "
            "Pass explicit --pdf per file instead of a mixed --pdf-dir."
        )

    reports = [
        records_to_report(parse_fn(pdf, year), year, pdf.name)
        for pdf, year in pdf_year_pairs
    ]
    years = sorted(r.year for r in reports)
    stem = f"{years[0]}" if years[0] == years[-1] else f"{years[0]}-{years[-1]}"
    tag = f"_{filename_tag}" if filename_tag else ""
    out = out_dir / f"sexual_crimes_mir{tag}_{stem}.json"
    write_dataset(MIRDataset(reports=reports), out)
    return out


def run_balance_batch(pdf_paths: list[Path], out_dir: Path) -> Path:
    """Balance de Criminalidad needs its own batch function, not `run_batch`:
    each year has 4 PDFs (one per quarter) that all infer to the SAME year,
    which would trip `run_batch`'s V22 year-collision guard. Only the Q4
    ("enero a diciembre") report's cumulative figures are used per year (see
    BalanceParser docstring, B24) -- Q1-Q3 are parsed too, purely to log the
    cumulative progression and the naive-sum overcount as evidence, not to
    contribute to the output dataset."""
    by_year: dict[int, dict[str, Path]] = {}
    for pdf in pdf_paths:
        year = infer_year(pdf)
        quarter = infer_quarter(pdf)
        if not year or not quarter:
            print(f"  SKIP {pdf.name} (cannot infer year/quarter)")
            continue
        by_year.setdefault(year, {})[quarter] = pdf

    reports = []
    for year in sorted(by_year):
        quarters = by_year[year]
        cumulative = {}
        for q in ("Q1", "Q2", "Q3", "Q4"):
            pdf = quarters.get(q)
            if pdf is None:
                continue
            print(f"  Parsing Balance {year} {q}: {pdf.name}")
            records = BalanceParser(pdf, year, q).parse()
            total_rec = next((r for r in records if r.crime_category == "total_sexual_crimes"), None)
            cumulative[q] = total_rec.count if total_rec else None
            if q == "Q4":
                q4_records = records
        if cumulative:
            naive_sum = sum(v for v in cumulative.values() if v is not None)
            print(f"  {year} cumulative by quarter: {cumulative}; naive sum={naive_sum} "
                  f"(overcounts vs Q4-alone -- see B24)")
        if "Q4" not in quarters:
            print(f"  SKIP {year}: no Q4 (enero-diciembre) report, cannot derive annual figure")
            continue
        if not q4_records:
            print(f"  SKIP {year}: Q4 report found but table extraction failed (no records) -- "
                  f"likely a pre-2019 layout not yet handled by BalanceParser")
            continue
        reports.append(records_to_report(q4_records, year, quarters["Q4"].name))

    years = sorted(r.year for r in reports)
    stem = f"{years[0]}" if years[0] == years[-1] else f"{years[0]}-{years[-1]}"
    out = out_dir / f"sexual_crimes_mir_balance_{stem}.json"
    write_dataset(MIRDataset(reports=reports), out)
    return out


def _year_range_stem(years: list[int]) -> str:
    """Build a filename stem from a sorted year list that keeps a gap
    visible (e.g. [2016..2021, 2023] -> "2016-2021_2023") instead of a
    plain first-last range, which would silently imply a continuous series
    when a year (e.g. Odio's missing 2022) is actually missing."""
    blocks = []
    start = prev = years[0]
    for y in years[1:]:
        if y == prev + 1:
            prev = y
            continue
        blocks.append((start, prev))
        start = prev = y
    blocks.append((start, prev))
    parts = [f"{a}" if a == b else f"{a}-{b}" for a, b in blocks]
    return "_".join(parts)


def run_odio_batch(pdf_paths: list[Path], out_dir: Path) -> Path:
    """Delitos de Odio needs its own batch function, not `run_batch`: its
    headline total lives under a "total_hate_crimes" key (not
    "total_sexual_crimes" -- see `records_to_report`'s `total_key` param),
    the output must be filed under a "hate_crimes_mir" prefix (this is an
    independently-sourced series, not sexual-crime data -- same reasoning
    as Anuario's separate filename_tag per B6/V13), and 2022 has no
    dedicated PDF (a genuine gap, not a parser bug -- see OdioParser
    docstring), so the year list is not guaranteed contiguous."""
    pairs = []
    for pdf in sorted(pdf_paths):
        year = infer_year(pdf)
        if not year:
            print(f"  SKIP {pdf.name} (cannot infer year)")
            continue
        pairs.append((pdf, year))
    if not pairs:
        sys.exit("run_odio_batch: no PDFs with inferable years found")

    by_year: dict[int, list[str]] = {}
    for pdf, year in pairs:
        by_year.setdefault(year, []).append(pdf.name)
    collisions = {y: names for y, names in by_year.items() if len(names) > 1}
    if collisions:
        detail = "; ".join(f"{y}: {names}" for y, names in sorted(collisions.items()))
        raise ValueError(f"run_odio_batch: multiple PDFs infer to the same year (V22) -- {detail}.")

    reports = []
    for pdf, year in pairs:
        records = run_odio(pdf, year)
        if not records:
            print(f"  SKIP {year}: hate-crime typology table not found/extracted (no records)")
            continue
        reports.append(records_to_report(records, year, pdf.name, total_key="total_hate_crimes"))

    if not reports:
        sys.exit("run_odio_batch: no reports produced")

    years = sorted(r.year for r in reports)
    stem = _year_range_stem(years)
    out = out_dir / f"hate_crimes_mir_{stem}.json"
    write_dataset(MIRDataset(reports=reports), out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["informe", "anuario", "balance", "odio"], required=True)
    ap.add_argument("--pdf-dir", type=Path, help="Directory of PDFs")
    ap.add_argument("--pdf", type=Path, help="Single PDF file")
    ap.add_argument("--year", type=int, help="Override year (use with --pdf)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    if args.mode == "balance":
        if not args.pdf_dir:
            ap.error("--mode balance requires --pdf-dir (needs all 4 quarters per year)")
        pdfs = sorted(args.pdf_dir.glob("*.pdf"))
        if not pdfs:
            sys.exit(f"No PDFs found in {args.pdf_dir}")
        run_balance_batch(pdfs, args.out_dir)
        return

    if args.mode == "odio":
        if not args.pdf_dir:
            ap.error("--mode odio requires --pdf-dir")
        pdfs = sorted(args.pdf_dir.glob("MIR_InformeDelitosOdio_*.pdf"))
        if not pdfs:
            sys.exit(f"No MIR_InformeDelitosOdio_*.pdf found in {args.pdf_dir}")
        run_odio_batch(pdfs, args.out_dir)
        return

    parse_fn = run_informe if args.mode == "informe" else run_anuario
    filename_tag = "anuario" if args.mode == "anuario" else ""
    # data/sources/ mixes Informe/Anuario/Odio/Balance PDFs together; a bare
    # "*.pdf" glob would feed the wrong parser wrong-format files (and can
    # trip run_batch's V22 year-collision guard, since e.g. an Anuario and an
    # Informe PDF for the same year both infer that year). Filter by each
    # mode's own filename prefix, same pattern odio mode already uses.
    dir_glob = {"informe": "MIR_Informe_DelitosSexuales*.pdf", "anuario": "MIR_AnuarioEstadistico*.pdf"}

    if args.pdf:
        year = args.year or infer_year(args.pdf)
        if not year:
            sys.exit("Cannot infer year from filename; pass --year")
        run_batch([(args.pdf, year)], parse_fn, args.out_dir, filename_tag)

    elif args.pdf_dir:
        pdfs = sorted(args.pdf_dir.glob(dir_glob.get(args.mode, "*.pdf")))
        if not pdfs:
            sys.exit(f"No PDFs found in {args.pdf_dir}")
        pairs = []
        for pdf in pdfs:
            year = infer_year(pdf)
            if not year:
                print(f"  SKIP {pdf.name} (cannot infer year)")
                continue
            pairs.append((pdf, year))
        if not pairs:
            sys.exit("No PDFs with inferable years found")
        run_batch(pairs, parse_fn, args.out_dir, filename_tag)

    else:
        ap.error("Pass either --pdf or --pdf-dir")


if __name__ == "__main__":
    main()
