"""Macroencuesta partner-perpetrator nationality parser (T101).

Extracts the nationality of the current partner by violence-perpetration status
from both 2019 and 2024 editions of the Macroencuesta de Violencia contra la Mujer.

2024: Tabla 1.18 (physical), Tabla 3.16 (combined). Chapter 2 (sexual) has no table.
2019: Equivalent tables in Chapters 1 (physical) and 2 (sexual).

Usage:
    uv run python src/parsers/macroencuesta_partner_nationality_parser.py --pdf-dir data/sources/
"""

import argparse
import json
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


class NationalityStat(BaseModel):
    """Partner-perpetrator nationality breakdown by violence status."""
    violence_type: str          # physical | sexual | physical_and_or_sexual
    violence_perpetrated: bool | None  # True/False = violence exercised, None = unavailable/N/A
    nationality: str | None     # españa | otro_país | nc; None if unavailable
    pct: float | None = None
    population_estimate: int | None = None  # population (2024) or raw N (2019)
    sample_n: int | None = None  # 2019 only
    significance: str | None = None
    note: str | None = None


class NationalityReport(BaseModel):
    wave_year: int
    nationality_stats: list[NationalityStat] = []
    source_document: str
    notes: str = ""


class NationalityDataset(BaseModel):
    reports: list[NationalityReport]


_NUM_RE = re.compile(r"\d{1,3}(?:\.\d{3})*(?:,\d+)?")

def _numbers_in(line: str) -> list[float]:
    return [parse_es_number(t) for t in _NUM_RE.findall(line)]

def _locate_page(pdf, keywords: list[str], start: int = 0):
    # Strip and uppercase keywords for comparison
    stripped_keywords = [strip_accents(kw).upper() for kw in keywords]
    for i in range(start, len(pdf.pages)):
        text = pdf.pages[i].extract_text() or ""
        upper = strip_accents(text).upper()
        if all(kw in upper for kw in stripped_keywords):
            return i, text
    return None

def _page_window_text(pdf, start_index: int, n_pages: int = 3) -> str:
    end = min(start_index + n_pages, len(pdf.pages))
    return "\n".join(pdf.pages[i].extract_text() or "" for i in range(start_index, end))

def _split_tokens_2024(remainder: str) -> list[float | None]:
    """Parse 2024 tokens: . = suppressed, ¨N = small sample."""
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

def parse_nacionalidad_2024(text: str, violence_type: str) -> list[NationalityStat]:
    """Extract nationality data from 2024 characteristic table."""
    lines = text.splitlines()
    out = []
    sig = None

    for i, line in enumerate(lines):
        if "País de nacimiento" in line and "España" in line:
            # Line like: "País de nacimiento España 71,8 146.656 83,9 11.217.154"
            # Extract numbers after "España"
            parts = line.split("España", 1)
            if len(parts) > 1:
                tokens = _split_tokens_2024(parts[1])
                if len(tokens) >= 4:
                    pct_si, n_si, pct_no, n_no = tokens[0], tokens[1], tokens[2], tokens[3]
                    out.append(NationalityStat(
                        violence_type=violence_type,
                        violence_perpetrated=True,
                        nationality="españa",
                        pct=pct_si,
                        population_estimate=int(n_si) if n_si is not None else None,
                    ))
                    out.append(NationalityStat(
                        violence_type=violence_type,
                        violence_perpetrated=False,
                        nationality="españa",
                        pct=pct_no,
                        population_estimate=int(n_no) if n_no is not None else None,
                    ))

            # Next line: "de la pareja actual Otro país 24,2 49.351 15,0 2.007.347"
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if "Otro país" in next_line:
                    parts = next_line.split("Otro país", 1)
                    if len(parts) > 1:
                        tokens = _split_tokens_2024(parts[1])
                        if len(tokens) >= 4:
                            pct_si, n_si, pct_no, n_no = tokens[0], tokens[1], tokens[2], tokens[3]
                            note_si = "small_sample" if "¨" in parts[1][:20] else None
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=True,
                                nationality="otro_país",
                                pct=pct_si,
                                population_estimate=int(n_si) if n_si is not None else None,
                                note=note_si,
                            ))
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=False,
                                nationality="otro_país",
                                pct=pct_no,
                                population_estimate=int(n_no) if n_no is not None else None,
                            ))

            # Next line: "NC ¨4,0 8.255 1,1 140.805"
            if i + 2 < len(lines):
                next_line = lines[i + 2]
                if next_line.strip().startswith("NC"):
                    parts = next_line.split("NC", 1)
                    if len(parts) > 1:
                        tokens = _split_tokens_2024(parts[1])
                        if len(tokens) >= 4:
                            pct_si, n_si, pct_no, n_no = tokens[0], tokens[1], tokens[2], tokens[3]
                            note_si = "small_sample" if "¨" in parts[1][:20] else None
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=True,
                                nationality="nc",
                                pct=pct_si,
                                population_estimate=int(n_si) if n_si is not None else None,
                                note=note_si,
                            ))
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=False,
                                nationality="nc",
                                pct=pct_no,
                                population_estimate=int(n_no) if n_no is not None else None,
                            ))

            # Extract significance marker (next line after NC)
            if i + 3 < len(lines):
                sig_line = lines[i + 3].strip()
                if sig_line.startswith("p<"):
                    sig = sig_line.split()[0]
                    for stat in out:
                        if stat.violence_perpetrated is not None:
                            stat.significance = sig
            break

    return out

