#!/usr/bin/env bash
# =============================================================================
# DEVELOPMENT SEED ONLY -- NEVER RUN THIS AGAINST PRODUCTION
# =============================================================================
# Imports the five schema dumps and resets the demo admin to a well-known
# password so a fresh clone has something to log in with.
#
# The dumps carry seeded accounts (john.doe / admin@hotel.com and two others)
# and this script sets a password that is published in the repo. Loading that
# into a live system hands anyone who has read the repo an admin login, so the
# guards below refuse to run anywhere that looks like production. Do not remove
# them; point a production deploy at a schema-only migration instead
# (see Backend/migrations).
#
# Usage:  ./import_and_seed.sh 'THE_MYSQL_ROOT_PASSWORD'
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

DB_HOST="${MYSQL_HOST:-127.0.0.1}"
DB_PORT="${MYSQL_PORT:-3306}"
DEMO_ADMIN_EMAIL="admin@hotel.com"
DEMO_ADMIN_PASSWORD="Admin@123"
# bcrypt of DEMO_ADMIN_PASSWORD
DEMO_ADMIN_HASH='$2b$12$g0ExlPiPDI0ZFrQbe6DzQeamf/qqrXWZGasjU2PugZrEkyDEJbxZa'

# ---- Guard 1: never in a production environment -----------------------------
env_name="$(printf '%s' "${ASCEND_ENV:-dev}" | tr '[:upper:]' '[:lower:]')"
case "$env_name" in
  prod|production)
    echo "REFUSING: ASCEND_ENV=$ASCEND_ENV. This script seeds a demo admin with a" >&2
    echo "password published in the repo and must never touch production." >&2
    exit 3
    ;;
esac

# ---- Guard 2: never against a remote database -------------------------------
case "$DB_HOST" in
  127.0.0.1|localhost|::1|0.0.0.0) ;;
  *)
    echo "REFUSING: MYSQL_HOST=$DB_HOST is not loopback." >&2
    echo "This script only seeds a local development database." >&2
    exit 3
    ;;
esac

PW="${1:-}"
if [ -z "$PW" ]; then
  echo "Usage: $0 'MYSQL_ROOT_PASSWORD'" >&2
  exit 2
fi

MYSQL=(mysql --no-defaults -h "$DB_HOST" -P "$DB_PORT" -u root -p"$PW")

echo "Target: $DB_HOST:$DB_PORT   (ASCEND_ENV=$env_name)"
echo "This DROPS AND REPLACES the five hotelerp_* schemas and sets the demo"
echo "admin password to a value published in this repo."
if [ -t 0 ] && [ "${SEED_ASSUME_YES:-}" != "1" ]; then
  printf 'Type "seed" to continue: '
  read -r reply
  [ "$reply" = "seed" ] || { echo "aborted"; exit 1; }
fi

echo "1) Verifying MySQL access..."
"${MYSQL[@]}" -e "SELECT VERSION();" >/dev/null

echo "2) Importing dumps..."
for f in hotelerp_users hotelerp_masterdata hotelerp_hotel hotelerp_restaurant hotelerp_bar; do
  echo "   - $f"
  "${MYSQL[@]}" < "$ROOT/$f.sql"
done

echo "3) Setting demo admin password ($DEMO_ADMIN_EMAIL -> $DEMO_ADMIN_PASSWORD)..."
"${MYSQL[@]}" hotelerp_users \
  -e "UPDATE users SET Password='${DEMO_ADMIN_HASH}' WHERE Company_Email='${DEMO_ADMIN_EMAIL}';"

# The previous version wrote MYSQL_PW into a root .env here. There is no shared
# root .env any more -- each service owns its own (see .env.example) -- so that
# step edited a file that does not exist. Set DB_URI in each service's .env.

echo
echo "DONE. Login: $DEMO_ADMIN_EMAIL / $DEMO_ADMIN_PASSWORD"
echo "Start the services with ./run.sh (or start-network.ps1 on Windows)."
