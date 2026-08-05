#!/usr/bin/env bash
# Launch all six HotelERP services on 0.0.0.0 (LAN-accessible).
# Usage: ./run.sh            (reads .env; DB import step must be done separately)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Load .env
set -a; . ./.env; set +a

PY="$ROOT/.venv/bin/uvicorn"
LOGDIR="$ROOT/.run-logs"
mkdir -p "$LOGDIR"

# Build a DB_URI for a given schema from the .env MySQL_* values.
db_uri() {
  local schema="$1"
  local auth="${MYSQL_USER}"
  if [ -n "${MYSQL_PW:-}" ]; then auth="${MYSQL_USER}:${MYSQL_PW}"; fi
  echo "mysql+pymysql://${auth}@${MYSQL_HOST}:${MYSQL_PORT}/${schema}"
}

# service_name  schema  port
run_service() {
  local name="$1" schema="$2" port="$3"
  local uri; uri="$(db_uri "$schema")"
  echo "  starting $name on :$port  (schema=$schema)"
  ( cd "$ROOT/Backend/Services/$name" && \
    DB_URI="$uri" \
    DB_AUTO_CREATE="${DB_AUTO_CREATE:-true}" \
    "$PY" main:app --host 0.0.0.0 --port "$port" \
      > "$LOGDIR/${name}.log" 2>&1 & echo $! > "$LOGDIR/${name}.pid" )
}

echo "Launching HotelERP backend (bind 0.0.0.0)…"
# 8020/8030/8000 are held by another long-running project → relocated to 812x/813x/8100.
run_service UserServices       hotelerp_users       8120
run_service MasterDataServices hotelerp_masterdata  8130
run_service HotelServices      hotelerp_hotel       8040
run_service RestaurantServices hotelerp_restaurant  8050
run_service BarServices        hotelerp_bar         8060
run_service LoginServices      hotelerp_users       8100   # gateway (last)

echo "PIDs written to $LOGDIR/*.pid ; logs in $LOGDIR/*.log"
