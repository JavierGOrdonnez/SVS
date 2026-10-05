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


class ContextStat(BaseModel):
    """Assault-context row (T104): where it happened (`dimension='location'`,
    Cap. 16.5) or whether the victim had interacted with the aggressor online
    beforehand (`dimension='online_prior'`, Cap. 16.6, 2024 only)."""
    dimension: str               # 'location' | 'online_prior'
    key: str                     # e.g. 'own_home', 'open_areas'; 'yes' | 'no' | 'nc' for online_prior
    violence_type: str           # 'any' (2019, pooled) | 'rape' | 'attempted_rape' | 'other'
    pct: float | None = None     # None = suppressed ('.') or not collected ('-')
    population_estimate: int | None = None  # 2024 only
    sample_n: int | None = None             # 2019 only


class NonReportingReason(BaseModel):
    """One cell of a "motivos para no denunciar" table (multiple-response
    question: columns don't sum to 100). `scope` is 'partner' (Cap. 9) or
    'outside_partner' (Cap. 16.8.1.5); `group` is the table's column."""
    scope: str                   # 'partner' | 'outside_partner'
    group: str                   # 'current_partner' | 'past_partners' | 'any_partner' |
                                 # 'any_sexual' | 'rape' | 'attempted_rape' | 'other'
    reason: str                  # canonical key, comparable across waves (see _REASON_PATTERNS)
    pct: float | None = None     # None = suppressed ('.', sample <6) or not asked ('-')
    n: int | None = None         # 2019: raw sample count; 2024: population estimate (partner only)
    low_n: bool = False          # 2024 '¨' flag: 6-19 observations, use with caution


class MacroencuestaReport(BaseModel):
    wave_year: int
    sample_size: int | None = None
    prevalence: list[PrevalenceStat] = []
    relationship: list[RelationshipStat] = []
    context: list[ContextStat] = []
    non_reporting_reasons: list[NonReportingReason] = []
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


# ── Assault context (T104): location + prior online interaction ──

_LOCATION_LABELS_2019 = [
    ("own_home", r"^En la casa donde vivía"), ("aggressor_home", r"^En la casa de la persona agresora"),
    ("other_home", r"^En la casa de otra persona"), ("educational", r"^En un centro educativo"),
    ("public_transport", r"^En el transporte público"), ("workplace", r"^En el lugar de trabajo"),
    ("shops_hotels_etc", r"^En tiendas, hoteles"), ("nightlife", r"^En discotecas, bares"),
    ("sports", r"^En eventos deportivos"), ("open_areas", r"^En zonas abiertas"),
    ("other", r"^En otros lugares"), ("nc", r"^N\.C\."),
]
_NUM_TAIL_RE = re.compile(r"^(?:¨?\d{1,3}(?:\.\d{3})*(?:,\d+)?|\.|-)$")


def _split_label_and_tail(line: str, n_tail: int) -> tuple[str, list[str]] | None:
    """Split a table row into (label, last `n_tail` value tokens), or None if
    the row doesn't end in `n_tail` numeric/'.'/'-' tokens."""
    toks = line.split()
    if len(toks) < n_tail:
        return None
    tail = toks[-n_tail:]
    if not all(_NUM_TAIL_RE.match(t) for t in tail):
        return None
    return " ".join(toks[:-n_tail]), tail


def _tok_value(tok: str) -> float | None:
    if tok in (".", "-"):
        return None
    return parse_es_number(tok.lstrip("¨"))