def parse_nacionalidad_2019(text: str, violence_type: str) -> list[NationalityStat]:
    """Extract nationality data from 2019 characteristic table."""
    lines = text.splitlines()
    out = []

    for i, line in enumerate(lines):
        if "País de nacimiento" in line:
            # Look for España line (might be on same line or next)
            for j in range(i, min(i + 5, len(lines))):
                l = lines[j]
                if "España" in l and not "Nivel de" in l:  # Skip Nivel de formación row
                    parts = l.split("España", 1)
                    if len(parts) > 1:
                        tokens = _numbers_in(parts[1])
                        # 2019 format: N% Sí, % Sí, N No, % No
                        if len(tokens) >= 4:
                            n_si, pct_si, n_no, pct_no = tokens[0], tokens[1], tokens[2], tokens[3]
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=True,
                                nationality="españa",
                                pct=pct_si,
                                sample_n=int(n_si) if n_si is not None else None,
                            ))
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=False,
                                nationality="españa",
                                pct=pct_no,
                                sample_n=int(n_no) if n_no is not None else None,
                            ))
                    break

            # Find Otro país line
            for j in range(i, min(i + 5, len(lines))):
                l = lines[j]
                if "Otro país" in l:
                    parts = l.split("Otro país", 1)
                    if len(parts) > 1:
                        tokens = _numbers_in(parts[1])
                        if len(tokens) >= 4:
                            n_si, pct_si, n_no, pct_no = tokens[0], tokens[1], tokens[2], tokens[3]
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=True,
                                nationality="otro_país",
                                pct=pct_si,
                                sample_n=int(n_si) if n_si is not None else None,
                            ))
                            out.append(NationalityStat(
                                violence_type=violence_type,
                                violence_perpetrated=False,
                                nationality="otro_país",
                                pct=pct_no,
                                sample_n=int(n_no) if n_no is not None else None,
                            ))
                    break

            # Find NC line
            for j in range(i, min(i + 5, len(lines))):
                l = lines[j].strip()
                if l.startswith("NC"):
                    tokens = _numbers_in(l.split("NC", 1)[1] if "NC" in l else "")
                    if len(tokens) >= 4:
                        n_si, pct_si, n_no, pct_no = tokens[0], tokens[1], tokens[2], tokens[3]
                        out.append(NationalityStat(
                            violence_type=violence_type,
                            violence_perpetrated=True,
                            nationality="nc",
                            pct=pct_si,
                            sample_n=int(n_si) if n_si is not None else None,
                        ))
                        out.append(NationalityStat(
                            violence_type=violence_type,
                            violence_perpetrated=False,
                            nationality="nc",
                            pct=pct_no,
                            sample_n=int(n_no) if n_no is not None else None,
                        ))
                    break

            # Extract significance
            for j in range(i, min(i + 6, len(lines))):
                l = lines[j].strip()
                if l.startswith("***") or l.startswith("Diferencias"):
                    if "***" in l:
                        for stat in out:
                            if stat.violence_perpetrated is not None:
                                stat.significance = "p<0.001"
                    elif "**" in l:
                        for stat in out:
                            if stat.violence_perpetrated is not None:
                                stat.significance = "p<0.01"
                    elif "*" in l:
                        for stat in out:
                            if stat.violence_perpetrated is not None:
                                stat.significance = "p<0.05"
                    break
            break

    return out


