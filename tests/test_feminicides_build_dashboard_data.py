"""Regression test for src/feminicides/build_dashboard_data.py's new
`relationship` key (T97) -- pareja/expareja + cohabitation breakdown, read
from the parsed feminicide JSON but never previously surfaced on the
dashboard.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.feminicides.build_dashboard_data import build


def test_relationship_key_present_for_every_timeline_year():
    result = build()
    rel = result["relationship"]

    assert rel["years"] == result["timeline"]["years"]
    assert len(rel["type_breakdown"]) == len(rel["years"])
    assert len(rel["cohabitation_breakdown"]) == len(rel["years"])


def test_relationship_type_breakdown_has_no_gaps_2003_2026():
    result = build()
    rel = result["relationship"]

    # unlike timeline.age_breakdown, every year (incl. the 2003-2005 legacy
    # stub reports) has relationship_type/cohabitation data -- no None entries.
    assert all(tb is not None for tb in rel["type_breakdown"])
    assert all(cb is not None for cb in rel["cohabitation_breakdown"])


def test_pareja_expareja_labels_present_every_year():
    result = build()
    rel = result["relationship"]

    for tb in rel["type_breakdown"]:
        labels = {row["label"] for row in tb}
        assert "Pareja" in labels
        assert any(l.startswith("Expareja") for l in labels)
