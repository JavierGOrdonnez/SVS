#!/usr/bin/env python3
"""
T83 -- general (non-nationality-specific) long-run crime trend, Spanish vs.
foreign, for 3 categories: homicide, robbery, sexual assault. Answers the
user's "subsequent step" request for a longer time series than the MIR
Informe/Anuario sexual-crimes series alone provides (2016+), using MIR
Anuario's general "Seguridad Ciudadana" chapter tables instead of a
nationality-specific source -- explicitly scoped down to Spanish-vs-foreign
only (no per-country breakdown), per the user's own "it is ok if we only
have spanish vs foreign for that plot" framing.

Two source tables per Anuario edition (`data/sources/MIR_AnuarioEstadistico_
{year}.pdf`, 2016-2023), both in chapter "3 SEGURIDAD CIUDADANA":

  (a) "INFRACCIONES PENALES. HECHOS CONOCIDOS/DETENCIONES E INVESTIGADOS.
      TOTAL NACIONAL. SERIE HISTORICA <y-4>-<y>" -- ALL-nationality totals,
      a *5-year rolling window* per edition (not just the edition's own
      year), located by content (row/column-header match) since table
      numbering shifts across editions (documented precedent: T21's
      AnuarioParser needed the same fix for the sexual-crimes table).
      Used for the per-capita trend (no nationality split needed/available
      here).
  (b) "DETENCIONES E INVESTIGADOS EXTRANJEROS POR CAUSA DE INFRACCION PENAL.
      TOTAL NACIONAL" (chapter 3.1.4 "EXTRANJEROS") -- FOREIGN-nationality-
      only detentions/investigated, sex-split (M/F/Total columns), only a
      *2-year window* (current + prior year) per edition. Used for the
      foreign-population-share trend; Spanish = table (a)'s ALL-nationality
      detenciones total minus this table's foreign total (per category),
      not a source-reported figure.

Both tables are pdfplumber `extract_tables()`-hostile (the per-category rows
aren't gridded, only the header/total rows are -- same rendering quirk noted
elsewhere in this codebase for chart/infographic-style Anuario pages) --
parsed via `extract_text()` + per-line regex instead.

3 categories, using each table's own row labels directly (not re-derived):
  homicide       <- "1. Homicidios dolosos/asesinatos" (I. Contra las personas)
                     -- the parent row (incl. attempts), not the "consumados"
                     (completed-only) sub-row.
  robbery        <- "2. Robos con fuerza en cosas" + "3. Robos ... violencia
                     o intimidacion" (V. Contra el patrimonio) SUMMED. Spanish
                     legal "robo" (force/violence) is distinct from "hurto"
                     (simple theft, no force) -- "1. Hurtos" is excluded.
  sexual_assault <- "III. Contra la libertad sexual" (same headline total
                     already cross-validated elsewhere against the Informe
                     series, see data/sources/mir_informes_delitos_sexuales.md)

Merge across the 8 editions: each year can appear in up to 5 different
editions' table (a) (rolling window) -- the MOST RECENT edition covering a
given year is kept (later-published editions revise earlier ones, same
precedent as B9/AnuarioParser's own docstring), not averaged or summed.
Table (b) only ever supplies 2 years per edition so overlap is smaller but
handled the same way.

Output: data/raw/mir_anuario_general_crime_2015-2023.csv
  columns: year, category, metric, sex, count, source_edition, source_page, notes
  metric in {hechos_conocidos_total, detenciones_total, detenciones_foreign}
  sex is 'all' for hechos_conocidos_total/detenciones_total (not sex-split in
  the source), 'male'/'female'/'all' for detenciones_foreign.
"""
import csv
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).parent.parent.parent
SOURCES_DIR = ROOT / "data" / "sources"
OUT_CSV = ROOT / "data" / "raw" / "mir_anuario_general_crime_2015-2023.csv"

EDITIONS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

# Search window: every table found so far lives well before page 350 across
# all 8 editions (largest is the 2016 edition at 964 pages) -- restricting
# the scan avoids wasting minutes re-parsing later, irrelevant chapters
# (international cooperation, extranjeria/residence-permit statistics, etc.)
# on every one of the 8 (700-960 page) PDFs.
SEARCH_PAGE_LIMIT = 400

