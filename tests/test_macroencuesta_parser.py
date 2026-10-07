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
    parse_injuries_2019,
    parse_medical_care_2019,
    parse_psychological_2019,
    parse_substance_use_2019,
    parse_disability_2019,
    parse_work_absence_2019,
    parse_self_perceived_health_2019,
    parse_suicidal_ideation_2019,
    parse_injuries_2024,
    parse_injury_types_2024,
    parse_medical_care_2024,
    parse_psychological_2024,
    parse_psychological_by_severity_2024,
    parse_psychological_types_2024,
    parse_substance_use_2024,
    parse_substance_use_types_2024,
    parse_disability_2024,
    parse_work_absence_2024,
    parse_self_perceived_health_2024,
    parse_suicidal_ideation_2024,
    parse_insecurity_streets_2024,
    parse_insecurity_known_person_2024,
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


def _find_c(rows, category, **extra):
    """Like _find but for ConsequenceStat, which has no .key -- matches on
    category plus any other field (item, violence_type, timeframe, ...)."""
    matches = [r for r in rows if r.category == category and all(getattr(r, k) == v for k, v in extra.items())]
    assert len(matches) == 1, f"expected exactly one match for category={category!r} {extra}, got {matches}"
    return matches[0]


# ── 2019: injuries (Tabla headline p.162 + tipos de lesiones p.163) ──
TEXT_2019_INJURIES = """Sí, alguna lesión 100 16,2 19 3,1 4 0,6 80 37,8
No, ninguna
518 83,5 599 96,6 614 99,1 130 61,2
lesión
NC 2 0,4 2 0,4 2 0,4 2 1,0
Total 620 100 620 100 620 100 213 100
Tipos de lesiones a consecuencia de la violencia sexual sufrida fuera del ámbito de la pareja
Tuvo Ud. cortes, rasguños,
69 11,1 53 25,0
moratones o dolores
Tuvo Ud. lesiones en sus ojos u
oídos, esguinces, luxaciones o 17 2,8 16 7,7
quemaduras
Tuvo Ud. heridas profundas,
fracturas de huesos, dientes
14 2,2 14 6,4
rotos, lesiones internas o
cualquier otra lesión similar
Tuvo Ud. un aborto involuntario 10 1,6 9 4,0
Tuvo Ud. lesiones en los
44 7,0 40 18,7
genitales
Ha contraído Ud. alguna
enfermedad de transmisión
5 0,8 5 2,5
sexual como VIH, hepatitis,
gonorrea, clamidia, sífilis, etc.
Le ha producido algún daño físico
permanente (cicatrices, pérdida
8 1,2 8 3,6
de visión o audición, problemas
respiratorios crónicos,…)
Ninguna (excluyente) 518 83,5 130 61,2
NC (excluyente) 2 0,4 2 1,0
16.10 Asistencia sanitaria como consecuencia de la violencia sexual fuera de la pareja"""

# ── 2019: medical care (p.164) ──
TEXT_2019_MEDICAL_CARE = """Asistencia sanitaria como consecuencia de la violencia sexual fuera de la pareja a lo largo de la
vida
Sí, tuve que permanecer en el hospital 13 2,1 11 5,1
Sí, me atendió alguien de los servicios
médicos (consulta médica,
32 5,2 27 12,7
enfermería...), pero no tuve que
permanecer en el hospital
No, no la necesité 490 79,0 120 56,5
No, pero debería haberla recibido 79 12,7 49 22,9
N.C. 6 1,0 6 2,8
Total 620 100,0 213 100,0
16.11 Consecuencias psicológicas derivadas de la violencia sexual fuera de la pareja"""