def parse_location_2019(text: str) -> list[ContextStat]:
    """Parse 2019's Cap. 16.7 location table. Four numeric columns:
    N/% among all victims of outside-partner sexual violence (pooled
    severities, N=620), then N/% among women who suffered a rape. NOTE (per
    the report's own footnote 128): the rape column means "some assault of
    theirs happened there", not "the rape happened there" -- 2019 could not
    ask location per severity. Labels wrap across lines, so a numbers-only
    row takes its label from the preceding line."""
    lines = [l.strip() for l in text.splitlines()]
    out = []
    for i, line in enumerate(lines):
        split = _split_label_and_tail(line, 4)
        if split is None:
            continue
        label = split[0] or (lines[i - 1] if i else "")
        for key, pat in _LOCATION_LABELS_2019:
            if re.search(pat, label):
                n_any, pct_any, n_rape, pct_rape = (_tok_value(t) for t in split[1])
                out.append(ContextStat(dimension="location", key=key, violence_type="any",
                                       pct=pct_any, sample_n=int(n_any) if n_any is not None else None))
                out.append(ContextStat(dimension="location", key=key, violence_type="rape",
                                       pct=pct_rape, sample_n=int(n_rape) if n_rape is not None else None))
                break
    return out


_LOCATION_KEYS_2024 = {
    "1.": "any_house", "1.1.": "own_home", "1.2.": "aggressor_home", "1.3.": "other_home",
    "2.": "educational", "3.": "public_transport", "4.": "workplace", "5.": "shops_hotels_etc",
    "6.": "official_places", "7.": "festive_any", "7.1.": "nightlife", "7.2.": "festive_outdoor",
    "8.": "sports", "9.": "open_areas", "10.": "online", "11.": "other",
}


def parse_location_2024(text: str) -> list[ContextStat]:
    """Parse Tabla 16.22: numbered rows ('1. En una casa', '1.1. ...'), six
    value tokens = (%, N) x (rape, attempted_rape, other). Parent rows
    ('1.' any house, '7.' any festive) overlap their '.x' children -- keep
    both, keyed distinctly, rather than picking one."""
    out = []
    for line in text.splitlines():
        split = _split_label_and_tail(line.strip(), 6)
        if split is None:
            continue
        label, tail = split
        key = _LOCATION_KEYS_2024.get(label.split(" ", 1)[0])
        if key is None:
            continue
        for i, violence_type in enumerate(_SEVERITY_ORDER_2024):
            pct, n = _tok_value(tail[2 * i]), _tok_value(tail[2 * i + 1])
            out.append(ContextStat(dimension="location", key=key, violence_type=violence_type,
                                   pct=pct, population_estimate=int(n) if n is not None else None))
    return out


def parse_online_prior_2024(text: str) -> list[ContextStat]:
    """Parse Tabla 16.23: Sí / No / NC rows, three % columns
    (rape, attempted_rape, other). The Sí/No labels wrap, so the numbers sit
    on the middle line of each label; NC is single-line."""
    out = []
    for line in text.splitlines():
        if line.startswith("Total "):
            break  # the page also carries the next table (16.24), which has its own NC row
        split = _split_label_and_tail(line.strip(), 3)
        if split is None:
            continue
        label = split[0]
        if label.startswith("Sí, algunos o todos") or label.endswith("online de"):
            key = "yes"
        elif label.startswith("haber conocido o interactuado online"):
            key = "no"
        elif label == "NC":
            key = "nc"
        else:
            continue
        for violence_type, tok in zip(_SEVERITY_ORDER_2024, split[1]):
            out.append(ContextStat(dimension="online_prior", key=key, violence_type=violence_type,
                                   pct=_tok_value(tok)))
    return out


# ──────────────────────────────────────────────────────────────
# Reasons for not reporting (T102) -- Cap. 9 (partner) + Cap. 16.8.1.5
# ──────────────────────────────────────────────────────────────

# Canonical reason key -> accent-stripped, lowercased regex. First match wins,
# so order matters where one label's words appear in another's.
_REASON_PATTERNS = [
    ("resolved_alone", r"resolvio sola"),
    ("low_importance", r"poca importancia"),
    ("fear_of_aggressor", r"miedo al agresor"),
    ("shame", r"verguenza"),
    ("not_believed", r"no la creyeran"),
    ("own_fault", r"su culpa"),
    ("unaware", r"desconocimiento"),
    ("no_resources", r"recursos"),
    ("relationship_ended", r"separo"),
    ("problem_ended", r"problema se termino"),
    ("prevented_by_other", r"pareja u otra persona|otra persona la disuadio"),
    ("not_physical", r"no ser algo fisico"),
    ("went_elsewhere", r"otro lugar"),
    ("in_love", r"enamorada"),
    ("fear_losing_children", r"perder a sus hijos"),
    ("children_father", r"pierdan a su padre"),
    ("avoid_arrest", r"arresten|arrestaran"),
    ("other_times", r"otros tiempos"),
    ("other_country", r"otro pais"),
    ("was_minor", r"era menor"),
    ("other", r"otros motivos"),
    ("nc", r"^n\.?c\.?$"),
]

