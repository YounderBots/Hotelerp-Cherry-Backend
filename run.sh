#!/usr/bin/env bash
# Launch the six HotelERP services and the frontend (POSIX parity with
# start-network.ps1, which starts the frontend too).
#
# Each service is self-configured by its OWN .env (Backend/Services/<Name>/.env),
# loaded by that service's configs/__init__.py. This script only reads
# SERVICE_HOST / SERVICE_PORT from each of those files to know where to bind,
# and Frontend/.env for the dev server's host and port.
#
# It deliberately does NOT hardcode a bind address. An earlier version passed
# `--host 0.0.0.0` for all six services, which published the five internal
# services to the LAN and silently defeated the localhost-only topology the
# per-service .env files describe. Only LoginServices (the gateway) is meant to
# have SERVICE_HOST=0.0.0.0.
#
# Usage: ./run.sh [--no-frontend] [--no-wait]
# Stop:  ./stop.sh   (or kill the PIDs in .run-logs/pids.txt)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

SVC_DIR="$ROOT/Backend/Services"
LOGDIR="$ROOT/.run-logs"
mkdir -p "$LOGDIR"
PIDFILE="$LOGDIR/pids.txt"

WITH_FRONTEND=1
WAIT_FOR_READY=1
for arg in "$@"; do
  case "$arg" in
    --no-frontend) WITH_FRONTEND=0 ;;
    --no-wait)     WAIT_FOR_READY=0 ;;
    -h|--help)     sed -n '1,17p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------
# `command -v python3` is NOT enough to know python3 works. On Windows, an "App
# execution alias" puts a Microsoft Store stub named python3 on PATH ahead of
# any real install. It is executable, so `command -v` finds it, but running it
# prints "Python was not found; run without arguments to install from the
# Microsoft Store" and exits 49. Every service then "started" and died
# instantly, leaving a one-line log and a script that reported six successes.
#
# So: test each candidate by actually running it, and take the first that works.
py_works() {
  [ -n "${1:-}" ] || return 1
  [ -x "$1" ] || command -v "$1" >/dev/null 2>&1 || return 1
  "$1" -c 'import sys; raise SystemExit(0)' >/dev/null 2>&1
}

PY=""
for candidate in \
    "$ROOT/.venv/bin/python" \
    "$ROOT/.venv/Scripts/python.exe" \
    "$(command -v python3 2>/dev/null || true)" \
    "$(command -v python 2>/dev/null || true)"; do
  if py_works "$candidate"; then PY="$candidate"; break; fi
done

if [ -z "$PY" ]; then
  echo "ERROR: no working Python interpreter found." >&2
  echo "  Tried: .venv, python3, python (all on PATH)." >&2
  echo "  If 'python3' exists but fails, it is probably the Microsoft Store" >&2
  echo "  alias — disable it under Settings > Apps > App execution aliases." >&2
  exit 1
fi
echo "python: $PY  ($("$PY" -c 'import sys; print(sys.version.split()[0])'))"

if ! "$PY" -c 'import uvicorn' >/dev/null 2>&1; then
  echo "ERROR: uvicorn is not installed for $PY" >&2
  echo "  Run: \"$PY\" -m pip install -r Backend/requirements.txt" >&2
  exit 1
fi

# Read one KEY from a .env file without sourcing it (a .env holds secrets and
# must never be executed as shell).
read_env() {
  local file="$1" key="$2"
  [ -f "$file" ] || return 0
  sed -n "s/^[[:space:]]*${key}[[:space:]]*=[[:space:]]*//p" "$file" | head -n1 | tr -d '\r'
}

# ---------------------------------------------------------------------------
# Refuse to start on top of a stack that is already running
# ---------------------------------------------------------------------------
# Starting a second uvicorn on a taken port fails with "only one usage of each
# socket address is normally permitted", which lands in the log rather than the
# terminal — the same silent failure this script exists to stop making.
port_busy() {
  if command -v netstat >/dev/null 2>&1; then
    netstat -an 2>/dev/null | grep -qE "[:.]$1[[:space:]]+.*LISTEN"
  else
    return 1
  fi
}

# Whether anything at all is already listening decides how pids.txt is handled,
# so it has to be known BEFORE the file is touched. Truncating first and
# discovering the ports were busy afterwards would leave ./stop.sh with an
# empty pidfile and the running stack orphaned — a worse failure than the one
# this guard exists to catch.
ALL_PORTS=""
for name in LoginServices UserServices MasterDataServices HotelServices RestaurantServices BarServices; do
  p="$(read_env "$SVC_DIR/$name/.env" SERVICE_PORT)"
  [ -n "$p" ] && ALL_PORTS="$ALL_PORTS $p"
done
if [ "$WITH_FRONTEND" = "1" ]; then
  p="$(read_env "$ROOT/Frontend/.env" VITE_DEV_PORT)"; [ -n "$p" ] || p="5173"
  ALL_PORTS="$ALL_PORTS $p"
