# End-to-end suites

These drive the **running** system over HTTP — the real gateway, the real MySQL
schemas, the same request shapes the SPA sends. `Backend/tests/` next door is
the offline suite: in-process, SQLite, no services required. Both matter, and
they catch different things.

```bash
./run.sh                                # start the six services
python Backend/tests/e2e/run_all.py     # run every suite
python Backend/tests/e2e/crud.py        # or one at a time
```

Exit code 0 when everything passes.

## What is here

| Suite | Covers |
|---|---|
| `crud.py` | Master Data create/read/update/delete, duplicates, blank and over-length input, unicode round-trip |
| `crud2.py` | Country/currency, discount, tax, room types — the entities with foreign keys and percentages |
| `reservation_flow.py` | Availability → quote → book → check in → part payment → settle → check out, plus cancel, no-show, double-booking, and the rules that must refuse |
| `fnb_flow.py` | Restaurant and bar: order → kitchen ticket → bill → payment, with the money guards |
| `hotel_ops_flow.py` | Housekeeping tasks, room incidents with an attachment, guest enquiries, night-audit reads |
| `security.py` | Missing/forged/tampered tokens, role authorisation, self-service scoping, password change, credential handling, login rate limiting |

`api.py` is the shared gateway client. It waits out the login rate limiter,
because `security.py` exhausts it on purpose.

## Credentials

Every suite signs in with the password the seed gives all accounts, so they
expect a **freshly seeded demo database**. Against a deployment whose passwords
have been rotated -- which every production deployment must do -- either point
them at the new one:

```bash
E2E_PASSWORD='the-new-password' python Backend/tests/e2e/run_all.py
```

...which works when the accounts still share a password, or reseed first. The
suites are not a production health check; `Backend/tools/preflight.py` is.

## Why these exist

Each one was written against a bug the offline suite could not see:

* a Master Data screen whose **Add and Edit both 500'd** because the endpoint
  demanded a string where the picker sends a number;
* over-length input reaching MySQL and coming back as **`Internal server
  error`** instead of a message naming the field;
* a bill generated with a **negative grand total** from a flat discount larger
  than the order;
* an endpoint returning the **raw SQL statement** to the browser on failure;
* a housekeeping task assigned to an **employee id that is not a user**;
* a guest **email never validated** anywhere but the browser;
* a payment recorded against a **payment method the property has not
  configured**.

None of those is visible from the code alone, and none of them is a unit.

## What they write

Each suite cleans up what it can. Some rows cannot be removed and should not
be: a reservation that has taken money, and a settled bill, are financial
records the API refuses to delete. A run therefore leaves a handful behind.

**Run these against a demo or staging database, never a property's live one.**
`python Backend/tools/seed_demo_data.py --confirm` rebuilds a clean dataset.

## Browser-side counterparts

`Frontend/e2e/` holds the same idea for the SPA: every route loaded and driven
in a real browser. See its README.