# ── 2019: psychological consequences (p.164-165) -- includes the prose
# paragraph whose "57,4% ... 55,9% ... 49,6% ... 16%" line has exactly 4
# numeric tokens, the same count the real "Depresión" table rows have. This
# is the regression fixture for the marker-collision bug caught during
# development (see parse_psychological_2019's own comment): the prose comes
# BEFORE "Depresión" here, so _section's "Depresión" start marker must
# exclude it, proving the fix still holds.
TEXT_2019_PSYCHOLOGICAL = """16.11 Consecuencias psicológicas derivadas de la violencia sexual fuera de la pareja a
lo largo de la vida
El 53% de las mujeres que han sufrido violencia sexual fuera de la pareja dicen que ésta ha tenido
para ellas consecuencias psicológicas, porcentaje que asciende al 78,9% entre las víctimas de
una violación. El 19,7% de las víctimas de violencia sexual afirma que a raíz de los episodios de
violencia sufrieron depresión, el 30,8% pérdida de autoestima, el 32,5% ansiedad o fobias, entre
otras consecuencias. Las víctimas de una violación dicen que los episodios de violencia sexual
les produjeron consecuencias psicológicas en porcentajes bastante más altos (39,8% depresión,
57,4% pérdida de autoestima, 55,9% ansiedad o fobias, 49,6% desesperación o fobias, 16%
pensamientos o intentos de suicidio, entre otras).
Depresión 122 19,7 85 39,8
Pérdida de autoestima 191 30,8 122 57,4
Ansiedad/fobias/ataques de
201 32,5 119 55,9
pánico
Desesperación/sensación de
197 31,8 106 49,6
impotencia
Problemas de concentración,
87 14,0 58 27,5
falta de memoria
Problemas de sueño o
118 19,0 77 36,0
alimentación
Dolor recurrente en algunas
51 8,2 43 20,4
partes de su cuerpo
Autolesionarse/pensamientos
49 7,9 34 16,0
de suicidio
Ninguno (excluyente) 286 46,2 42 20,0
N.C. (excluyente) 5 0,9 2 1,1
16.12 Discapacidad como consecuencia de la violencia sexual fuera de la pareja a lo
largo de la vida"""

# ── 2019: disability (p.165) ──
TEXT_2019_DISABILITY = """16.12 Discapacidad como consecuencia de la violencia sexual fuera de la pareja a lo
largo de la vida
Sí 26 14,3
No 155 84,2
N.C. 3 1,4
Total 185 100
16.13 Absentismo laboral como consecuencia de la violencia sexual fuera de la pareja"""

# ── 2019: work absence (p.165-166) ──
TEXT_2019_WORK_ABSENCE = """16.13 Absentismo laboral como consecuencia de la violencia sexual fuera de la pareja
Absentismo laboral o estudiantil como consecuencia de la violencia sexual fuera de la pareja
Sí 63 10,1
No 509 82,1
En ese momento no trabajaba/no estudiaba 44 7,2
N.C. 4 0,6
Total 620 100
16.14 Consumo de sustancias como consecuencia de la violencia sexual fuera de la
pareja a lo largo de la vida"""

# ── 2019: substance use (p.166) ──
TEXT_2019_SUBSTANCE_USE = """16.14 Consumo de sustancias como consecuencia de la violencia sexual fuera de la
pareja a lo largo de la vida
Sí, medicamentos 49 7,9 35 16,5
Sí, alcohol 34 5,5 26 12,2
Sí, drogas 18 2,8 16 7,4
No, nada (excluyente) 539 86,9 155 73,1
N.C.(excluyente) 3 0,4 1 0,3
16.15 Denuncia de la violencia sexual fuera de la pareja a lo largo de la vida"""

# ── 2019: self-perceived health (p.175-176) ──
TEXT_2019_HEALTH = """Estado de salud autopercibido en los 12 meses previos a las entrevistas (N=frecuencia muestral,
%=porcentaje)
Muy bueno 117 18,8 34 16,1 1.720 19,2
Bueno 281 45,3 86 40,6 4.374 48,9
Estado de
Regular 143 23,0 51 24,1 2.208 24,7
salud en el
Malo 54 8,8 25 12,0 479 5,4
último año
Muy malo 25 4,1 15 7,2 151 1,7
N.C. 0 0,0 0 0,0 5 0,1
Síntomas de mala salud sufridos con frecuencia en los 12 meses previos a las entrevistas"""