# (row label prefix in the source, our category key). 2020+ editions
# restructured this chapter's tables (see EVOLUTION_TITLE_A/B/EXTRANJEROS
# below) and along with it shortened "III. Contra la libertad sexual" to
# "III. Libertad sexual" -- both wordings accepted.
CATEGORY_ROWS = [
    (re.compile(r"^1\.\s*Homicidios dolosos/asesinatos", re.I), "homicide"),
    (re.compile(r"^2\.\s*Robos con fuerza en cosas", re.I), "robbery_force"),
    (re.compile(r"^3\.\s*Robos.*violencia", re.I), "robbery_violence"),
    (re.compile(r"^III\.\s*(Contra la libertad sexual|Libertad sexual)", re.I), "sexual_assault"),
]

_NUM_RE = re.compile(r"\d{1,3}(?:\.\d{3})*(?:,\d+)?")


def _strip_accents(s: str) -> str:
    repl = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    return s.translate(repl)


def parse_es_int(tok: str) -> int | None:
    """'322.705' -> 322705. Rejects comma-decimal tokens (var% columns)."""
    if "," in tok:
        return None
    try:
        return int(tok.replace(".", ""))
    except ValueError:
        return None


_YEAR_HEADER_TRIGGERS = (
    r"diciembre",         # pre-2020 format: "Acumulado Enero-diciembre 2015 2016 ..."
    r"tipologia penal",   # 2020+ format: "Tipologia penal 2017 2018 2019 2020 2021" (no "diciembre" at all)
)  # matched against accent-stripped text (see _strip_accents call below), so "tipologia" (no accent) is correct here


