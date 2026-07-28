#!/usr/bin/env python3
"""Serve the SVS dashboard over the network with live-rebuild.

Pattern from finances-dashboard: basic auth + 0.0.0.0 bind for Tailscale.

Modes:
  --port PORT     Listen port (default 8080)
  --no-auth       Skip basic auth (for local dev)
  --no-watch      Disable automatic data rebuild on source changes

Env vars:
  BASIC_AUTH_USERNAME / BASIC_AUTH_PASSWORD  — if set, required for access.

Live-rebuild: on each request, checks whether any source file (CSV, raw JSON,
Python build scripts) is newer than docs/data/*.json and triggers a rebuild
before serving.  No background thread needed.
"""

import argparse
import base64
import http.server
import json
import os
import secrets
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA_DIR = DOCS / "data"
SRC_DIR = ROOT / "src"

BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME", "")
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD", "")

WATCH_PATTERNS = [
    SRC_DIR / "analysis" / "build_dashboard.py",
    SRC_DIR / "migration" / "build_dashboard_data.py",
    SRC_DIR / "mortality" / "build_dashboard_data.py",
    SRC_DIR / "feminicides" / "build_dashboard_data.py",
    SRC_DIR / "sexual_crimes" / "build_dashboard_data.py",
    SRC_DIR / "crime" / "build_dashboard_data.py",
]

_no_auth = False
_watch = True


def _newest_mtime(paths):
    latest = 0.0
    for p in paths:
        if p.is_file():
            latest = max(latest, p.stat().st_mtime)
    return latest


def _data_newest():
    return _newest_mtime(DATA_DIR.glob("*.json"))


def _sources_newest():
    candidates = list(WATCH_PATTERNS)
    candidates.extend((ROOT / "data" / "raw").glob("*.csv"))
    candidates.extend((ROOT / "data" / "raw").glob("*.json"))
    return _newest_mtime(candidates)


def maybe_rebuild():
    """Rebuild docs/data/*.json if any source is newer."""
    if not _watch:
        return
    if _sources_newest() > _data_newest():
        print("[live-rebuild] source changed — rebuilding data…")
        subprocess.run(
            [sys.executable, str(SRC_DIR / "analysis" / "build_dashboard.py")],
            cwd=str(ROOT),
            check=True,
        )
        print("[live-rebuild] done.")


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS), **kwargs)

    def log_message(self, fmt, *args):
        # Quieter logging — just method + path + status
        pass

    def do_GET(self):
        # Lazy rebuild before serving
        maybe_rebuild()
        super().do_GET()

    def end_headers(self):
        # Enable CORS for local dev
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_HEAD(self):
        maybe_rebuild()
        super().do_HEAD()


class AuthHandler(DashboardHandler):
    def do_GET(self):
        if not self._check_auth():
            return
        super().do_GET()

    def do_HEAD(self):
        if not self._check_auth():
            return
        super().do_HEAD()

    def _check_auth(self):
        if _no_auth or (not BASIC_AUTH_USERNAME):
            return True

        auth = self.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="SVS Dashboard"')
            self.end_headers()
            return False

        try:
            decoded = base64.b64decode(auth.removeprefix("Basic ")).decode("utf-8")
            username, password = decoded.split(":", 1)
        except Exception:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="SVS Dashboard"')
            self.end_headers()
            return False

        if not secrets.compare_digest(username, BASIC_AUTH_USERNAME) or \
           not secrets.compare_digest(password, BASIC_AUTH_PASSWORD):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="SVS Dashboard"')
            self.end_headers()
            return False

        return True


def main():
    global _no_auth, _watch

    parser = argparse.ArgumentParser(description="Serve SVS dashboard with live-rebuild")
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument("--no-auth", action="store_true", help="Skip basic auth")
    parser.add_argument("--no-watch", action="store_true", help="Disable auto-rebuild")
    args = parser.parse_args()

    _no_auth = args.no_auth
    _watch = not args.no_watch

    handler = AuthHandler
    server = http.server.HTTPServer(("0.0.0.0", args.port), handler)

    auth_status = "no auth" if _no_auth or not BASIC_AUTH_USERNAME else "basic auth"
    watch_status = "on" if _watch else "off"

    print(f"SVS Dashboard — http://0.0.0.0:{args.port}")
    print(f"  LAN:        http://192.168.1.22:{args.port}")
    print(f"  Tailscale:  http://100.100.85.125:{args.port}")
    print(f"  Auth:       {auth_status}")
    print(f"  Live-rebuild: {watch_status}")
    print(f"  Serving:    {DOCS}")
    print(f"  Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