# ── 2019: suicidal ideation (p.178) ──
TEXT_2019_SUICIDAL = """Tenencia Sí 172 27,7 81 38,3 703 7,9
pensamientos No 442 71,3 127 59,7 8212 91,9
suicidas*** N.C. 6 1,0 4 2,0 21 0,2"""

# ── 2024: injuries (Tabla 16.46 headline, p.275 + Tabla 16.47 by severity, p.276) ──
TEXT_2024_INJURIES = """Tabla 16.46 Lesiones a lo largo de la vida, en los últimos 4 años, y en los últimos 12 meses como consecuencia de la
violencia sexual fuera de la pareja
Sí 11,6 1,7 354.954 2,2 0,3 67.333 ¨0,7 ¨0,1 20.043
IC 95% (10,1 - 13,3) (1,4 - 1,9) (1,5 - 3,0) (0,2 - 0,4) (0,3 - 1,2) (0,0 - 0,2)
No 85,2 97,9 94,2 99,2 95,8 99,4
NC 3,1 0,5 3,6 0,5 3,6 0,5
Total 100,0 100,0 100,0 100,0 100,0 100,0
Violaciones
Sí 33,8 224.853 7,9 52.438 ¨2,5 16.970
IC 95% (28,8 - 39,0) (5,3 - 11,2) (1,2 - 4,7)
Intentos de violación
Sí 19,8 131.367 ¨3,6 24.062 . .
IC 95% (15,7 - 24,4) (2,0 - 6,1) .
Otras formas de violencia sexual
Sí 6,4 171.000 1,4 37.415 ¨0,3 8.939
IC 95% (5,1 - 7,8) (0,9 - 2,1) (0,1 - 0,8)"""

# ── 2024: injury types (Tabla 16.48, p.277) ──
TEXT_2024_INJURY_TYPES = """Cortes, rasguños, moratones o dolores 24,6 163.835 15,3 101.659 4,0 108.136
Lesiones en sus ojos u oídos, esguinces,
¨2,9 19.149 ¨2,1 14.223 ¨1,0 26.849
luxaciones o quemaduras
Heridas profundas, fracturas de huesos,
dientes rotos, lesiones internas o ¨2,7 18.192 ¨1,7 11.143 ¨0,6 15.413
cualquier otra lesión similar
Aborto involuntario ¨2,7 17.814 ¨1,6 10.807 ¨0,5 14.649
Lesiones en los genitales 12,2 81.068 ¨5,7 37.813 1,5 39.924
Infección de transmisión sexual (de forma
temporal o crónica) como VIH, hepatitis, 8,3 55.292 ¨3,9 25.946 1,3 35.987
gonorrea, clamidia, sífilis, etc.
Algún daño físico permanente (cicatrices,
pérdida de visión o audición, problemas ¨2,2 14.925 ¨1,6 10.889 ¨0,5 13.877
respiratorios crónicos, etc.)
Alguna otra lesión de tipo físico 6,0 40.127 ¨2,8 18.502 1,3 34.643"""

# ── 2024: medical care (Tabla 16.49, p.277-278) ──
TEXT_2024_MEDICAL_CARE = """Sí, tuve que permanecer en el hospital ¨2,0 13.438 ¨1,6 10.568 ¨0,6 15.045
Sí, me atendió alguien de los servicios
médicos, pero no tuve que 7,2 48.250 ¨4,3 28.242 1,7 44.484
permanecer en el hospital
No, no la necesité 65,2 434.428 80,3 532.888 90,1 2.418.900
No, pero debería haberla recibido 21,8 144.884 11,9 78.979 6,7 178.610
NC ¨3,7 24.811 ¨1,9 12.612 ¨1,0 27.530"""