def _year_header(text: str) -> list[int] | None:
    """Find the column-header line giving the years this table's numeric
    columns cover -- e.g. "Enero-diciembre 2015 2016 2017 2018 2019" (table a,
    up to 5 years, pre-2020) or "Enero-diciembre 2018 2019 Variacion % ..."
    (table b, 2 years, repeated 3x for M/F/Total -- only the first 2 years
    wanted) or "Tipologia penal 2017 2018 2019 2020 2021" (table a, 2020+
    format -- restructured with no "diciembre" trigger word at all).
    Matches a trailing run of >=2 consecutive years directly after one of
    the trigger phrases, not just any line containing years (avoids false
    positives from unrelated lines with a stray year mention)."""
    norm = _strip_accents(text)
    for line in norm.split("\n"):
        for trigger in _YEAR_HEADER_TRIGGERS:
            m = re.search(trigger + r"\s+((?:20[0-2]\d\s*)+)", line, re.I)
            if not m:
                continue
            years = [int(y) for y in re.findall(r"20[0-2]\d", m.group(1))]
            if len(years) >= 2:
                # table (b) repeats the same 2 years 3x (M/F/Total) back to
                # back -- de-dupe consecutive runs down to the first distinct
                # pair.
                if len(years) > 5 and years[: len(years) // 3] * (len(years) // (len(years) // 3)) == years:
                    years = years[: len(years) // 3]
                return years

    # Fallback: 2020+ editions' EXTRANJEROS table splits its "Hombre / Mujer
    # / Total" header and its "<y0> <y1>[ Variacion %]..." year-pair row onto
    # separate, non-adjacent lines (an intervening "Tipologia penal" row in
    # between) -- neither trigger word above sits on the same line as the
    # years. Some editions' year-row is purely years (e.g. "2020* 2021 2020*
    # 2021 2020* 2021"); others interleave the repeated "Variacion %" column
    # label between each year-pair on the SAME line (e.g. "2022 2023
    # Variacion % 2022 2023 Variacion % 2022 2023 Variacion %"). Both
    # accepted by requiring the line to consist ONLY of year tokens (with an
    # optional trailing "*" data-quality-footnote marker), "Variacion", "%",
    # and whitespace -- specific enough that a line matching this by chance
    # elsewhere on the page is not a real risk.
    for line in norm.split("\n"):
        stripped = line.strip()
        if not re.fullmatch(r"(?:20[0-2]\d\*?|variacion|%|\s)+", stripped, re.I):
            continue
        tokens = re.findall(r"20[0-2]\d\*?", stripped)
        if len(tokens) >= 4:
            years = [int(t[:4]) for t in tokens]
            if len(years) > 5 and years[: len(years) // 3] * (len(years) // (len(years) // 3)) == years:
                years = years[: len(years) // 3]
            elif len(years) >= 2:
                years = years[:2]
            return years
    return None


def _extract_category_rows(text: str) -> dict[str, list[int | None]]:
    """{category: [values in header-year order]} for the 4 tracked rows.
    Numbers are extracted only from AFTER the matched label -- the label
    itself starts with a row-number prefix ("1.", "2.", "3.") that the
    numeric regex would otherwise also capture as a spurious leading value
    (e.g. "1. Homicidios ... 964 1.107 ..." -> a bare leading "1" alongside
    the 5 real values, silently shifting/miscounting the row)."""
    out = {}
    for line in text.split("\n"):
        stripped = line.strip()
        for pat, key in CATEGORY_ROWS:
            if key in out:
                continue
            m = pat.match(stripped)
            if m:
                rest = stripped[m.end():]
                nums = [parse_es_int(t) for t in _NUM_RE.findall(rest)]
                nums = [n for n in nums if n is not None]
                out[key] = nums
                break
    return out


def _locate_page(pdf, format_variants: list[tuple[re.Pattern, list[str]]]) -> int | None:
    """Try each (title_phrase_regex, must_not_have) variant against every
    page in turn, returning the first page matching ANY variant. Matched
    against WHITESPACE-NORMALIZED text (newlines collapsed to spaces) since
    these tables' titles routinely wrap mid-phrase across a PDF line break
    (e.g. "... POR TIPOLOGIA\nPENAL. EVOLUCION ..." -- a plain multi-keyword
    substring check would still find "TIPOLOGIA" and "PENAL" independently
    anywhere on the page, but a regex requiring them adjacent needs the
    newline gone first). The title_phrase_regex itself matters just as much
    as the normalization: this chapter's running page-header/breadcrumb text
    ("... DETENCIONES E INVESTIGADOS, Y VICTIMIZACIONES") repeats
    "DETENCIONES E INVESTIGADOS" on literally every page of the section, so
    a loose "these 3 words appear somewhere on the page" check (this
    function's previous design) matched the WRONG table -- e.g. the HECHOS
    CONOCIDOS page also satisfied a DETENCIONES-table keyword check purely
    from its shared breadcrumb, not from its own title. Requiring the
    specific title's own word order as one regex closes that gap.
    2020+ Anuario editions restructured this chapter's table titles
    entirely (see parse_total_nacional_table's docstring) -- rather than a
    single fixed pattern, callers pass one variant per known title format so
    both eras are found in one page scan instead of two."""
    limit = min(SEARCH_PAGE_LIMIT, len(pdf.pages))
    for i in range(limit):
        raw = _strip_accents(pdf.pages[i].extract_text() or "").upper()
        norm = re.sub(r"\s+", " ", raw)
        for title_re, must_not_have in format_variants:
            if title_re.search(norm) and not any(kw in raw for kw in must_not_have):
                return i
    return None


# The "3.1.4. EXTRANJEROS" section has at least 3 sibling subsections across
# editions -- "a) ... por infraccion penal y sexo" (the one wanted here),
# "b) ... por distribucion territorial y sexo", and (2016 only) "c) ... por
# nacionalidad de origen y sexo" -- and their OWN section-intro prose
# paragraphs cross-reference each other by name, so a subsection (b)'s intro
# text literally contains the sentence fragment "detenciones e investigados
# extranjeros por infraccion penal a nivel territorial" -- which satisfies
# both "EXTRANJEROS POR ... INFRACCI" AND, a few lines later, "de sexo
# masculino ... de sexo femenino" in its own explanatory prose. Neither a
# title-phrase regex nor a column-header keyword check can reliably
# distinguish a real data table from a false-positive intro page this way
# -- both were tried and both produced false matches on different editions.
# Confirmed the wanted table's own printed title, across every format seen
# 2016-2023: "... EXTRANJEROS POR (CAUSA DE) INFRACCION PENAL (Y SEXO)".
_EXTRANJEROS_TITLE_RE = re.compile(r"EXTRANJEROS\s+POR\s+(CAUSA\s+DE\s+)?INFRACCI", re.I)


def _locate_extranjeros_page(pdf):
    """Generate title-regex-matching CANDIDATE pages (cheap, page-text-only)
    without deciding acceptance here -- the caller (parse_extranjeros_table)
    validates each candidate by actually attempting the real extraction
    (year header + >=1 category row), which is the only check precise
    enough to reject the prose-only false positives described above.
    Yields (page_index) in document order."""
    limit = min(SEARCH_PAGE_LIMIT, len(pdf.pages))
    for i in range(limit):
        text = _strip_accents(pdf.pages[i].extract_text() or "").upper()
        norm = re.sub(r"\s+", " ", text)
        if _EXTRANJEROS_TITLE_RE.search(norm):
            yield i


def _table_text(pdf, page_idx: int, extra_pages: int = 2) -> str:
    """These tables list 12 categories + subcategories -- long enough that
    some editions' font/spacing overflow it onto a continuation page with no
    repeated header (confirmed: 2021's EXTRANJEROS table splits "1.
    Homicidios.../III. Libertad sexual" on the located page from "2. Robos
    con fuerza.../3. Robos ... violencia" on the next page, silently
    dropping the robbery categories when only the located page was read).
    Concatenating a couple of trailing pages is safe here since every row is
    matched independently by its own label regex -- unrelated content on a
    later page just won't match any CATEGORY_ROWS pattern."""
    limit = min(page_idx + extra_pages + 1, len(pdf.pages))
    return "\n".join(pdf.pages[i].extract_text() or "" for i in range(page_idx, limit))


def parse_total_nacional_table(pdf, edition: int, want_conocidos: bool):
    """Table (a): ALL-nationality HECHOS CONOCIDOS or DETENCIONES E
    INVESTIGADOS. Two known title formats, tried in one pass (2020+ Anuario
    editions restructured this chapter -- "TABLA 3-1-2 ... SERIE HISTORICA
    2015-2019" (2016-2019) became "TABLA 3-1-5 ... HECHOS CONOCIDOS POR
    TIPOLOGIA PENAL. EVOLUCION 2017-2021" (2020+), a genuinely different
    title with no "SERIE HISTORICA"/"TOTAL NACIONAL" wording at all -- same
    underlying row/column data, different presentation). Returns
    [(year, category, metric, count, page, notes), ...]."""
    if want_conocidos:
        variants = [
            (re.compile(r"HECHOS CONOCIDOS.{0,60}SERIE HISTORIC", re.I), ["ESCLARECID"]),
            (re.compile(r"HECHOS CONOCIDOS\s+POR\s+TIPOLOGIA\s+PENAL", re.I), ["ESCLARECID"]),
        ]
        metric = "hechos_conocidos_total"
    else:
        variants = [
            (re.compile(r"DETENCIONES E INVESTIGADOS.{0,60}SERIE HISTORIC", re.I), ["EXTRANJER"]),
            (re.compile(r"DETENCIONES E INVESTIGADOS\s+POR\s+TIPOLOGIA\s+PENAL", re.I), ["EXTRANJER"]),
        ]
        metric = "detenciones_total"

    page_idx = _locate_page(pdf, variants)
    if page_idx is None:
        return [], None
    text = _table_text(pdf, page_idx)
    years = _year_header(text)
    rows = _extract_category_rows(text)
    if not years or not rows:
        return [], page_idx

    out = []
    robbery_by_year = {}
    for key, vals in rows.items():
        if len(vals) != len(years):
            continue  # a row we can't confidently align to the header
        for y, v in zip(years, vals):
            if key == "robbery_force":
                robbery_by_year.setdefault(y, [None, None])[0] = v
            elif key == "robbery_violence":
                robbery_by_year.setdefault(y, [None, None])[1] = v
            elif key == "homicide":
                out.append((y, "homicide", metric, v, page_idx + 1, ""))
            elif key == "sexual_assault":
                out.append((y, "sexual_assault", metric, v, page_idx + 1, ""))
    for y, (force, viol) in robbery_by_year.items():
        if force is not None and viol is not None:
            out.append((y, "robbery", metric, force + viol, page_idx + 1,
                        "robo con fuerza + robo con violencia/intimidacion; excludes hurto (simple theft)"))
    return out, page_idx


def _try_extranjeros_page(pdf, page_idx: int):
    """Attempt the real extraction against one candidate page. Returns
    (rows, page_idx) on success (>=1 row extracted) or (None, page_idx) if
    this candidate turns out to be a false positive (e.g. a sibling
    subsection's cross-referencing intro prose -- see
    _locate_extranjeros_page's docstring)."""
    text = _table_text(pdf, page_idx)
    years = _year_header(text)
    # This table's header sometimes wraps its "<y1>-<y0>" var.% column label
    # across a soft-hyphen line break (e.g. "2017\xad" then "2016" on the
    # next physical line), which the digit-only regex above can't
    # distinguish from a real 3rd year -- table (b) is always exactly a
    # 2-year window, so any extra captured tokens are that artifact, not
    # real data; truncate defensively rather than reject the whole page.
    if years and len(years) > 2:
        years = years[:2]
    if not years or len(years) != 2:
        return None, page_idx

    out = []
    robbery_by_year_sex = {}
    for line in text.split("\n"):
        stripped = line.strip()
        for pat, key in CATEGORY_ROWS:
            m = pat.match(stripped)
            if not m:
                continue
            rest = stripped[m.end():]  # numbers only, drops the row's own "N." prefix
            toks = _NUM_RE.findall(rest)
            nums = [parse_es_int(t) for t in toks]  # drops comma var% tokens
            nums = [n for n in nums if n is not None]
            if len(nums) != 6:  # expect M_y0,M_y1,F_y0,F_y1,T_y0,T_y1
                break
            m0, m1, f0, f1, t0, t1 = nums
            per_year = {years[0]: {"male": m0, "female": f0, "all": t0},
                        years[1]: {"male": m1, "female": f1, "all": t1}}
            for y, sexes in per_year.items():
                for sex, v in sexes.items():
                    if key == "robbery_force":
                        robbery_by_year_sex.setdefault((y, sex), [None, None])[0] = v
                    elif key == "robbery_violence":
                        robbery_by_year_sex.setdefault((y, sex), [None, None])[1] = v
                    elif key == "homicide":
                        out.append((y, "homicide", "detenciones_foreign", sex, v, page_idx + 1, ""))
                    elif key == "sexual_assault":
                        out.append((y, "sexual_assault", "detenciones_foreign", sex, v, page_idx + 1, ""))
            break
    for (y, sex), (force, viol) in robbery_by_year_sex.items():
        if force is not None and viol is not None:
            out.append((y, "robbery", "detenciones_foreign", sex, force + viol, page_idx + 1,
                        "robo con fuerza + robo con violencia/intimidacion; excludes hurto (simple theft)"))
    if not out:
        return None, page_idx
    return out, page_idx


def parse_extranjeros_table(pdf, edition: int):
    """Table (b): FOREIGN-only DETENCIONES E INVESTIGADOS, sex-split, 2-year
    window. Tries each title-regex-matching candidate page in document
    order, accepting the first one that actually yields real rows (see
    _locate_extranjeros_page/_try_extranjeros_page docstrings for why a
    pre-validation keyword check isn't reliable enough here). Returns
    [(year, category, 'detenciones_foreign', sex, count, page, notes), ...]."""
    last_page_tried = None
    for page_idx in _locate_extranjeros_page(pdf):
        last_page_tried = page_idx
        rows, _ = _try_extranjeros_page(pdf, page_idx)
        if rows:
            return rows, page_idx
    return [], last_page_tried


def main():
    all_rows = {}  # (year, category, metric, sex) -> row dict, keyed so later editions overwrite earlier

    for edition in EDITIONS:
        pdf_path = SOURCES_DIR / f"MIR_AnuarioEstadistico_{edition}.pdf"
        if not pdf_path.exists():
            print(f"  SKIP {edition}: PDF not found")
            continue
        print(f"  Parsing Anuario {edition}: {pdf_path.name}")
        with pdfplumber.open(pdf_path) as pdf:
            conocidos, p1 = parse_total_nacional_table(pdf, edition, want_conocidos=True)
            detenciones, p2 = parse_total_nacional_table(pdf, edition, want_conocidos=False)
            extranjeros, p3 = parse_extranjeros_table(pdf, edition)
            print(f"    hechos_conocidos_total page={p1} ({len(conocidos)} rows), "
                  f"detenciones_total page={p2} ({len(detenciones)} rows), "
                  f"detenciones_foreign page={p3} ({len(extranjeros)} rows)")

        for y, cat, metric, count, page, notes in conocidos + detenciones:
            key = (y, cat, metric, "all")
            all_rows[key] = {
                "year": y, "category": cat, "metric": metric, "sex": "all", "count": count,
                "source_edition": edition, "source_page": page, "notes": notes,
            }
        for y, cat, metric, sex, count, page, notes in extranjeros:
            key = (y, cat, metric, sex)
            all_rows[key] = {
                "year": y, "category": cat, "metric": metric, "sex": sex, "count": count,
                "source_edition": edition, "source_page": page, "notes": notes,
            }

    rows = sorted(all_rows.values(), key=lambda r: (r["category"], r["metric"], r["sex"], r["year"]))
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year", "category", "metric", "sex", "count",
                                          "source_edition", "source_page", "notes"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} rows -> {OUT_CSV}")

    for metric in ("hechos_conocidos_total", "detenciones_total", "detenciones_foreign"):
        years = sorted({r["year"] for r in rows if r["metric"] == metric and r["sex"] == "all"})
        print(f"  {metric}: years {years}")


if __name__ == "__main__":
    main()
