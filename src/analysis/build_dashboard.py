"""Generate the dashboard data layer: docs/data/*.json.

One orchestrator that reads the project's processed CSVs and nested raw JSON
and emits one clean, fetch-ready JSON file per analytical domain. The web
dashboard (docs/index.html) fetches these at runtime, so there is no more
hand-copied inline data and the GitHub-Pages fetch paths resolve correctly
(files live under docs/data/, the Pages root).

Run:  uv run python src/analysis/build_dashboard.py
"""

import importlib.util
import json
import os
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent


def _load_domain(name):
    # Every domain's build script is named build_dashboard_data.py, so a
    # plain `import build_dashboard_data` would only ever bind the first
    # one loaded (sys.modules caches by that bare name) -- load each under
    # a distinct module name instead.
    path = _SRC / name / "build_dashboard_data.py"
    spec = importlib.util.spec_from_file_location(f"{name}_dashboard_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mortality_mod = _load_domain("mortality")
migration_mod = _load_domain("migration")
feminicides_mod = _load_domain("feminicides")
sexual_crimes_mod = _load_domain("sexual_crimes")
crime_mod = _load_domain("crime")

OUT_DIR = os.path.join("docs", "data")


def write(name, blob):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blob, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  wrote {path}  ({os.path.getsize(path):,} bytes)")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Building dashboard data -> {OUT_DIR}/")
    write("mortality.json", mortality_mod.build())
    write("migration.json", migration_mod.build())
    write("feminicides.json", feminicides_mod.build())
    write("sexual_crimes.json", sexual_crimes_mod.build())
    write("hate_crimes.json", crime_mod.build_hate_crimes())
    write("cohort_tenure.json", crime_mod.build_cohort_tenure())
    print("Done.")


if __name__ == "__main__":
    main()