# ── 2024: psychological consequences overall (Tabla 16.50, p.278) ──
TEXT_2024_PSYCHOLOGICAL = """Sí 53,8 7,7 1.647.557
IC 95% (51,3 - 56,4) (7,2 - 8,3)
No 43,9 91,9
NC 2,2 0,3
Total 100,0 100,0"""

# ── 2024: psychological consequences by severity (Tabla 16.51, p.279) ──
TEXT_2024_PSYCHOLOGICAL_BY_SEVERITY = """Sí 77,1 513.013 69,2 458.808 50,2 1.347.918
IC 95% (72,2 - 81,4) (64,0 - 74,0) (47,5 - 52,9)
No 20,3 26,7 47,7
NC ¨2,6 ¨4,1 2,1
Total 100,0 100,0 100,0"""

# ── 2024: psychological consequence types (Tabla 16.52, p.280) ──
TEXT_2024_PSYCHOLOGICAL_TYPES = """Depresión 35,1 233.706 22,0 145.831 10,2 274.696
Pérdida de autoestima 56,0 373.077 39,2 259.823 25,3 679.589
Ansiedad/fobias/ataques de pánico 50,9 338.966 38,2 253.697 22,3 598.160
Desesperación, sensación de impotencia 42,1 279.992 40,0 265.436 29,7 796.034
Problemas de concentración, falta de memoria 26,1 173.867 17,4 115.414 9,2 246.126
Problemas de sueño o alimentación 37,0 246.407 27,4 181.933 13,9 374.079
Dolor recurrente en algunas partes de su cuerpo 15,2 100.914 8,7 57.816 2,8 75.657
Autolesionarse/pensamientos o intentos de suicidio 13,8 92.149 8,7 57.867 3,3 87.319"""

# ── 2024: substance use overall (Tabla 16.53, p.281) ──
TEXT_2024_SUBSTANCE_USE = """Sí 21,3 18,7 6,8 8,9 1,3 271.624
IC 95% (17,1 - 26,0) (14,8 - 23,3) (5,5 - 8,2) (7,5 - 10,4) (1,1 - 1,5)
No 75,0 79,8 91,6 89,4
NC 3,7 1,5 1,6 1,8
Total 100,0 100,0 100,0 100,0"""

# ── 2024: substance use types (Tabla 16.54, p.282) ──
TEXT_2024_SUBSTANCE_USE_TYPES = """Medicamentos 11,5 76.243 10,7 70.894 3,9 105.491 5,2 157.698
Alcohol 10,6 70.598 10,2 67.347 3,3 88.119 4,4 134.476
Drogas 6,1 40.579 ¨3,3 22.075 ¨1,3 35.015 1,9 58.953"""

# ── 2024: disability (Tabla 16.55, p.282) ──
TEXT_2024_DISABILITY = """Sí ¨15,1 31.099 ¨10,9 23.965 8,3 51.100 10,4 75.029
IC 95% (9,1 - 23,1) (6,0 - 17,8) (5,6 - 11,8) (7,5 - 13,9)
No 76,9 85,2 89,0 85,8
NC ¨7,9 . ¨2,7 ¨3,8
Total 100,0 100,0 100,0 100,0"""

# ── 2024: work absence (Tabla 16.56, p.283) ──
TEXT_2024_WORK_ABSENCE = """Sí 15,1 100.291 9,1 60.174 4,3 115.294 6,1 187.121
IC 95% (11,5 - 19,3) (6,3 - 12,6) (3,3 - 5,5) (5,0 - 7,4)
No 76,0 80,8 88,5 86,0
En ese
momento no
6,7 7,3 6,3 6,6
trabajaba/
no estudiaba
NC ¨2,2 ¨2,9 ¨0,9 1,3
Total 100,0 100,0 100,0 100,0"""

# ── 2024: self-perceived health (Tabla 16.59, p.286) ──
TEXT_2024_HEALTH = """Muy bueno 11,4 10,9 14,6 14,7 24,2
Bueno 33,3 32,5 43,7 42,6 43,7
Regular 36,9 39,4 29,8 30,8 24,3
Malo 11,2 10,3 7,9 8,0 5,5
Muy malo 7,2 6,8 3,9 3,8 2,0
NC . . . . 0,3"""