_VAL = r"(?:¨?\d{1,3}(?:\.\d{3})*(?:,\d+)?|[.\-])"


def _reason_key(context: str) -> str | None:
    norm = strip_accents(context).lower().strip()
    for key, pat in _REASON_PATTERNS:
        if re.search(pat, norm):
            return key
    return None


def _reason_cells(tokens: list[str], layout) -> list[tuple[str, float | None, int | None, bool]]:
    """Map a data row's value tokens to (group, pct, n, low_n) per `layout`
    (kind, groups): 'n_pct' = (N, %) pairs, 'pct_n' = (%, N) pairs,
    'pct' = % only."""
    def num(t):
        t = t.lstrip("¨")
        return None if t in (".", "-") else parse_es_number(t)
    kind, groups = layout
    step = 1 if kind == "pct" else 2
    out = []
    for i, g in enumerate(groups):
        chunk = tokens[i * step:(i + 1) * step]
        if kind == "n_pct":
            n, pct = num(chunk[0]), num(chunk[1])
        elif kind == "pct_n":
            pct, n = num(chunk[0]), num(chunk[1])
        else:
            pct, n = num(chunk[0]), None
        pct_tok = chunk[1] if kind == "n_pct" else chunk[0]
        out.append((g, pct, int(n) if n is not None else None, pct_tok.startswith("¨")))
    return out


