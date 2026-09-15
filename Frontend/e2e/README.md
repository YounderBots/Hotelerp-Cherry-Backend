# Browser audits

Four Playwright scripts that drive the SPA the way a client would. They need
the **whole stack running** — the six services and a server for the frontend —
and they sign in through the real login form.

```bash
./run.sh                                          # from the repo root

cd Frontend
node e2e/audit.mjs    admin@cherryhotel.com admin   # every route, one role
node e2e/interact.mjs admin@cherryhotel.com admin   # drive the controls
node e2e/perm_ui.mjs  rahul.nair@cherryhotel.com fd # controls vs permissions
node e2e/perf.mjs     admin@cherryhotel.com admin   # load times, request shape
node e2e/client_sim.mjs admin@cherryhotel.com        # one full round trip
```

`PW_PASSWORD` sets the sign-in password when it is no longer the seeded one:

```bash
PW_PASSWORD='the-new-password' node e2e/audit.mjs admin@cherryhotel.com admin
```

Each exits non-zero (or prints `!!` lines) when something is wrong, and writes
a JSON report beside itself.

| Script | What it asserts |
|---|---|
| `audit.mjs` | Every route renders: no blank page, no error boundary, no console error, no failed request, no broken image, no horizontal overflow. Pass `--width=375 --height=667` to sweep a viewport; `--shots` to save screenshots. |
| `interact.mjs` | On every table screen: search finds and misses correctly, sorting reorders, pagination advances, filters apply and clear, the Add dialog opens and refuses an empty submit, Cancel closes, a row's View and Edit open and close. |
| `perm_ui.mjs` | For each page a role can open, the Add button and the row Edit/Delete icons match that role's own permissions. A control the gateway would answer 403 to must not be drawn. **Run it per role** — that is the whole point. |
| `perf.mjs` | Time to DOM-ready and to a settled network per route, how many API calls each page issues, and whether any URL is requested twice in one load. |
| `client_sim.mjs` | One complete round trip with nothing but mouse and keyboard: sign in, dashboard, add a record (empty submit refused, duplicate refused), edit it, reload, delete it with confirmation, sign out, then check a signed-out session cannot reach a page by URL. |

## Run `perf.mjs` against the production build

`npm run dev` runs under React StrictMode, which double-invokes effects, so
every page appears to fetch everything twice. That is a development behaviour
and not what a client experiences. Measure the real thing:

```bash
npm run build
npx vite preview --port 5173 --strictPort   # the port CORS already allows
node e2e/perf.mjs admin@cherryhotel.com prod
```

Serving the preview on a different port will fail to sign in: the gateway's
`CORS_ALLOWED_ORIGINS` lists the dev port, and the browser blocks the login
request before it is sent.

## Why these exist

They were written against bugs nothing else caught: twenty-five room
photographs rendering as broken images because the URL missed its service
prefix and carried no token; every bar menu tile answering 403 because the
gateway had no permission row for that upload directory; a user's own avatar
403ing on their own profile page for every role but Admin; and one screen
fetching the same photograph seven times to draw it once.