# ── 2024: suicidal ideation (Tabla 16.62, p.289) ──
TEXT_2024_SUICIDAL = """Sí 41,3 35,9 22,9 23,8 733.707 5,9
No 54,3 60,3 74,2 73,1 92,8
NC ¨4,4 ¨3,8 2,9 3,1 1,3"""

# ── 2024: insecurity, avoided streets (Tabla 16.71, p.296) ──
TEXT_2024_INSECURITY_STREETS = """Sí 63,8 63,0 60,7 59,8 1.840.402 26,3
No 36,2 37,0 39,3 40,2 73,4
NC . . . . 0,3"""

# ── 2024: insecurity, avoided being alone with known person (Tabla 16.72, p.297) ──
TEXT_2024_INSECURITY_KNOWN_PERSON = """Sí 28,1 24,7 16,9 17,6 542.152 5,0
No 69,5 73,5 82,3 81,5 94,7
NC ¨2,5 ¨1,8 ¨0,8 ¨0,8 0,4"""


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


# ── 2019 consequences (T106) ──

def test_2019_injuries_headline_by_timeframe():
    rows = parse_injuries_2019(TEXT_2019_INJURIES)
    lifetime = _find_c(rows, "injury", violence_type="any", timeframe="lifetime")
    assert (lifetime.sample_n, lifetime.pct) == (100, 16.2)
    rape = _find_c(rows, "injury", violence_type="rape", timeframe="lifetime")
    assert (rape.sample_n, rape.pct) == (80, 37.8)


def test_2019_injuries_by_type():
    rows = parse_injuries_2019(TEXT_2019_INJURIES)
    cuts_rape = _find_c(rows, "injury_type", item="cuts_bruises_pain", violence_type="rape")
    assert (cuts_rape.sample_n, cuts_rape.pct) == (53, 25.0)
    genital_any = _find_c(rows, "injury_type", item="genital_injuries", violence_type="any")
    assert (genital_any.sample_n, genital_any.pct) == (44, 7.0)


def test_2019_medical_care():
    rows = parse_medical_care_2019(TEXT_2019_MEDICAL_CARE)
    hospital_rape = _find_c(rows, "medical_care", item="hospital_stay", violence_type="rape")
    assert (hospital_rape.sample_n, hospital_rape.pct) == (11, 5.1)
    not_needed_any = _find_c(rows, "medical_care", item="not_needed", violence_type="any")
    assert (not_needed_any.sample_n, not_needed_any.pct) == (490, 79.0)


def test_2019_psychological_by_type():
    rows = parse_psychological_2019(TEXT_2019_PSYCHOLOGICAL)
    depression_rape = _find_c(rows, "psychological_type", item="depression", violence_type="rape")
    assert (depression_rape.sample_n, depression_rape.pct) == (85, 39.8)
    self_harm_any = _find_c(rows, "psychological_type", item="self_harm_suicidal_thoughts", violence_type="any")
    assert (self_harm_any.sample_n, self_harm_any.pct) == (49, 7.9)


def test_2019_psychological_derived_headline_not_corrupted_by_prose():
    """Regression test for the marker-collision bug: the prose paragraph's
    "57,4% ... 55,9% ... 49,6% ... 16%" line has 4 numeric tokens, same as a
    real table row -- if _section started at the chapter heading instead of
    "Depresión", this derived headline would be wrong."""
    rows = parse_psychological_2019(TEXT_2019_PSYCHOLOGICAL)
    headline_any = _find_c(rows, "psychological", violence_type="any")
    assert headline_any.pct == 52.9  # matches "53%" prose, complement of 46,2% + 0,9%
    headline_rape = _find_c(rows, "psychological", violence_type="rape")
    assert headline_rape.pct == 78.9  # matches "78,9%" prose exactly


