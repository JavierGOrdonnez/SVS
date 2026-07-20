"""Flatten INE table 7947 JSON dump into a tidy CSV.

Input:  raw JSON from https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/7947?tip=A
Output: CSV with columns year, sex, age_group, cause, cause_chapter, deaths, series_cod

Series name format is inconsistent in the source:
  A:  "{cause}. {sex}. {age}. Total Nacional. Personas."
  B:  "{sex}. {age}. Total Nacional. {cause}. Personas."

We identify sex/age by string match against fixed vocabularies; remainder = cause.
"""

import csv
import json
import re
import sys

SEX_VOCAB = {
    "Ambos sexos": "all",
    "Hombres": "male",
    "Mujeres": "female",
}

AGE_VOCAB = {
    "Todas las edades": "all",
    "Menos de 1 año": "<1",
    "De 1 a 4 años": "1-4",
    "95 y más años": "95+",
}
for lo in range(5, 95, 5):
    AGE_VOCAB[f"De {lo} a {lo+4} años"] = f"{lo}-{lo+4}"

CHAPTER_RE = re.compile(r"^([IVXLC]+(?:-[IVXLC]+)?)\.(.+)$")


def parse_name(nombre: str):
    raw = nombre.strip().rstrip(".").strip()
    parts = [p.strip() for p in raw.split(". ") if p.strip()]

    sex = age = None
    leftovers = []
    for p in parts:
        if p in SEX_VOCAB and sex is None:
            sex = SEX_VOCAB[p]
        elif p in AGE_VOCAB and age is None:
            age = AGE_VOCAB[p]
        elif p in ("Total Nacional", "Personas"):
            continue
        else:
            leftovers.append(p)

    if sex is None or age is None or not leftovers:
        return None

    cause_str = ". ".join(leftovers).strip().rstrip(".")
    m = CHAPTER_RE.match(cause_str)
    if m:
        chapter, cause = m.group(1), m.group(2).strip()
    else:
        chapter, cause = "", cause_str

    return sex, age, chapter, cause


def main(in_path: str, out_path: str) -> int:
    with open(in_path) as f:
        data = json.load(f)

    rows = []
    skipped = 0
    for series in data:
        parsed = parse_name(series["Nombre"])
        if parsed is None:
            skipped += 1
            continue
        sex, age, chapter, cause = parsed
        cod = series["COD"]
        for d in series["Data"]:
            rows.append(
                {
                    "year": d["Anyo"],
                    "sex": sex,
                    "age_group": age,
                    "cause_chapter": chapter,
                    "cause": cause,
                    "deaths": int(d["Valor"]) if d["Valor"] == int(d["Valor"]) else d["Valor"],
                    "data_type": d["T3_TipoDato"],
                    "series_cod": cod,
                }
            )

    rows.sort(key=lambda r: (r["year"], r["sex"], r["age_group"], r["cause_chapter"], r["cause"]))

    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["year", "sex", "age_group", "cause_chapter", "cause", "deaths", "data_type", "series_cod"],
            quoting=csv.QUOTE_MINIMAL,
        )
        w.writeheader()
        w.writerows(rows)

    print(f"series parsed: {len(data) - skipped}/{len(data)} (skipped {skipped})")
    print(f"rows written: {len(rows)} → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
