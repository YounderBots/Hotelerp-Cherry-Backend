#!/usr/bin/env bash
# One-shot: import all 5 dumps, set admin password to Admin@123, restart services.
# Usage:  ./import_and_seed.sh 'THE_MYSQL_ROOT_PASSWORD'
set -euo pipefail

PW="${1:-}"
if [ -z "$PW" ]; then
  echo "Usage: $0 'MYSQL_ROOT_PASSWORD'" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
MYSQL=(mysql --no-defaults -h 127.0.0.1 -P 3306 -u root -p"$PW")

echo "1) Verifying MySQL access…"
"${MYSQL[@]}" -e "SELECT VERSION();" >/dev/null

echo "2) Importing dumps…"
for f in hotelerp_users hotelerp_masterdata hotelerp_hotel hotelerp_restaurant hotelerp_bar; do
  echo "   - $f"
  "${MYSQL[@]}" < "$ROOT/$f.sql"
done

echo "3) Setting admin password (admin@hotel.com -> Admin@123)…"
"${MYSQL[@]}" hotelerp_users -e \
  "UPDATE users SET Password='\$2b\$12\$g0ExlPiPDI0ZFrQbe6DzQeamf/qqrXWZGasjU2PugZrEkyDEJbxZa' WHERE Company_Email='admin@hotel.com';"

echo "4) Writing password into .env (MYSQL_PW) …"
# Escape for sed replacement
esc=$(printf '%s' "$PW" | sed -e 's/[&/\]/\\&/g')
sed -i '' "s/^MYSQL_PW=.*/MYSQL_PW=${esc}/" "$ROOT/.env"

echo "5) Restarting backend with live DB (DB_AUTO_CREATE=true)…"
pkill -f "$ROOT/.venv/bin/uvicorn" 2>/dev/null || true
sleep 1
DB_AUTO_CREATE=true bash "$ROOT/run.sh"
sleep 4

echo "6) Health + login check…"
for p in 8100 8120 8130 8040 8050 8060; do
  printf "   :%s -> " "$p"; curl -s -m3 -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:$p/healthz"
done
echo "   login round-trip:"
curl -s -m8 -X POST "http://127.0.0.1:8100/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hotel.com","password":"Admin@123"}' | head -c 400
echo
echo "DONE. Login: admin@hotel.com / Admin@123"
