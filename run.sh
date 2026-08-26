#!/usr/bin/env bash
# Launch all six HotelERP services (POSIX parity with start-network.ps1).
#
# Each service is self-configured by its OWN .env (Backend/Services/<Name>/.env),
# loaded by that service's configs/__init__.py. This script only reads
# SERVICE_HOST / SERVICE_PORT from each of those files to know where to bind.
#
# It deliberately does NOT hardcode a bind address. The previous version passed
# `--host 0.0.0.0` for all six services, which published the five internal
# services to the LAN and silently defeated the localhost-only topology the
# per-service .env files describe. Only LoginServices (the gateway) is meant to
# have SERVICE_HOST=0.0.0.0.
#
# Usage: ./run.sh
# Stop:  ./stop.sh   (or kill the PIDs in .run-logs/pids.txt)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

SVC_DIR="$ROOT/Backend/Services"
LOGDIR="$ROOT/.run-logs"
mkdir -p "$LOGDIR"
PIDFILE="$LOGDIR/pids.txt"
: > "$PIDFILE"

# Prefer a project virtualenv if one exists, else whatever python is on PATH.
if [ -x "$ROOT/.venv/bin/python" ]; then
  PY="$ROOT/.venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi
echo "python: $PY"

# Read one KEY from a .env file without sourcing it (a .env holds secrets and
# must never be executed as shell).
read_env() {
  local file="$1" key="$2"
  [ -f "$file" ] || return 0
  sed -n "s/^[[:space:]]*${key}[[:space:]]*=[[:space:]]*//p" "$file" | head -n1 | tr -d '\r'
}

SERVICES="LoginServices UserServices MasterDataServices HotelServices RestaurantServices BarServices"

for name in $SERVICES; do
  cwd="$SVC_DIR/$name"
  envfile="$cwd/.env"

  if [ ! -f "$envfile" ]; then
    echo "skip  $name - no .env (copy from Backend/Services/.env.example)" >&2
    continue
  fi

  port="$(read_env "$envfile" SERVICE_PORT)"
  if [ -z "$port" ]; then
    echo "skip  $name - no SERVICE_PORT in its .env" >&2
    continue
  fi

  # Default to loopback, never to 0.0.0.0: a service that forgets to declare a
  # bind address must stay private rather than becoming reachable.
  bind="$(read_env "$envfile" SERVICE_HOST)"
  [ -n "$bind" ] || bind="127.0.0.1"

  ( cd "$cwd" && exec "$PY" -m uvicorn main:app --host "$bind" --port "$port" \
      > "$LOGDIR/$name.log" 2>&1 ) &
  echo "$name=$!" >> "$PIDFILE"
  printf 'started %-20s pid %-8s %s:%s\n' "$name" "$!" "$bind" "$port"
done

echo
echo "PIDs: $PIDFILE   logs: $LOGDIR/*.log"
