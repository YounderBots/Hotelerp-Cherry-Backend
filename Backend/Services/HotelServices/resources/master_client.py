"""Master Data and Users, read over HTTP from the services that own them.

WHY THIS EXISTS
    Reservation cannot be correct without Master Data: a booking has to know
    that room 20 exists, that it is a Deluxe, that a Deluxe costs 11,000 a
    night, that tax type 3 is 12% and that "Confirmed" is a real status. Those
    tables belong to MasterDataServices. Until now this service read them
    directly, as SQLAlchemy mappings onto another schema on the same MySQL
    server, and wrote three columns of `room` back the same way.

    That was one transaction and zero HTTP, and it was also a deployment
    coupling that nothing provisioned: this service's MySQL account had to
    hold privileges in two schemas it does not own. Miss them and the service
    starts cleanly, housekeeping and the night audit keep working, and every
    reservation screen answers 500 -- which is exactly what the deployment at
    168.231.103.18 did for three days over one missing GRANT.

    So the boundary is now the one the rest of the system already uses:
    HTTP, on the caller's behalf. This module asks Master Data for
    `/snapshot` -- everything a reservation needs to be interpreted or
    priced, in one round trip -- and writes room state back through
    `PUT /room/{id}/state`. The Hotel service's database account touches the
    Hotel schema and nothing else.

THROUGH THE GATEWAY, NOT TO THE PORT
    Every call goes to the login gateway -- `API_GATEWAY_URL` -- as
    `/masterdata/...` and `/user/...`, exactly as the browser's calls do. Not
    to the sibling's own port. Two reasons, and the first is the one that
    cost a day:

      * There is one address to configure, and it is the one every deployment
        already knows, because the frontend is pointed at it. A per-service
        internal URL is a second, invisible fact about the deployment; the
        live server's Hotel service spent a day calling a Master Data that
        was not at the default port, with nothing on screen to say so.

      * The gateway is where authentication and authorisation live. A call
        that goes round it is a call the permission map never sees. Going
        through it, the Hotel service can do on the caller's behalf exactly
        what the caller may do, and the map has rows for these routes
        (Backend/tools/build_rbac_map.py, SERVICE_ROWS).

    The gateway forwards the same token, so Master Data still scopes the
    snapshot by the caller's company.

WHAT IT COSTS, AND WHAT IT DOES NOT
    One GET per request that needs master data, memoised for the life of the
    request, so a booking that validates a status, a payment method, an
    identity type, five rooms and their rate card makes one call, not seven.
    On loopback that is a millisecond or two, against a database round trip
    of about the same.

    The double-booking guard does NOT move here. It never depended on Master
    Data's rows, only on a row to lock; `reservation_rules.lock_rooms` now
    locks a row in this service's own `room_lock` table instead, and the
    overlap check it guards reads `room_reservation`, which is also ours. The
    one transaction that matters -- check availability, then insert -- is
    still one transaction.

THE RECORDS
    Plain frozen dataclasses named by the public field names the Master Data
    API already uses (`room_no`, `daily_rate`, `tax_percentage`). They carry
    only what Reservation and Housekeeping read. Values arrive as the API
    sends them -- `room_type_id` and the percentages are strings in that
    schema and stay strings here; the rules module already converts at the
    point of use.

WHEN THE OTHER SERVICE IS DOWN
    `MasterDataUnavailable`. The controllers turn it into a 503 that names the
    service, and /readyz reports the same thing before any request does. A
    503 rather than a 500 because the code did nothing wrong; a dependency is
    not there.
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass
from typing import Optional, Protocol

import httpx

from configs.base_config import BaseConfig

logger = logging.getLogger(__name__)

ACTIVE = "ACTIVE"
TIMEOUT_SECONDS = 5.0

MASTER = "master"
USERS = "users"
ENV_VAR = "API_GATEWAY_URL"
# The gateway's proxy prefix for each sibling: the browser calls
# /masterdata/room; so does this service.
PREFIX = {MASTER: "masterdata", USERS: "user"}


class MasterDataUnavailable(Exception):
    """A sibling service could not be reached or refused this service.

    Carries the address this service tried and the .env key that set it, so
    the 503 can say "Master Data at http://127.0.0.1:8000 (API_GATEWAY_URL)"
    to whoever is looking -- which, on a box whose main.py predates /readyz,
    is the browser and not a journal.
    """

    def __init__(self, service: str, detail: str, *, base_url: str = "", env_var: str = ""):
        self.service = service
        self.detail = detail
        self.base_url = base_url
        self.env_var = env_var
        super().__init__(f"{service}: {detail}")

    @property
    def label(self) -> str:
        return {MASTER: "Master Data", USERS: "Users"}.get(self.service, self.service)

    def where(self) -> str:
        """`at http://127.0.0.1:8000 (API_GATEWAY_URL)`, or '' when unknown."""
        if not self.base_url:
            return ""
        return f" at {self.base_url}" + (f" ({self.env_var})" if self.env_var else "")


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Room:
    id: int
    room_no: str
    room_name: Optional[str] = None
    room_type_id: Optional[str] = None      # a string in the master schema
    bed_type_id: Optional[str] = None
    max_adult: Optional[str] = None
    max_child: Optional[str] = None
    booking_status: Optional[str] = None    # Available | Reserved | Occupied
    working_status: Optional[str] = None    # Ready | Not Ready | Not Assigne
    room_status: Optional[str] = None       # Blocking | UnBlocking (legacy: ACTIVE)
    status: str = ACTIVE


@dataclass(frozen=True)
class RoomType:
    id: int
    room_type_name: str
    room_cost: Optional[float] = None
    bed_cost: Optional[float] = None
    daily_rate: Optional[float] = None
    weekly_rate: Optional[float] = None
    bed_only_rate: Optional[float] = None
    bed_breakfast_rate: Optional[float] = None
    half_board_rate: Optional[float] = None
    full_board_rate: Optional[float] = None
    status: str = ACTIVE


@dataclass(frozen=True)
class TaxType:
    id: int
    tax_name: str
    tax_percentage: Optional[str] = None    # free text in the master schema
    status: str = ACTIVE


@dataclass(frozen=True)
class Discount:
    id: int
    discount_name: str
    discount_percentage: Optional[str] = None
    status: str = ACTIVE


@dataclass(frozen=True)
class PaymentMethod:
    id: int
    payment_method: str
    status: str = ACTIVE


@dataclass(frozen=True)
class IdentityProof:
    id: int
    proof_name: str
    status: str = ACTIVE


@dataclass(frozen=True)
class ReservationStatus:
    id: int
    reservation_status: str
    color: Optional[str] = None
    status: str = ACTIVE


@dataclass(frozen=True)
class Staff:
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: str = ACTIVE


def _build(cls, row: dict):
    """A record from a wire row, ignoring fields this service does not read."""
    names = {f.name for f in dataclasses.fields(cls)}
    kwargs = {k: v for k, v in (row or {}).items() if k in names}
    kwargs["id"] = int(kwargs["id"])
    return cls(**kwargs)


# ---------------------------------------------------------------------------
# Transport -- the only thing that knows about HTTP. Tests substitute it.
# ---------------------------------------------------------------------------


class Transport(Protocol):
    def get(self, service: str, path: str) -> Optional[dict]: ...
    def put(self, service: str, path: str, body: dict) -> Optional[dict]: ...
    def base_url(self, service: str) -> str: ...     # "" when it has no address


class HttpTransport:
    """The gateway, on the caller's own token.

    `GET /snapshot` of Master Data becomes `GET {gateway}/masterdata/snapshot`
    with the caller's `Authorization` header, which is precisely the request
    the browser would make. The gateway verifies the token, consults its
    permission map for that route, and proxies to Master Data with the same
    header -- so Master Data sees the same user, role and company_id this
    service did, and scopes accordingly.
    """

    def __init__(self, token: str, *, gateway_url: str, timeout: float = TIMEOUT_SECONDS):
        self._headers = {"Authorization": f"Bearer {token}"}
        self._gateway = gateway_url.rstrip("/")
        self._timeout = timeout

    def _url(self, service: str, path: str) -> str:
        return f"{self._gateway}/{PREFIX[service]}/{path.lstrip('/')}"

    def base_url(self, service: str) -> str:
        return self._gateway

    def _fail(self, service: str, detail: str) -> MasterDataUnavailable:
        return MasterDataUnavailable(service, detail, base_url=self._gateway, env_var=ENV_VAR)

    def _send(self, method: str, service: str, path: str, body=None) -> Optional[dict]:
        url = self._url(service, path)
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.request(method, url, headers=self._headers, json=body)
        except httpx.HTTPError as exc:
            raise self._fail(
                service, f"{url} is unreachable ({exc.__class__.__name__}). "
                f"Check that the gateway is running and that {ENV_VAR} in this "
                "service's .env is its address -- the same one the frontend uses."
            ) from exc

        if resp.status_code == 404:
            return None
        if resp.status_code == 401:
            # Our own caller's token was accepted here and refused by the
            # gateway: the two are not verifying the same JWT. A deploy fault
            # (JWT_SECRET_KEY / JWT_ISSUER differ), not the caller's.
            raise self._fail(
                service, f"{url} rejected the forwarded token (401). JWT_SECRET_KEY "
                "and JWT_ISSUER must be identical in every service's .env."
            )
        if resp.status_code == 403:
            # The gateway's permission map refused this route for this role.
            # The row for it comes from build_rbac_map.py (SERVICE_ROWS); a
            # gateway on a build without that row, or a map not regenerated
            # since, denies it under enforce.
            raise self._fail(
                service, f"{url} was refused by the gateway's permission map "
                f"({resp.text[:160]}). Regenerate it with "
                "`python Backend/tools/build_rbac_map.py` on the gateway's build "
                "and restart the gateway."
            )
        if resp.status_code == 502:
            # The gateway is up; what it proxies to is not.
            raise self._fail(
                service, f"{url}: the gateway could not reach the {PREFIX[service]} "
                f"service ({resp.text[:120]}). Check that service and the gateway's "
                "own *_SERVICE_URL for it."
            )
        if resp.status_code >= 400:
            raise self._fail(service, f"{url} answered {resp.status_code}: {resp.text[:200]}")
        try:
            return resp.json()
        except ValueError as exc:
            raise self._fail(service, f"{url} did not return JSON") from exc

    def get(self, service: str, path: str) -> Optional[dict]:
        return self._send("GET", service, path)

    def put(self, service: str, path: str, body: dict) -> Optional[dict]:
        return self._send("PUT", service, path, body)


# ---------------------------------------------------------------------------
# The client
# ---------------------------------------------------------------------------
class MasterData:
    """One request's view of Master Data and Users.

    Fetched lazily and once: nothing leaves this process until a lookup asks
    for it, and the snapshot is then held for the life of the object -- which
    is the life of the request, because controllers build one per request
    from the caller's token. A write through `set_room_state` updates the held
    copy too, so a later read in the same request sees what was written.
    """

    def __init__(self, transport: Transport):
        self._t = transport
        self._snapshot: Optional[dict] = None
        self._staff: dict[int, Optional[Staff]] = {}

    @classmethod
    def for_token(cls, token: str) -> "MasterData":
        return cls(HttpTransport(token, gateway_url=BaseConfig.API_GATEWAY_URL))

    # -- the snapshot -------------------------------------------------------
    def _load(self) -> dict:
        if self._snapshot is None:
            payload = self._t.get(MASTER, "/snapshot")
            data = (payload or {}).get("data")
            if not isinstance(data, dict):
                # Reachable, answering, and not Master Data as this build knows
                # it: a MasterDataServices older than /snapshot, or something
                # else entirely on that port. Say where, as the transport does
                # for a connection that fails outright.
                base = getattr(self._t, "base_url", lambda _s: "")(MASTER)
                raise MasterDataUnavailable(
                    MASTER, f"{base or 'the gateway'}/{PREFIX[MASTER]}/snapshot returned "
                    "no data -- is that the gateway, and is Master Data behind it on a "
                    "build that has /snapshot?",
                    base_url=base, env_var=ENV_VAR if base else "",
                )
            self._snapshot = {
                "rooms": {r.id: r for r in map(lambda x: _build(Room, x), data.get("rooms", []))},
                "room_types": {t.id: t for t in map(lambda x: _build(RoomType, x), data.get("room_types", []))},
                "tax_types": {t.id: t for t in map(lambda x: _build(TaxType, x), data.get("tax_types", []))},
                "discounts": {d.id: d for d in map(lambda x: _build(Discount, x), data.get("discounts", []))},
                "payment_methods": {p.id: p for p in map(lambda x: _build(PaymentMethod, x), data.get("payment_methods", []))},
                "identity_proofs": {i.id: i for i in map(lambda x: _build(IdentityProof, x), data.get("identity_proofs", []))},
                "statuses": sorted(
                    (_build(ReservationStatus, s) for s in data.get("reservation_statuses", [])),
                    key=lambda s: s.id,
                ),
            }
        return self._snapshot

    # Every row, active or not: for labelling what a stored reservation
    # already references, which may since have been retired.
    @property
    def rooms(self) -> dict[int, Room]:
        return self._load()["rooms"]

    @property
    def room_types(self) -> dict[int, RoomType]:
        return self._load()["room_types"]

    @property
    def tax_types(self) -> dict[int, TaxType]:
        return self._load()["tax_types"]

    @property
    def discounts(self) -> dict[int, Discount]:
        return self._load()["discounts"]

    @property
    def payment_methods(self) -> dict[int, PaymentMethod]:
        return self._load()["payment_methods"]

    @property
    def identity_proofs(self) -> dict[int, IdentityProof]:
        return self._load()["identity_proofs"]

    @property
    def statuses(self) -> list[ReservationStatus]:
        return self._load()["statuses"]

    # Only what may be chosen today.
    def active_rooms(self) -> dict[int, Room]:
        return {k: v for k, v in self.rooms.items() if v.status == ACTIVE}

    def active_room_types(self) -> dict[int, RoomType]:
        return {k: v for k, v in self.room_types.items() if v.status == ACTIVE}

    def active_statuses(self) -> list[ReservationStatus]:
        return [s for s in self.statuses if s.status == ACTIVE]

    def status_by_id(self, status_id) -> Optional[ReservationStatus]:
        try:
            wanted = int(status_id)
        except (TypeError, ValueError):
            return None
        return next((s for s in self.active_statuses() if s.id == wanted), None)

    def status_id(self, label: str) -> Optional[int]:
        """The id of an active status spelled exactly `label`, or None."""
        return next(
            (s.id for s in self.active_statuses() if s.reservation_status == label),
            None,
        )

    # -- users --------------------------------------------------------------
    def staff(self, user_id) -> Optional[Staff]:
        """An active member of staff by id, or None. Memoised per id."""
        try:
            pk = int(user_id)
        except (TypeError, ValueError):
            return None
        if pk not in self._staff:
            payload = self._t.get(USERS, f"/users/{pk}")
            row = (payload or {}).get("data") if payload else None
            person = _build(Staff, row) if row else None
            self._staff[pk] = person if person and person.status == ACTIVE else None
        return self._staff[pk]

    # -- the one write ------------------------------------------------------
    def set_room_state(self, room_id: int, *, booking_status: Optional[str] = None,
                       working_status: Optional[str] = None,
                       room_status: Optional[str] = None) -> Optional[Room]:
        """Write the operational facts about a room back to Master Data.

        Only the fields given are sent, and only a change is a write: a room
        already in the wanted state costs no request. Returns the room as
        Master Data now holds it, or None if the room is no longer there.
        PUT, because the gateway proxies GET/POST/PUT/DELETE and nothing else.
        """
        wanted = {
            "booking_status": booking_status,
            "working_status": working_status,
            "room_status": room_status,
        }
        current = self.rooms.get(int(room_id))
        changes = {
            k: v for k, v in wanted.items()
            if v is not None and (current is None or getattr(current, k) != v)
        }
        if not changes:
            return current

        payload = self._t.put(MASTER, f"/room/{int(room_id)}/state", changes)
        if payload is None:
            logger.warning("room_state_write_skipped room_id=%s reason=not_found", room_id)
            return None
        row = (payload or {}).get("data") or {}
        updated = _build(Room, row) if row.get("id") is not None else (
            dataclasses.replace(current, **changes) if current else None
        )
        if updated is not None:
            self.rooms[updated.id] = updated
        return updated


# ---------------------------------------------------------------------------
# Readiness
# ---------------------------------------------------------------------------
def probe(gateway_url: str, timeout: float = 3.0) -> tuple[bool, str]:
    """Can this service reach the gateway? For /readyz and the boot log.

    Asks the gateway's own liveness endpoint, which needs no token. Master
    Data and Users are behind it; a gateway that answers but cannot reach one
    of them shows up per request as a 503 naming that service, not here --
    their liveness endpoints are behind the proxy's authentication and a
    readiness probe holds no token.
    """
    url = f"{gateway_url.rstrip('/')}/healthz"
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url)
    except httpx.HTTPError as exc:
        return False, (
            f"gateway unreachable at {url} ({exc.__class__.__name__}). Master Data "
            "and Users are reached through it, so every reservation screen and "
            f"housekeeping assignment answers 503 until it is. Check that {ENV_VAR} "
            "in this service's .env is the gateway's address -- the same one the "
            "frontend uses."
        )
    if resp.status_code != 200:
        return False, f"gateway at {url} answered {resp.status_code}"
    return True, f"gateway reachable at {url}; Master Data and Users are called through it"
