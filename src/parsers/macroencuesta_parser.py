"""Macroencuesta de Violencia contra la Mujer parser (T99).

Parses the "Violencia sexual fuera del ámbito de la pareja" chapter
(Cap. 16 in both the 2019 and 2024 editions) of the Ministerio de Igualdad's
victimization survey — the two data points this repo needs from it:
  1. Prevalence (lifetime / last-4-years / last-12-months / childhood),
     overall and — 2024 only — broken out by severity tier (rape / attempted
     rape / other sexual violence).
  2. Victim-perpetrator relationship (familiar / conocido / desconocido),
     overall (2019, pooled across severities) or by severity tier (2024).

Replaces the hand-transcribed `data/raw/macroencuesta_relationship_2015-2024.csv`
with a parser-generated, re-runnable `data/raw/macroencuesta_2019-2024.json` —
every figure here can be regenerated from the source PDF by anyone, rather
than trusted on the strength of a manual transcription. Every value produced
by this module was cross-checked against the earlier hand-transcription
during development and matches exactly (see PR discussion / SPEC-sexual-
crimes.md T99) — this parser doesn't introduce new figures, it makes the
existing ones auditable.

Both waves' relevant tables print as clean, consistently-ordered text via
pdfplumber's `extract_text()` — `extract_tables()` returns the same kind of
glued-cell mess as MIR's own relación table (see mir_parser.py's
`_locate_relationship_rows` docstring), so this module uses the same
text-regex strategy, not table objects.

Only 2019 and 2024 are implemented: those are the two waves this repo has a
full-report PDF for (`data/sources/Macroencuesta_{2019,2024}.pdf`). The 2015
wave's relación figures are known only from a footnote quoted in the 2019
report (not from its own full-report PDF) and stay in `macroencuesta.md`'s
prose rather than this parser's output — see that doc's own caveat.

Usage:
    python src/parsers/macroencuesta_parser.py --pdf-dir data/sources/
    python src/parsers/macroencuesta_parser.py --pdf data/sources/Macroencuesta_2024.pdf --year 2024
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

try:
    import pdfplumber
    from pydantic import BaseModel
except ImportError:
    sys.exit("Install: pip install pdfplumber pydantic")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import parse_es_number

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "data" / "raw"


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# ──────────────────────────────────────────────────────────────
# Output schema
# ──────────────────────────────────────────────────────────────

class PrevalenceStat(BaseModel):
    violence_type: str          # 'any' | 'rape' | 'attempted_rape' | 'other'
    timeframe: str               # 'lifetime' | 'last_4_years' | 'last_12_months' | 'childhood'
    pct: float | None = None
    population_estimate: int | None = None
    ci_low: float | None = None
    ci_high: float | None = None
    sample_n: int | None = None  # 2019 only -- report gives raw survey N, not a population estimate


class RelationshipStat(BaseModel):
    key: str                     # e.g. 'familiar_hombre', 'desconocido_hombre'
    violence_type: str           # 'any' (2019, pooled) | 'rape' | 'attempted_rape' | 'other' (2024)
    pct_within_severity: float | None = None   # % of women who suffered that severity tier
    pct_of_all_women: float | None = None      # % of all women 16+ resident in Spain (2024 only)
    population_estimate: int | None = None
    sample_n: int | None = None                # 2019 only -- raw survey N


class MacroencuestaReport(BaseModel):
    wave_year: int
    sample_size: int | None = None
    prevalence: list[PrevalenceStat] = []
    relationship: list[RelationshipStat] = []
    source_document: str
    source_table: str = ""
    verified: bool = False
    notes: str = ""


class MacroencuestaDataset(BaseModel):
    reports: list[MacroencuestaReport]


# ──────────────────────────────────────────────────────────────
# Shared text-block helpers
# ──────────────────────────────────────────────────────────────

_NUM_RE = re.compile(r"\d{1,3}(?:\.\d{3})*(?:,\d+)?")


def _numbers_in(line: str) -> list[float]:
    return [parse_es_number(t) for t in _NUM_RE.findall(line)]


def _locate_page(pdf, keywords: list[str], start: int = 0) -> tuple[int, str] | None:
    """First page (from `start`) whose accent-stripped/uppercased text
    contains every keyword in `keywords`. Content-based, not a hardcoded
    page number -- the two waves' chapter start at very different absolute
    page indices (152 in 2019, 249 in 2024) and even a table's own number
    ("Tabla 16.1") isn't stable in general, though it happens to be for the
    two specific tables/waves this module targets."""
    for i in range(start, len(pdf.pages)):
        text = pdf.pages[i].extract_text() or ""
        upper = strip_accents(text).upper()
        if all(kw in upper for kw in keywords):
            return i, text
    return None


def _page_window_text(pdf, start_index: int, n_pages: int = 3) -> str:
    """Join `start_index`'s page with the next `n_pages - 1` pages' text, so
    a table spanning a page break (Tabla 16.1/16.2 in 2024 both do) isn't
    silently truncated -- the label-based regexes below search this whole
    blob rather than assuming single-page containment."""
    end = min(start_index + n_pages, len(pdf.pages))
    return "\n".join(pdf.pages[i].extract_text() or "" for i in range(start_index, end))


def _find_si_ic_block(text: str, start_after: str | None = None) -> tuple[list[float] | None, list[tuple[float, float]] | None]:
    """Return (sí_numbers, ci_pairs_or_None) for the first 'Sí ...' line
    (optionally only after the first occurrence of `start_after`, to target
    one of several repeated 'Sí'/'IC 95%' blocks on the same page — e.g.
    Tabla 16.2's three severity-tier sub-blocks), plus the following line's
    'IC 95% (lo - hi) (lo - hi) ...' pairs if present (2024 only; 2019
    predates published CIs for this table)."""
    lines = text.splitlines()
    start = 0
    if start_after:
        for i, l in enumerate(lines):
            if start_after in l:
                start = i
                break
    for i in range(start, len(lines)):
        l = lines[i].strip()
        if l == "Sí" or l.startswith("Sí "):
            si_nums = _numbers_in(l[2:])
            ic_pairs = None
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("IC 95%"):
                ic_pairs = [
                    (parse_es_number(lo), parse_es_number(hi))
                    for lo, hi in re.findall(r"\(([\d.,]+)\s*-\s*([\d.,]+)\)", lines[i + 1])
                ]
            return si_nums, ic_pairs
    return None, None


TIMEFRAMES = ["lifetime", "last_4_years", "last_12_months", "childhood"]


# ──────────────────────────────────────────────────────────────
# Pure text -> stats functions (no PDF/page-location involved -- these are
# what the unit tests exercise directly, against literal page-text fixtures;
# the *Parser classes below only do PDF page-location, then hand the found
# text to these).
# ──────────────────────────────────────────────────────────────

def parse_prevalence_2019(text: str) -> list[PrevalenceStat]:
    si, _ = _find_si_ic_block(text)
    if si is None or len(si) < 10:
        return []
    # order: (N, pct) x5 -- lifetime, last_4_years, last_12_months, childhood, rape_lifetime
    labels = TIMEFRAMES + ["rape_lifetime"]
    out = []
    for i, label in enumerate(labels):
        n, pct = si[2 * i], si[2 * i + 1]
        out.append(PrevalenceStat(
            violence_type="rape" if label == "rape_lifetime" else "any",
            timeframe="lifetime" if label == "rape_lifetime" else label,
            pct=pct, sample_n=int(n) if n is not None else None,
        ))
    return out


_REL_LABELS_2019 = [
    ("familiar_hombre", r"^Familiar hombre"), ("familiar_mujer", r"^Familiar mujer"),
    ("conocido_hombre", r"^Amigo o conocido hombre"), ("conocido_mujer", r"^Amiga o conocida mujer"),
    ("desconocido_hombre", r"^Desconocido hombre"), ("desconocido_mujer", r"^Desconocida mujer"),
]


def parse_relationship_2019(text: str) -> list[RelationshipStat]:
    """Parse 2019's vínculo-con-el-agresor Tabla II. NOTE: this function
    has no way to tell chapter 15's (physical violence) near-identical table
    apart from chapter 16's (sexual violence) if both are present in `text`
    -- `re.search` returns the first match, so the caller (Macroencuesta
    2019Parser) is responsible for only ever handing this function text from
    a page located *after* chapter 16's own start (see that class's `parse()`
    docstring/comment for why this matters -- it's a real bug this repo hit)."""
    out = []
    for key, pat in _REL_LABELS_2019:
        m = re.search(pat, text, re.MULTILINE)
        if not m:
            continue
        line_end = text.find("\n", m.end())
        remainder = text[m.end():line_end if line_end != -1 else None]
        toks = _numbers_in(remainder)
        if len(toks) < 2:
            continue
        n, pct = toks[0], toks[1]
        out.append(RelationshipStat(key=key, violence_type="any", sample_n=int(n), pct_within_severity=pct))
    return out


def parse_prevalence_block_2024(text: str, violence_type: str, start_after: str) -> list[PrevalenceStat]:
    si, ic = _find_si_ic_block(text, start_after=start_after)
    if si is None or len(si) < 8:
        return []
    out = []
    for i, timeframe in enumerate(TIMEFRAMES):
        pct, n = si[2 * i], si[2 * i + 1]
        stat = PrevalenceStat(violence_type=violence_type, timeframe=timeframe,
                               pct=pct, population_estimate=int(n) if n is not None else None)
        if ic and i < len(ic):
            stat.ci_low, stat.ci_high = ic[i]
        out.append(stat)
    return out


_REL_LABELS_2024 = [
    ("familiar_hombre", r"^Familiar hombre"), ("familiar_mujer", r"^Familiar mujer"),
    ("conocido_hombre", r"^Amigo o conocido \(hombre\)"), ("conocido_mujer", r"^Amiga o conocida \(mujer\)"),
    ("desconocido_hombre", r"^Desconocido \(hombre\)"), ("desconocido_mujer", r"^Desconocida \(mujer\)"),
]
_SEVERITY_ORDER_2024 = ["rape", "attempted_rape", "other"]


def _split_tokens_2024(remainder: str) -> list[float | None]:
    """Tokenize a Tabla 16.21 data row: space-separated numbers, a lone '.'
    means suppressed (sample <6, no figure given), and a leading '¨' flags a
    small-but-present sample (6-19 obs) -- kept as a real number (the
    report's own convention: use with caution, not "no data")."""
    out = []
    for tok in remainder.split():
        tok = tok.strip()
        if tok == ".":
            out.append(None)
        elif tok.startswith("¨"):
            out.append(parse_es_number(tok[1:]))
        else:
            v = parse_es_number(tok)
            if v is not None:
                out.append(v)
    return out


def parse_relationship_2024(text: str) -> list[RelationshipStat]:
    out = []
    for key, pat in _REL_LABELS_2024:
        m = re.search(pat, text, re.MULTILINE)
        if not m:
            continue
        line_end = text.find("\n", m.end())
        remainder = text[m.end():line_end if line_end != -1 else None]
        toks = _split_tokens_2024(remainder)
        for i, violence_type in enumerate(_SEVERITY_ORDER_2024):
            base = i * 3
            if base + 2 >= len(toks):
                continue
            pct_within, pct_total, n = toks[base], toks[base + 1], toks[base + 2]
            out.append(RelationshipStat(
                key=key, violence_type=violence_type,
                pct_within_severity=pct_within, pct_of_all_women=pct_total,
                population_estimate=int(n) if n is not None else None,
            ))
    return out


# ──────────────────────────────────────────────────────────────
# 2019 wave
# ──────────────────────────────────────────────────────────────

class Macroencuesta2019Parser:
    """2019 wave (single PDF, N=9,568 women 16+). Chapter 16 "Violencia
    sexual fuera del ámbito de la pareja" -- no published confidence
    intervals (added starting the 2024 wave), and relationship-to-
    perpetrator could only be asked pooled across every severity (not
    per rape/attempted/other -- the report's own text says this was a
    questionnaire-length constraint, see p.158)."""

    SAMPLE_SIZE = 9568

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.source = pdf_path.name

    def parse(self) -> MacroencuestaReport:
        with pdfplumber.open(self.pdf_path) as pdf:
            # Chapter 15 ("Violencia física fuera del ámbito de la pareja")
            # has a table with the exact same title phrase and row labels
            # ("Familiar hombre", "vínculo que las une con el agresor (II)")
            # as chapter 16's sexual-violence table, just for physical
            # violence instead -- a keyword search without first anchoring
            # past chapter 15 silently grabs chapter 15's numbers instead
            # (confirmed: this happened during development, caught by
            # comparing the parser's output against the manually-verified
            # figures it was meant to reproduce). Every subsequent page
            # search in this class is scoped to start no earlier than here.
            located = _locate_page(pdf, ["CAPITULO 16", "EN ESTE CAPITULO"])
            chapter_start = located[0] if located else 0
            if located is None:
                print("  ⚠ 2019: could not locate Capítulo 16 start -- "
                      "falling back to searching the whole document (risk of "
                      "matching chapter 15's near-identical table instead)", file=sys.stderr)
            prevalence = self._parse_prevalence(pdf, chapter_start)
            relationship = self._parse_relationship(pdf, chapter_start)
        return MacroencuestaReport(
            wave_year=2019, sample_size=self.SAMPLE_SIZE,
            prevalence=prevalence, relationship=relationship,
            source_document=self.source,
            source_table="p.154 (prevalencia), p.159 (vínculo con el agresor, Tabla II)",
            notes=(
                "Relationship-to-perpetrator pooled across all severities (rape through "
                "non-penetrative touching) -- 2019 questionnaire couldn't ask it per severity "
                "tier, unlike 2024 (see report's own text, p.158)."
            ),
        )

    def _parse_prevalence(self, pdf, chapter_start: int) -> list[PrevalenceStat]:
        # "Violación alguna vez" and "en la vida" print on different lines
        # (multi-column table header wrap) -- kept as two independent
        # substring checks rather than one phrase spanning both.
        located = _locate_page(pdf, ["EN LA INFANCIA", "VIOLACION ALGUNA VEZ"], start=chapter_start)
        if located is None:
            print("  ⚠ 2019: could not locate prevalence table", file=sys.stderr)
            return []
        idx, _ = located
        out = parse_prevalence_2019(_page_window_text(pdf, idx, n_pages=1))
        if not out:
            print("  ⚠ 2019: prevalence 'Sí' row incomplete", file=sys.stderr)
        return out

    def _parse_relationship(self, pdf, chapter_start: int) -> list[RelationshipStat]:
        located = _locate_page(pdf, ["VINCULO QUE LAS UNE CON EL", "FAMILIAR HOMBRE"], start=chapter_start)
        if located is None:
            print("  ⚠ 2019: could not locate vínculo-con-el-agresor table", file=sys.stderr)
            return []
        idx, _ = located
        out = parse_relationship_2019(_page_window_text(pdf, idx, n_pages=1))
        if len(out) < 6:
            print(f"  ⚠ 2019: vínculo table only found {len(out)}/6 rows", file=sys.stderr)
        return out


# ──────────────────────────────────────────────────────────────
# 2024 wave
# ──────────────────────────────────────────────────────────────

class Macroencuesta2024Parser:
    """2024 wave. First edition to (a) publish 95% CIs and (b) ask
    relationship-to-perpetrator separately per severity tier (Tabla 16.21)."""

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.source = pdf_path.name

    def parse(self) -> MacroencuestaReport:
        with pdfplumber.open(self.pdf_path) as pdf:
            sample_size = self._parse_sample_size(pdf)
            prevalence = self._parse_prevalence(pdf)
            relationship = self._parse_relationship(pdf)
        return MacroencuestaReport(
            wave_year=2024, sample_size=sample_size,
            prevalence=prevalence, relationship=relationship,
            source_document=self.source,
            source_table="Tabla 16.1/16.2 (prevalencia), Tabla 16.21 (vínculo con el agresor)",
        )

    @staticmethod
    def _parse_sample_size(pdf) -> int | None:
        located = _locate_page(pdf, ["METODOLOGIA"])
        if located is None:
            return None
        idx, _ = located
        text = _page_window_text(pdf, idx, n_pages=1)
        m = re.search(r"[Nn]\s*=\s*([\d.]+)", text)
        return int(parse_es_number(m.group(1))) if m else None

    def _parse_prevalence(self, pdf) -> list[PrevalenceStat]:
        located = _locate_page(pdf, ["TABLA 16.1 PREVALENCIA"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 16.1 (overall prevalence)", file=sys.stderr)
            return []
        idx, _ = located
        overall_text = _page_window_text(pdf, idx, n_pages=2)
        out = parse_prevalence_block_2024(overall_text, "any", start_after="Tabla 16.1")

        located2 = _locate_page(pdf, ["TABLA 16.2"], start=idx)
        if located2 is None:
            print("  ⚠ 2024: could not locate Tabla 16.2 (by-severity prevalence)", file=sys.stderr)
            return out
        idx2, _ = located2
        severity_text = _page_window_text(pdf, idx2, n_pages=2)
        for violence_type, label in (
            ("rape", "Violaciones"), ("attempted_rape", "Intentos de violación"),
            ("other", "Otras formas de violencia sexual"),
        ):
            out += parse_prevalence_block_2024(severity_text, violence_type, start_after=label)
        return out

    def _parse_relationship(self, pdf) -> list[RelationshipStat]:
        # The table's own title ("Tabla 16.21 Mujeres...") plus a
        # parenthesized row label ("Desconocida (mujer)") that only appears
        # in the actual data table -- not "TABLA 16.21"/"FAMILIAR HOMBRE"
        # alone, both of which also appear in the *prose* on the preceding
        # page ("...se concluye lo siguiente (Tabla 16.21)... agresor fue un
        # familiar hombre...", not the table itself).
        located = _locate_page(pdf, ["TABLA 16.21 MUJERES", "DESCONOCIDA (MUJER)"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 16.21 (vínculo con el agresor)", file=sys.stderr)
            return []
        idx, _ = located
        out = parse_relationship_2024(_page_window_text(pdf, idx, n_pages=1))
        rows_found = len({r.key for r in out})
        if rows_found < 6:
            print(f"  ⚠ 2024: vínculo table only found {rows_found}/6 label rows", file=sys.stderr)
        return out


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

_PARSERS = {2019: Macroencuesta2019Parser, 2024: Macroencuesta2024Parser}


def infer_year(pdf_path: Path) -> int | None:
    m = re.search(r"(2019|2024)", pdf_path.name)
    return int(m.group(1)) if m else None


def write_dataset(dataset: MacroencuestaDataset, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(dataset.model_dump_json(indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", type=Path, help="Directory containing Macroencuesta_{2019,2024}.pdf")
    ap.add_argument("--pdf", type=Path, help="Single PDF file")
    ap.add_argument("--year", type=int, choices=[2019, 2024], help="Override year (use with --pdf)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    if args.pdf:
        pdfs = [(args.pdf, args.year or infer_year(args.pdf))]
    elif args.pdf_dir:
        pdfs = [(p, infer_year(p)) for p in sorted(args.pdf_dir.glob("Macroencuesta_*.pdf"))]
    else:
        sys.exit("Provide --pdf or --pdf-dir")

    reports = []
    for pdf_path, year in pdfs:
        if year not in _PARSERS:
            print(f"  SKIP {pdf_path.name} (unsupported year {year} -- only 2019/2024 implemented)", file=sys.stderr)
            continue
        print(f"  Parsing Macroencuesta {year}: {pdf_path.name}")
        reports.append(_PARSERS[year](pdf_path).parse())

    if not reports:
        sys.exit("No reports parsed.")
    reports.sort(key=lambda r: r.wave_year)
    years = [r.wave_year for r in reports]
    stem = f"{years[0]}" if years[0] == years[-1] else f"{years[0]}-{years[-1]}"
    out = args.out_dir / f"macroencuesta_{stem}.json"
    write_dataset(MacroencuestaDataset(reports=reports), out)
    print(f"  -> {out} ({len(reports)} report(s))")


if __name__ == "__main__":
    main()