def test_2019_substance_use_derived_headline():
    rows = parse_substance_use_2019(TEXT_2019_SUBSTANCE_USE)
    medication_rape = _find_c(rows, "substance_use_type", item="medication", violence_type="rape")
    assert (medication_rape.sample_n, medication_rape.pct) == (35, 16.5)
    headline_any = _find_c(rows, "substance_use", violence_type="any")
    assert headline_any.pct == 12.7
    headline_rape = _find_c(rows, "substance_use", violence_type="rape")
    assert headline_rape.pct == 26.6


def test_2019_disability():
    rows = parse_disability_2019(TEXT_2019_DISABILITY)
    assert len(rows) == 1
    assert (rows[0].sample_n, rows[0].pct) == (26, 14.3)


def test_2019_work_absence():
    rows = parse_work_absence_2019(TEXT_2019_WORK_ABSENCE)
    assert len(rows) == 1
    assert (rows[0].sample_n, rows[0].pct) == (63, 10.1)


def test_2019_self_perceived_health_three_columns():
    rows = parse_self_perceived_health_2019(TEXT_2019_HEALTH)
    very_good_any = _find_c(rows, "self_perceived_health", item="very_good", violence_type="any")
    assert (very_good_any.sample_n, very_good_any.pct) == (117, 18.8)
    very_bad_rape = _find_c(rows, "self_perceived_health", item="very_bad", violence_type="rape")
    assert (very_bad_rape.sample_n, very_bad_rape.pct) == (15, 7.2)
    good_no_violence = _find_c(rows, "self_perceived_health", item="good", violence_type="no_violence")
    assert (good_no_violence.sample_n, good_no_violence.pct) == (4374, 48.9)
    assert len(rows) == 15  # 5 labels x 3 violence_type columns, NC row excluded


def test_2019_suicidal_ideation():
    rows = parse_suicidal_ideation_2019(TEXT_2019_SUICIDAL)
    any_ = _find_c(rows, "suicidal_ideation", violence_type="any")
    assert (any_.sample_n, any_.pct) == (172, 27.7)
    rape = _find_c(rows, "suicidal_ideation", violence_type="rape")
    assert (rape.sample_n, rape.pct) == (81, 38.3)
    no_violence = _find_c(rows, "suicidal_ideation", violence_type="no_violence")
    assert (no_violence.sample_n, no_violence.pct) == (703, 7.9)


# ── 2024 consequences (T106) ──

def test_2024_injuries_headline_with_ci():
    rows = parse_injuries_2024(TEXT_2024_INJURIES)
    lifetime = _find_c(rows, "injury", violence_type="any", timeframe="lifetime")
    assert (lifetime.pct, lifetime.population_estimate) == (11.6, 354954)
    assert (lifetime.ci_low, lifetime.ci_high) == (10.1, 13.3)


def test_2024_injuries_by_severity():
    rows = parse_injuries_2024(TEXT_2024_INJURIES)
    rape_lifetime = _find_c(rows, "injury", violence_type="rape", timeframe="lifetime")
    assert (rape_lifetime.pct, rape_lifetime.population_estimate) == (33.8, 224853)
    assert (rape_lifetime.ci_low, rape_lifetime.ci_high) == (28.8, 39.0)


def test_2024_injuries_suppressed_cell_produces_no_row():
    # Intentos de violación / últimos 12 meses is suppressed (". .") in the
    # source table -- no stat should be emitted for it, not a None-valued one.
    rows = parse_injuries_2024(TEXT_2024_INJURIES)
    matches = [r for r in rows if r.violence_type == "attempted_rape" and r.timeframe == "last_12_months"]
    assert matches == []
    attempted_4y = _find_c(rows, "injury", violence_type="attempted_rape", timeframe="last_4_years")
    assert (attempted_4y.pct, attempted_4y.population_estimate) == (3.6, 24062)