fi

BUSY_COUNT=0
TOTAL_COUNT=0
for p in $ALL_PORTS; do
  TOTAL_COUNT=$((TOTAL_COUNT + 1))
  port_busy "$p" && BUSY_COUNT=$((BUSY_COUNT + 1))
done

if [ "$TOTAL_COUNT" -gt 0 ] && [ "$BUSY_COUNT" -eq "$TOTAL_COUNT" ]; then
  echo "everything is already listening — nothing to start."
  echo "Run ./stop.sh first if you want to restart."
  exit 0
fi

if [ "$BUSY_COUNT" -eq 0 ]; then
  # Clean slate: no stale pid can refer to a process still holding a port.
  : > "$PIDFILE"
else
  # Partial start. Append, so the pids of whatever is already up survive and
  # ./stop.sh can still stop the whole stack. Stale entries are harmless —
  # stop.sh reports them as "already gone".
  echo "note: $BUSY_COUNT of $TOTAL_COUNT ports already in use; starting the rest" >&2
  touch "$PIDFILE"
fi

STARTED=""
FAILED=""

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
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

  if port_busy "$port"; then
    echo "skip  $name - port $port is already in use (already running?)" >&2
    continue
  fi

  ( cd "$cwd" && exec "$PY" -m uvicorn main:app --host "$bind" --port "$port" \
      > "$LOGDIR/$name.log" 2>&1 ) &
  echo "$name=$!" >> "$PIDFILE"
  printf 'starting %-20s pid %-8s %s:%s\n' "$name" "$!" "$bind" "$port"
  STARTED="$STARTED $name:$port"
done

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
if [ "$WITH_FRONTEND" = "1" ]; then
  fe_env="$ROOT/Frontend/.env"
  fe_host="$(read_env "$fe_env" VITE_DEV_HOST)"; [ -n "$fe_host" ] || fe_host="0.0.0.0"
  fe_port="$(read_env "$fe_env" VITE_DEV_PORT)"; [ -n "$fe_port" ] || fe_port="5173"

  if [ ! -d "$ROOT/Frontend/node_modules" ]; then
    echo "skip  Frontend - node_modules missing (run: cd Frontend && npm install)" >&2
  elif port_busy "$fe_port"; then
    echo "skip  Frontend - port $fe_port is already in use (already running?)" >&2
  else
    # Vite's entry script is run directly, NOT through `npm run dev` or `npx`.
    # Both of those sit in the middle as a parent process, so the pid recorded
    # here is the wrapper's; ./stop.sh kills it, node keeps running, and the
    # dev server carries on holding the port while claiming to be stopped.
    # `exec node <entry>` makes the recorded pid the server itself.
    ( cd "$ROOT/Frontend" \
      && exec node node_modules/vite/bin/vite.js --host "$fe_host" --port "$fe_port" \
        > "$LOGDIR/Frontend.log" 2>&1 ) &
    echo "Frontend=$!" >> "$PIDFILE"
    printf 'starting %-20s pid %-8s %s:%s\n' "Frontend" "$!" "$fe_host" "$fe_port"
    STARTED="$STARTED Frontend:$fe_port"
  fi
fi

# ---------------------------------------------------------------------------
# Verify. "started" is not the same as "listening".
# ---------------------------------------------------------------------------
if [ "$WAIT_FOR_READY" = "1" ] && [ -n "$STARTED" ]; then
  echo
  echo "waiting for services to answer..."
  for entry in $STARTED; do
    name="${entry%%:*}"
    port="${entry##*:}"
    ok=0
    # ~20s: enough for a cold import of SQLAlchemy plus a first DB connection.
    for _ in $(seq 1 40); do
      if curl -fsS -m 2 -o /dev/null "http://127.0.0.1:$port/healthz" 2>/dev/null; then ok=1; break; fi
      # The frontend has no /healthz; any answer on / means Vite is serving.
      if [ "$name" = "Frontend" ] && curl -fsS -m 2 -o /dev/null "http://127.0.0.1:$port/" 2>/dev/null; then ok=1; break; fi
      sleep 0.5
    done
    if [ "$ok" = "1" ]; then
      printf '  ok    %-20s http://127.0.0.1:%s\n' "$name" "$port"
    else
      printf '  FAIL  %-20s see %s\n' "$name" "$LOGDIR/$name.log" >&2
      tail -n 3 "$LOGDIR/$name.log" 2>/dev/null | sed 's/^/          /' >&2
      FAILED="$FAILED $name"
    fi
  done
fi

echo
echo "PIDs: $PIDFILE   logs: $LOGDIR/*.log"

if [ -n "$FAILED" ]; then
  echo "FAILED:$FAILED" >&2
  exit 1
fi
