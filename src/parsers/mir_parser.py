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

Output (data/raw/sexual_crimes_mir_YYYY.json per year, plus a consolidated
data/raw/sexual_crimes_mir_{min_year}-{max_year}.json): nested, Pydantic-
validated MIRDataset -> MIRReport (one per year) -> categories: [CategorySex
Breakdown] for category x sex, nationality: {victims, perpetrators} for
nationality x sex at report-total level -- see the MIRReport/MIRDataset
models below for the full schema.

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


def find_number_in_row(cells: list[str]) -> int | None:
    for c in reversed(cells):
        v = parse_es_number(c)
        if v is not None and v >= 0:
            return int(round(v))
    return None


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
        with pdfplumber.open(self.pdf_path) as pdf:
            self._extract_typology(pdf)
            self._extract_sex_breakdown(pdf)
            self._extract_nationality(pdf)
        self._validate()
        return self.records

    def _extract_typology(self, pdf):
        """Extract the crime-typology and clearance-rate tables (the report's
        headline multi-year 'Tipología penal' tables), which are far more
        reliable than scanning every page for scattered category mentions."""
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
    The MIR "Anuario Estadístico" has sexual crimes in Chapter 4 (Delincuencia)
    or Chapter 5, depending on year. The relevant table is titled something like
    "Delitos contra la Libertad e Indemnidad Sexual" or "Infracciones Penales".

    Format varies significantly by year:
    - 2000–2011: partial territory (Policía Nacional + Guardia Civil only)
    - 2012+: national coverage (includes Mossos, Ertzaintza, Policía Foral)
    - 2015: break due to Código Penal reform

    The chapter is typically pp. 130–200 in recent Anuarios.
    """

    CHAPTER_KEYWORDS = re.compile(
        r"delito(s)?.{0,30}(libertad|sexual|indemnidad)|"
        r"infracci(on|ón).{0,30}penal",
        re.I
    )

    def __init__(self, pdf_path: Path, year: int):
        self.pdf_path = pdf_path
        self.year = year
        self.source = pdf_path.name
        self.records: list[MIRRecord] = []

    def parse(self) -> list[MIRRecord]:
        with pdfplumber.open(self.pdf_path) as pdf:
            in_chapter = False
            chapter_pages = 0
            for page in pdf.pages:
                text = page.extract_text() or ""
                if self.CHAPTER_KEYWORDS.search(text):
                    in_chapter = True
                    chapter_pages = 0
                if in_chapter:
                    chapter_pages += 1
                    self._process_page(page)
                    # Stop after 30 pages within chapter (Anuarios are large)
                    if chapter_pages > 30 and not self.CHAPTER_KEYWORDS.search(text):
                        in_chapter = False
        self._validate()
        return self.records

    def _process_page(self, page):
        tables = page.extract_tables()
        for table in tables:
            if not table:
                continue
            flat = [[str(c or "").strip() for c in row] for row in table]
            self._try_crime_table(flat, page.page_number)

    def _try_crime_table(self, table: list[list[str]], page_no: int):
        for row in table:
            if not row:
                continue
            label = row[0]
            count = find_number_in_row(row[1:])
            label_l = label.lower()

            if re.search(r"total.*libert|libert.*sexual.*total|infracci.*total", label_l):
                if count:
                    self._upsert("total_sexual_crimes", "all", count, page_no)

            elif re.search(r"violaci[oó]n|art\.?\s*179", label_l):
                self._upsert("violacion", "Art.179", count, page_no)

            elif re.search(r"agres.{0,20}sin penetra|art\.?\s*178", label_l):
                self._upsert("agresion_sin_penetracion", "Art.178", count, page_no)

            elif re.search(r"abuso sexual|art\.?\s*181", label_l):
                self._upsert("abuso_sexual", "Art.181", count, page_no)

            elif re.search(r"exhibicion|provocaci[oó]n sexual", label_l):
                self._upsert("exhibicionismo", "Art.185", count, page_no)

            elif re.search(r"prostituci[oó]n|corrupci[oó]n", label_l):
                self._upsert("prostitucion", "Art.187", count, page_no)

    def _upsert(self, category: str, article: str, count: int | None, page_no: int):
        for r in self.records:
            if r.crime_category == category:
                if count:
                    r.count = count
                return
        notes = ""
        if self.year <= 2011:
            notes = "TERRITORIAL LIMITATION: excludes Cataluña/PaísVasco/Navarra (~25-30% population). Multiply by ~1.3-1.5 for national estimate."
        self.records.append(MIRRecord(
            year=self.year,
            crime_category=category,
            legal_article=article,
            count=count,
            source_document=self.source,
            source_table="anuario_chapter",
            source_page=page_no,
            confidence="medium" if self.year >= 2012 else "low",
            notes=notes,
        ))

    def _validate(self):
        total_rec = next((r for r in self.records if r.crime_category == "total_sexual_crimes"), None)
        if total_rec is None or total_rec.count is None:
            print(f"  ⚠ {self.year}: no total sexual crimes found", file=sys.stderr)
            return
        total = total_rec.count
        sub_cats = ["violacion", "agresion_sin_penetracion", "abuso_sexual",
                    "exhibicionismo", "prostitucion"]
        sub_sum = sum(r.count for r in self.records if r.crime_category in sub_cats and r.count)
        if sub_sum > 0 and abs(sub_sum - total) / max(total, 1) > 0.20:
            note = f"VALIDATION: sub-cat sum {sub_sum} vs headline {total}"
            total_rec.notes += note
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


def records_to_report(records: list[MIRRecord], year: int, source_document: str) -> MIRReport:
    total_rec = next((r for r in records if r.crime_category == "total_sexual_crimes"), None)
    categories = [
        CategorySexBreakdown(
            category=r.crime_category,
            legal_article=r.legal_article,
            count=r.count,
            victims=SexCounts(female=r.victims_female, male=r.victims_male, unknown=r.victims_unknown),
            perpetrators=SexCounts(female=r.perp_female, male=r.perp_male),
            notes=r.notes,
        )
        for r in records if r.crime_category != "total_sexual_crimes"
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


def run_informe(pdf_path: Path, year: int) -> list[MIRRecord]:
    print(f"  Parsing Informe {year}: {pdf_path.name}")
    parser = InformeParser(pdf_path, year)
    return parser.parse()


def run_anuario(pdf_path: Path, year: int) -> list[MIRRecord]:
    print(f"  Parsing Anuario {year}: {pdf_path.name}")
    parser = AnuarioParser(pdf_path, year)
    return parser.parse()


def run_batch(pdf_year_pairs: list[tuple[Path, int]], parse_fn, out_dir: Path) -> Path:
    """Parse each (pdf, year) pair and write exactly one MIRDataset JSON file
    (V21) -- named by the actual year range, or the single year if there's
    only one report -- instead of one file per input plus a redundant
    consolidated copy of the same data."""
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
    out = out_dir / f"sexual_crimes_mir_{stem}.json"
    write_dataset(MIRDataset(reports=reports), out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["informe", "anuario"], required=True)
    ap.add_argument("--pdf-dir", type=Path, help="Directory of PDFs")
    ap.add_argument("--pdf", type=Path, help="Single PDF file")
    ap.add_argument("--year", type=int, help="Override year (use with --pdf)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    parse_fn = run_informe if args.mode == "informe" else run_anuario

    if args.pdf:
        year = args.year or infer_year(args.pdf)
        if not year:
            sys.exit("Cannot infer year from filename; pass --year")
        run_batch([(args.pdf, year)], parse_fn, args.out_dir)

    elif args.pdf_dir:
        pdfs = sorted(args.pdf_dir.glob("*.pdf"))
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
        run_batch(pairs, parse_fn, args.out_dir)

    else:
        ap.error("Pass either --pdf or --pdf-dir")


if __name__ == "__main__":
    main()
