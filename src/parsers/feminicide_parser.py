"""Delegación del Gobierno Feminicide Report Parser (T19/T20).

Parses the annual "ficha" PDF series published by the Delegación del
Gobierno contra la Violencia de Género (Ministerio de Igualdad):
"Mujeres Víctimas Mortales por Violencia de Género en España a manos de
sus parejas o exparejas", one PDF per year, 2003-present.

Two source-format eras exist:
  - 2006-present: numbered-table format (Tabla 2.1-2.4, 3.1-3.4). This
    parser extracts headline totals plus Tables 2.1 (region), 2.2 (age),
    2.3 (country of birth), 2.4 (relationship/cohabitation), 3.1 (prior
    complaint / process continuation), 3.2 (protective measures requested
    and adopted), 3.3 (restraining order breach), 3.4 (perpetrator suicide
    attempt).
  - 2003-2005: an older "ficha resumen" layout (DENUNCIA / MEDIDAS DE
    PROTECCIÓN / QUEBRANTAMIENTO chart-style page) with a structurally
    different, harder-to-parse table. Only year + source metadata are
    extracted for these three years; all breakdowns are left null.

Region/age/nationality/relationship *labels* are matched against fixed,
order-stable vocabularies (confirmed identical ordering across every
sampled year, 2011-2026) rather than split out of the source text, since
category names run together on one line with no reliable per-item
delimiter (e.g. "Andalucía Aragón Asturias, Principado de Balears,
Illes..."); only the (unambiguous, whitespace-separated) numeric values
are actually parsed out of the PDF text.

Usage:
    python src/parsers/feminicide_parser.py --pdf-dir data/sources/
    python src/parsers/feminicide_parser.py --pdf data/sources/VMujeres_2024.pdf

Output: one consolidated data/raw/feminicidios_delegacion_{min}-{max}.json,
Pydantic-validated FeminicideDataset -> FeminicideReport (one per year).
source_document/source_page/confidence/verified live once per report, not
per category row (matches mir_parser.py's MIRReport shape).
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from pydantic import BaseModel
except ImportError:
    sys.exit("Install: uv add pydantic")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import extract_text

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "data" / "raw"

# Fixed, order-stable vocabularies -- confirmed identical ordering in every
# sampled year 2011-2026 (2019 and 2024 cross-checked in full).
REGIONS = [
    "Andalucía", "Aragón", "Asturias, Principado de", "Balears, Illes",
    "Canarias", "Cantabria", "Castilla y León", "Castilla-La Mancha",
    "Cataluña", "Comunitat Valenciana", "Extremadura", "Galicia",
    "Madrid, Comunidad de", "Murcia, Región de",
    "Navarra, Comunidad Foral de", "País Vasco", "Rioja, La", "Ceuta",
    "Melilla",
]
AGE_BRACKETS = [
    "13 a 14 años", "15 a 17 años", "18 a 20 años", "21 a 30 años",
    "31 a 40 años", "41 a 50 años", "51 a 60 años", "61 a 70 años",
    "71 a 84 años", "85 años o más",
]
ORIGINS = ["España", "Otro país"]
RELATIONSHIP_TYPES = ["Pareja", "Expareja o pareja en fase de ruptura"]
COHABITATION = ["Convivían", "No convivían", "No consta"]

# Tables 3.1/3.2: two mini-tables back to back, TOTAL rows kept (each TOTAL is
# a distinct, meaningful count -- not a redundant grand total to drop).
PRIOR_COMPLAINT_LABELS = [
    "TOTAL víctimas por violencia de género",
    "Con una o más denuncias previas",
    "Interpuestas por la víctima",
    "Interpuestas por otros",
    "Sin denuncias previas",
    "TOTAL casos con una o más denuncias previas",
    "Proceso iniciado",
    "Continuación del proceso por parte de la víctima",
    "No continuación del proceso",
    "Proceso no iniciado",
]
PROTECTIVE_MEASURES_LABELS = [
    "TOTAL casos con una o más denuncias previas",
    "Con medidas solicitadas por la víctima",
    "Con medidas solicitadas por otros",
    "Existían medidas de oficio",
    "No se solicitaron medidas",
    "TOTAL casos con medidas adoptadas",
    "Vigentes",
    "No vigentes",
    "Por renuncia de la víctima",
    "Por final periodo vigencia",
    "Por otros motivos",
]
RESTRAINING_ORDER_BREACH_LABELS = [
    "TOTAL", "Sin oposición de la víctima", "Con oposición de la víctima", "No consta",
]
SUICIDE_ATTEMPT_LABELS = [
    "TOTAL", "Suicidio consumado", "Tentativa no consumada", "No hubo tentativa",
]

# 2003-2005 legacy "ficha resumen" format (T63). Confirmed identical section
# order/counts across all 3 sampled years via direct PDF-text dump: labels
# and "N.º de casos"/"% del total" numbers are clean text (just laid out
# differently from the modern "Número" tables), EXCEPT the DENUNCIA/MEDIDAS
# DE PROTECCIÓN/QUEBRANTAMIENTO block, whose figures beyond the headline
# total are chart/graphic-rendered and not recoverable as text.
LEGACY_NATIONALITY = ["España", "Otro país", "No consta"]
LEGACY_AGE_BRACKETS = [
    "<16 años", "16-17 años", "18-20 años", "21-30 años", "31-40 años",
    "41-50 años", "51-64 años", ">64 años", "No consta",
]
# Value order as printed in this layout -- reversed/reworded vs the modern
# RELATIONSHIP_TYPES/SUICIDE_ATTEMPT_LABELS vocabs, so mapped explicitly
# rather than reusing those lists' order.
_LEGACY_RELATIONSHIP_VALUE_ORDER = [
    "Expareja o pareja en fase de ruptura", "Pareja",
]
_LEGACY_SUICIDE_VALUE_ORDER = [
    "No hubo tentativa", "Tentativa no consumada", "Suicidio consumado",
]


# ──────────────────────────────────────────────────────────────
# Output schema
# ──────────────────────────────────────────────────────────────

class CategoryCount(BaseModel):
    label: str
    count: int | None = None
    pct: float | None = None


class VictimPerpCategoryCount(BaseModel):
    label: str
    victim_count: int | None = None
    victim_pct: float | None = None
    perp_count: int | None = None
    perp_pct: float | None = None


class FeminicideReport(BaseModel):
    year: int
    total_victims: int | None = None
    cumulative_total_since_2003: int | None = None
    update_date: str | None = None
    orphaned_children: int | None = None
    investigation_note: str | None = None
    regional: list[CategoryCount] = []
    age: list[VictimPerpCategoryCount] = []
    origin: list[VictimPerpCategoryCount] = []
    relationship_type: list[CategoryCount] = []
    cohabitation: list[CategoryCount] = []
    prior_complaint: list[CategoryCount] = []
    protective_measures: list[CategoryCount] = []
    restraining_order_breach: list[CategoryCount] = []
    perpetrator_suicide_attempt: list[CategoryCount] = []
    source_document: str
    source_page: int = 1
    confidence: str = "high"
    verified: bool = False
    notes: str = ""


class FeminicideDataset(BaseModel):
    reports: list[FeminicideReport]


# ──────────────────────────────────────────────────────────────
# Number extraction helpers
# ──────────────────────────────────────────────────────────────

_NUM_RE = re.compile(r"-?\d+\.?\d*")


def _numbers_after(label_pattern: str, text: str, limit: int | None = None) -> list[str]:
    """Return every numeric token found after the first match of
    `label_pattern` in `text` (up to `limit` tokens)."""
    m = re.search(label_pattern, text)
    if not m:
        return []
    nums = _NUM_RE.findall(text[m.end():])
    return nums[:limit] if limit else nums


def _slice_block(text: str, start_pattern: str, end_pattern: str | None) -> str | None:
    m1 = re.search(start_pattern, text)
    if not m1:
        return None
    start = m1.end()
    if end_pattern:
        m2 = re.search(end_pattern, text[start:])
        end = start + m2.start() if m2 else len(text)
    else:
        end = len(text)
    return text[start:end]


def _extract_simple_table(block: str, vocab: list[str]) -> list[CategoryCount]:
    """Table with a single 'Número'/'%' pair (no victim/perpetrator split)."""
    n = len(vocab) + 1  # +1 for the leading TOTAL entry
    nums = _numbers_after(r"Número", block, 2 * n)
    if len(nums) < 2 * n:
        return []
    counts, pcts = nums[:n], nums[n:2 * n]
    return [
        CategoryCount(label=label, count=int(float(c)), pct=float(p))
        for label, c, p in zip(vocab, counts[1:], pcts[1:])
    ]


def _extract_victim_perp_table(block: str, vocab: list[str]) -> list[VictimPerpCategoryCount]:
    """Table with separate 'Mujeres víctimas mortales' and 'Presuntos
    agresores' Número/% sub-blocks. Two layouts exist across report years
    (B33): 2023+ interleaves per-actor Número/% pairs (vc,vp then, after a
    'Presuntos agresores' sub-header, pc,pp); 2006-2022 instead prints both
    'Mujeres víctimas mortales'/'Presuntos agresores' as column headers
    BEFORE either actor's data, then both actors' raw counts back-to-back,
    then both actors' percentages back-to-back (vc,pc,vp,pp). Splitting on
    the position of 'Presuntos agresores' (as the 2023+ layout requires)
    lands before any numbers in the 2006-2022 layout, silently zeroing out
    victim_block and returning [] -- detect which layout this block uses
    instead of assuming the newer one."""
    n = len(vocab) + 1
    num_ms = list(re.finditer(r"Número", block))
    if not num_ms:
        return []
    perp_header_m = re.search(r"Presuntos agresores", block)
    # old layout: the perp header (if present) appears before any 'Número'
    # -- it's a column label, not a section boundary.
    old_layout = bool(perp_header_m) and perp_header_m.start() < num_ms[0].start()

    if old_layout:
        nums = _numbers_after(r"Número", block, 4 * n)
        if len(nums) < 4 * n:
            return []
        vc, pc, vp, pp = nums[0:n], nums[n:2 * n], nums[2 * n:3 * n], nums[3 * n:4 * n]
    else:
        perp_m = perp_header_m
        victim_block = block[:perp_m.start()] if perp_m else block
        perp_block = block[perp_m.start():] if perp_m else ""

        v_nums = _numbers_after(r"Número", victim_block, 2 * n)
        p_nums = _numbers_after(r"Número", perp_block, 2 * n) if perp_block else []

        if len(v_nums) < 2 * n:
            return []
        vc, vp = v_nums[:n], v_nums[n:2 * n]
        pc, pp = (p_nums[:n], p_nums[n:2 * n]) if len(p_nums) >= 2 * n else ([None] * n, [None] * n)

    out = []
    for i, label in enumerate(vocab, start=1):
        out.append(VictimPerpCategoryCount(
            label=label,
            victim_count=int(float(vc[i])),
            victim_pct=float(vp[i]),
            perp_count=int(float(pc[i])) if pc[i] is not None else None,
            perp_pct=float(pp[i]) if pp[i] is not None else None,
        ))
    return out


def _extract_flat_table(block: str, labels: list[str]) -> list[CategoryCount]:
    """Table where every 'Número'-block token maps 1:1, in order, to
    `labels` -- no leading TOTAL is dropped (used for Tables 3.1-3.4, whose
    TOTAL rows are distinct, meaningful counts, not a redundant grand total
    to discard)."""
    n = len(labels)
    nums = _numbers_after(r"Número", block, 2 * n)
    if len(nums) < 2 * n:
        return []
    counts, pcts = nums[:n], nums[n:2 * n]
    return [
        CategoryCount(label=label, count=int(float(c)), pct=float(p))
        for label, c, p in zip(labels, counts, pcts)
    ]


def _extract_relationship_table(block: str) -> tuple[list[CategoryCount], list[CategoryCount]]:
    """Table 2.4: one Número/% pair holding TOTAL+2 relationship-type values
    followed by TOTAL+3 cohabitation values, back to back."""
    n_rel, n_cohab = len(RELATIONSHIP_TYPES) + 1, len(COHABITATION) + 1
    total_n = n_rel + n_cohab
    nums = _numbers_after(r"Número", block, 2 * total_n)
    if len(nums) < 2 * total_n:
        return [], []
    counts, pcts = nums[:total_n], nums[total_n:2 * total_n]

    rel_counts, rel_pcts = counts[:n_rel], pcts[:n_rel]
    cohab_counts, cohab_pcts = counts[n_rel:], pcts[n_rel:]

    relationship = [
        CategoryCount(label=label, count=int(float(c)), pct=float(p))
        for label, c, p in zip(RELATIONSHIP_TYPES, rel_counts[1:], rel_pcts[1:])
    ]
    cohabitation = [
        CategoryCount(label=label, count=int(float(c)), pct=float(p))
        for label, c, p in zip(COHABITATION, cohab_counts[1:], cohab_pcts[1:])
    ]
    return relationship, cohabitation


# ──────────────────────────────────────────────────────────────
# Per-format parsers
# ──────────────────────────────────────────────────────────────

def _parse_modern_format(text: str, year: int, pdf_name: str) -> FeminicideReport:
    """2006-present numbered-table format."""
    region_block = _slice_block(
        text, r"Comunidad/ciudad autónoma", r"Grupo de edad")
    age_block = _slice_block(
        text, r"Grupo de edad", r"País de nacimiento")
    origin_block = _slice_block(
        text, r"País de nacimiento", r"Tipo de relación")
    relationship_block = _slice_block(
        text, r"Tipo de relación/convivencia", r"3\. Denuncias previas|Tabla 3\.1")
    prior_complaint_block = _slice_block(text, r"Tabla 3\.1", r"Tabla 3\.2")
    protective_measures_block = _slice_block(text, r"Tabla 3\.2", r"Tabla 3\.3")
    breach_block = _slice_block(text, r"Tabla 3\.3", r"Tabla 3\.4")
    suicide_attempt_block = _slice_block(text, r"Tabla 3\.4", None)

    regional = _extract_simple_table(region_block, REGIONS) if region_block else []
    age = _extract_victim_perp_table(age_block, AGE_BRACKETS) if age_block else []
    origin = _extract_victim_perp_table(origin_block, ORIGINS) if origin_block else []
    relationship_type, cohabitation = (
        _extract_relationship_table(relationship_block) if relationship_block else ([], [])
    )
    prior_complaint = (
        _extract_flat_table(prior_complaint_block, PRIOR_COMPLAINT_LABELS)
        if prior_complaint_block else []
    )
    protective_measures = (
        _extract_flat_table(protective_measures_block, PROTECTIVE_MEASURES_LABELS)
        if protective_measures_block else []
    )
    restraining_order_breach = (
        _extract_flat_table(breach_block, RESTRAINING_ORDER_BREACH_LABELS)
        if breach_block else []
    )
    perpetrator_suicide_attempt = (
        _extract_flat_table(suicide_attempt_block, SUICIDE_ATTEMPT_LABELS)
        if suicide_attempt_block else []
    )

    total_victims = None
    if region_block:
        total_nums = _numbers_after(r"Número", region_block, 1)
        if total_nums:
            total_victims = int(float(total_nums[0]))

    cum_m = re.search(
        r"TOTAL MUJERES VÍCTIMAS MORTALES \d{4} - \d{4}:\s*(\d+)", text)
    cumulative_total = int(cum_m.group(1)) if cum_m else None

    update_m = re.search(
        r"Fecha de actualización de datos:\s*\n*\s*([^\n]+)", text)
    update_date = update_m.group(1).strip() if update_m else None

    orphans_m = re.search(
        r"N\.º huérfanas/os menores de 18 años:\s*\n*\s*(-|\d+)", text)
    orphaned_children = (
        int(orphans_m.group(1)) if orphans_m and orphans_m.group(1) != "-" else None
    )

    invest_m = re.search(
        r"Casos en investigación:\s*\n*\s*([^\n]+)", text)
    investigation_note = invest_m.group(1).strip() if invest_m else None

    return FeminicideReport(
        year=year,
        total_victims=total_victims,
        cumulative_total_since_2003=cumulative_total,
        update_date=update_date,
        orphaned_children=orphaned_children,
        investigation_note=investigation_note,
        regional=regional,
        age=age,
        origin=origin,
        relationship_type=relationship_type,
        cohabitation=cohabitation,
        prior_complaint=prior_complaint,
        protective_measures=protective_measures,
        restraining_order_breach=restraining_order_breach,
        perpetrator_suicide_attempt=perpetrator_suicide_attempt,
        source_document=pdf_name,
        confidence="high",
        notes="",
    )


def _legacy_counts(block: str, n: int) -> list[int] | None:
    """First `n` integer tokens after this block's 'N.º de casos' header, or
    None if fewer than `n` are found. Percentages (comma-decimal, e.g.
    "87,3%") are deliberately never requested -- CategoryCount.pct stays
    unset for legacy rows rather than mis-tokenizing "87,3" as two ints."""
    nums = _numbers_after(r"N\.º de casos", block, n)
    if len(nums) < n:
        return None
    return [int(float(x)) for x in nums]


def _parse_legacy_format(text: str, year: int, pdf_name: str) -> FeminicideReport:
    """2003-2005 'ficha resumen' format. A direct PDF-text dump (all 3
    years) shows age/origin/regional/relationship/cohabitation breakdowns
    are present as clean label-then-number blocks, just laid out
    differently from the 2006+ numbered tables (T63). Only the DENUNCIA/
    MEDIDAS DE PROTECCIÓN/QUEBRANTAMIENTO block remains unextractable --
    its figures beyond the headline total are chart-rendered, not text."""
    victim_block = _slice_block(
        text, r"Características de las víctimas", r"Ámbito geográfico")
    geo_block = _slice_block(
        text, r"Ámbito geográfico", r"Características de los agresores")
    perp_block = _slice_block(text, r"Características de los agresores", None)

    victim_nums = _legacy_counts(victim_block, 18) if victim_block else None
    geo_nums = _legacy_counts(geo_block, 20) if geo_block else None
    perp_nums = _legacy_counts(perp_block, 16) if perp_block else None

    if not (victim_nums and geo_nums and perp_nums):
        return FeminicideReport(
            year=year,
            source_document=pdf_name,
            confidence="low",
            notes=(
                "Legacy 'ficha resumen' format (pre-2006): expected section "
                "(Características de las víctimas / Ámbito geográfico / "
                "Características de los agresores) not found or incomplete "
                "in this PDF's extracted text -- no fields extracted, see "
                "data/sources/delegacion_gobierno_femicidio.md for a "
                "manually curated headline count."
            ),
        )

    total_victims = victim_nums[0]
    total_agresores = perp_nums[0]

    # V39 gate: nationality/age/regional sub-totals must reconcile to the
    # header total before that specific block is trusted. Gated per-block
    # (not all-or-nothing) because real source PDFs have isolated, single-
    # block rounding/data-entry inconsistencies (e.g. 2004 perpetrator
    # nationality sums to 73 vs a header total of 72; 2005 perpetrator age
    # sums to 56 vs 57) alongside otherwise-clean blocks -- discarding an
    # entire year's breakdown over one bad row would lose good data (B32).
    nat_victim_ok = sum(victim_nums[1:4]) == total_victims
    nat_perp_ok = sum(perp_nums[1:4]) == total_agresores
    age_victim_ok = sum(victim_nums[4:13]) == total_victims
    age_perp_ok = sum(perp_nums[4:13]) == total_agresores
    regional_ok = sum(geo_nums[1:20]) == total_victims

    gate_failures = []
    if not nat_victim_ok:
        gate_failures.append(
            f"victim nationality sums to {sum(victim_nums[1:4])}, "
            f"expected {total_victims}")
    if not nat_perp_ok:
        gate_failures.append(
            f"perpetrator nationality sums to {sum(perp_nums[1:4])}, "
            f"expected {total_agresores}")
    if not age_victim_ok:
        gate_failures.append(
            f"victim age sums to {sum(victim_nums[4:13])}, "
            f"expected {total_victims}")
    if not age_perp_ok:
        gate_failures.append(
            f"perpetrator age sums to {sum(perp_nums[4:13])}, "
            f"expected {total_agresores}")
    if not regional_ok:
        gate_failures.append(
            f"regional sums to {sum(geo_nums[1:20])}, "
            f"expected {total_victims}")

    origin = [
        VictimPerpCategoryCount(
            label=label,
            victim_count=vc if nat_victim_ok else None,
            perp_count=pc if nat_perp_ok else None,
        )
        for label, vc, pc in zip(
            LEGACY_NATIONALITY, victim_nums[1:4], perp_nums[1:4])
    ]
    age = [
        VictimPerpCategoryCount(
            label=label,
            victim_count=vc if age_victim_ok else None,
            perp_count=pc if age_perp_ok else None,
        )
        for label, vc, pc in zip(
            LEGACY_AGE_BRACKETS, victim_nums[4:13], perp_nums[4:13])
    ]
    regional = [
        CategoryCount(label=label, count=c)
        for label, c in zip(REGIONS, geo_nums[1:20])
    ] if regional_ok else []
    cohabitation = [
        CategoryCount(label=label, count=c)
        for label, c in zip(COHABITATION, victim_nums[13:16])
    ]
    relationship_values = dict(
        zip(_LEGACY_RELATIONSHIP_VALUE_ORDER, victim_nums[16:18]))
    relationship_type = [
        CategoryCount(label=label, count=relationship_values[label])
        for label in RELATIONSHIP_TYPES
    ]
    suicide_values = dict(zip(_LEGACY_SUICIDE_VALUE_ORDER, perp_nums[13:16]))
    suicide_values["TOTAL"] = total_agresores
    perpetrator_suicide_attempt = [
        CategoryCount(label=label, count=suicide_values[label])
        for label in SUICIDE_ATTEMPT_LABELS
    ]

    update_m = re.search(
        r"Fecha de actualización de esta ficha:\s*([^\n]+)", text)
    update_date = update_m.group(1).strip() if update_m else None

    return FeminicideReport(
        year=year,
        total_victims=total_victims,
        update_date=update_date,
        regional=regional,
        age=age,
        origin=origin,
        relationship_type=relationship_type,
        cohabitation=cohabitation,
        perpetrator_suicide_attempt=perpetrator_suicide_attempt,
        source_document=pdf_name,
        confidence="low" if gate_failures else "medium",
        notes=(
            "Legacy 'ficha resumen' format (pre-2006): age/origin/regional/"
            "relationship/cohabitation extracted directly from this PDF's "
            "text (T63); prior_complaint/protective_measures/"
            "restraining_order_breach stay unset -- that block's figures "
            "are chart/graphic-rendered, not text, in this format."
        ) + (
            " V39 GATE WARNINGS (source PDF sub-total doesn't reconcile "
            "to header total for this block, value withheld): "
            + "; ".join(gate_failures) + "."
            if gate_failures else ""
        ),
    )


def parse_pdf(pdf_path: Path, year: int | None = None) -> FeminicideReport:
    """Parse one yearly Delegación feminicide PDF into a FeminicideReport."""
    year = year or infer_year(pdf_path)
    if not year:
        raise ValueError(f"Cannot infer year from filename: {pdf_path.name}")
    text = extract_text(pdf_path, timeout=30)
    if re.search(r"Tabla 2\.1", text):
        return _parse_modern_format(text, year, pdf_path.name)
    return _parse_legacy_format(text, year, pdf_path.name)


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def infer_year(pdf_path: Path) -> int | None:
    m = re.search(r"(20\d{2})", pdf_path.stem)
    return int(m.group(1)) if m else None


def write_dataset(dataset: FeminicideDataset, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(dataset.model_dump_json(indent=2), encoding="utf-8")
    print(f"  -> {out_path} ({len(dataset.reports)} report(s))")


def run_batch(pdf_paths: list[Path], out_dir: Path) -> Path:
    """Parse every PDF and write exactly one FeminicideDataset JSON file,
    named by the actual year range -- not one file per input plus a
    redundant consolidated copy."""
    by_year: dict[int, list[str]] = {}
    for pdf in pdf_paths:
        y = infer_year(pdf)
        if y:
            by_year.setdefault(y, []).append(pdf.name)
    collisions = {y: names for y, names in by_year.items() if len(names) > 1}
    if collisions:
        detail = "; ".join(f"{y}: {names}" for y, names in sorted(collisions.items()))
        raise ValueError(
            f"run_batch: multiple PDFs infer to the same year -- {detail}. "
            "Pass explicit --pdf per file instead of a mixed --pdf-dir."
        )

    reports = []
    for pdf in pdf_paths:
        year = infer_year(pdf)
        if not year:
            print(f"  SKIP {pdf.name} (cannot infer year)")
            continue
        print(f"  Parsing {year}: {pdf.name}")
        reports.append(parse_pdf(pdf, year))

    reports.sort(key=lambda r: r.year)
    years = [r.year for r in reports]
    stem = f"{years[0]}" if years[0] == years[-1] else f"{years[0]}-{years[-1]}"
    out = out_dir / f"feminicidios_delegacion_{stem}.json"
    write_dataset(FeminicideDataset(reports=reports), out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf-dir", type=Path, help="Directory of PDFs")
    ap.add_argument("--pdf", type=Path, help="Single PDF file")
    ap.add_argument("--year", type=int, help="Override year (use with --pdf)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    if args.pdf:
        run_batch([args.pdf], args.out_dir)
    elif args.pdf_dir:
        pdfs = sorted(args.pdf_dir.glob("VMujeres_*.pdf"))
        if not pdfs:
            sys.exit(f"No VMujeres_*.pdf files found in {args.pdf_dir}")
        run_batch(pdfs, args.out_dir)
    else:
        ap.error("Pass either --pdf or --pdf-dir")


if __name__ == "__main__":
    main()