def test_2024_injury_types():
    rows = parse_injury_types_2024(TEXT_2024_INJURY_TYPES)
    genital_rape = _find_c(rows, "injury_type", item="genital_injuries", violence_type="rape")
    assert (genital_rape.pct, genital_rape.population_estimate) == (12.2, 81068)
    other_physical_other = _find_c(rows, "injury_type", item="other_physical_injury", violence_type="other")
    assert (other_physical_other.pct, other_physical_other.population_estimate) == (1.3, 34643)
    assert len(rows) == 24  # 8 items x 3 severity tiers


def test_2024_medical_care_excludes_nc_row():
    rows = parse_medical_care_2024(TEXT_2024_MEDICAL_CARE)
    not_needed_other = _find_c(rows, "medical_care", item="not_needed", violence_type="other")
    assert (not_needed_other.pct, not_needed_other.population_estimate) == (90.1, 2418900)
    assert len(rows) == 12  # 4 items x 3 severity tiers, NC row excluded


def test_2024_psychological_overall():
    rows = parse_psychological_2024(TEXT_2024_PSYCHOLOGICAL)
    assert len(rows) == 1
    assert (rows[0].violence_type, rows[0].pct, rows[0].population_estimate) == ("any", 53.8, 1647557)
    assert (rows[0].ci_low, rows[0].ci_high) == (51.3, 56.4)


def test_2024_psychological_by_severity():
    rows = parse_psychological_by_severity_2024(TEXT_2024_PSYCHOLOGICAL_BY_SEVERITY)
    rape = _find_c(rows, "psychological", violence_type="rape")
    assert (rape.pct, rape.population_estimate) == (77.1, 513013)
    assert (rape.ci_low, rape.ci_high) == (72.2, 81.4)
    other = _find_c(rows, "psychological", violence_type="other")
    assert (other.pct, other.population_estimate) == (50.2, 1347918)


def test_2024_psychological_types():
    rows = parse_psychological_types_2024(TEXT_2024_PSYCHOLOGICAL_TYPES)
    self_esteem_rape = _find_c(rows, "psychological_type", item="loss_of_self_esteem", violence_type="rape")
    assert (self_esteem_rape.pct, self_esteem_rape.population_estimate) == (56.0, 373077)
    assert len(rows) == 24  # 8 items x 3 severity tiers


def test_2024_substance_use_overall_and_by_severity():
    rows = parse_substance_use_2024(TEXT_2024_SUBSTANCE_USE)
    any_ = _find_c(rows, "substance_use", violence_type="any")
    assert (any_.pct, any_.population_estimate) == (8.9, 271624)
    assert (any_.ci_low, any_.ci_high) == (7.5, 10.4)
    rape = _find_c(rows, "substance_use", violence_type="rape")
    assert rape.pct == 21.3
    assert rape.population_estimate is None  # only 'any' carries a population estimate here


def test_2024_substance_use_types():
    rows = parse_substance_use_types_2024(TEXT_2024_SUBSTANCE_USE_TYPES)
    alcohol_any = _find_c(rows, "substance_use_type", item="alcohol", violence_type="any")
    assert (alcohol_any.pct, alcohol_any.population_estimate) == (4.4, 134476)
    drugs_attempted = _find_c(rows, "substance_use_type", item="drugs", violence_type="attempted_rape")
    assert (drugs_attempted.pct, drugs_attempted.population_estimate) == (3.3, 22075)


def test_2024_disability_by_severity_and_total():
    rows = parse_disability_2024(TEXT_2024_DISABILITY)
    rape = _find_c(rows, "disability", violence_type="rape")
    assert (rape.pct, rape.population_estimate) == (15.1, 31099)
    assert (rape.ci_low, rape.ci_high) == (9.1, 23.1)
    any_ = _find_c(rows, "disability", violence_type="any")
    assert (any_.pct, any_.population_estimate) == (10.4, 75029)


