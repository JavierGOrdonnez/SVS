"""Tests for the "motivos para no denunciar" extractor (T102).

Fixtures are literal `page.extract_text()` output (trimmed to the table) from
data/sources/Macroencuesta_{2019,2024}.pdf; expected values were read off the
same PDF pages. Row labels wrap inconsistently in the 2019 text (numbers can sit
on the first, middle or last label line) -- the 2019 fixtures keep that wrapping.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.macroencuesta_parser import (
    parse_non_reporting_reasons,
    _LAYOUT_2019_PARTNER, _LAYOUT_2019_SEXUAL, _LAYOUT_2024_PARTNER, _LAYOUT_2024_SEXUAL,
)

TEXT_2019_PARTNER = """Motivos para no denunciar la VFSEM de la pareja (N=frecuencia muestral, %=porcentaje)
Pareja actual Parejas pasadas
N actual y no han denunciado N
ni en el juzgado (N=565)
juzgado (N= 1520 mujeres)
Lo resolvió sola 277 49,1 811 53,4
Tuvo muy poca importancia/no era
lo suficientemente grave/no era 262 46,4 361 23,7
necesario/no lo consideró violencia
Por miedo al agresor, por temor a las
26 4,7 137 9,0
represalias
Por vergüenza, apuro, no quería que
32 5,7 160 10,5
nadie lo supiera
Carece/carecía de recursos
15 2,6 47 3,1
económicos propios
La pareja u otra persona se lo ha
1 0,2 9 0,6
impedido o la ha disuadido/disuadió
Se separó/terminó la relación (solo
en el caso de violencia de parejas - - 483 31,8
pasadas)
Por no querer que
arresten/arrestaran a su pareja o 6 1,1 38 2,5
que tuviera problemas con la policía
(NO LEER) Otros motivos 32 5,6 61 4,0
N.C. 7 1,2 12 0,8
Pregunta de respuesta múltiple
10.2 Reacción de la pareja ante la denuncia"""

TEXT_2019_SEXUAL = """Motivos para no denunciar la violencia sexual fuera de la pareja a lo largo de la vida
(N=frecuencia muestral, %=porcentaje)
Violencia sexual Violación
(N= 184 mujeres)
(N=570)
Tuvo muy poca importancia/no era lo
suficientemente grave/no era 174 30,5 31 16,8
necesario/no lo consideró violencia
Por vergüenza, apuro, no quería que
nadie lo supiera 148 25,9 74 40,3
Otra persona la disuadió de denunciar 15 2,6 2 1,1
Era menor, era una niña 202 35,4 74 40,2
NC 5 1,0 1 0,3
Pregunta de respuesta múltiple
16.16 Asistencia a algún servicio"""

TEXT_2024_PARTNER = """CAPÍTULO 9. DENUNCIA DE LA VIOLENCIA EN LA PAREJA
Tabla 9.7 Motivos para no denunciar la VFSEM de la pareja*
Pareja actual Parejas pasadas Cualquier pareja
1. Lo resolvió sola 53,7 670.688 47,9 1.599.074 50,3 2.114.825
2. Le dio muy poca importancia/no lo consideró
suficientemente grave/no lo consideró necesario/no lo 42,8 534.980 26,7 893.016 32,0 1.344.569
consideró violencia
3. Por miedo al agresor, por temor a las represalias ¨2,5 31.149 9,4 313.700 8,2 344.849
9. Se separó/terminó la relación - - 28,4 947.241 22,5 947.241
11. La pareja u otra persona se lo impidió o la disuadió . . ¨0,8 27.837 ¨0,8 32.747
NC 6,7 83.237 3,1 103.484 4,4 183.056
1. Porcentaje sobre mujeres que han sufrido VFSEM de su pareja actual"""

TEXT_2024_SEXUAL = """16.8.1.5 Motivos para no denunciar la violencia sexual fuera de la pareja
- Los motivos más citados entre quienes han sido víctimas de una violación son “era menor,
Tabla 16.30 Motivos para no denunciar la violencia sexual fuera de la pareja*
Violaciones violación sexual
%¹ %² %³
1. Le dio muy poca importancia/no lo consideró suficientemente
32,7 34,8 45,4
grave/no lo consideró necesario/no lo consideró violencia
5. Temor a que no la creyeran 21,4 17,9 9,9
6. Era menor, era una niña 37,9 35,2 33,8
8. Carecía de recursos económicos propios ¨2,4 ¨1,5 ¨1,0
9. Fue a otro lugar para obtener ayuda ¨1,8 . ¨0,9
1. Porcentaje sobre el total de mujeres que han sufrido una violación"""


def _by(rows):
    return {(r.group, r.reason): r for r in rows}


def test_2019_partner_wrapped_labels():
    r = _by(parse_non_reporting_reasons(TEXT_2019_PARTNER, "partner", "Motivos para no denunciar la VFSEM", _LAYOUT_2019_PARTNER))
    assert (r["current_partner", "resolved_alone"].n, r["current_partner", "resolved_alone"].pct) == (277, 49.1)
    assert r["past_partners", "low_importance"].pct == 23.7
    assert r["past_partners", "fear_of_aggressor"].n == 137
    assert r["current_partner", "shame"].pct == 5.7
    assert r["past_partners", "no_resources"].pct == 3.1          # key is on the line *before* the numbers
    assert r["past_partners", "prevented_by_other"].pct == 0.6    # key is on the line *after* the numbers
    assert r["past_partners", "relationship_ended"].pct == 31.8
    assert r["current_partner", "relationship_ended"].pct is None  # '-' = not asked
    assert r["past_partners", "avoid_arrest"].pct == 2.5
    assert r["past_partners", "other"].pct == 4.0
    assert r["current_partner", "nc"].pct == 1.2
    assert len(r) == 20  # 10 reasons x 2 groups; header/trailing lines produce nothing


def test_2019_sexual():
    r = _by(parse_non_reporting_reasons(TEXT_2019_SEXUAL, "outside_partner", "Motivos para no denunciar la violencia sexual", _LAYOUT_2019_SEXUAL))
    assert r["any_sexual", "low_importance"].pct == 30.5
    assert r["rape", "shame"].pct == 40.3
    assert r["rape", "prevented_by_other"].n == 2
    assert r["any_sexual", "was_minor"].pct == 35.4
    assert r["rape", "nc"].pct == 0.3


def test_2024_partner_flags_and_suppression():
    r = _by(parse_non_reporting_reasons(TEXT_2024_PARTNER, "partner", "Tabla 9.7", _LAYOUT_2024_PARTNER))
    assert (r["current_partner", "resolved_alone"].pct, r["current_partner", "resolved_alone"].n) == (53.7, 670688)
    assert r["any_partner", "low_importance"].pct == 32.0
    f = r["current_partner", "fear_of_aggressor"]
    assert f.pct == 2.5 and f.low_n
    assert not r["past_partners", "fear_of_aggressor"].low_n
    assert r["current_partner", "relationship_ended"].pct is None
    assert r["current_partner", "prevented_by_other"].pct is None   # '.' = suppressed
    assert r["past_partners", "prevented_by_other"].low_n


def test_2024_sexual_by_severity():
    r = _by(parse_non_reporting_reasons(TEXT_2024_SEXUAL, "outside_partner", "Tabla 16.30 Motivos", _LAYOUT_2024_SEXUAL))
    assert r["rape", "low_importance"].pct == 32.7
    assert r["other", "low_importance"].pct == 45.4
    assert r["attempted_rape", "not_believed"].pct == 17.9
    assert r["rape", "was_minor"].pct == 37.9
    assert r["rape", "no_resources"].low_n
    assert r["attempted_rape", "went_elsewhere"].pct is None
    assert r["other", "went_elsewhere"].low_n
