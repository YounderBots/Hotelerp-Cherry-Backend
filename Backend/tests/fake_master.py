"""An in-memory Master Data + Users service for the Hotel suites.

`MasterData` (resources/master_client.py) talks to a `Transport` -- the one
thing that knows about HTTP. This is a Transport that answers from a dict
instead, shaped exactly like the wire: `GET /snapshot` returns the seven
lists, `PATCH /room/{id}/state` writes into them, `GET /users/{id}` answers
from a staff list. So the suites exercise the real client, the real records
and the real lookups, with no HTTP and no second database -- which is also
what makes them honest about the boundary: if the wire shape changes here it
has to change in `snapshotController.py` too, and vice versa.

    md, master = fake_master()
    master.add_room(id=1, room_no="101", room_type_id="7")
    md.rooms[1].room_no            # "101", through the real client

Every row defaults to ACTIVE and takes any wire field as a keyword.
"""

from __future__ import annotations

from typing import Optional

from resources.master_client import MasterData, MasterDataUnavailable

TENANT = "1"


class FakeMaster:
    """The sibling services, as data."""

    def __init__(self):
        self.snapshot = {
            "rooms": [], "room_types": [], "tax_types": [], "discounts": [],
            "payment_methods": [], "identity_proofs": [], "reservation_statuses": [],
        }
        self.staff: dict[int, dict] = {}
        self.down = False            # every call raises MasterDataUnavailable
        self.calls: list[tuple] = []  # (method, service, path, body)

    # -- authoring --------------------------------------------------------------
    def _add(self, key: str, **row) -> dict:
        row.setdefault("status", "ACTIVE")
        self.snapshot[key].append(row)
        return row

    def add_room(self, **row) -> dict:
        row.setdefault("room_no", str(100 + int(row["id"])))
        row.setdefault("room_name", f"Room {row['id']}")
        row.setdefault("room_type_id", "1")
        row.setdefault("bed_type_id", "1")
        row.setdefault("max_adult", "2")
        row.setdefault("max_child", "1")
        row.setdefault("booking_status", "Available")
        row.setdefault("working_status", "Ready")
        row.setdefault("room_status", "UnBlocking")
        return self._add("rooms", **row)

    def add_room_type(self, **row) -> dict:
        row.setdefault("room_type_name", f"Type {row['id']}")
        return self._add("room_types", **row)

    def add_tax(self, **row) -> dict:
        return self._add("tax_types", **row)

    def add_discount(self, **row) -> dict:
        return self._add("discounts", **row)

    def add_payment_method(self, **row) -> dict:
        return self._add("payment_methods", **row)

    def add_identity_proof(self, **row) -> dict:
        return self._add("identity_proofs", **row)

    def add_status(self, **row) -> dict:
        row.setdefault("color", "#000000")
        return self._add("reservation_statuses", **row)

    def add_staff(self, **row) -> dict:
        row.setdefault("status", "ACTIVE")
        self.staff[int(row["id"])] = row
        return row

    def room(self, room_id: int) -> Optional[dict]:
        return next((r for r in self.snapshot["rooms"] if int(r["id"]) == int(room_id)), None)

    # -- the Transport protocol -------------------------------------------------
    def base_url(self, service: str) -> str:
        return f"fake://{service}"

    def get(self, service: str, path: str) -> Optional[dict]:
        self.calls.append(("GET", service, path, None))
        if self.down:
            raise MasterDataUnavailable(service, f"{path} is unreachable (test)")
        if service == "master" and path == "/snapshot":
            # A copy, so the client cannot reach in and edit the fixture.
            return {"status": "success",
                    "data": {k: [dict(r) for r in v] for k, v in self.snapshot.items()}}
        if service == "users" and path.startswith("/users/"):
            row = self.staff.get(int(path.rsplit("/", 1)[1]))
            return {"status": "success", "data": dict(row)} if row else None
        raise AssertionError(f"unexpected GET {service} {path}")

    def patch(self, service: str, path: str, body: dict) -> Optional[dict]:
        self.calls.append(("PATCH", service, path, dict(body)))
        if self.down:
            raise MasterDataUnavailable(service, f"{path} is unreachable (test)")
        assert service == "master" and path.startswith("/room/") and path.endswith("/state"), path
        room = self.room(int(path.split("/")[2]))
        if not room or room.get("status") != "ACTIVE":
            return None
        for k, v in body.items():
            assert k in ("booking_status", "working_status", "room_status"), k
            room[k] = v
        return {"status": "success", "data": dict(room)}

    # -- what was written -------------------------------------------------------
    def writes(self) -> list[tuple[int, dict]]:
        return [(int(p.split("/")[2]), b) for m, _s, p, b in self.calls if m == "PATCH"]


def fake_master() -> tuple[MasterData, FakeMaster]:
    master = FakeMaster()
    return MasterData(master), master
