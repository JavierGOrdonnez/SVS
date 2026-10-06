"""Tests for the Macroencuesta de Violencia contra la Mujer parser (T99).

Fixture text blocks are literal `page.extract_text()` output from the
source PDFs (data/sources/Macroencuesta_{2019,2024}.pdf). Every expected
value here was cross-checked against a manual read of the same PDF pages
during development (see SPEC-sexual-crimes.md T99) and against this
module's own end-to-end CLI run, whose output is byte-identical before and
after the pure-function refactor these tests exercise.

Regression coverage note: the pure `parse_*` functions can't by themselves
catch the real bug this module hit during development -- chapter 15
("violencia física fuera de la pareja") in the 2019 PDF has a table with
the *exact same* title phrase and row labels ("Familiar hombre", "vínculo
que las une con el agresor (II)") as chapter 16's sexual-violence table.
`re.search` only returns the first match, so handing these functions the
wrong page's text (or a blob containing both tables) silently returns
chapter 15's numbers with no error. That failure mode lives in *page
selection* (`Macroencuesta2019Parser._parse_relationship`'s chapter-16
anchor, `_locate_page`), not in these text-parsing functions, and isn't
practical to unit-test without opening the real ~340-page PDF (~25s), which
this repo's test suite avoids for parser tests (see mir_parser's test
files, all fixture-based). `test_relationship_2019_only_returns_first_match_in_given_text`
below documents the behavior explicitly instead, so a future reader
understands why the caller's page-scoping is load-bearing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.macroencuesta_parser import (
    parse_prevalence_2019,
    parse_prevalence_block_2024,
    parse_relationship_2019,
    parse_relationship_2024,
    parse_frequency_2019,
    parse_frequency_2024,
    parse_participants_2019,
    parse_participants_2024,
)


# ── 2019: prevalence (p.154 of Macroencuesta_2019.pdf) ──
TEXT_2019_PREVALENCE = """Violencia sexual fuera de la pareja (N=frecuencia muestral, %=porcentaje sobre el total de
mujeres residentes en España de 16 o más años)
En la infancia
Últimos 12 Violación alguna vez
A lo largo de la vida Últimos 4 años (antes de los 15
meses en la vida
años de edad)
N % N % N % N % N %
Sí 620 6,5 134 1,4 49 0,5 330 3,4 213 2,2
No 8937 93,4 9423 98,5 9507 99,4 9227 96,4 9347 97,7
NC 11 0,1 11 0,1 12 0,1 11 0,1 8 0,1
Total 9568 100 9568 100 9568 100 9568 100 9568 100"""

# ── 2019: vínculo con el agresor, Tabla II (p.159) ──
TEXT_2019_RELATIONSHIP = """Mujeres que han sufrido violencia sexual fuera de la pareja, según vínculo que las une con el
agresor (II) (N=frecuencia muestral, %=porcentaje)
% sobre el total de mujeres que han sufrido violencia sexual
N
fuera de la pareja (N=620)
Familiar hombre 134 21,6
Familiar mujer 1 0,0
Amigo o conocido hombre 304 49,0
Amiga o conocida mujer 9 1,5
Desconocido hombre 242 39,1
Desconocida mujer 0 0,0
Pregunta de respuesta múltiple"""

# ── 2019: chapter 15's near-identical physical-violence table (p.149) --
# same title phrase/row labels, DIFFERENT numbers -- used to demonstrate the
# first-match ambiguity documented in this module's docstring above.
TEXT_2019_CHAPTER15_LOOKALIKE = """Mujeres que han sufrido violencia física fuera de la pareja, según vínculo que las une con el
agresor (II) (N=frecuencia muestral, %=porcentaje)
Familiar hombre 424 33,1
Familiar mujer 286 22,3
Amigo o conocido hombre 357 27,8
Amiga o conocida mujer 394 30,7
Desconocido hombre 224 17,4
Desconocida mujer 87 6,8"""

# ── 2024: Tabla 16.1 (overall prevalence, p.250) ──
TEXT_2024_PREVALENCE_OVERALL = """Tabla 16.1 Prevalencia de la violencia sexual fuera del ámbito de la pareja a lo largo de la vida, en los últimos 4 años,
en los últimos 12 meses y en la infancia
A lo largo de la vida Últimos 4 años Últimos 12 meses Infancia
Número de Número de Número de Número de
%¹ %¹ %¹ %¹
mujeres mujeres mujeres mujeres
Sí 14,5 3.076.748 3,4 725.595 2,0 416.112 7,4 1.582.380
IC 95% (13,8 - 15,2) (3,1 - 3,8) (1,7 - 2,2) (6,9 - 8,0)
No 84,2 94,8 96,2 91,0
NC 1,4 1,8 1,9 1,5
Total 100,0 100,0 100,0 100,0"""

# ── 2024: Tabla 16.2 (by-severity prevalence, p.251) ──
TEXT_2024_PREVALENCE_BY_SEVERITY = """Tabla 16.2 Prevalencia a lo largo de la vida, en los últimos 4 años, en los últimos 12 meses y en la infancia, de la
violación, los intentos de violación y otras formas de violencia sexual fuera del ámbito de la pareja
A lo largo de la vida Últimos 4 años Últimos 12 meses Infancia
Número de Número de Número de Número de
%¹ %¹ %¹ %¹
mujeres mujeres mujeres mujeres
Violaciones
Sí 3,1 665.811 0,9 191.484 0,5 105.542 1,2 251.358
IC 95% (2,8 - 3,5) (0,7 - 1,1) (0,4 - 0,6) (1,0 - 1,4)
Intentos de violación
Sí 3,2 680.942 0,7 157.137 0,3 74.488 1,3 266.280
IC 95% (2,9 - 3,6) (0,6 - 0,9) (0,2 - 0,5) (1,0 - 1,5)
Otras formas de violencia sexual
Sí 12,7 2.693.342 2,6 555.273 1,4 304.034 6,6 1.410.076
IC 95% (12,0 - 13,3) (2,3 - 2,9) (1,2 - 1,7) (6,2 - 7,1)"""

# ── 2024: Tabla 16.21 (vínculo con el agresor, p.270) ──
TEXT_2024_RELATIONSHIP = """Tabla 16.21 Mujeres víctimas de cada tipo de violencia sexual (violaciones, intentos de violación, otras formas de
violencia sexual) fuera del ámbito de la pareja a lo largo de la vida, según el vínculo que las une con el agresor (II)*
Otras formas de violencia
Violaciones Intentos de violación
sexual
Número de Número de Número de
%¹ %² %¹ %² %¹ %²
mujeres mujeres mujeres
Familiar hombre 23,1 0,7 151.898 17,9 0,6 118.162 18,6 2,3 495.613
Familiar mujer . . . . . . ¨1,0 0,1 26.747
Amigo o conocido (hombre) 62,7 1,9 412.660 66,0 2,0 435.469 48,5 6,1 1.294.160
Amiga o conocida (mujer) . . . . . . 1,9 0,2 51.497
Desconocido (hombre) 12,0 0,4 78.730 21,7 0,7 143.482 46,5 5,8 1.238.686
Desconocida (mujer) . . . . . . ¨0,8 0,1 21.162"""


def _find(rows, key, **extra):
    matches = [r for r in rows if r.key == key and all(getattr(r, k) == v for k, v in extra.items())]
    assert len(matches) == 1, f"expected exactly one match for key={key!r} {extra}, got {matches}"
    return matches[0]


# ── 2019 prevalence ──

def test_2019_prevalence_lifetime_any():
    rows = parse_prevalence_2019(TEXT_2019_PREVALENCE)
    lifetime = next(r for r in rows if r.violence_type == "any" and r.timeframe == "lifetime")
    assert (lifetime.sample_n, lifetime.pct) == (620, 6.5)


def test_2019_prevalence_rape_lifetime_is_its_own_row():
    rows = parse_prevalence_2019(TEXT_2019_PREVALENCE)
    rape = next(r for r in rows if r.violence_type == "rape")
    assert rape.timeframe == "lifetime"
    assert (rape.sample_n, rape.pct) == (213, 2.2)


def test_2019_prevalence_all_five_columns_present():
    rows = parse_prevalence_2019(TEXT_2019_PREVALENCE)
    assert len(rows) == 5
    assert {r.timeframe for r in rows if r.violence_type == "any"} == {
        "lifetime", "last_4_years", "last_12_months", "childhood"}


def test_2019_prevalence_no_ci_this_wave():
    rows = parse_prevalence_2019(TEXT_2019_PREVALENCE)
    assert all(r.ci_low is None and r.ci_high is None for r in rows)


# ── 2019 relationship ──

def test_2019_relationship_all_six_rows():
    rows = parse_relationship_2019(TEXT_2019_RELATIONSHIP)
    assert len(rows) == 6
    assert {r.violence_type for r in rows} == {"any"}


def test_2019_relationship_familiar_hombre():
    rows = parse_relationship_2019(TEXT_2019_RELATIONSHIP)
    r = _find(rows, "familiar_hombre")
    assert (r.sample_n, r.pct_within_severity) == (134, 21.6)


def test_2019_relationship_desconocido_hombre():
    rows = parse_relationship_2019(TEXT_2019_RELATIONSHIP)
    r = _find(rows, "desconocido_hombre")
    assert (r.sample_n, r.pct_within_severity) == (242, 39.1)


def test_relationship_2019_only_returns_first_match_in_given_text():
    """Documents the real ambiguity this module hit during development (see
    module docstring): given text containing BOTH chapter 15's lookalike
    table and chapter 16's real one, the function has no way to prefer the
    right one -- it's on the caller to only ever pass chapter-16-scoped
    text. Here chapter 15's block comes first, so its (wrong, for this
    dataset's purposes) numbers win -- proving page-scoping, not text
    content, is what makes the real parser correct."""
    combined = TEXT_2019_CHAPTER15_LOOKALIKE + "\n" + TEXT_2019_RELATIONSHIP
    rows = parse_relationship_2019(combined)
    r = _find(rows, "familiar_hombre")
    assert (r.sample_n, r.pct_within_severity) == (424, 33.1)  # chapter 15's number, not chapter 16's 134/21.6


# ── 2024 prevalence ──

def test_2024_prevalence_overall_lifetime_with_ci():
    rows = parse_prevalence_block_2024(TEXT_2024_PREVALENCE_OVERALL, "any", start_after="Tabla 16.1")
    lifetime = next(r for r in rows if r.timeframe == "lifetime")
    assert (lifetime.pct, lifetime.population_estimate) == (14.5, 3076748)
    assert (lifetime.ci_low, lifetime.ci_high) == (13.8, 15.2)


def test_2024_prevalence_by_severity_rape_block():
    rows = parse_prevalence_block_2024(TEXT_2024_PREVALENCE_BY_SEVERITY, "rape", start_after="Violaciones")
    lifetime = next(r for r in rows if r.timeframe == "lifetime")
    assert (lifetime.pct, lifetime.population_estimate) == (3.1, 665811)
    assert (lifetime.ci_low, lifetime.ci_high) == (2.8, 3.5)


def test_2024_prevalence_by_severity_targets_the_right_sub_block():
    # "Sí"/"IC 95%" repeats 3x on this page (rape/attempted/other) --
    # start_after must select the right one, not always the first.
    rows_other = parse_prevalence_block_2024(
        TEXT_2024_PREVALENCE_BY_SEVERITY, "other", start_after="Otras formas de violencia sexual")
    lifetime = next(r for r in rows_other if r.timeframe == "lifetime")
    assert (lifetime.pct, lifetime.population_estimate) == (12.7, 2693342)


# ── 2024 relationship ──

def test_2024_relationship_leaf_rows_per_severity():
    rows = parse_relationship_2024(TEXT_2024_RELATIONSHIP)
    rape = _find(rows, "desconocido_hombre", violence_type="rape")
    assert (rape.pct_within_severity, rape.pct_of_all_women, rape.population_estimate) == (12.0, 0.4, 78730)

    other = _find(rows, "desconocido_hombre", violence_type="other")
    assert (other.pct_within_severity, other.population_estimate) == (46.5, 1238686)


def test_2024_relationship_suppressed_values_are_none_not_zero():
    rows = parse_relationship_2024(TEXT_2024_RELATIONSHIP)
    suppressed = _find(rows, "familiar_mujer", violence_type="rape")
    assert suppressed.pct_within_severity is None
    assert suppressed.population_estimate is None


def test_2024_relationship_small_sample_flag_kept_as_real_number():
    # '¨1,0' (6-19 observations, caution flag) must parse to 1.0, not be
    # dropped like a genuinely suppressed '.' value.
    rows = parse_relationship_2024(TEXT_2024_RELATIONSHIP)
    flagged = _find(rows, "familiar_mujer", violence_type="other")
    assert flagged.pct_within_severity == 1.0
    assert flagged.population_estimate == 26747


def test_2024_relationship_all_18_rows_present():
    # 6 label rows x 3 severity tiers = 18, even though several are None-valued
    rows = parse_relationship_2024(TEXT_2024_RELATIONSHIP)
    assert len(rows) == 18


def test_empty_text_produces_no_rows():
    assert parse_prevalence_2019("") == []
    assert parse_relationship_2019("") == []
    assert parse_prevalence_block_2024("", "any", "Tabla 16.1") == []
    assert parse_relationship_2024("") == []
    assert parse_frequency_2019("") == []
    assert parse_frequency_2024("") == []
    assert parse_participants_2019("") == []
    assert parse_participants_2024("") == []


# ── T105: frequency + single-vs-multiple perpetrators ──

# ── 2019: "16.5 Frecuencia..." (p.159 of Macroencuesta_2019.pdf) ──
TEXT_2019_FREQUENCY = """16.5 Frecuencia de la violencia sexual fuera de la pareja a lo largo de la vida
El 50,4% de las mujeres que han sufrido violencia sexual fuera de la pareja afirman que esta
violencia ha tenido lugar solo una vez frente al 49,6% que dicen que ha sucedido en más de una
ocasión. De las que responden que tuvo lugar más de una vez, el 41% dicen que la violencia
sexual tenía lugar al menos una vez al mes (5,8% todos o casi todos los días, 16,9% al menos una
vez por semana, y 18,3% al menos una vez al mes).
Frecuencia (1) de la violencia sexual fuera de la pareja a lo largo de la vida (N=frecuencia
muestral, %=porcentaje)
% sobre el total de mujeres residentes en España de 16 o más años
N
que han sufrido violencia sexual fuera de la pareja (N=620 mujeres)
Una vez 312 50,4
Más de una vez 308 49,6
NC 0 0,0
Total 620 100
Frecuencia (2) de la violencia sexual fuera de la pareja a lo largo de la vida (N=frecuencia
muestral, %=porcentaje)
% sobre mujeres que han sufrido violencia
N sexual fuera de la pareja más de una vez
(N=308)
Todos los días o casi todos los días 18 5,8
Al menos una o más veces por semana 52 16,9
Al menos una o más veces al mes 56 18,3
Al menos una o más veces al año 65 21,1
Menos de una vez al año, rara vez, de forma aislada 81 26,4
Solo en períodos particulares (navidades, vacaciones de
23 7,6
verano, curso escolar, etc.)
NC 13 3,9
Total 308 100
16.6 País en el que sucedió la violencia sexual fuera de la pareja a lo largo de la vida"""

# ── 2019: "16.8 Agresiones sexuales... en grupo" (p.161) ──
TEXT_2019_PARTICIPANTS = """16.8 Agresiones sexuales sufridas a lo largo de la vida en las que participó más de una
persona
El 12,4% de las mujeres que han sufrido violencia sexual fuera de la pareja manifiesta que en
alguna de las agresiones sexuales participó más de una persona, porcentaje que asciende al
17,3% entre las mujeres que han sufrido una violación. Se reitera que no es posible saber si la
agresión colectiva sucedió en la violación o en otro episodio de violencia sexual porque la
pregunta se hace de forma global y no para cada ítem de violencia sexual.
Agresiones sexuales en grupo (N=frecuencia muestral, %=porcentaje)
% sobre el total de % sobre el total de
mujeres que han mujeres que han
N sufrido violencia N sufrido una
sexual fuera de la violación fuera de
pareja (N=620) la pareja (N=213)
No, en todos los incidentes
541 87,3 176 82,7
participó una sola persona
Sí, en al menos un incidente
77 12,4 37 17,3
participaron varias personas
NC 2 0,3 0 0
Total 620 100 213 100"""

# ── 2024: Tabla 16.16/16.17 (frecuencia, p.249) ──
TEXT_2024_FREQUENCY = """Tabla 16.16 Distribución de las mujeres víctimas de cada tipo de violencia sexual (violaciones, intentos de violación,
otras formas de violencia sexual) fuera del ámbito de la pareja a lo largo de la vida, según si la violencia ha sucedido
una vez o más de una vez
Intentos de Otras formas de
Violaciones
violación violencia sexual
%¹ %² %³
Una vez 42,4 48,9 43,2
Más de una vez 53,9 47,5 55,0
NC 3,8 3,7 1,8
Total 100,0 100,0 100,0
1. Porcentaje sobre el total de mujeres que han sufrido una violación fuera de la pareja; 2. Porcentaje sobre el total de mujeres que
han sufrido un intento de violación fuera de la pareja; 3. Porcentaje sobre el total de mujeres que han sufrido otras formas de
violencia sexual fuera de la pareja distintas de la violación y de los intentos de violación.
Tabla 16.17 Distribución de las mujeres que han sufrido en más de una ocasión cada tipo de violencia sexual
(violaciones, intentos de violación, otras formas de violencia sexual) fuera del ámbito de la pareja a lo largo de la vida,
según la frecuencia de la violencia
Intentos de Otras formas de
Violaciones
violación violencia sexual
%¹ %² %³
Diariamente (todos los días o casi todos los días) ¨3,9 ¨4,6 3,4
Semanalmente (al menos una o más veces por semana) 23,3 ¨10,6 11,0
Mensualmente (al menos una o más veces al mes) 29,0 18,4 17,2
Anualmente (al menos una o más veces al año) 11,0 21,5 23,3
Menos de una vez al año, rara vez, de forma aislada 18,1 28,2 32,4
Solo en períodos particulares (navidades, vacaciones de
¨9,1 ¨8,8 8,9
verano, curso escolar, etc.)
NC ¨5,6 ¨8,0 3,9
Total 100,0 100,0 100,0
El símbolo '¨' debe interpretarse como "dato con un número de observaciones muestrales de entre 6 y 19" por lo que ha de ser
tomado con precaución, ya que puede estar afectado de un elevado error de muestreo."""

# ── 2024: Tabla 16.18 (más de una persona agresora, p.249-250) ──
TEXT_2024_PARTICIPANTS = """de una persona (Tabla 16.18). Por tipo de violencia sexual, el 11,3% de las mujeres que han
sufrido una violación fuera de la pareja a lo largo de la vida manifiesta que en la violación o en
alguna de las violaciones (si hubo más de una) participó más de una persona.
Tabla 16.18 Distribución de las mujeres que han sufrido cada tipo de violencia sexual (violaciones, intentos de violación,
otras formas de violencia sexual) fuera del ámbito de la pareja a lo largo de la vida, según si en alguna de las agresiones
participó más de una persona
Intentos de Otras formas de Violencia sexual
Violaciones
violación violencia sexual (total)
%¹ %² %³ %⁴
Solo una persona 86,3 89,5 88,0 87,9
Al menos en una ocasión
participó más de una 11,3 7,6 10,0 10,4
persona (varias personas)
NC ¨2,4 ¨2,9 1,9 1,7
Total 100,0 100,0 100,0 100,0
1. Porcentaje sobre el total de mujeres que han sufrido una violación fuera de la pareja; 2. Porcentaje sobre el total de mujeres que
han sufrido un intento de violación fuera de la pareja."""


def test_2019_frequency_episodes():
    rows = parse_frequency_2019(TEXT_2019_FREQUENCY)
    once = next(r for r in rows if r.measure == "episodes" and r.category == "once")
    multiple = next(r for r in rows if r.measure == "episodes" and r.category == "multiple")
    assert (once.sample_n, once.pct) == (312, 50.4)
    assert (multiple.sample_n, multiple.pct) == (308, 49.6)
    assert all(r.violence_type == "any" for r in rows if r.measure == "episodes")


def test_2019_frequency_cadence_wrapped_label_row():
    # "Solo en períodos particulares..." wraps its label onto its own line,
    # with the data row's numbers printed on the following line.
    rows = parse_frequency_2019(TEXT_2019_FREQUENCY)
    particular = next(r for r in rows if r.measure == "cadence" and r.category == "particular_periods")
    assert (particular.sample_n, particular.pct) == (23, 7.6)


def test_2019_frequency_all_rows_present():
    rows = parse_frequency_2019(TEXT_2019_FREQUENCY)
    assert {r.category for r in rows if r.measure == "episodes"} == {"once", "multiple", "nc"}
    assert {r.category for r in rows if r.measure == "cadence"} == {
        "daily", "weekly", "monthly", "yearly", "less_than_yearly", "particular_periods", "nc"}


def test_2019_participants_rape_column():
    rows = parse_participants_2019(TEXT_2019_PARTICIPANTS)
    single_rape = next(r for r in rows if r.category == "single" and r.violence_type == "rape")
    multiple_rape = next(r for r in rows if r.category == "multiple" and r.violence_type == "rape")
    assert (single_rape.sample_n, single_rape.pct) == (176, 82.7)
    assert (multiple_rape.sample_n, multiple_rape.pct) == (37, 17.3)


def test_2019_participants_any_column():
    rows = parse_participants_2019(TEXT_2019_PARTICIPANTS)
    multiple_any = next(r for r in rows if r.category == "multiple" and r.violence_type == "any")
    assert (multiple_any.sample_n, multiple_any.pct) == (77, 12.4)


def test_2024_frequency_episodes_by_severity():
    rows = parse_frequency_2024(TEXT_2024_FREQUENCY)
    multiple_rape = next(r for r in rows if r.measure == "episodes" and r.category == "multiple" and r.violence_type == "rape")
    assert multiple_rape.pct == 53.9


def test_2024_frequency_cadence_small_sample_flag_kept():
    # '¨3,9' (6-19 observations) must parse to 3.9, not be dropped.
    rows = parse_frequency_2024(TEXT_2024_FREQUENCY)
    daily_rape = next(r for r in rows if r.measure == "cadence" and r.category == "daily" and r.violence_type == "rape")
    assert daily_rape.pct == 3.9


def test_2024_participants_wrapped_multiple_row():
    # The "multiple" row's label wraps onto three lines ("Al menos en una
    # ocasión" / "participó más de una ... <numbers>" / "persona (varias
    # personas)") with the numbers on the middle line, mixed with more
    # label text -- the real bug this parser had to handle (8/12 cells
    # found instead of 12/12 before the fix).
    rows = parse_participants_2024(TEXT_2024_PARTICIPANTS)
    multiple = {r.violence_type: r.pct for r in rows if r.category == "multiple"}
    assert multiple == {"rape": 11.3, "attempted_rape": 7.6, "other": 10.0, "any": 10.4}


def test_2024_participants_all_four_severity_columns():
    # Tabla 16.18 has a 4th "Violencia sexual (total)" column the other
    # chapter-16 tables don't.
    rows = parse_participants_2024(TEXT_2024_PARTICIPANTS)
    single = {r.violence_type: r.pct for r in rows if r.category == "single"}
    assert single == {"rape": 86.3, "attempted_rape": 89.5, "other": 88.0, "any": 87.9}
