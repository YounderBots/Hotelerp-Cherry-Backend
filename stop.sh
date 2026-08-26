#!/usr/bin/env bash
# Stops every process started by run.sh (reads .run-logs/pids.txt).
# POSIX parity with stop-network.ps1.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$ROOT/.run-logs/pids.txt"

if [ ! -f "$PIDFILE" ]; then
  echo "no pids.txt - nothing to stop"
  exit 0
fi

while IFS='=' read -r name proc_id; do
  [ -n "${proc_id:-}" ] || continue
  if kill "$proc_id" 2>/dev/null; then
    echo "stopped $name (pid $proc_id)"
  else
    echo "skip $name (pid $proc_id): already gone"
  fi
done < "$PIDFILE"

rm -f "$PIDFILE"
