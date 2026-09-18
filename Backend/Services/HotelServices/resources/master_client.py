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
    Restaurant and Bar ask Users and Master Data over HTTP, the night audit
    asks `/room` over HTTP, and this module asks `/snapshot` -- everything a
    reservation needs to be interpreted or priced, in one round trip -- and
    writes room state back through `PATCH /room/{id}/state`. The Hotel
    service's database account touches the Hotel schema and nothing else.

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


class MasterDataUnavailable(Exception):
    """A sibling service could not be reached or refused this service."""

    def __init__(self, service: str, detail: str):
        self.service = service
        self.detail = detail
        super().__init__(f"{service}: {detail}")


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
MASTER = "master"
USERS = "users"


class Transport(Protocol):
    def get(self, service: str, path: str) -> Optional[dict]: ...
    def patch(self, service: str, path: str, body: dict) -> Optional[dict]: ...


class HttpTransport:
    """Forwards the caller's own token, so the sibling scopes by its company.

    Every service verifies the same JWT (shared secret and issuer), which is
    what makes "on behalf of the caller" work without a service account: the
    sibling sees the same user, the same role and the same company_id this
    service did.
    """

    def __init__(self, token: str, *, master_url: str, users_url: str,
                 timeout: float = TIMEOUT_SECONDS):
        self._headers = {"Authorization": f"Bearer {token}"}
        self._base = {MASTER: master_url.rstrip("/"), USERS: users_url.rstrip("/")}
        self._timeout = timeout

    def _url(self, service: str, path: str) -> str:
        return f"{self._base[service]}/{path.lstrip('/')}"

    def _send(self, method: str, service: str, path: str, body=None) -> Optional[dict]:
        url = self._url(service, path)
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.request(method, url, headers=self._headers, json=body)
        except httpx.HTTPError as exc:
            raise MasterDataUnavailable(
                service, f"{url} is unreachable ({exc.__class__.__name__}). "
                "Check that the service is running and that this service's "
                "MASTER_SERVICE_URL / USER_SERVICE_URL point at it."
            ) from exc

        if resp.status_code == 404:
            return None
        if resp.status_code in (401, 403):
            # Our own caller's token was accepted here and refused there: the
            # two services are not verifying the same JWT. That is a deploy
            # fault (JWT_SECRET_KEY / JWT_ISSUER differ), not the caller's.
            raise MasterDataUnavailable(
                service, f"{url} rejected the forwarded token ({resp.status_code}). "
                "JWT_SECRET_KEY and JWT_ISSUER must be identical in every "
                "service's .env."
            )
        if resp.status_code >= 400:
            raise MasterDataUnavailable(
                service, f"{url} answered {resp.status_code}: {resp.text[:200]}"
            )
        try:
            return resp.json()
        except ValueError as exc:
            raise MasterDataUnavailable(service, f"{url} did not return JSON") from exc

    def get(self, service: str, path: str) -> Optional[dict]:
        return self._send("GET", service, path)

    def patch(self, service: str, path: str, body: dict) -> Optional[dict]:
        return self._send("PATCH", service, path, body)


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
        return cls(HttpTransport(
            token,
            master_url=BaseConfig.MASTER_SERVICE_URL,
            users_url=BaseConfig.USER_SERVICE_URL,
        ))

    # -- the snapshot -------------------------------------------------------
    def _load(self) -> dict:
        if self._snapshot is None:
            payload = self._t.get(MASTER, "/snapshot")
            data = (payload or {}).get("data")
            if not isinstance(data, dict):
                raise MasterDataUnavailable(
                    MASTER, "/snapshot returned no data -- is MasterDataServices "
                    "on a build that has it?"
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

        payload = self._t.patch(MASTER, f"/room/{int(room_id)}/state", changes)
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
def probe(service: str, base_url: str, env_var: str, consequence: str,
          timeout: float = 3.0) -> tuple[bool, str]:
    """Can this service reach the sibling it depends on? For /readyz and boot.

    Asks the sibling's own liveness endpoint, which needs no token. A 200 is
    "reachable"; anything else is reported with the URL and the .env key that
    set it, so the operator reads which value is wrong rather than which
    screen is down.
    """
    url = f"{base_url.rstrip('/')}/healthz"
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url)
    except httpx.HTTPError as exc:
        return False, (
            f"{service} service unreachable at {url} ({exc.__class__.__name__}). "
            f"{consequence} Check that it is running and that {env_var} in this "
            "service's .env points at it."
        )
    if resp.status_code != 200:
        return False, f"{service} service at {url} answered {resp.status_code}. {consequence}"
    return True, f"{service} service reachable at {url}"