def main():
    parser = argparse.ArgumentParser(description="Extract partner-perpetrator nationality from Macroencuesta PDFs (T101)")
    parser.add_argument("--pdf-dir", help="Directory with Macroencuesta_YYYY.pdf files")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    reports = []
    pdf_dir = Path(args.pdf_dir) if args.pdf_dir else ROOT / "data" / "sources"

    # 2024
    pdf_2024 = pdf_dir / "Macroencuesta_2024.pdf"
    if pdf_2024.exists():
        with pdfplumber.open(pdf_2024) as pdf:
            stats_2024 = []

            # Tabla 1.18 (physical)
            result = _locate_page(pdf, ["TABLA 1.18", "PAIS DE NACIMIENTO"], start=0)
            if result:
                idx, _ = result
                window = _page_window_text(pdf, idx, 2)
                stats_2024.extend(parse_nacionalidad_2024(window, "physical"))

            # Tabla 3.16 (combined)
            result = _locate_page(pdf, ["TABLA 3.16", "PAIS DE NACIMIENTO"], start=0)
            if result:
                idx, _ = result
                window = _page_window_text(pdf, idx, 2)
                stats_2024.extend(parse_nacionalidad_2024(window, "physical_and_or_sexual"))

            # Chapter 2 (sexual)
            result = _locate_page(pdf, ["CAPÍTULO 2", "VIOLENCIA SEXUAL"], start=0)
            if result:
                idx, _ = result
                window = _page_window_text(pdf, idx, 15)
                if "2.1.7" in window and "no se muestran los resultados" in window.lower():
                    stats_2024.append(NationalityStat(
                        violence_type="sexual",
                        violence_perpetrated=None,
                        nationality=None,
                        note="unavailable - no table published in 2024",
                    ))

            if stats_2024:
                reports.append(NationalityReport(
                    wave_year=2024,
                    nationality_stats=stats_2024,
                    source_document="Macroencuesta_2024.pdf",
                ))

    # 2019
    pdf_2019 = pdf_dir / "Macroencuesta_2019.pdf"
    if pdf_2019.exists():
        with pdfplumber.open(pdf_2019) as pdf:
            stats_2019 = []

            # Search for País de nacimiento and classify by context
            # Find chapter boundaries for context
            ch1_pages = []  # pages in Chapter 1
            ch2_pages = []  # pages in Chapter 2

            for i in range(len(pdf.pages)):
                text = pdf.pages[i].extract_text() or ""
                # Check for actual chapter heading (not TOC)
                if i > 5 and "CAPÍTULO 1" in text and "Violencia física en la pareja" in text:
                    ch1_start = i
                elif i > 10 and "CAPÍTULO 2" in text and "Violencia sexual en la pareja" in text:
                    ch2_start = i
                    break
            else:
                # Fallback: use heuristic page ranges based on typical layout
                ch1_start = 13
                ch2_start = 23

            # Search for País de nacimiento in Chapter 1 range
            # Must be from the "sociodemográficas de la pareja agresora" section (violence-specific table)
            for i in range(ch1_start, ch2_start):
                text = pdf.pages[i].extract_text() or ""
                if "País de nacimiento" in text and ("pareja agresora" in text or "ejercido o no violencia" in text):
                    window = _page_window_text(pdf, i, 3)
                    stats_2019.extend(parse_nacionalidad_2019(window, "physical"))
                    break

            # Search for País de nacimiento in Chapter 2 range
            ch3_start = len(pdf.pages)  # Assume Chapter 2 extends to end
            for i in range(ch2_start, min(ch3_start, len(pdf.pages))):
                text = pdf.pages[i].extract_text() or ""
                if "País de nacimiento" in text:
                    window = _page_window_text(pdf, i, 3)
                    stats_2019.extend(parse_nacionalidad_2019(window, "sexual"))
                    break

            if stats_2019:
                reports.append(NationalityReport(
                    wave_year=2019,
                    nationality_stats=stats_2019,
                    source_document="Macroencuesta_2019.pdf",
                ))

    dataset = NationalityDataset(reports=reports)
    output_path = Path(args.output or OUT_DIR / "macroencuesta_nationality_partner.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dataset.model_dump_json(indent=2))
    print(f"Wrote {len(reports)} report(s) to {output_path}")


if __name__ == "__main__":
    main()
