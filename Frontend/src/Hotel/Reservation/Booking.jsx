import React, { useMemo, useState } from "react";

import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import RowActions from "../../stories/RowActions";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import "./Reservation.css";

/**
 * Booking requests — an enquiry that names dates and room *types* but no
 * specific room, and carries no money. It becomes a Reservation later.
 *
 * WHY THIS SCREEN WAS REWRITTEN
 *   It hand-rolled everything the design system already owns: its own modal
 *   (`.modal-overlay` / `.modal-card`), its own Toast, its own ConfirmDialog,
 *   its own three action buttons, and bare `<label>` / `<input>` / `<select>`
 *   markup styled by global element selectors in Reservation.css.
 *
 *   That last part had a consequence beyond this file. Those globals could not
 *   be scoped while any screen depended on them, and scoping them is what
 *   stops Reservation.css reaching into the shared components on every other
 *   Reservation screen. This screen was the last holdout.
 *
 *   The View mode is now a DetailList rather than the same form with every
 *   field disabled — a record to read, not a form somebody switched off.
 */

const SALUTATIONS = ["Mr.", "Mrs.", "Ms.", "Mx.", "Dr.", "Prof."];
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[+()\-\s\d]{7,20}$/;

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");

const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

const parseArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v === null || v === undefined || v === "") return [];
  try {
    const parsed = JSON.parse(v);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const nightsBetween = (start, end) => {
  if (!start || !end) return 0;
  const a = new Date(start);
  const d = new Date(end);
  if (Number.isNaN(a.getTime()) || Number.isNaN(d.getTime())) return 0;
  const ms = d.getTime() - a.getTime();
  return ms <= 0 ? 0 : Math.round(ms / (1000 * 60 * 60 * 24));
};

const guestName = (r) =>
  [r?.first_name, r?.last_name].filter(Boolean).join(" ").trim() || "—";

const emptyForm = {
  salutation: "Mr.",
  first_name: "",
  last_name: "",
  phone_number: "",
  email: "",
  arrival_date: "",
  departure_date: "",
  room_type: [], // room type ids
  no_of_rooms: "",
  no_of_adults: "",
  no_of_children: 0,
};

const Booking = () => {
  const {
    data: [bookings, roomTypes],
    loading,
    error,
    reload,
  } = useApiResources([
    {
      fetch: () => APICall.getT("/hotel/room_booking"),
      select: readList,
      fallback: "Failed to load bookings.",
    },
    { fetch: () => APICall.getT("/masterdata/room_types"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formError, setFormError] = useState(null);
  const [saving, setSaving] = useState(false);

  const [viewRow, setViewRow] = useState(null);
  const [deleteRow, setDeleteRow] = useState(null);

  const roomTypeOptions = useMemo(
    () => roomTypes.map((t) => ({ value: t.id, label: t.room_type_name })),
    [roomTypes],
  );

  // `room_booking.room_type` holds TWO shapes in live data. Rows written by
  // the current API hold room-type ids; rows already in the client's database
  // hold the type NAMES ("Deluxe Room"). Both have to render, and both have to
  // survive a round trip through the edit form.
  //
  // This is not hypothetical: reading only ids meant every existing booking
  // displayed "#Deluxe Room", and -- worse -- opening one for edit resolved
  // its types to an empty list, so the guest's requested room types silently
  // vanished from the form and validation then refused to save until the user
  // picked them again.
  const resolveRoomType = (value) => {
    const raw = String(value ?? "").trim();
    if (!raw) return null;
    const byId = roomTypes.find((t) => String(t.id) === raw);
    if (byId) return byId;
    const byName = roomTypes.find(
      (t) => (t.room_type_name || "").toLowerCase() === raw.toLowerCase(),
    );
    return byName || null;
  };

  /** Ids for the multi-select, from either shape. */
  const roomTypeIds = (value) =>
    parseArr(value)
      .map((v) => resolveRoomType(v)?.id)
      .filter((id) => id !== undefined && id !== null);

  /** Human labels for the table and the View modal, from either shape. */
  const roomTypeNames = (value) => {
    const parts = parseArr(value).map((v) => {
      const match = resolveRoomType(v);
      if (match) return match.room_type_name;
      // A type that no longer exists in Master Data. Show what was stored
      // rather than a dangling id, so the record stays readable.
      return String(v);
    });
    return parts.join(", ") || "—";
  };

  const nights = nightsBetween(form.arrival_date, form.departure_date);

  const setField = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  /* ============================== Handlers ============================== */

  const openAdd = () => {
    setForm(emptyForm);
    setEditId(null);
    setFormError(null);
    setShowForm(true);
  };

  const openEdit = (row) => {
    setForm({
      salutation: row.salutation || "Mr.",
      first_name: row.first_name || "",
      last_name: row.last_name || "",
      phone_number: row.phone_number || "",
      email: row.email || "",
      arrival_date: isoDay(row.arrival_date),
      departure_date: isoDay(row.departure_date),
      room_type: roomTypeIds(row.room_type),
      no_of_rooms: row.no_of_rooms ?? "",
      no_of_adults: row.no_of_adults ?? "",
      no_of_children: row.no_of_children ?? 0,
    });
    setEditId(row.id);
    setFormError(null);
    setShowForm(true);
  };

  const closeForm = () => {
    if (saving) return;
    setShowForm(false);
    setEditId(null);
    setFormError(null);
  };

  const validate = () => {
    if (!form.first_name?.trim()) return "First name is required.";
    if (!form.last_name?.trim()) return "Last name is required.";
    if (!form.phone_number?.trim()) return "Phone number is required.";
    if (!PHONE_RE.test(form.phone_number.trim())) return "Enter a valid phone number.";
    if (form.email && !EMAIL_RE.test(form.email.trim())) return "Enter a valid email address.";
    if (!form.arrival_date) return "Arrival date is required.";
    if (!form.departure_date) return "Departure date is required.";
    if (isoDay(form.arrival_date) >= isoDay(form.departure_date))
      return "Departure date must be after arrival date.";
    if (!form.room_type.length) return "Pick at least one room type.";
    if (num(form.no_of_rooms) < 1) return "Number of rooms must be at least 1.";
    if (num(form.no_of_adults) < 1) return "Number of adults must be at least 1.";
    if (num(form.no_of_children) < 0) return "Children count cannot be negative.";
    return null;
  };

  const handleSave = async () => {
    if (saving) return;
    const problem = validate();
    if (problem) {
      setFormError(problem);
      return;
    }
    setFormError(null);
    setSaving(true);

    const payload = {
      salutation: form.salutation || null,
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      phone_number: form.phone_number.trim(),
      email: form.email ? form.email.trim().toLowerCase() : null,
      arrival_date: form.arrival_date,
      departure_date: form.departure_date,
      no_of_nights: nights || 1,
      room_type: form.room_type.map(Number).filter(Number.isFinite),
      no_of_rooms: num(form.no_of_rooms) || 1,
      no_of_adults: num(form.no_of_adults) || 1,
      no_of_children: num(form.no_of_children),
    };

    try {
      if (editId) {
        await APICall.putT("/hotel/room_booking", { ...payload, id: editId });
        showToast("Booking updated", "update");
      } else {
        await APICall.postT("/hotel/room_booking", payload);
        showToast("Booking created", "success");
      }
      setShowForm(false);
      setEditId(null);
      reload();
    } catch (err) {
      setFormError(errMsg(err, editId ? "Failed to update booking." : "Failed to create booking."));
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    const row = deleteRow;
    setDeleteRow(null);
    if (!row) return;
    try {
      await APICall.deleteT(`/hotel/room_booking/${row.id}`);
      showToast("Booking deleted", "delete");
      reload();
    } catch (err) {
      showToast(errMsg(err, "Failed to delete booking."), "error");
    }
  };

  /* ================================= UI ================================= */

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Booking Requests"
        loading={loading}
        emptyMessage="No booking requests yet. Use Add Booking to create the first one."
        hasActionButton
        searchable
        pagination
        // TableTemplate's own toolbar already offers CSV, Excel, print and
        // copy. This screen used to render a second "Export CSV" bar beneath
        // the table that did the same job with a hand-written serialiser.
        exportable
        actionButton={{
          label: "Add Booking",
          onClick: openAdd,
          variant: "primary",
        }}
        columns={[
          { key: "room_booking_id", title: "Booking ID", align: "left" },
          {
            key: "first_name",
            title: "Guest",
            align: "left",
            type: "custom",
            exportValue: guestName,
            render: (row) => (
              <div className="res-guest-cell">
                <span className="res-guest-name">{guestName(row)}</span>
                <span className="res-guest-phone">{row.phone_number || "—"}</span>
              </div>
            ),
          },
          {
            key: "arrival_date",
            title: "Stay",
            align: "left",
            type: "custom",
            exportValue: (row) => `${isoDay(row.arrival_date)} to ${isoDay(row.departure_date)}`,
            render: (row) => (
              <div className="res-stay-cell">
                <span className="res-stay-dates">{isoDay(row.arrival_date)}</span>
                <span className="res-stay-dates">{isoDay(row.departure_date)}</span>
                <span className="res-stay-nights">
                  {row.no_of_nights} night{row.no_of_nights === 1 ? "" : "s"}
                </span>
              </div>
            ),
          },
          {
            // Room type names, not the raw ids the column used to omit
            // entirely — a booking request is *about* which types were asked
            // for, so the list was missing its most useful field.
            key: "room_type",
            title: "Room Types",
            align: "left",
            type: "custom",
            exportValue: (row) => roomTypeNames(row.room_type),
            render: (row) => roomTypeNames(row.room_type),
          },
          {
            key: "no_of_rooms",
            title: "Party",
            align: "left",
            type: "custom",
            exportValue: (row) =>
              `${row.no_of_rooms} room(s), ${row.no_of_adults} adult(s), ${row.no_of_children || 0} child(ren)`,
            render: (row) => (
              <div className="res-stay-cell">
                <span>{row.no_of_rooms} room{row.no_of_rooms === 1 ? "" : "s"}</span>
                <span className="res-stay-nights">
                  {row.no_of_adults} adult{row.no_of_adults === 1 ? "" : "s"}
                  {row.no_of_children ? `, ${row.no_of_children} child` : ""}
                </span>
              </div>
            ),
          },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`booking ${row.room_booking_id || row.id}`}
                onView={() => setViewRow(row)}
                onEdit={() => openEdit(row)}
                onDelete={() => setDeleteRow(row)}
              />
            ),
          },
        ]}
        data={bookings}
      />

      {/* ============================== VIEW ============================== */}
      <Modal
        isOpen={Boolean(viewRow)}
        title={`Booking ${viewRow?.room_booking_id || ""}`}
        onClose={() => setViewRow(null)}
        // Large, not medium: at medium the Guest section auto-fitted to a
        // single column (the email value sets the minimum track width) while
        // Requested Stay beside it sat 2-up, so one modal showed two different
        // grids.
        size="large"
        viewMode
        showFooter
        actions={[
          { label: "Close", variant: "secondary", onClick: () => setViewRow(null) },
        ]}
      >
        <ViewSection title="Guest">
          <DetailList columns={2}>
            <DetailItem label="Name" value={guestName(viewRow)} />
            <DetailItem label="Salutation" value={viewRow?.salutation} />
            <DetailItem label="Phone" value={viewRow?.phone_number} />
            <DetailItem label="Email" value={viewRow?.email} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Requested stay">
          <DetailList columns={2}>
            <DetailItem label="Arrival" value={isoDay(viewRow?.arrival_date)} />
            <DetailItem label="Departure" value={isoDay(viewRow?.departure_date)} />
            <DetailItem label="Nights" value={viewRow?.no_of_nights} />
            <DetailItem label="Rooms" value={viewRow?.no_of_rooms} />
            <DetailItem label="Adults" value={viewRow?.no_of_adults} />
            <DetailItem label="Children" value={viewRow?.no_of_children ?? 0} />
            <DetailItem
              label="Room types"
              value={roomTypeNames(viewRow?.room_type)}
              span={2}
            />
          </DetailList>
        </ViewSection>
      </Modal>

      {/* ============================ ADD / EDIT ============================ */}
      <Modal
        isOpen={showForm}
        title={editId ? "Edit Booking" : "Add Booking"}
        onClose={closeForm}
        size="large"
        showFooter
        bodyLayout="grid"
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeForm, disabled: saving },
          {
            label: saving ? "Saving…" : "Save",
            variant: "primary",
            onClick: handleSave,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} />

        <Select
          label="Salutation"
          value={form.salutation}
          onChange={setField("salutation")}
          options={SALUTATIONS}
        />
        <Input
          label="First Name"
          required
          value={form.first_name}
          onChange={setField("first_name")}
          maxLength={100}
          autoComplete="given-name"
        />
        <Input
          label="Last Name"
          required
          value={form.last_name}
          onChange={setField("last_name")}
          maxLength={100}
          autoComplete="family-name"
        />
        <Input
          label="Phone Number"
          required
          type="tel"
          inputMode="tel"
          value={form.phone_number}
          onChange={setField("phone_number")}
          maxLength={20}
          autoComplete="tel"
        />
        <Input
          label="Email"
          type="email"
          inputMode="email"
          value={form.email}
          onChange={setField("email")}
          maxLength={100}
          autoComplete="email"
        />
        <Select
          label="Room Types"
          required
          multiple
          value={form.room_type}
          onChange={(e) => setForm((prev) => ({ ...prev, room_type: e.target.value }))}
          options={roomTypeOptions}
          placeholder="Select room types…"
          helperText="A request can name more than one type."
        />
        <Input
          label="Arrival Date"
          required
          type="date"
          value={form.arrival_date}
          onChange={setField("arrival_date")}
          min={isoDay(new Date().toISOString())}
        />
        <Input
          label="Departure Date"
          required
          type="date"
          value={form.departure_date}
          onChange={setField("departure_date")}
          min={form.arrival_date || undefined}
        />
        <Input
          label="Nights"
          type="number"
          value={nights}
          readOnly
          helperText="Calculated from the dates"
        />
        <Input
          label="No. of Rooms"
          required
          type="number"
          min="1"
          value={form.no_of_rooms}
          onChange={setField("no_of_rooms")}
        />
        <Input
          label="No. of Adults"
          required
          type="number"
          min="1"
          value={form.no_of_adults}
          onChange={setField("no_of_adults")}
        />
        <Input
          label="No. of Children"
          type="number"
          min="0"
          value={form.no_of_children}
          onChange={setField("no_of_children")}
        />
      </Modal>

      {/* ============================== DELETE ============================== */}
      <ConfirmModal
        isOpen={Boolean(deleteRow)}
        onClose={() => setDeleteRow(null)}
        onConfirm={confirmDelete}
        title="Delete booking"
        confirmText="Delete"
        size="small"
        destructive
      >
        Delete booking {deleteRow?.room_booking_id || deleteRow?.id} for{" "}
        {guestName(deleteRow)}? This cannot be undone.
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default Booking;
