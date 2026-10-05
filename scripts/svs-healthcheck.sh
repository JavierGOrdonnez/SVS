#!/usr/bin/env bash
# Health check for the SVS dashboard.
# Runs every minute from svs-healthcheck.timer; restarts the dashboard
# service if the HTTP probe fails (process down, hung, or HTTP error).
set -euo pipefail

PORT="${SVS_DASHBOARD_PORT:-8088}"
SERVICE="svs-dashboard.service"
URL="http://127.0.0.1:${PORT}/"

if ! curl --silent --show-error --max-time 10 --fail "${URL}" >/dev/null; then
    echo "[svs-healthcheck] dashboard down/unhealthy — restarting ${SERVICE}"
    systemctl --user restart "${SERVICE}"
fi