def parse_non_reporting_reasons(text: str, scope: str, title_anchor: str, layout) -> list[NonReportingReason]:
    """Parse a "Motivos para no denunciar" table from `page.extract_text()`.

    Row labels wrap unpredictably (the number cells can sit on the first, a
    middle, or the last label line), so a row's reason key is matched against
    the non-numeric lines pending since the previous data row plus the data
    line's own label text; rows no key matches (headers, footnotes) are
    skipped. `layout` is (kind, groups) -- see `_reason_cells`."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if title_anchor in l), None)
    if start is None:
        return []
    kind, groups = layout
    n_vals = len(groups) * (1 if kind == "pct" else 2)
    row_re = re.compile(rf"^(.*?)\s*((?:{_VAL}\s+){{{n_vals - 1}}}{_VAL})$")
    out, pending = [], []
    for line in lines[start + 1:]:
        line = line.strip()
        if line.startswith(("1. Porcentaje", "* Pregunta", "Pregunta de respuesta")):
            break
        m = row_re.match(line)
        if not m:
            pending.append(line)
            continue
        key = _reason_key(" ".join(pending + [m.group(1)]))
        pending = []
        if key is None:
            continue
        for g, pct, n, low in _reason_cells(m.group(2).split(), layout):
            out.append(NonReportingReason(scope=scope, group=g, reason=key, pct=pct, n=n, low_n=low))
    return out


_LAYOUT_2019_PARTNER = ("n_pct", ["current_partner", "past_partners"])
_LAYOUT_2019_SEXUAL = ("n_pct", ["any_sexual", "rape"])
_LAYOUT_2024_PARTNER = ("pct_n", ["current_partner", "past_partners", "any_partner"])
_LAYOUT_2024_SEXUAL = ("pct", ["rape", "attempted_rape", "other"])


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
            context = self._parse_location(pdf, chapter_start)
            reasons = self._parse_reasons(pdf, chapter_start)
        return MacroencuestaReport(
            wave_year=2019, sample_size=self.SAMPLE_SIZE,
            prevalence=prevalence, relationship=relationship, context=context,
            non_reporting_reasons=reasons,
            source_document=self.source,
            source_table="p.154 (prevalencia), p.159 (vínculo con el agresor, Tabla II), p.161 (lugar)",
            notes=(
                "Location (Cap. 16.7) is likewise pooled across severities; its 'rape' rows mean "
                "'some assault of theirs happened there', not 'the rape happened there' (report fn. 128). "
                "No prior-online-interaction question in this wave. "
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

    def _parse_location(self, pdf, chapter_start: int) -> list[ContextStat]:
        located = _locate_page(pdf, ["EN LA CASA DONDE VIVIA", "EN ZONAS ABIERTAS"], start=chapter_start)
        if located is None:
            print("  ⚠ 2019: could not locate lugar table (Cap. 16.7)", file=sys.stderr)
            return []
        out = parse_location_2019(located[1])
        if len(out) < 24:
            print(f"  ⚠ 2019: lugar table only found {len(out) // 2}/12 rows", file=sys.stderr)
        return out

    def _parse_reasons(self, pdf, chapter_start: int) -> list[NonReportingReason]:
        out = []
        # The partner table (2019's "capítulo 10") precedes chapter 16.
        located = _locate_page(pdf, ["MOTIVOS PARA NO DENUNCIAR LA VFSEM DE LA PAREJA", "LO RESOLVIO SOLA"])
        if located:
            out += parse_non_reporting_reasons(
                located[1], "partner", "Motivos para no denunciar la VFSEM", _LAYOUT_2019_PARTNER)
        else:
            print("  ⚠ 2019: could not locate partner non-reporting reasons table", file=sys.stderr)
        located = _locate_page(pdf, ["MOTIVOS PARA NO DENUNCIAR LA VIOLENCIA SEXUAL FUERA DE LA PAREJA", "ERA MENOR"],
                               start=chapter_start)
        if located:
            out += parse_non_reporting_reasons(
                located[1], "outside_partner", "Motivos para no denunciar la violencia sexual", _LAYOUT_2019_SEXUAL)
        else:
            print("  ⚠ 2019: could not locate outside-partner non-reporting reasons table", file=sys.stderr)
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
            context = self._parse_context(pdf)
            reasons = self._parse_reasons(pdf)
        return MacroencuestaReport(
            wave_year=2024, sample_size=sample_size,
            prevalence=prevalence, relationship=relationship, context=context,
            non_reporting_reasons=reasons,
            source_document=self.source,
            source_table=("Tabla 16.1/16.2 (prevalencia), Tabla 16.21 (vínculo con el agresor), "
                          "Tabla 16.22 (lugar), Tabla 16.23 (interacción online previa)"),
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

    def _parse_context(self, pdf) -> list[ContextStat]:
        out: list[ContextStat] = []
        located = _locate_page(pdf, ["TABLA 16.22 MUJERES", "ONLINE (SOLO PARA"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 16.22 (lugar)", file=sys.stderr)
        else:
            out += parse_location_2024(located[1])
        located = _locate_page(pdf, ["TABLA 16.23 DISTRIBUCION", "INTERACTUADO ONLINE"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 16.23 (interacción online previa)", file=sys.stderr)
        else:
            out += parse_online_prior_2024(located[1])
        return out

    def _parse_reasons(self, pdf) -> list[NonReportingReason]:
        out = []
        for scope, kws, anchor, layout in (
            ("partner", ["TABLA 9.7 MOTIVOS PARA NO DENUNCIAR", "LO RESOLVIO SOLA"],
             "Tabla 9.7", _LAYOUT_2024_PARTNER),
            ("outside_partner", ["TABLA 16.30 MOTIVOS PARA NO DENUNCIAR", "ERA MENOR"],
             "Tabla 16.30 Motivos", _LAYOUT_2024_SEXUAL),
        ):
            located = _locate_page(pdf, kws)
            if located is None:
                print(f"  ⚠ 2024: could not locate {anchor} (non-reporting reasons)", file=sys.stderr)
                continue
            out += parse_non_reporting_reasons(located[1], scope, anchor, layout)
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
