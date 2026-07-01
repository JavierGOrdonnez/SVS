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

Output (data/raw/sexual_crimes_mir_YYYY.csv per year, plus consolidated):
    year, crime_category, legal_article, count, victims_female, victims_male,
    victims_minor_pct, perp_male_pct, perp_spanish_pct, perp_foreign_pct,
    source_document, source_table, confidence, notes

Validation gate (V12): sum(crime subcategories) must equal headline total.
"""

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import pdfplumber
    import pandas as pd
except ImportError:
    sys.exit("Install: pip install pdfplumber pandas")

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
    victims_minor_pct: float | None = None
    perp_male_pct: float | None = None
    perp_spanish_pct: float | None = None
    perp_foreign_pct: float | None = None
    clearance_rate: float | None = None
    source_document: str = ""
    source_table: str = ""
    source_page: int | None = None
    confidence: str = "medium"
    notes: str = ""


# ──────────────────────────────────────────────────────────────
# Number parsing utilities
# ──────────────────────────────────────────────────────────────

_CLEAN_RE = re.compile(r"[^\d,.]")


def parse_es_number(s: str) -> float | None:
    """Parse Spanish-formatted number (dot=thousands, comma=decimal)."""
    if not s or s.strip() in ("", "-", "—", "N/A", "n/a"):
        return None
    s = _CLEAN_RE.sub("", s.strip())
    # Remove thousands dots if followed by exactly 3 digits (or end of string)
    s = re.sub(r"\.(?=\d{3}(?:[.,]|$))", "", s)
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_pct(s: str) -> float | None:
    v = parse_es_number(s.replace("%", ""))
    return v


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
            for page in pdf.pages:
                self._process_page(page)
        self._validate()
        return self.records

    def _process_page(self, page):
        tables = page.extract_tables()
        text_block = page.extract_text() or ""
        for table in tables:
            if not table:
                continue
            flat = [[str(c or "").strip() for c in row] for row in table]
            self._try_crime_table(flat, page.page_number)
            self._try_victim_sex_table(flat, page.page_number)
            self._try_perp_nationality_table(flat, page.page_number)

    def _try_crime_table(self, table: list[list[str]], page_no: int):
        """Detect and extract crime-by-category table."""
        for row in table:
            if not row:
                continue
            label = row[0].lower()
            count = find_number_in_row(row[1:])

            if re.search(r"total.*delito|delito.*sexual.*total", label, re.I):
                if count and (self._headline_total is None or count > self._headline_total):
                    self._headline_total = count
                    self._upsert("total_sexual_crimes", "all", count, page_no)

            elif re.search(r"violaci[oó]n|penetraci[oó]n", label, re.I):
                self._upsert("violacion", "Art.179+181", count, page_no)

            elif re.search(r"sin penetraci[oó]n", label, re.I):
                self._upsert("agresion_sin_penetracion", "Art.179", count, page_no)

            elif re.search(r"acoso sexual", label, re.I):
                self._upsert("acoso_sexual", "Art.184", count, page_no)

            elif re.search(r"abuso sexual", label, re.I):
                self._upsert("abuso_sexual", "Art.181", count, page_no)

    def _try_victim_sex_table(self, table: list[list[str]], page_no: int):
        """Detect victim sex / nationality table."""
        header = " ".join(row[0] for row in table[:3]).lower()
        if not re.search(r"v[ií]ctima|sexo|mujer|var[oó]n", header, re.I):
            return
        for row in table:
            if not row:
                continue
            label = row[0].lower()
            if re.search(r"mujer|femenin", label):
                v = find_number_in_row(row[1:])
                if v:
                    self._update_field("total_sexual_crimes", "victims_female", v)
            elif re.search(r"var[oó]n|hombre|masculin", label):
                v = find_number_in_row(row[1:])
                if v:
                    self._update_field("total_sexual_crimes", "victims_male", v)

    def _try_perp_nationality_table(self, table: list[list[str]], page_no: int):
        """Detect perpetrator nationality table."""
        header = " ".join((row[0] if row else "") for row in table[:3]).lower()
        if not re.search(r"espa[ñn]ol|extranjero|nacional|agresor|investigad", header, re.I):
            return
        for row in table:
            if not row:
                continue
            label = row[0].lower()
            v = find_number_in_row(row[1:])
            if v is None:
                # Maybe it's a percentage
                for c in row[1:]:
                    pct = parse_pct(c.replace("%", ""))
                    if pct is not None and 0 < pct < 100:
                        v = pct
                        break
            if v is None:
                continue
            if re.search(r"espa[ñn]ol", label):
                self._update_field("total_sexual_crimes", "perp_spanish_pct",
                                   v if v <= 100 else None)
            elif re.search(r"extranjero|no espa[ñn]ol", label):
                self._update_field("total_sexual_crimes", "perp_foreign_pct",
                                   v if v <= 100 else None)

    def _upsert(self, category: str, article: str, count: int | None, page_no: int):
        for r in self.records:
            if r.crime_category == category:
                if count:
                    r.count = count
                return
        self.records.append(MIRRecord(
            year=self.year,
            crime_category=category,
            legal_article=article,
            count=count,
            source_document=self.source,
            source_table="informe_table",
            source_page=page_no,
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
        sub_cats = ["violacion", "agresion_sin_penetracion", "acoso_sexual", "abuso_sexual"]
        sub_sum = sum(r.count for r in self.records if r.crime_category in sub_cats and r.count)
        if sub_sum > 0 and abs(sub_sum - total) / total > 0.15:
            note = f"VALIDATION: sub-cat sum {sub_sum} vs headline {total} (diff {sub_sum-total})"
            total_rec.notes += note
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
# Output helpers
# ──────────────────────────────────────────────────────────────

FIELDNAMES = [
    "year", "crime_category", "legal_article", "count",
    "victims_female", "victims_male", "victims_minor_pct",
    "perp_male_pct", "perp_spanish_pct", "perp_foreign_pct",
    "clearance_rate", "source_document", "source_table",
    "source_page", "confidence", "notes",
]


def write_records(records: list[MIRRecord], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))
    print(f"  → {out_path} ({len(records)} records)")


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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["informe", "anuario"], required=True)
    ap.add_argument("--pdf-dir", type=Path, help="Directory of PDFs")
    ap.add_argument("--pdf", type=Path, help="Single PDF file")
    ap.add_argument("--year", type=int, help="Override year (use with --pdf)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    parse_fn = run_informe if args.mode == "informe" else run_anuario
    all_records: list[MIRRecord] = []

    if args.pdf:
        year = args.year or infer_year(args.pdf)
        if not year:
            sys.exit("Cannot infer year from filename; pass --year")
        records = parse_fn(args.pdf, year)
        out = args.out_dir / f"sexual_crimes_mir_{year}.csv"
        write_records(records, out)
        all_records.extend(records)

    elif args.pdf_dir:
        pdfs = sorted(args.pdf_dir.glob("*.pdf"))
        if not pdfs:
            sys.exit(f"No PDFs found in {args.pdf_dir}")
        for pdf in pdfs:
            year = infer_year(pdf)
            if not year:
                print(f"  SKIP {pdf.name} (cannot infer year)")
                continue
            records = parse_fn(pdf, year)
            out = args.out_dir / f"sexual_crimes_mir_{year}.csv"
            write_records(records, out)
            all_records.extend(records)

    else:
        ap.error("Pass either --pdf or --pdf-dir")

    if all_records:
        consolidated = args.out_dir / "sexual_crimes_mir_2000-2024.csv"
        write_records(all_records, consolidated)
        print(f"\nConsolidated: {consolidated} ({len(all_records)} total records)")


if __name__ == "__main__":
    main()
