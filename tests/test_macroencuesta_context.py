"""Tests for the Macroencuesta assault-context parsers (T104): location
(Cap. 16.5/16.7) and prior online interaction (Cap. 16.6, 2024 only).
Fixtures are literal `page.extract_text()` excerpts from
data/sources/Macroencuesta_{2019,2024}.pdf."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.macroencuesta_parser import (
    parse_location_2019,
    parse_location_2024,
    parse_online_prior_2024,
)

TEXT_2019_LOCATION = """En la casa donde vivía la
114 18,5 55 25,7
entrevistada
En la casa de la persona agresora 125 20,1 61 28,6
En tiendas, hoteles, cine, teatro,
18 2,9 7 3,4
oficinas gubernamentales, etc.
En discotecas, bares, cafeterías,
111 17,8 26 12,2
pubs, restaurantes, etc.
En zonas abiertas (calles, zonas
198 32,0 72 34,1
rurales, bosques, parques)
Pregunta de respuesta múltiple."""

TEXT_2024_LOCATION = """1. En una casa 68,5 455.912 51,6 342.426 33,7 905.313
1.1. En la casa donde vivía la entrevistada 31,6 210.690 23,3 154.227 14,1 377.701
3. En el transporte público . . ¨2,1 13.680 16,8 451.588
10. Online (solo para otras formas de violencia sexual) - - - - 2,6 70.245
9. En zonas abiertas (calles, bosques, parques, etc.) 16,3 108.701 23,8 158.091 22,9 614.194"""

TEXT_2024_ONLINE = """Sí, algunos o todos los episodios sucedieron
tras haber conocido o interactuado online de 13,1 8,9 5,7
forma previa con la persona agresora
No, ninguno de los episodios sucedió tras
haber conocido o interactuado online de forma 83,7 87,0 92,2
previa con la persona agresora
NC ¨3,2 ¨4,1 2,1
Total 100,0 100,0 100,0
NC ¨1,0 ¨1,0 0,9"""


def _get(stats, key, vt):
    return next(s for s in stats if s.key == key and s.violence_type == vt)


def test_2019_location_wrapped_labels_and_both_columns():
    out = parse_location_2019(TEXT_2019_LOCATION)
    own = _get(out, "own_home", "any")
    assert (own.pct, own.sample_n) == (18.5, 114)
    assert _get(out, "own_home", "rape").pct == 25.7
    assert _get(out, "nightlife", "any").pct == 17.8
    assert _get(out, "open_areas", "rape").sample_n == 72
    assert len(out) == 10  # 5 rows x (any, rape)


def test_2024_location_values_and_markers():
    out = parse_location_2024(TEXT_2024_LOCATION)
    assert len(out) == 15
    assert (_get(out, "any_house", "rape").pct, _get(out, "any_house", "rape").population_estimate) == (68.5, 455912)
    assert _get(out, "own_home", "other").pct == 14.1
    assert _get(out, "public_transport", "rape").pct is None            # '.' suppressed
    assert _get(out, "public_transport", "attempted_rape").pct == 2.1   # '¨' kept
    assert _get(out, "online", "rape").pct is None                      # '-' not collected
    assert _get(out, "online", "other").population_estimate == 70245


def test_2024_online_prior_rows_and_stops_at_total():
    out = parse_online_prior_2024(TEXT_2024_ONLINE)
    assert len(out) == 9
    assert _get(out, "yes", "rape").pct == 13.1
    assert _get(out, "no", "other").pct == 92.2
    assert _get(out, "nc", "rape").pct == 3.2   # not the next table's NC row


def test_empty_text_produces_no_rows():
    assert parse_location_2019("") == parse_location_2024("") == parse_online_prior_2024("") == []
