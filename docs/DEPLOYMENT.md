# Deployment — Cherry Hotel ERP

Written after the network-binding audit. It records what the bind addresses
are, why they are loopback, and what to change before a real deployment.

## 1. Topology

Six Python services and one Vite dev server, all started by
`start-network.ps1`. `LoginServices` is the **gateway**: the browser talks only
to it, and it proxies to the other five over loopback.

| Service | Port | Role |
|---|---|---|
| LoginServices | 8000 | gateway + auth (JWT issuance, RBAC enforcement, proxying) |
| UserServices | 8020 | users, roles, permissions |
| MasterDataServices | 8030 | rooms, taxes, statuses, lookups |
| HotelServices | 8040 | reservations, guests, housekeeping, night audit |
| RestaurantServices | 8050 | restaurant + kitchen |
| BarServices | 8060 | bar |
| Frontend (Vite) | 5173 | SPA dev server |

## 2. Bind addresses are loopback

Every service binds `127.0.0.1`. **The gateway included.**

The gateway was previously pinned to `0.0.0.0` with the comment "for LAN
access". That could never have worked and was actively harmful:

- `Frontend/.env` sets `VITE_API_BASE_URL=http://127.0.0.1:8000`, which Vite
  bakes into the bundle. A browser on any other machine resolves that address
  to **its own** loopback, so it never reaches this API. There is no dev-server
  proxy (`Frontend/vite.config.js` defines no `server.proxy`) to rewrite it.
- So the wider bind bought nothing, while making `/login_post` — the
  credential endpoint — answerable by every host on the network. That was
  confirmed empirically: the gateway answered `200` on `10.201.194.48:8000`
  and `10.54.90.167:8000` before the change.
- `CORS_ALLOWED_ORIGINS` also carried a stale `http://192.168.1.7:5173` from
  that same abandoned experiment. Removed.

There is **no containerisation** in this repository (no Dockerfile,
docker-compose, Kubernetes or Terraform), so nothing depends on the gateway
being reachable from outside the host.

## 3. Exposing the app properly

Do not widen `SERVICE_HOST`. Keep the six services on loopback and put a
reverse proxy in front of the SPA. The proxy is the only thing that should
listen on a public interface.

```
                    ┌──────────────────────────────┐
  browser ──TLS──▶  │ reverse proxy  (public iface)│
                    │  • terminates TLS             │
                    │  • serves the built SPA      │
                    │  • proxy_pass /api ──┐       │
                    └──────────────────────┼───────┘
                                           ▼
                              127.0.0.1:8000  (gateway)
                                           │ loopback only
                                           ▼
                      8020 · 8030 · 8040 · 8050 · 8060
```

Checklist before going live:

1. Build the SPA and serve the static output; do not run the Vite dev server in
   production. Point `VITE_API_BASE_URL` at the proxy's public API path.
2. Terminate TLS at the proxy.
3. Keep all six services on `127.0.0.1`.
4. Restrict `CORS_ALLOWED_ORIGINS` to the real public origin.
5. Set `ASCEND_ENV=production` in all six `.env` files.
6. Replace the shared demo passwords — see §4.
7. Rotate the JWT/session secrets — see §5.
8. Put uploads on durable storage and back them up together with the database.

## 4. Demo credentials must not ship

All ten seeded accounts share one password, supplied at seed time through
`SEED_PASSWORD`. That is deliberate for a demo and wrong for a deployment.

```bash
# unique strong password per account, printed once
python Backend/tools/rotate_passwords.py --confirm

# or provision one account's password
python Backend/tools/rotate_passwords.py --confirm --email someone@property.com

# then verify nothing is left on the demo value
python Backend/tools/preflight.py
```

`preflight.py` check 5 fails while the published demo password is live. That
is the check working, not a false positive.

Passwords are stored as bcrypt hashes and are never written to logs. The
rotation tool prints each generated password exactly once, on stdout, and
stores it nowhere — if the output is lost, rotate again; a hash cannot be
reversed.

## 5. Secrets

`JWT_SECRET_KEY`, `SESSION_SECRET` and `JWT_ISSUER` must be **identical across
all six services**, or every authenticated request returns 401. Generate them
once and distribute them; do not commit them. `.env` is git-ignored and only
`.env.example` templates are tracked.

## 6. Running it

```bash
# development
powershell -ExecutionPolicy Bypass -File .\start-network.ps1
powershell -ExecutionPolicy Bypass -File .\stop-network.ps1

# reseed the demo dataset (DESTROYS DATA)
$env:SEED_PASSWORD='choose-a-demo-password'
python Backend\tools\seed_demo_data.py --confirm
python Backend\tools\build_rbac_map.py
python Backend\tools\verify_seed.py
```