def test_2024_work_absence_by_severity_and_total():
    rows = parse_work_absence_2024(TEXT_2024_WORK_ABSENCE)
    other = _find_c(rows, "work_absence", violence_type="other")
    assert (other.pct, other.population_estimate) == (4.3, 115294)
    any_ = _find_c(rows, "work_absence", violence_type="any")
    assert (any_.pct, any_.population_estimate) == (6.1, 187121)
    assert (any_.ci_low, any_.ci_high) == (5.0, 7.4)


def test_2024_self_perceived_health_includes_no_violence_comparison():
    rows = parse_self_perceived_health_2024(TEXT_2024_HEALTH)
    very_good_no_violence = _find_c(rows, "self_perceived_health", item="very_good", violence_type="no_violence")
    assert very_good_no_violence.pct == 24.2
    very_bad_any = _find_c(rows, "self_perceived_health", item="very_bad", violence_type="any")
    assert very_bad_any.pct == 3.8
    assert len(rows) == 25  # 5 labels x 5 columns (rape/attempted/other/any/no_violence)


def test_2024_suicidal_ideation_severity_any_and_no_violence():
    rows = parse_suicidal_ideation_2024(TEXT_2024_SUICIDAL)
    rape = _find_c(rows, "suicidal_ideation", violence_type="rape")
    assert rape.pct == 41.3
    any_ = _find_c(rows, "suicidal_ideation", violence_type="any")
    assert (any_.pct, any_.population_estimate) == (23.8, 733707)
    no_violence = _find_c(rows, "suicidal_ideation", violence_type="no_violence")
    assert no_violence.pct == 5.9


def test_2024_insecurity_streets():
    rows = parse_insecurity_streets_2024(TEXT_2024_INSECURITY_STREETS)
    any_ = _find_c(rows, "insecurity", item="avoided_streets_areas", violence_type="any")
    assert (any_.pct, any_.population_estimate) == (59.8, 1840402)
    no_violence = _find_c(rows, "insecurity", item="avoided_streets_areas", violence_type="no_violence")
    assert no_violence.pct == 26.3


def test_2024_insecurity_known_person():
    rows = parse_insecurity_known_person_2024(TEXT_2024_INSECURITY_KNOWN_PERSON)
    rape = _find_c(rows, "insecurity", item="avoided_being_alone_with_known_person", violence_type="rape")
    assert rape.pct == 28.1
    any_ = _find_c(rows, "insecurity", item="avoided_being_alone_with_known_person", violence_type="any")
    assert (any_.pct, any_.population_estimate) == (17.6, 542152)


def test_empty_text_produces_no_rows():
    assert parse_prevalence_2019("") == []
    assert parse_relationship_2019("") == []
    assert parse_prevalence_block_2024("", "any", "Tabla 16.1") == []
    assert parse_relationship_2024("") == []
    assert parse_frequency_2019("") == []
    assert parse_frequency_2024("") == []
    assert parse_participants_2019("") == []
    assert parse_participants_2024("") == []
    assert parse_injuries_2019("") == []
    assert parse_medical_care_2019("") == []
    assert parse_psychological_2019("") == []
    assert parse_substance_use_2019("") == []
    assert parse_disability_2019("") == []
    assert parse_work_absence_2019("") == []
    assert parse_self_perceived_health_2019("") == []
    assert parse_suicidal_ideation_2019("") == []
    assert parse_injuries_2024("") == []
    assert parse_injury_types_2024("") == []
    assert parse_medical_care_2024("") == []
    assert parse_psychological_2024("") == []
    assert parse_psychological_by_severity_2024("") == []
    assert parse_psychological_types_2024("") == []
    assert parse_substance_use_2024("") == []
    assert parse_substance_use_types_2024("") == []
    assert parse_disability_2024("") == []
    assert parse_work_absence_2024("") == []
    assert parse_self_perceived_health_2024("") == []
    assert parse_suicidal_ideation_2024("") == []
    assert parse_insecurity_streets_2024("") == []
    assert parse_insecurity_known_person_2024("") == []


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
