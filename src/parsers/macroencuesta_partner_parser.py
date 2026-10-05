"""Macroencuesta de Violencia contra la Mujer -- partner-violence prevalence (T100).

Extracts prevalence of violence BY A PARTNER (physical, sexual, rape-by-partner,
physical and/or sexual combined) for lifetime / last 4 years / last 12 months,
split by partner status (`current` / `past` / `any` / `all_women`) -- the
partner-violence mirror of what `macroencuesta_parser.py` (T99) extracts for
violence outside the partner. Output: `data/raw/macroencuesta_partner_2019-2024.json`.

Where the tables live (page-located by content, never hardcoded):
  2024: Cap. 1 Tablas 1.1/1.19/1.20 (physical), Cap. 2 Tablas 2.1/2.18/2.19
        (sexual + violación), Cap. 3 Tabla 3.1 (physical and/or sexual, all
        three timeframes on one page). One shape: `Sí <pct> <N> <pct> <N> <pct>
        <pct> <N>` + `IC 95% (lo - hi) x4`.
  2019: Cap. 1 (physical), Cap. 2 (sexual) and a 3-row violación table at the
        end of Cap. 2 have the sample-count shape `Sí <N> <pct> x4 <estimate>`;
        NO confidence intervals. **2019's Cap. 3 is psychological violence, not
        physical-and/or-sexual** -- the 2019 combined figures live in Cap. 7
        ("Combinaciones de la violencia en la pareja", "Resumen prevalencias").

Column semantics (same in both waves) -- the four denominators differ, so they
are separate rows (`partner_status`), never one blended number:
  current    % of women with a current partner         (+ N)
  past       % of women with past partners             (+ N)
  any        % of women who ever had a partner         (2024 prints no N here)
  all_women  % of all women 16+ resident in Spain      (+ N, the population estimate)

2019 vs 2024 comparability (V47): the 2024 methodology changed; a 2019->2024
delta mixes measurement and real change. 2019 has no CIs (`ci_*` stay None).

Usage:
    uv run python src/parsers/macroencuesta_partner_parser.py --pdf-dir data/sources/
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import pdfplumber
    from pydantic import BaseModel
except ImportError:
    sys.exit("Install: pip install pdfplumber pydantic")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from macroencuesta_parser import (  # noqa: E402
    Macroencuesta2019Parser, Macroencuesta2024Parser,
    _locate_page, _page_window_text, infer_year,
)
from utils import parse_es_number  # noqa: E402

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "data" / "raw"

# Unlike macroencuesta_parser._NUM_RE (thousands-grouped only), accepts bare
# 4+ digit counts such as 2019's "1048" sample N.
_NUM_RE = re.compile(r"\d+(?:\.\d{3})*(?:,\d+)?")

PARTNER_STATUSES = ["current", "past", "any", "all_women"]
TIMEFRAMES = ["lifetime", "last_4_years", "last_12_months"]


class PartnerPrevalenceStat(BaseModel):
    violence_type: str   # 'physical' | 'sexual' | 'rape' | 'physical_or_sexual'
    timeframe: str       # 'lifetime' | 'last_4_years' | 'last_12_months'
    partner_status: str  # 'current' | 'past' | 'any' | 'all_women' (denominator, see module docstring)
    pct: float | None = None
    population_estimate: int | None = None  # 2024 only; None for 'any' (not printed)
    ci_low: float | None = None
    ci_high: float | None = None
    sample_n: int | None = None             # 2019 only -- raw survey N


class PartnerReport(BaseModel):
    wave_year: int
    sample_size: int | None = None
    prevalence: list[PartnerPrevalenceStat] = []
    source_document: str
    source_table: str = ""
    notes: str = ""


class PartnerDataset(BaseModel):
    reports: list[PartnerReport]


# ──────────────────────────────────────────────────────────────
# Pure text -> stats functions (unit-tested against literal page text)
# ──────────────────────────────────────────────────────────────

def _int(v: float | None) -> int | None:
    return int(v) if v is not None else None


def _after(lines: list[str], marker: str) -> int:
    """Index of the first line containing `marker` (case-sensitive), or -1."""
    for i, l in enumerate(lines):
        if marker in l:
            return i
    return -1


def parse_partner_block_2024(text: str, violence_type: str, timeframe: str,
                             start_after: str) -> list[PartnerPrevalenceStat]:
    """First `Sí` row after the first line containing `start_after`:
    `Sí pct_cur N_cur pct_past N_past pct_any pct_all N_all` + the CI line."""
    lines = text.splitlines()
    start = _after(lines, start_after)
    if start < 0:
        return []
    for i in range(start, len(lines)):
        l = lines[i].strip()
        if not (l == "Sí" or l.startswith("Sí ")):
            continue
        nums = [parse_es_number(t) for t in _NUM_RE.findall(l[2:])]
        if len(nums) != 7:
            return []
        ci = []
        if i + 1 < len(lines) and lines[i + 1].strip().startswith("IC 95%"):
            ci = [(parse_es_number(lo), parse_es_number(hi))
                  for lo, hi in re.findall(r"\(([\d.,]+)\s*[-–]\s*([\d.,]+)\)", lines[i + 1])]
        cur, past, any_, tot = ((nums[0], nums[1]), (nums[2], nums[3]), (nums[4], None), (nums[5], nums[6]))
        out = []
        for k, (status, (pct, n)) in enumerate(zip(PARTNER_STATUSES, (cur, past, any_, tot))):
            stat = PartnerPrevalenceStat(violence_type=violence_type, timeframe=timeframe,
                                         partner_status=status, pct=pct, population_estimate=_int(n))
            if k < len(ci):
                stat.ci_low, stat.ci_high = ci[k]
            out.append(stat)
        return out
    return []


def _stats_from_counts_2019(nums: list[float], violence_type: str, timeframe: str) -> list[PartnerPrevalenceStat]:
    """`N pct N pct N pct N pct estimate` -> four rows (+ population estimate on all_women)."""
    out = []
    for k, status in enumerate(PARTNER_STATUSES):
        out.append(PartnerPrevalenceStat(
            violence_type=violence_type, timeframe=timeframe, partner_status=status,
            sample_n=_int(nums[2 * k]), pct=nums[2 * k + 1],
            population_estimate=_int(nums[8]) if status == "all_women" else None,
        ))
    return out


def parse_partner_block_2019(text: str, violence_type: str, timeframe: str,
                             start_after: str | None = None) -> list[PartnerPrevalenceStat]:
    """First `Sí <9 numbers>` row after `start_after` (2019 prevalence tables)."""
    lines = text.splitlines()
    start = max(_after(lines, start_after), 0) if start_after else 0
    for l in lines[start:]:
        l = l.strip()
        if l.startswith("Sí "):
            nums = [parse_es_number(t) for t in _NUM_RE.findall(l[2:])]
            return _stats_from_counts_2019(nums, violence_type, timeframe) if len(nums) == 9 else []
    return []


def parse_rape_table_2019(text: str) -> list[PartnerPrevalenceStat]:
    """2019's 'Violación (ítems 1 a 4)' table: three rows (lifetime, 4y, 12m),
    each 9 numbers. The lifetime row's label wraps across the lines around the
    numbers, so rows are taken positionally: the first three lines after the
    title carrying exactly 9 numbers."""
    lines = text.splitlines()
    start = _after(lines, "Violación (ítems 1 a 4)")
    if start < 0:
        return []
    rows = []
    for l in lines[start + 1:]:
        # drop the 'Últimos 4 años' / 'Últimos 12 meses' labels' own digits
        l = re.sub(r"Últimos \d+ (?:años|meses)", "", l)
        nums = [parse_es_number(t) for t in _NUM_RE.findall(l)]
        if len(nums) == 9:
            rows.append(nums)
        if len(rows) == 3:
            break
    if len(rows) < 3:
        return []
    out = []
    for timeframe, nums in zip(TIMEFRAMES, rows):
        out += _stats_from_counts_2019(nums, "rape", timeframe)
    return out


def parse_combined_row_2019(text: str, timeframe: str) -> list[PartnerPrevalenceStat]:
    """Cap. 7 summary table's `3. Física y/o sexual` row. The label wraps in
    the lifetime/4-year tables (numbers on the line between 'Física y/o' and
    'sexual') but not in the 12-month one, so: from the label line, the first
    line with 9 numbers once the leading '3.' is stripped."""
    lines = text.splitlines()
    start = _after(lines, "3. Física y/o")
    if start < 0:
        return []
    for l in lines[start:start + 3]:
        nums = [parse_es_number(t) for t in _NUM_RE.findall(re.sub(r"^\s*3\.", "", l))]
        if len(nums) == 9:
            return _stats_from_counts_2019(nums, "physical_or_sexual", timeframe)
    return []


# ──────────────────────────────────────────────────────────────
# Wave parsers (page-location only; hand text to the pure functions)
# ──────────────────────────────────────────────────────────────

_VIOLENCE_2024 = [
    # (violence_type, timeframe, table title keyword, start_after label)
    ("physical", "lifetime", "TABLA 1.1 PREVALENCIA", "Tabla 1.1 "),
    ("physical", "last_12_months", "TABLA 1.19 PREVALENCIA", "Tabla 1.19"),
    ("physical", "last_4_years", "TABLA 1.20 PREVALENCIA", "Tabla 1.20"),
    ("sexual", "lifetime", "TABLA 2.1 PREVALENCIA", "Violencia sexual de la pareja"),
    ("rape", "lifetime", "TABLA 2.1 PREVALENCIA", "Violación de la pareja"),
    ("sexual", "last_12_months", "TABLA 2.18 PREVALENCIA", "Violencia sexual de la pareja en los"),
    ("rape", "last_12_months", "TABLA 2.18 PREVALENCIA", "Violación de la pareja en los"),
    ("sexual", "last_4_years", "TABLA 2.19 PREVALENCIA", "Violencia sexual de la pareja en los"),
    ("rape", "last_4_years", "TABLA 2.19 PREVALENCIA", "Violación de la pareja en los"),
]
_CHAPTER_2024 = {"1": "CAPITULO 1. VIOLENCIA FISICA EN LA PAREJA",
                 "2": "CAPITULO 2. VIOLENCIA SEXUAL EN LA PAREJA",
                 "3": "CAPITULO 3. VIOLENCIA FISICA Y/O SEXUAL EN LA PAREJA"}


class PartnerMacroencuesta2024Parser:
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.source = pdf_path.name

    def parse(self) -> PartnerReport:
        with pdfplumber.open(self.pdf_path) as pdf:
            sample_size = Macroencuesta2024Parser._parse_sample_size(pdf)
            out: list[PartnerPrevalenceStat] = []
            for vtype, tf, keyword, label in _VIOLENCE_2024:
                chapter = _CHAPTER_2024[keyword.split()[1].split(".")[0]]
                out += self._table(pdf, chapter, keyword, vtype, tf, label)
            out += self._combined(pdf)
        return PartnerReport(
            wave_year=2024, sample_size=sample_size, prevalence=out, source_document=self.source,
            source_table="Tablas 1.1, 1.19, 1.20 (física), 2.1, 2.18, 2.19 (sexual / violación), 3.1 (física y/o sexual)",
        )

    @staticmethod
    def _table(pdf, chapter: str, keyword: str, vtype: str, tf: str, label: str) -> list[PartnerPrevalenceStat]:
        # V48: anchor on the chapter's running header AND the table title; a
        # located page must carry both so a lookalike table in another chapter
        # (physical vs sexual vs outside-partner) can't be picked up.
        located = _locate_page(pdf, [chapter, keyword])
        if located is None:
            print(f"  ⚠ 2024: could not locate {keyword}", file=sys.stderr)
            return []
        out = parse_partner_block_2024(_page_window_text(pdf, located[0], n_pages=1), vtype, tf, label)
        if not out:
            print(f"  ⚠ 2024: {keyword} ({vtype}/{tf}) 'Sí' row not parsed", file=sys.stderr)
        return out

    @staticmethod
    def _combined(pdf) -> list[PartnerPrevalenceStat]:
        located = _locate_page(pdf, [_CHAPTER_2024["3"], "TABLA 3.1 PREVALENCIA"])
        if located is None:
            print("  ⚠ 2024: could not locate Tabla 3.1", file=sys.stderr)
            return []
        text = _page_window_text(pdf, located[0], n_pages=1)
        out = []
        for tf, label in (("lifetime", "A lo largo de la vida"), ("last_4_years", "Últimos 4 años"),
                          ("last_12_months", "Últimos 12 meses")):
            block = parse_partner_block_2024(text, "physical_or_sexual", tf, label)
            if not block:
                print(f"  ⚠ 2024: Tabla 3.1 {tf} block not parsed", file=sys.stderr)
            out += block
        return out


_TF_LABELS_2019 = {"lifetime": "A lo largo de la vida", "last_4_years": "Últimos 4 años",
                   "last_12_months": "Últimos 12 meses"}


class PartnerMacroencuesta2019Parser:
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.source = pdf_path.name

    def parse(self) -> PartnerReport:
        with pdfplumber.open(self.pdf_path) as pdf:
            # TOC lists "CAPÍTULO 1 ___ 14" on one line, so the newline-joined
            # title below only matches the real chapter-opening pages.
            c1 = self._start(pdf, "CAPITULO 1\nVIOLENCIA FISICA EN LA PAREJA")
            c2 = self._start(pdf, "CAPITULO 2\nVIOLENCIA SEXUAL EN LA PAREJA", c1)
            c3 = self._start(pdf, "CAPITULO 3\nVIOLENCIA PSICOLOGICA", c2)  # end bound for Cap. 2
            c7 = self._start(pdf, "CAPITULO 7\nCOMBINACIONES DE LA VIOLENCIA EN LA PAREJA", c3)
            out: list[PartnerPrevalenceStat] = []
            out += self._three_timeframes(pdf, "physical", c1, c2,
                                          "VIOLENCIA FISICA DE ALGUNA PAREJA (ACTUAL O PASADA)")
            out += self._three_timeframes(pdf, "sexual", c2, c3,
                                          "VIOLENCIA SEXUAL DE ALGUNA PAREJA (ACTUAL O PASADA)")
            out += self._rape(pdf, c2, c3)
            out += self._combined(pdf, c7)
        return PartnerReport(
            wave_year=2019, sample_size=Macroencuesta2019Parser.SAMPLE_SIZE, prevalence=out,
            source_document=self.source,
            source_table="Cap. 1 (física), Cap. 2 (sexual + tabla de violación, ítems 1-4), Cap. 7 'Resumen prevalencias' (física y/o sexual)",
            notes=(
                "No published confidence intervals in 2019. Physical-and/or-sexual comes from Cap. 7 "
                "(2019's Cap. 3 is psychological violence). 'rape' = items 1-4 of the sexual screener. "
                "'any'/'all_women' rows differ only in denominator (ever-partnered vs all women 16+)."
            ),
        )

    @staticmethod
    def _start(pdf, keyword: str, start: int = 0) -> int:
        located = _locate_page(pdf, [keyword], start=start)
        if located is None:
            print(f"  ⚠ 2019: could not locate chapter start {keyword!r}", file=sys.stderr)
            return start
        return located[0]

    def _three_timeframes(self, pdf, vtype: str, lo: int, hi: int, title: str) -> list[PartnerPrevalenceStat]:
        located = _locate_page(pdf, [title], start=lo)
        if located is None or located[0] >= max(hi, lo + 1):
            print(f"  ⚠ 2019: could not locate {vtype} prevalence table inside its chapter", file=sys.stderr)
            return []
        text = _page_window_text(pdf, located[0], n_pages=1)
        out = []
        for tf, label in _TF_LABELS_2019.items():
            block = parse_partner_block_2019(text, vtype, tf, start_after=label)
            if not block:
                print(f"  ⚠ 2019: {vtype}/{tf} block not parsed", file=sys.stderr)
            out += block
        return out

    def _rape(self, pdf, lo: int, hi: int) -> list[PartnerPrevalenceStat]:
        located = _locate_page(pdf, ["VIOLACION (ITEMS 1 A 4) DE ALGUNA PAREJA"], start=lo)
        if located is None or located[0] >= hi:
            print("  ⚠ 2019: could not locate violación table inside Cap. 2", file=sys.stderr)
            return []
        out = parse_rape_table_2019(_page_window_text(pdf, located[0], n_pages=1))
        if len(out) != 12:
            print(f"  ⚠ 2019: violación table gave {len(out)}/12 rows", file=sys.stderr)
        return out

    def _combined(self, pdf, c7: int) -> list[PartnerPrevalenceStat]:
        out = []
        for tf, phrase in (("lifetime", "A LO LARGO DE LA VIDA"), ("last_4_years", "EN LOS ULTIMOS 4 ANOS"),
                           ("last_12_months", "EN LOS ULTIMOS 12 MESES")):
            located = _locate_page(pdf, [f"RESUMEN PREVALENCIAS DE VIOLENCIA DE ALGUNA PAREJA (ACTUAL O PASADA) {phrase}"], start=c7)
            if located is None:
                print(f"  ⚠ 2019: could not locate Cap. 7 summary ({tf})", file=sys.stderr)
                continue
            block = parse_combined_row_2019(_page_window_text(pdf, located[0], n_pages=1), tf)
            if not block:
                print(f"  ⚠ 2019: Cap. 7 combined row ({tf}) not parsed", file=sys.stderr)
            out += block
        return out


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

_PARSERS = {2019: PartnerMacroencuesta2019Parser, 2024: PartnerMacroencuesta2024Parser}


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
            print(f"  SKIP {pdf_path.name} (unsupported year {year})", file=sys.stderr)
            continue
        print(f"  Parsing Macroencuesta partner violence {year}: {pdf_path.name}")
        reports.append(_PARSERS[year](pdf_path).parse())

    if not reports:
        sys.exit("No reports parsed.")
    reports.sort(key=lambda r: r.wave_year)
    years = [r.wave_year for r in reports]
    stem = f"{years[0]}" if years[0] == years[-1] else f"{years[0]}-{years[-1]}"
    out = args.out_dir / f"macroencuesta_partner_{stem}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(PartnerDataset(reports=reports).model_dump_json(indent=2), encoding="utf-8")
    for r in reports:
        print(f"  {r.wave_year}: {len(r.prevalence)} stats")
    print(f"  -> {out} ({len(reports)} report(s))")


if __name__ == "__main__":
    main()
