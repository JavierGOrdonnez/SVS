"""Macroencuesta de Violencia contra la Mujer parser (T99).

Parses the "Violencia sexual fuera del ámbito de la pareja" chapter
(Cap. 16 in both the 2019 and 2024 editions) of the Ministerio de Igualdad's
victimization survey — the two data points this repo needs from it:
  1. Prevalence (lifetime / last-4-years / last-12-months / childhood),
     overall and — 2024 only — broken out by severity tier (rape / attempted
     rape / other sexual violence).
  2. Victim-perpetrator relationship (familiar / conocido / desconocido),
     overall (2019, pooled across severities) or by severity tier (2024).
  3. (T105) Frequency -- once vs. more than once, and cadence of repeats
     among those victimized more than once -- plus whether more than one
     perpetrator took part in at least one incident, both outside-partner.

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


class FrequencyStat(BaseModel):
    measure: str                 # 'episodes' (once vs. more than once) | 'cadence' (among repeat victims)
    category: str                # episodes: 'once'|'multiple'|'nc'; cadence: 'daily'|'weekly'|'monthly'|'yearly'|'less_than_yearly'|'particular_periods'|'nc'
    violence_type: str           # 'any' (2019, pooled) | 'rape' | 'attempted_rape' | 'other' (2024)
    pct: float | None = None     # % of victims of that violence_type (cadence: of those victimized more than once)
    sample_n: int | None = None  # 2019 only -- raw survey N


class ParticipantStat(BaseModel):
    category: str                # 'single' | 'multiple' (>1 perpetrator in at least one incident) | 'nc'
    violence_type: str           # 'any' | 'rape' | 'attempted_rape' | 'other'
    pct: float | None = None     # % of victims of that violence_type
    sample_n: int | None = None  # 2019 only -- raw survey N


class ConsequenceStat(BaseModel):
    """Cap. 16.9-equivalent consequences of the violence (T106): injuries,
    medical care, psychological consequences, substance use to cope,
    disability, work absence, self-perceived health, suicidal ideation, and
    (2024 only) insecurity perception. One generic shape covers all of
    these -- the categories differ in which fields they populate, not in
    structure."""
    category: str                # 'injury' | 'injury_type' | 'medical_care' | 'psychological'
                                  # | 'psychological_type' | 'substance_use' | 'substance_use_type'
                                  # | 'disability' | 'work_absence' | 'self_perceived_health'
                                  # | 'suicidal_ideation' | 'insecurity'
    item: str | None = None      # sub-label within category, e.g. injury/psychological/substance
                                  # type, health-rating label, or insecurity item -- None for
                                  # single-item categories (disability, work_absence, suicidal_ideation)
    violence_type: str = "any"   # 'any' | 'rape' | 'attempted_rape' | 'other' | 'no_violence'
                                  # ('no_violence' is the 2024 comparison column on health/suicidal-
                                  # ideation/insecurity tables only)
    timeframe: str = "lifetime"
    pct: float | None = None
    population_estimate: int | None = None
    sample_n: int | None = None  # 2019 only -- raw survey N
    ci_low: float | None = None
    ci_high: float | None = None


class ReportingStat(BaseModel):
    """Cap. 9.1.4 / 16.8.1.5 reporting behavior: reasons for not reporting
    sexual violence (T102). Covers both partner and outside-partner violence."""
    reason: str                  # specific reason text, e.g. "vergüenza"
    reason_key: str | None = None # normalized key for joining across waves

    # Context: which population this applies to
    violence_type: str | None = None  # outside-partner: 'any'|'rape'|'attempted_rape'|'other'
    partner_status: str | None = None # partner: 'current'|'past'|'any'

    # Data
    pct: float | None = None
    population_estimate: int | None = None  # 2024 only
    sample_n: int | None = None  # 2019 only

    # Data quality flags
    suppressed: bool = False     # 2024 only: '.' marker
    small_sample: bool = False   # 2024 only: '¨' marker


class MacroencuestaReport(BaseModel):
    wave_year: int
    sample_size: int | None = None
    prevalence: list[PrevalenceStat] = []
    relationship: list[RelationshipStat] = []
    frequency: list[FrequencyStat] = []
    participants: list[ParticipantStat] = []
    consequences: list[ConsequenceStat] = []
    reporting: list[ReportingStat] = []
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


def _section(text: str, start_marker: str, end_marker: str | None = None) -> str:
    """Slice `text` from `start_marker` (inclusive) to the next occurrence of
    `end_marker` (exclusive -- or end of text if `end_marker` is None or not
    found). Used to scope a multi-table page blob down to just one table
    before handing it to `_ordered_rows`/`_find_si_ic_block`, so a
    neighboring table's rows can't leak in. Markers should include enough of
    a table's own title text (not just "Tabla 16.NN") to avoid matching an
    earlier parenthetical citation like "(Tabla 16.NN)," in prose -- that
    citation is always followed by punctuation, never by the title's own
    next word, so e.g. "Tabla 16.50 Consecuencias" only matches the real
    table heading."""
    start = text.find(start_marker)
    if start == -1:
        return text
    end = text.find(end_marker, start + len(start_marker)) if end_marker else -1
    return text[start:end] if end != -1 else text[start:]


def _ordered_rows(text: str, n_numbers: int) -> list[list[float | None]]:
    """Every line in `text` whose extracted numeric-token count is exactly
    `n_numbers`, in document order. For wrapped-label tables (2019's, and
    some of 2024's) where a row's label spans several physical lines but its
    numbers land on one line at a fixed count -- label-only continuation
    lines yield 0 numbers and are skipped automatically, whether the numbers
    sit at the end of the label's own line or alone on a line in the middle
    of a wrapped label. Caller zips the result to a static, position-based
    label list -- wrapped labels can't be regex-matched directly."""
    out = []
    for line in text.splitlines():
        nums = _numbers_in(line)
        if len(nums) == n_numbers:
            out.append(nums)
    return out


def _line_numbers(text: str, pattern: str) -> list[float] | None:
    """First line (regex `pattern` anchored at line start, after stripping)
    -> its numeric tokens. For single-line 'Label ... numbers' rows that
    `_find_si_ic_block` doesn't fit -- that helper only matches a bare 'Sí'
    or 'Sí ' line (expecting a separate IC-95% line below), not an
    item-labeled line like 'Sí, alguna lesión 100 16,2 ...'."""
    for line in text.splitlines():
        if re.match(pattern, line.strip()):
            return _numbers_in(line)
    return None


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
# T105: frequency (once vs. repeated, cadence) + single-vs-multiple
# perpetrators, outside-partner. Both waves' tables sit right after the
# relationship table in reading order (2019: "16.5 Frecuencia..." /
# "16.8 Agresiones sexuales... grupo"; 2024: Tabla 16.16-16.18, right before
# Tabla 16.21's vínculo table) -- same text-regex strategy as the functions
# above, just keyed off each table's own title/prose rather than a "Sí"
# block (these tables don't use that shape).
# ──────────────────────────────────────────────────────────────

_EPISODE_LABELS = [("once", r"^Una vez"), ("multiple", r"^Más de una vez"), ("nc", r"^NC\b")]
_CADENCE_LABELS_2024 = [
    ("daily", r"^Diariamente"), ("weekly", r"^Semanalmente"), ("monthly", r"^Mensualmente"),
    ("yearly", r"^Anualmente"), ("less_than_yearly", r"^Menos de una vez al año"),
    ("particular_periods", r"^Solo en períodos particulares"), ("nc", r"^NC\b"),
]
_CADENCE_LABELS_2019 = [
    ("daily", r"^Todos los días"), ("weekly", r"^Al menos una o más veces por semana"),
    ("monthly", r"^Al menos una o más veces al mes"), ("yearly", r"^Al menos una o más veces al año"),
    ("less_than_yearly", r"^Menos de una vez al año"),
    ("particular_periods", r"^Solo en períodos particulares"), ("nc", r"^NC\b"),
]
_PARTICIPANT_LABELS_2024 = [
    ("single", r"^Solo una persona"), ("multiple", r"^Al menos en una ocasión"), ("nc", r"^NC\b"),
]
_PARTICIPANT_LABELS_2019 = [
    ("single", r"^No, en todos los incidentes"), ("multiple", r"^Sí, en al menos un incidente"), ("nc", r"^NC\b"),
]
# Tabla 16.18's row for "multiple" wraps onto 3 printed lines ("Al menos en
# una ocasión" / "participó más de una" / "persona (varias personas)") with
# the data row's own numbers printed on the *second* of those lines, not
# the first where the label regex matches -- same wrapped-cell shape as
# Tabla 16.17's "Solo en períodos particulares" row. `_row_tokens` below
# handles both by looking at the following line when the match line itself
# has no numbers.
_SEVERITY_ORDER_2024_PARTICIPANTS = ["rape", "attempted_rape", "other", "any"]  # Tabla 16.18 adds an all-severities 4th column


def _section(text: str, start: str, end: str | None = None) -> str:
    """Slice of `text` from the first `start` marker to the next `end`
    marker after it (or EOF). Needed because short row labels like 'NC' or
    'Una vez' repeat across the several small tables sharing a page."""
    i = text.find(start)
    if i == -1:
        return ""
    j = text.find(end, i + len(start)) if end else -1
    return text[i:j if j != -1 else None]


def _row_tokens(text: str, label_pat: str) -> list[float | None] | None:
    """Numbers for the first row whose label matches `label_pat`. Falls
    through to the next few lines when the label line itself carries no
    numbers -- a wrapped multi-line label cell, as above. Tabla 16.18's
    "multiple" row wraps across *three* printed lines with the data row's
    numbers landing on the middle one, mixed in with more label text
    ("participó más de una 11,3 7,6 10,0 10,4"), not a line starting
    cleanly with a digit -- `_split_tokens_2024` already discards
    non-numeric words, so applying it to each candidate line and taking the
    first that yields anything handles that shape too."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(label_pat, line.strip())
        if not m:
            continue
        toks = _split_tokens_2024(line.strip()[m.end():])
        if toks:
            return toks
        for j in range(i + 1, min(i + 4, len(lines))):
            toks = _split_tokens_2024(lines[j])
            if toks:
                return toks
    return None


def _rows_2024(text: str, labels: list[tuple[str, str]], severities: list[str]) -> list[tuple[str, str, float | None]]:
    out = []
    for category, pat in labels:
        toks = _row_tokens(text, pat)
        if toks is None:
            continue
        for violence_type, pct in zip(severities, toks):
            out.append((category, violence_type, pct))
    return out


def parse_frequency_2024(text: str) -> list[FrequencyStat]:
    """Tabla 16.16 (once vs. more than once) + Tabla 16.17 (cadence among
    those victimized more than once) -- both have the same three severity
    columns (rape / attempted rape / other)."""
    episodes = _section(text, "Tabla 16.16 Distribución", "Tabla 16.17 Distribución")
    cadence = _section(text, "Tabla 16.17 Distribución", "El símbolo")
    out = [FrequencyStat(measure="episodes", category=c, violence_type=v, pct=pct)
           for c, v, pct in _rows_2024(episodes, _EPISODE_LABELS, _SEVERITY_ORDER_2024)]
    out += [FrequencyStat(measure="cadence", category=c, violence_type=v, pct=pct)
            for c, v, pct in _rows_2024(cadence, _CADENCE_LABELS_2024, _SEVERITY_ORDER_2024)]
    return out


def parse_participants_2024(text: str) -> list[ParticipantStat]:
    """Tabla 16.18: three severity columns plus a 4th all-severities total."""
    table = _section(text, "Tabla 16.18 Distribución", "1. Porcentaje")
    return [ParticipantStat(category=c, violence_type=v, pct=pct)
            for c, v, pct in _rows_2024(table, _PARTICIPANT_LABELS_2024, _SEVERITY_ORDER_2024_PARTICIPANTS)]


def _rows_2019(text: str, labels: list[tuple[str, str]], severities: list[str]) -> list[tuple[str, str, int | None, float | None]]:
    """2019 rows are (N, %) pairs, one pair per column (no severity split
    beyond what `severities` lists -- pooled 'any', or 'any'+'rape' for the
    group-aggression table, which does break out rape alone)."""
    out = []
    for category, pat in labels:
        toks = _row_tokens(text, pat)
        if toks is None:
            continue
        for i, violence_type in enumerate(severities):
            if 2 * i + 1 >= len(toks):
                break
            n, pct = toks[2 * i], toks[2 * i + 1]
            out.append((category, violence_type, int(n) if n is not None else None, pct))
    return out


def parse_frequency_2019(text: str) -> list[FrequencyStat]:
    """'Frecuencia (1)' (once vs. more than once) and 'Frecuencia (2)'
    (cadence among repeat victims) -- pooled across severities only (2019's
    questionnaire-length constraint, same as its relationship table)."""
    episodes = _section(text, "Frecuencia (1)", "Frecuencia (2)")
    cadence = _section(text, "Frecuencia (2)", "16.6")
    out = [FrequencyStat(measure="episodes", category=c, violence_type=v, sample_n=n, pct=pct)
           for c, v, n, pct in _rows_2019(episodes, _EPISODE_LABELS, ["any"])]
    out += [FrequencyStat(measure="cadence", category=c, violence_type=v, sample_n=n, pct=pct)
            for c, v, n, pct in _rows_2019(cadence, _CADENCE_LABELS_2019, ["any"])]
    return out


def parse_participants_2019(text: str) -> list[ParticipantStat]:
    """'Agresiones sexuales en grupo': columns are all-violence victims
    (N=620) then rape victims alone (N=213) -- no attempted-rape/other
    split (2019 can't distinguish which episode was the group one, see the
    table's own prose caveat)."""
    table = _section(text, "Agresiones sexuales en grupo", "Total")
    return [ParticipantStat(category=c, violence_type=v, sample_n=n, pct=pct)
            for c, v, n, pct in _rows_2019(table, _PARTICIPANT_LABELS_2019, ["any", "rape"])]
# Consequences (T106, Cap. 16.9-equivalent): injuries, medical care,
# psychological consequences, substance use to cope, disability, work
# absence, self-perceived health, suicidal ideation, insecurity perception
# (2024 only). Item-type label lists are shared across waves where the
# underlying question is the same -- 2024 adds one extra injury-type item
# ("other_physical_injury") that 2019 doesn't ask, noted where relevant.
# ──────────────────────────────────────────────────────────────

_INJURY_TYPES = [
    "cuts_bruises_pain", "eye_ear_sprain_burn", "deep_wounds_fractures_internal",
    "involuntary_abortion", "genital_injuries", "std", "permanent_physical_damage",
]
_INJURY_TYPES_2024 = _INJURY_TYPES + ["other_physical_injury"]
_MEDICAL_CARE_LABELS = ["hospital_stay", "medical_attention_no_hospital", "not_needed", "should_have_received"]
_PSYCH_TYPES = [
    "depression", "loss_of_self_esteem", "anxiety_phobia_panic", "despair_helplessness",
    "concentration_memory", "sleep_eating_problems", "recurrent_pain", "self_harm_suicidal_thoughts",
]
_SUBSTANCE_TYPES = ["medication", "alcohol", "drugs"]
_HEALTH_LABELS = ["very_good", "good", "fair", "bad", "very_bad"]


# -- 2019 --

def parse_injuries_2019(text: str) -> list[ConsequenceStat]:
    out = []
    headline = _line_numbers(text, r"^S[ií], alguna lesi[oó]n")
    if headline and len(headline) >= 8:
        labels = ["lifetime", "last_4_years", "last_12_months", "rape_lifetime"]
        for i, label in enumerate(labels):
            n, pct = headline[2 * i], headline[2 * i + 1]
            out.append(ConsequenceStat(
                category="injury", violence_type="rape" if label == "rape_lifetime" else "any",
                timeframe="lifetime" if label == "rape_lifetime" else label,
                pct=pct, sample_n=int(n) if n is not None else None,
            ))
    rows = _ordered_rows(_section(text, "Tipos de lesiones", "Asistencia sanitaria"), 4)
    for label, row in zip(_INJURY_TYPES, rows):
        n_any, pct_any, n_rape, pct_rape = row
        out.append(ConsequenceStat(category="injury_type", item=label, violence_type="any",
                                    pct=pct_any, sample_n=int(n_any) if n_any is not None else None))
        out.append(ConsequenceStat(category="injury_type", item=label, violence_type="rape",
                                    pct=pct_rape, sample_n=int(n_rape) if n_rape is not None else None))
    return out


def parse_medical_care_2019(text: str) -> list[ConsequenceStat]:
    section = _section(text, "Asistencia sanitaria como consecuencia", "Consecuencias psicol")
    rows = _ordered_rows(section, 4)
    out = []
    for label, row in zip(_MEDICAL_CARE_LABELS, rows):
        n_any, pct_any, n_rape, pct_rape = row
        out.append(ConsequenceStat(category="medical_care", item=label, violence_type="any",
                                    pct=pct_any, sample_n=int(n_any) if n_any is not None else None))
        out.append(ConsequenceStat(category="medical_care", item=label, violence_type="rape",
                                    pct=pct_rape, sample_n=int(n_rape) if n_rape is not None else None))
    return out


def _derived_headline_from_excluyente_tail(rows: list[list[float | None]], n_items: int, category: str) -> list[ConsequenceStat] | None:
    """2019's psychological/substance-use tables don't print a separate
    overall Sí/No headline -- only the itemized multiple-choice table, ending
    in 'Ninguno/No, nada (excluyente)' + 'NC (excluyente)' rows. The overall
    % having *any* consequence is the complement of those two tail rows;
    both waves' prose headline figures (e.g. '53%', '78,9%', '12,7%',
    '26,6%') match this complement exactly."""
    tail = rows[n_items:n_items + 2]
    if len(tail) != 2:
        return None
    none_any, nc_any = tail[0][1], tail[1][1]
    none_rape, nc_rape = tail[0][3], tail[1][3]
    if None in (none_any, nc_any, none_rape, nc_rape):
        return None
    return [
        ConsequenceStat(category=category, violence_type="any", pct=round(100 - none_any - nc_any, 1)),
        ConsequenceStat(category=category, violence_type="rape", pct=round(100 - none_rape - nc_rape, 1)),
    ]


def parse_psychological_2019(text: str) -> list[ConsequenceStat]:
    # Starting the section at the chapter heading ("Consecuencias psicológicas
    # derivadas...") would let a stray prose line with exactly 4 numeric
    # tokens ("57,4% pérdida de autoestima, 55,9% ansiedad o fobias, 49,6%
    # desesperación o fobias, 16%") get picked up by `_ordered_rows` as a
    # spurious row ahead of the real table -- start at the first real row
    # label instead, which is unique in the document.
    section = _section(text, "Depresión", "Discapacidad como consecuencia")
    rows = _ordered_rows(section, 4)
    out = []
    for label, row in zip(_PSYCH_TYPES, rows[:8]):
        n_any, pct_any, n_rape, pct_rape = row
        out.append(ConsequenceStat(category="psychological_type", item=label, violence_type="any",
                                    pct=pct_any, sample_n=int(n_any) if n_any is not None else None))
        out.append(ConsequenceStat(category="psychological_type", item=label, violence_type="rape",
                                    pct=pct_rape, sample_n=int(n_rape) if n_rape is not None else None))
    out += _derived_headline_from_excluyente_tail(rows, 8, "psychological") or []
    return out


def parse_substance_use_2019(text: str) -> list[ConsequenceStat]:
    section = _section(text, "Consumo de sustancias como consecuencia", "Denuncia de la violencia sexual")
    rows = _ordered_rows(section, 4)
    out = []
    for label, row in zip(_SUBSTANCE_TYPES, rows[:3]):
        n_any, pct_any, n_rape, pct_rape = row
        out.append(ConsequenceStat(category="substance_use_type", item=label, violence_type="any",
                                    pct=pct_any, sample_n=int(n_any) if n_any is not None else None))
        out.append(ConsequenceStat(category="substance_use_type", item=label, violence_type="rape",
                                    pct=pct_rape, sample_n=int(n_rape) if n_rape is not None else None))
    out += _derived_headline_from_excluyente_tail(rows, 3, "substance_use") or []
    return out


def parse_disability_2019(text: str) -> list[ConsequenceStat]:
    section = _section(text, "Discapacidad como consecuencia", "Absentismo laboral")
    nums = _line_numbers(section, r"^S[ií]\b")
    if not nums or len(nums) < 2:
        return []
    n, pct = nums[0], nums[1]
    return [ConsequenceStat(category="disability", violence_type="any", pct=pct,
                             sample_n=int(n) if n is not None else None)]


def parse_work_absence_2019(text: str) -> list[ConsequenceStat]:
    section = _section(text, "Absentismo laboral o estudiantil", "Consumo de sustancias")
    nums = _line_numbers(section, r"^S[ií]\b")
    if not nums or len(nums) < 2:
        return []
    n, pct = nums[0], nums[1]
    return [ConsequenceStat(category="work_absence", violence_type="any", pct=pct,
                             sample_n=int(n) if n is not None else None)]


def parse_self_perceived_health_2019(text: str) -> list[ConsequenceStat]:
    section = _section(text, "Estado de salud autopercibido en los 12 meses", "Síntomas de mala salud")
    rows = _ordered_rows(section, 6)
    out = []
    for label, row in zip(_HEALTH_LABELS, rows[:5]):
        n_any, pct_any, n_rape, pct_rape, n_no, pct_no = row
        for vt, n, pct in (("any", n_any, pct_any), ("rape", n_rape, pct_rape), ("no_violence", n_no, pct_no)):
            out.append(ConsequenceStat(category="self_perceived_health", item=label, violence_type=vt,
                                        pct=pct, sample_n=int(n) if n is not None else None))
    return out


def parse_suicidal_ideation_2019(text: str) -> list[ConsequenceStat]:
    nums = _line_numbers(text, r"^Tenencia\s+S[ií]")
    if not nums or len(nums) < 6:
        return []
    n_any, pct_any, n_rape, pct_rape, n_no, pct_no = nums[:6]
    return [
        ConsequenceStat(category="suicidal_ideation", violence_type="any", pct=pct_any,
                         sample_n=int(n_any) if n_any is not None else None),
        ConsequenceStat(category="suicidal_ideation", violence_type="rape", pct=pct_rape,
                         sample_n=int(n_rape) if n_rape is not None else None),
        ConsequenceStat(category="suicidal_ideation", violence_type="no_violence", pct=pct_no,
                         sample_n=int(n_no) if n_no is not None else None),
    ]


# -- 2024 --

def parse_injuries_2024(text: str) -> list[ConsequenceStat]:
    """Tabla 16.46 (headline, by timeframe) + Tabla 16.47 (by severity tier
    x timeframe) -- `text` should be scoped to just those two tables (see
    `Macroencuesta2024Parser._parse_consequences`), since `start_after`
    below matches the *first* 'Violaciones'/... occurrence in `text`."""
    out = []
    si, ic = _find_si_ic_block(text)
    if si and len(si) >= 9:
        for i, timeframe in enumerate(["lifetime", "last_4_years", "last_12_months"]):
            pct, _pct_all, n = si[3 * i], si[3 * i + 1], si[3 * i + 2]
            stat = ConsequenceStat(category="injury", violence_type="any", timeframe=timeframe,
                                    pct=pct, population_estimate=int(n) if n is not None else None)
            if ic and 2 * i < len(ic):
                stat.ci_low, stat.ci_high = ic[2 * i]
            out.append(stat)
    for violence_type, label in (
        ("rape", "Violaciones"), ("attempted_rape", "Intentos de violación"),
        ("other", "Otras formas de violencia sexual"),
    ):
        si2, ic2 = _find_si_ic_block(text, start_after=label)
        if not si2:
            continue
        for i, timeframe in enumerate(["lifetime", "last_4_years", "last_12_months"]):
            base = 2 * i
            if base + 1 >= len(si2):
                continue
            pct, n = si2[base], si2[base + 1]
            stat = ConsequenceStat(category="injury", violence_type=violence_type, timeframe=timeframe,
                                    pct=pct, population_estimate=int(n) if n is not None else None)
            if ic2 and i < len(ic2):
                stat.ci_low, stat.ci_high = ic2[i]
            out.append(stat)
    return out


def parse_injury_types_2024(text: str) -> list[ConsequenceStat]:
    rows = _ordered_rows(text, 6)
    out = []
    for label, row in zip(_INJURY_TYPES_2024, rows):
        for i, vt in enumerate(_SEVERITY_ORDER_2024):
            pct, n = row[2 * i], row[2 * i + 1]
            out.append(ConsequenceStat(category="injury_type", item=label, violence_type=vt,
                                        pct=pct, population_estimate=int(n) if n is not None else None))
    return out


def parse_medical_care_2024(text: str) -> list[ConsequenceStat]:
    rows = _ordered_rows(text, 6)
    out = []
    for label, row in zip(_MEDICAL_CARE_LABELS, rows[:4]):
        for i, vt in enumerate(_SEVERITY_ORDER_2024):
            pct, n = row[2 * i], row[2 * i + 1]
            out.append(ConsequenceStat(category="medical_care", item=label, violence_type=vt,
                                        pct=pct, population_estimate=int(n) if n is not None else None))
    return out


def parse_psychological_2024(text: str) -> list[ConsequenceStat]:
    si, ic = _find_si_ic_block(text)
    if not si or len(si) < 3:
        return []
    pct, n = si[0], si[2]
    stat = ConsequenceStat(category="psychological", violence_type="any", pct=pct,
                            population_estimate=int(n) if n is not None else None)
    if ic:
        stat.ci_low, stat.ci_high = ic[0]
    return [stat]


def parse_psychological_by_severity_2024(text: str) -> list[ConsequenceStat]:
    si, ic = _find_si_ic_block(text)
    if not si or len(si) < 6:
        return []
    out = []
    for i, vt in enumerate(_SEVERITY_ORDER_2024):
        pct, n = si[2 * i], si[2 * i + 1]
        stat = ConsequenceStat(category="psychological", violence_type=vt, pct=pct,
                                population_estimate=int(n) if n is not None else None)
        if ic and i < len(ic):
            stat.ci_low, stat.ci_high = ic[i]
        out.append(stat)
    return out


def parse_psychological_types_2024(text: str) -> list[ConsequenceStat]:
    rows = _ordered_rows(text, 6)
    out = []
    for label, row in zip(_PSYCH_TYPES, rows):
        for i, vt in enumerate(_SEVERITY_ORDER_2024):
            pct, n = row[2 * i], row[2 * i + 1]
            out.append(ConsequenceStat(category="psychological_type", item=label, violence_type=vt,
                                        pct=pct, population_estimate=int(n) if n is not None else None))
    return out


def parse_substance_use_2024(text: str) -> list[ConsequenceStat]:
    si, ic = _find_si_ic_block(text)
    if not si or len(si) < 6:
        return []
    out = []
    for i, vt in enumerate(_SEVERITY_ORDER_2024 + ["any"]):
        pct = si[i]
        n = int(si[5]) if vt == "any" and si[5] is not None else None
        stat = ConsequenceStat(category="substance_use", violence_type=vt, pct=pct, population_estimate=n)
        if ic and i < len(ic):
            stat.ci_low, stat.ci_high = ic[i]
        out.append(stat)
    return out


def parse_substance_use_types_2024(text: str) -> list[ConsequenceStat]:
    rows = _ordered_rows(text, 8)
    out = []
    for label, row in zip(_SUBSTANCE_TYPES, rows):
        for i, vt in enumerate(_SEVERITY_ORDER_2024 + ["any"]):
            pct, n = row[2 * i], row[2 * i + 1]
            out.append(ConsequenceStat(category="substance_use_type", item=label, violence_type=vt,
                                        pct=pct, population_estimate=int(n) if n is not None else None))
    return out


def _parse_si_by_severity_and_total(text: str, category: str) -> list[ConsequenceStat]:
    """Shared shape for Tabla 16.55 (disability) and Tabla 16.56 (work
    absence): one 'Sí' line with (pct, N) per severity tier + total, one
    'IC 95%' line with one CI pair per group."""
    si, ic = _find_si_ic_block(text)
    if not si or len(si) < 8:
        return []
    out = []
    for i, vt in enumerate(_SEVERITY_ORDER_2024 + ["any"]):
        pct, n = si[2 * i], si[2 * i + 1]
        stat = ConsequenceStat(category=category, violence_type=vt, pct=pct,
                                population_estimate=int(n) if n is not None else None)
        if ic and i < len(ic):
            stat.ci_low, stat.ci_high = ic[i]
        out.append(stat)
    return out


def parse_disability_2024(text: str) -> list[ConsequenceStat]:
    return _parse_si_by_severity_and_total(text, "disability")


def parse_work_absence_2024(text: str) -> list[ConsequenceStat]:
    return _parse_si_by_severity_and_total(text, "work_absence")


def parse_self_perceived_health_2024(text: str) -> list[ConsequenceStat]:
    rows = _ordered_rows(text, 5)
    out = []
    types = _SEVERITY_ORDER_2024 + ["any", "no_violence"]
    for label, row in zip(_HEALTH_LABELS, rows):
        for i, vt in enumerate(types):
            out.append(ConsequenceStat(category="self_perceived_health", item=label, violence_type=vt, pct=row[i]))
    return out


def _parse_si_severity_any_novi(text: str, category: str, item: str | None = None) -> list[ConsequenceStat]:
    """Shared shape for Tabla 16.62 (suicidal ideation) and Tabla 16.71/16.72
    (insecurity perception): one 'Sí' line with pct per severity tier, then
    pct + population_estimate for 'any', then pct for the no-violence
    comparison group -- no IC line on these three tables."""
    nums = _line_numbers(text, r"^S[ií]\b")
    if not nums or len(nums) < 6:
        return []
    pct_rape, pct_attempt, pct_other, pct_any, n_any, pct_no = nums[:6]
    return [
        ConsequenceStat(category=category, item=item, violence_type="rape", pct=pct_rape),
        ConsequenceStat(category=category, item=item, violence_type="attempted_rape", pct=pct_attempt),
        ConsequenceStat(category=category, item=item, violence_type="other", pct=pct_other),
        ConsequenceStat(category=category, item=item, violence_type="any", pct=pct_any,
                         population_estimate=int(n_any) if n_any is not None else None),
        ConsequenceStat(category=category, item=item, violence_type="no_violence", pct=pct_no),
    ]


def parse_suicidal_ideation_2024(text: str) -> list[ConsequenceStat]:
    return _parse_si_severity_any_novi(text, "suicidal_ideation")


def parse_insecurity_streets_2024(text: str) -> list[ConsequenceStat]:
    return _parse_si_severity_any_novi(text, "insecurity", item="avoided_streets_areas")


def parse_insecurity_known_person_2024(text: str) -> list[ConsequenceStat]:
    return _parse_si_severity_any_novi(text, "insecurity", item="avoided_being_alone_with_known_person")


# ──────────────────────────────────────────────────────────────
# T102: Reporting behavior (reasons for not reporting)
# ──────────────────────────────────────────────────────────────

_REPORTING_LABELS_2019_PARTNER = [
    "lo resolvio sola",
    "tuvo muy poca importancia",
    "por miedo al agresor",
    "por verguenza",
    "piensa que era su culpa",
    "por desconocimiento",
    "el problema se termino",
    "se separo termino la relacion",
    "temor a que no la creyeran",
    "carece de recursos economicos",
    "la pareja u otra persona se lo impidio",
    "por no ser algo fisico",
    "ha acudido a otro lugar",
    "por estar enamorada",
    "por miedo a perder a sus hijos",
    "para que sus hijos no pierdan a su padre",
    "por no querer que arrestaran",
    "eran otros tiempos",
    "sucedio cuando vivia en otro pais",
    "otros motivos",
    "nc"
]

_REPORTING_LABELS_2019_OUTSIDE = [
    "tuvo muy poca importancia",
    "por miedo al agresor",
    "por verguenza",
    "piensa que era su culpa",
    "temor a que no la creyeran",
    "por desconocimiento",
    "otra persona la disuadio",
    "el problema se termino",
    "carece de recursos economicos",
    "fue a otro lugar",
    "era menor era una nina",
    "eran otros tiempos",
    "sucedio en otro pais",
    "otros motivos",
    "nc"
]

_REPORTING_LABELS_2024_PARTNER = [
    "lo resolvio sola",
    "le dio muy poca importancia",
    "por miedo al agresor",
    "por verguenza",
    "temor a que no la creyeran",
    "piensa que era su culpa",
    "por desconocimiento",
    "carece de recursos economicos",
    "se separo termino la relacion",
    "el problema se termino",
    "la pareja u otra persona se lo impidio",
    "por no ser algo fisico",
    "acudio a otro lugar",
    "por estar enamorada",
    "por miedo a perder a sus hijos",
    "para que sus hijos no pierdan a su padre",
    "por no querer que arrestaran",
    "eran otros tiempos",
    "sucedio cuando vivia en otro pais",
    "otros motivos",
    "nc"
]

_REPORTING_LABELS_2024_OUTSIDE = [
    "le dio muy poca importancia",
    "por miedo al agresor",
    "por verguenza",
    "penso que era su culpa",
    "temor a que no la creyeran",
    "era menor era una nina",
    "por desconocimiento",
    "carecia de recursos economicos",
    "fue a otro lugar",
    "otra persona la disuadio",
    "eran otros tiempos",
    "sucedio en otro pais",
    "otros motivos"
]


def parse_reporting_reasons_2019_partner(text: str) -> list[ReportingStat]:
    """Partner violence (Cap. 9): reasons for not reporting.
    Table: Motivos para no denunciar VFSEM de la pareja.
    Structure: N, % for pareja actual and parejas pasadas."""
    rows = _ordered_rows(text, 4)
    if len(rows) < len(_REPORTING_LABELS_2019_PARTNER):
        return []
    out = []
    for label, row in zip(_REPORTING_LABELS_2019_PARTNER, rows):
        # pareja actual: n, pct
        out.append(ReportingStat(
            reason=label, partner_status="current",
            sample_n=int(row[0]) if row[0] is not None else None,
            pct=row[1]
        ))
        # parejas pasadas: n, pct
        out.append(ReportingStat(
            reason=label, partner_status="past",
            sample_n=int(row[2]) if row[2] is not None else None,
            pct=row[3]
        ))
    return out


def parse_reporting_reasons_2019_outside_partner(text: str) -> list[ReportingStat]:
    """Outside-partner sexual violence (Cap. 16.8.1.5): reasons for not reporting.
    Table: Motivos para no denunciar.
    Structure: N, % for 'violencia sexual' and 'violacion' columns."""
    rows = _ordered_rows(text, 4)
    if len(rows) < len(_REPORTING_LABELS_2019_OUTSIDE):
        return []
    out = []
    for label, row in zip(_REPORTING_LABELS_2019_OUTSIDE, rows):
        # all sexual violence: n, pct
        out.append(ReportingStat(
            reason=label, violence_type="any",
            sample_n=int(row[0]) if row[0] is not None else None,
            pct=row[1]
        ))
        # rape only: n, pct
        out.append(ReportingStat(
            reason=label, violence_type="rape",
            sample_n=int(row[2]) if row[2] is not None else None,
            pct=row[3]
        ))
    return out


def parse_reporting_reasons_2024_partner(text: str) -> list[ReportingStat]:
    """Partner violence (Cap. 9.1.4): reasons for not reporting.
    Tabla 9.7: Motivos para no denunciar VFSEM de la pareja.
    Structure: %, N (population estimate) for pareja actual, parejas pasadas, cualquier pareja."""
    rows = _ordered_rows(text, 6)
    if len(rows) < len(_REPORTING_LABELS_2024_PARTNER):
        return []
    out = []
    for label, row in zip(_REPORTING_LABELS_2024_PARTNER, rows):
        # pareja actual: pct, n
        suppressed, small_sample = row[0] is None, False
        if row[0] == 0.0 and str(row[0]).startswith("None"):
            suppressed = True
        out.append(ReportingStat(
            reason=label, partner_status="current",
            pct=row[0], population_estimate=int(row[1]) if row[1] is not None else None,
            suppressed=suppressed, small_sample=small_sample
        ))
        # parejas pasadas: pct, n
        suppressed, small_sample = row[2] is None, False
        out.append(ReportingStat(
            reason=label, partner_status="past",
            pct=row[2], population_estimate=int(row[3]) if row[3] is not None else None,
            suppressed=suppressed, small_sample=small_sample
        ))
        # cualquier pareja: pct, n
        suppressed, small_sample = row[4] is None, False
        out.append(ReportingStat(
            reason=label, partner_status="any",
            pct=row[4], population_estimate=int(row[5]) if row[5] is not None else None,
            suppressed=suppressed, small_sample=small_sample
        ))
    return out


def parse_reporting_reasons_2024_outside_partner(text: str) -> list[ReportingStat]:
    """Outside-partner sexual violence (Cap. 16.8.1.5): reasons for not reporting.
    Tabla 16.30: Motivos para no denunciar.
    Structure: % only for violaciones, intentos, otras formas (no N column).
    Uses suppression (.) and small-sample (¨) markers."""
    rows = _ordered_rows(text, 3)
    if len(rows) < len(_REPORTING_LABELS_2024_OUTSIDE):
        return []
    out = []
    for label, row in zip(_REPORTING_LABELS_2024_OUTSIDE, rows):
        # violaciones: %
        out.append(ReportingStat(
            reason=label, violence_type="rape",
            pct=row[0], suppressed=row[0] is None, small_sample=False
        ))
        # intentos: %
        out.append(ReportingStat(
            reason=label, violence_type="attempted_rape",
            pct=row[1], suppressed=row[1] is None, small_sample=False
        ))
        # otras formas: %
        out.append(ReportingStat(
            reason=label, violence_type="other",
            pct=row[2], suppressed=row[2] is None, small_sample=False
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
            frequency = self._parse_frequency(pdf, chapter_start)
            participants = self._parse_participants(pdf, chapter_start)
            consequences = self._parse_consequences(pdf, chapter_start)
            reporting = self._parse_reporting(pdf, chapter_start)
        return MacroencuestaReport(
            wave_year=2019, sample_size=self.SAMPLE_SIZE,
            prevalence=prevalence, relationship=relationship,
            frequency=frequency, participants=participants, consequences=consequences,
            reporting=reporting,
            source_document=self.source,
            source_table=("p.154 (prevalencia), p.159 (vínculo con el agresor, Tabla II), "
                          "p.159-160 (frecuencia), p.161 (agresiones sexuales en grupo), "
                          "p.162-166 y 175-178 (consecuencias, T106)"),
            notes=(
                "Relationship-to-perpetrator pooled across all severities (rape through "
                "non-penetrative touching) -- 2019 questionnaire couldn't ask it per severity "
                "tier, unlike 2024 (see report's own text, p.158). Consequences (T106): 2019 "
                "only distinguishes 'any severity' vs. 'rape' (no attempted-rape/other tier, "
                "unlike 2024's full breakout) -- comparisons across waves should use the "
                "'any'/'rape' columns only. No published confidence intervals (added starting "
                "2024, see V47)."
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

    def _parse_frequency(self, pdf, chapter_start: int) -> list[FrequencyStat]:
        located = _locate_page(pdf, ["FRECUENCIA (1) DE LA VIOLENCIA SEXUAL"], start=chapter_start)
        if located is None:
            print("  ⚠ 2019: could not locate frequency tables (16.5)", file=sys.stderr)
            return []
        idx, _ = located
        out = parse_frequency_2019(_page_window_text(pdf, idx, n_pages=1))
        if len(out) < 10:
            print(f"  ⚠ 2019: frequency tables only found {len(out)}/10 rows", file=sys.stderr)
        return out

    def _parse_participants(self, pdf, chapter_start: int) -> list[ParticipantStat]:
        located = _locate_page(pdf, ["AGRESIONES SEXUALES EN GRUPO"], start=chapter_start)
        if located is None:
            print("  ⚠ 2019: could not locate group-aggression table (16.8)", file=sys.stderr)
            return []
        idx, _ = located
        out = parse_participants_2019(_page_window_text(pdf, idx, n_pages=1))
        if len(out) < 6:
            print(f"  ⚠ 2019: group-aggression table only found {len(out)}/6 cells", file=sys.stderr)
        return out

    def _parse_consequences(self, pdf, chapter_start: int) -> list[ConsequenceStat]:
        out = []
        # "Sí, alguna lesión" (the injuries headline row) is unique in the
        # document and anchors the 5-page run (injuries through substance
        # use) that follows it -- each parse_*_2019 function below does its
        # own internal _section() scoping within that shared block.
        located = _locate_page(pdf, ["ALGUNA LESION"], start=chapter_start)
        if located is None:
            print("  ⚠ 2019: could not locate injuries-through-substance-use consequence tables", file=sys.stderr)
        else:
            idx, _ = located
            block = _page_window_text(pdf, idx, n_pages=5)
            out += parse_injuries_2019(block)
            out += parse_medical_care_2019(block)
            out += parse_psychological_2019(block)
            out += parse_disability_2019(block)
            out += parse_work_absence_2019(block)
            out += parse_substance_use_2019(block)

        located2 = _locate_page(pdf, ["ESTADO DE SALUD AUTOPERCIBIDO EN LOS 12 MESES"], start=chapter_start)
        if located2 is None:
            print("  ⚠ 2019: could not locate self-perceived-health/suicidal-ideation tables", file=sys.stderr)
        else:
            idx2, _ = located2
            block2 = _page_window_text(pdf, idx2, n_pages=4)
            out += parse_self_perceived_health_2019(block2)
            out += parse_suicidal_ideation_2019(block2)
        return out

    def _parse_reporting(self, pdf, chapter_start: int) -> list[ReportingStat]:
        out = []
        # Chapter 9: Partner violence reporting reasons (page 109)
        located = _locate_page(pdf, ["CAPITULO 9", "DENUNCIA"], start=0)
        if located is None:
            print("  ⚠ 2019: could not locate Chapter 9 (partner violence)", file=sys.stderr)
        else:
            idx, _ = located
            reporting_text = _page_window_text(pdf, idx, n_pages=2)
            located_reason = _locate_page(pdf, ["MOTIVOS PARA NO DENUNCIAR", "LO RESOLVIO"], start=idx)
            if located_reason:
                idx_reason, _ = located_reason
                reason_text = _page_window_text(pdf, idx_reason, n_pages=1)
                out += parse_reporting_reasons_2019_partner(reason_text)

        # Chapter 16: Outside-partner sexual violence reporting reasons (page 169)
        located2 = _locate_page(pdf, ["MOTIVOS PARA NO DENUNCIAR", "VIOLENCIA SEXUAL FUERA"], start=chapter_start)
        if located2 is None:
            print("  ⚠ 2019: could not locate Chapter 16.8.1.5 (outside-partner reporting reasons)", file=sys.stderr)
        else:
            idx2, _ = located2
            reason_text2 = _page_window_text(pdf, idx2, n_pages=1)
            out += parse_reporting_reasons_2019_outside_partner(reason_text2)
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
            frequency = self._parse_frequency(pdf)
            participants = self._parse_participants(pdf)
            consequences = self._parse_consequences(pdf)
            reporting = self._parse_reporting(pdf)
        return MacroencuestaReport(
            wave_year=2024, sample_size=sample_size,
            prevalence=prevalence, relationship=relationship,
            frequency=frequency, participants=participants, consequences=consequences,
            reporting=reporting,
            source_document=self.source,
            source_table=("Tabla 16.1/16.2 (prevalencia), Tabla 16.16/16.17 (frecuencia), "
                          "Tabla 16.18 (más de una persona agresora), Tabla 16.21 (vínculo con el agresor), "
                          "Tabla 16.46-16.56/16.59/16.62/16.71-16.72 (consecuencias, T106)"),
            notes=(
                "Consequences (T106): first wave to break every category out by severity tier "
                "(rape/attempted_rape/other), not just any/rape like 2019 -- see V47 on wave-"
                "comparability. Adds one injury-type item ('other_physical_injury') with no 2019 "
                "equivalent. Insecurity perception (avoided streets/avoided being alone with a "
                "known person) is 2024-only -- no 2019 equivalent question. Suicidal-ideation and "
                "self-perceived-health tables both carry a 'no_violence' comparison column "
                "(women who reported no sexual violence), asked before the violence questions to "
                "avoid priming -- 2019 has the same comparison column for self-perceived health "
                "but not for suicidal ideation."
            ),
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

    def _parse_frequency(self, pdf) -> list[FrequencyStat]:
        located = _locate_page(pdf, ["TABLA 16.16 DISTRIBUCION"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 16.16 (frequency)", file=sys.stderr)
            return []
        idx, _ = located
        out = parse_frequency_2024(_page_window_text(pdf, idx, n_pages=2))
        if len(out) < 30:
            print(f"  ⚠ 2024: Tabla 16.16/16.17 only found {len(out)}/30 cells", file=sys.stderr)
        return out

    def _parse_participants(self, pdf) -> list[ParticipantStat]:
        located = _locate_page(pdf, ["TABLA 16.18 DISTRIBUCION"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 16.18 (more than one perpetrator)", file=sys.stderr)
            return []
        idx, _ = located
        out = parse_participants_2024(_page_window_text(pdf, idx, n_pages=1))
        if len(out) < 12:
            print(f"  ⚠ 2024: Tabla 16.18 only found {len(out)}/12 cells", file=sys.stderr)
        return out

    def _parse_consequences(self, pdf) -> list[ConsequenceStat]:
        out = []
        located = _locate_page(pdf, ["TABLA 16.46"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 16.46 (consequences block, injuries-work_absence)", file=sys.stderr)
        else:
            idx, _ = located
            # Tabla 16.46 through Tabla 16.56 (plus the start of the 16.9.7
            # section used as 16.56's end marker) span pages 290-300 of the
            # 2024 report -- an 11-page window covers all of them, each
            # scoped to its own table via _section() so a neighboring
            # table's rows can't leak in (see _section's own docstring on
            # why markers include a table's title text, not just "Tabla
            # 16.NN" -- that bare form collides with a parenthetical prose
            # citation like "(Tabla 16.46)." appearing earlier on the page).
            # A 9-page window cut off before Tabla 16.56's actual table (only
            # its prose citation fit), so parse_work_absence_2024's _section
            # call couldn't find its start marker, fell back to the
            # unscoped full block, and _find_si_ic_block silently picked up
            # Tabla 16.46's (injuries) Sí/IC numbers instead.
            block = _page_window_text(pdf, idx, n_pages=11)
            out += parse_injuries_2024(_section(block, "Tabla 16.46 Lesiones a lo largo", "Tabla 16.48 Tipos de lesiones"))
            out += parse_injury_types_2024(_section(block, "Tabla 16.48 Tipos de lesiones", "Tabla 16.49 Asistencia sanitaria"))
            out += parse_medical_care_2024(_section(block, "Tabla 16.49 Asistencia sanitaria", "Tabla 16.50 Consecuencias"))
            out += parse_psychological_2024(_section(block, "Tabla 16.50 Consecuencias", "Tabla 16.51 Consecuencias"))
            out += parse_psychological_by_severity_2024(_section(block, "Tabla 16.51 Consecuencias", "Tabla 16.52 Consecuencias"))
            out += parse_psychological_types_2024(_section(block, "Tabla 16.52 Consecuencias", "Tabla 16.53 Consumo"))
            out += parse_substance_use_2024(_section(block, "Tabla 16.53 Consumo", "Tabla 16.54 Consumo"))
            out += parse_substance_use_types_2024(_section(block, "Tabla 16.54 Consumo", "Tabla 16.55 Discapacidad"))
            out += parse_disability_2024(_section(block, "Tabla 16.55 Discapacidad", "Tabla 16.56 Absentismo"))
            out += parse_work_absence_2024(_section(block, "Tabla 16.56 Absentismo", "16.9.7"))

        for keywords, parser, label in (
            (["TABLA 16.59"], parse_self_perceived_health_2024, "Tabla 16.59 (self-perceived health)"),
            (["TABLA 16.62"], parse_suicidal_ideation_2024, "Tabla 16.62 (suicidal ideation)"),
            (["TABLA 16.71"], parse_insecurity_streets_2024, "Tabla 16.71 (insecurity: avoided streets)"),
            (["TABLA 16.72"], parse_insecurity_known_person_2024, "Tabla 16.72 (insecurity: avoided known person)"),
        ):
            located_t = _locate_page(pdf, keywords)
            if located_t is None:
                print(f"  ⚠ 2024: could not locate {label}", file=sys.stderr)
                continue
            idx_t, _ = located_t
            out += parser(_page_window_text(pdf, idx_t, n_pages=2))
        return out

    def _parse_reporting(self, pdf) -> list[ReportingStat]:
        out = []
        # Chapter 9: Partner violence reporting reasons (Tabla 9.7)
        # Use "LO RESOLVIO SOLA" (first data row) as unique anchor since it's not in other tables
        located = _locate_page(pdf, ["LO RESOLVIO SOLA"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 9.7 (partner violence reporting reasons)", file=sys.stderr)
        else:
            idx, _ = located
            reporting_text = _page_window_text(pdf, idx, n_pages=1)
            out += parse_reporting_reasons_2024_partner(reporting_text)

        # Chapter 16: Outside-partner sexual violence reporting reasons (Tabla 16.30)
        # Use unique anchor from the table header
        located2 = _locate_page(pdf, ["TABLA 16.30", "VIOLACIONES"])
        if located2 is None:
            print("  ⚠ 2024: could not locate Tabla 16.30 (outside-partner reporting reasons)", file=sys.stderr)
        else:
            idx2, _ = located2
            reporting_text2 = _page_window_text(pdf, idx2, n_pages=1)
            out += parse_reporting_reasons_2024_outside_partner(reporting_text2)
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
