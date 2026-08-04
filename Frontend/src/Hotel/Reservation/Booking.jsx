import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { Eye, Pencil, Trash2, X, AlertCircle, CheckCircle, Download } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./Reservation.css";

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
    const p = JSON.parse(v);
    return Array.isArray(p) ? p : [];
  } catch {
    return [];
  }
};

const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const nightsBetween = (start, end) => {
  if (!start || !end) return 0;
  const a = new Date(start);
  const d = new Date(end);
  if (Number.isNaN(a.getTime()) || Number.isNaN(d.getTime())) return 0;
  const ms = d.getTime() - a.getTime();
  if (ms <= 0) return 0;
  return Math.round(ms / (1000 * 60 * 60 * 24));
};

const Toast = ({ toast, onClose }) => {
  if (!toast) return null;
  const Icon = toast.kind === "success" ? CheckCircle : AlertCircle;
  return (
    <div
      className={`reservation-toast ${toast.kind}`}
      role={toast.kind === "success" ? "status" : "alert"}
      aria-live={toast.kind === "success" ? "polite" : "assertive"}
    >
      <Icon size={18} aria-hidden="true" />
      <span>{toast.text}</span>
      <button
        type="button"
        className="reservation-toast-close"
        onClick={onClose}
        aria-label="Dismiss notification"
      >
        <X size={14} aria-hidden="true" />
      </button>
    </div>
  );
};

const ConfirmDialog = ({
  open,
  title,
  body,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  tone = "danger",
  onConfirm,
  onCancel,
  loading = false,
}) => {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => { if (e.key === "Escape" && !loading) onCancel(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onCancel, loading]);

  if (!open) return null;
  return (
    <div
      className="modal-container"
      role="dialog"
      aria-modal="true"
      aria-labelledby="booking-confirm-title"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel(); }}
    >
      <div className="modal-content confirm-modal">
        <div className="modal-header">
          <h2 className="modal-title" id="booking-confirm-title">{title}</h2>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onCancel}
            aria-label="Close confirmation"
            disabled={loading}
          >
            <X size={22} />
          </button>
        </div>
        <div className="modal-body"><p>{body}</p></div>
        <div className="modal-footer">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            className={`btn ${tone === "danger" ? "btn-danger" : "btn-primary"}`}
            onClick={onConfirm}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? "Working…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

const initialForm = {
  salutation: "Mr.",
  first_name: "",
  last_name: "",
  phone_number: "",
  email: "",
  arrival_date: "",
  departure_date: "",
  room_type: [], // array of room type ids
  no_of_rooms: "",
  no_of_adults: "",
  no_of_children: 0,
};

const Booking = () => {
  const [data, setData] = useState(null); // null = loading
  const [error, setError] = useState(null);
  const [roomTypes, setRoomTypes] = useState([]);
  const [refreshTick, setRefreshTick] = useState(0);

  const [formData, setFormData] = useState(initialForm);
  const [showModal, setShowModal] = useState(false);
  const [mode, setMode] = useState("add");
  const [selectedId, setSelectedId] = useState(null);
  const [formError, setFormError] = useState(null);
  const [saving, setSaving] = useState(false);

  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [toast, setToast] = useState(null);
  const mounted = useRef(true);

  const showToast = useCallback((kind, text) => setToast({ kind, text, at: Date.now() }), []);

  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  const loadBookings = useCallback(async () => {
    try {
      const res = await APICall.getT("/hotel/room_booking");
      if (!mounted.current) return;
      setData(Array.isArray(res?.data) ? res.data : readList(res));
      setError(null);
    } catch (err) {
      if (!mounted.current) return;
      setData([]);
      setError(errMsg(err, "Failed to load bookings."));
    }
  }, []);

  useEffect(() => {
    mounted.current = true;
    setData(null);
    loadBookings();

    APICall.getT("/masterdata/room_types")
      .then((res) => {
        if (!mounted.current) return;
        setRoomTypes(readList(res));
      })
      .catch(() => {
        if (!mounted.current) return;
        setRoomTypes([]);
      });

    return () => { mounted.current = false; };
  }, [loadBookings, refreshTick]);

  // Escape to close the CRUD modal.
  useEffect(() => {
    if (!showModal) return undefined;
    const onKey = (e) => { if (e.key === "Escape" && !saving) closeModal(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
     
  }, [showModal, saving]);

  useEffect(() => {
    const anyOpen = showModal || Boolean(pendingDelete);
    if (!anyOpen) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [showModal, pendingDelete]);

  // ----------------------------------------------------------------
  const openAddModal = () => {
    setFormData(initialForm);
    setMode("add");
    setSelectedId(null);
    setFormError(null);
    setShowModal(true);
  };

  const openEditModal = (row) => {
    setFormData({
      salutation: row.salutation || "Mr.",
      first_name: row.first_name || "",
      last_name: row.last_name || "",
      phone_number: row.phone_number || "",
      email: row.email || "",
      arrival_date: isoDay(row.arrival_date),
      departure_date: isoDay(row.departure_date),
      room_type: parseArr(row.room_type).map(Number).filter(Number.isFinite),
      no_of_rooms: row.no_of_rooms ?? "",
      no_of_adults: row.no_of_adults ?? "",
      no_of_children: row.no_of_children ?? 0,
    });
    setSelectedId(row.id);
    setMode("edit");
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setFormData({
      salutation: row.salutation || "",
      first_name: row.first_name || "",
      last_name: row.last_name || "",
      phone_number: row.phone_number || "",
      email: row.email || "",
      arrival_date: isoDay(row.arrival_date),
      departure_date: isoDay(row.departure_date),
      room_type: parseArr(row.room_type).map(Number).filter(Number.isFinite),
      no_of_rooms: row.no_of_rooms ?? "",
      no_of_adults: row.no_of_adults ?? "",
      no_of_children: row.no_of_children ?? 0,
    });
    setMode("view");
    setSelectedId(row.id);
    setFormError(null);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedId(null);
    setFormError(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const totalNights = useMemo(
    () => nightsBetween(formData.arrival_date, formData.departure_date),
    [formData.arrival_date, formData.departure_date],
  );

  const validate = () => {
    if (!formData.first_name?.trim()) return "First name is required.";
    if (!formData.last_name?.trim()) return "Last name is required.";
    if (!formData.phone_number?.trim()) return "Phone number is required.";
    if (!PHONE_RE.test(formData.phone_number.trim())) return "Enter a valid phone number.";
    if (formData.email && !EMAIL_RE.test(formData.email.trim())) return "Enter a valid email address.";
    if (!formData.arrival_date) return "Arrival date is required.";
    if (!formData.departure_date) return "Departure date is required.";
    if (isoDay(formData.arrival_date) >= isoDay(formData.departure_date)) return "Departure date must be after arrival date.";
    if (!Array.isArray(formData.room_type) || formData.room_type.length === 0) return "Pick at least one room type.";
    if (num(formData.no_of_rooms) < 1) return "Number of rooms must be at least 1.";
    if (num(formData.no_of_adults) < 1) return "Number of adults must be at least 1.";
    if (num(formData.no_of_children) < 0) return "Children count cannot be negative.";
    return null;
  };

  const buildPayload = (includeId = false) => {
    const payload = {
      salutation: formData.salutation || null,
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      phone_number: formData.phone_number.trim(),
      email: formData.email ? formData.email.trim().toLowerCase() : null,
      arrival_date: formData.arrival_date,
      departure_date: formData.departure_date,
      no_of_nights: totalNights || 1,
      room_type: formData.room_type.map(Number).filter(Number.isFinite),
      no_of_rooms: num(formData.no_of_rooms) || 1,
      no_of_adults: num(formData.no_of_adults) || 1,
      no_of_children: num(formData.no_of_children),
    };
    if (includeId) payload.id = selectedId;
    return payload;
  };

  const handleSave = async () => {
    const v = validate();
    if (v) {
      setFormError(v);
      showToast("error", v);
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      if (mode === "edit") {
        await APICall.putT("/hotel/room_booking", buildPayload(true));
        showToast("success", "Booking updated.");
      } else {
        await APICall.postT("/hotel/room_booking", buildPayload(false));
        showToast("success", "Booking created.");
      }
      closeModal();
      loadBookings();
    } catch (err) {
      const m = errMsg(err, mode === "edit" ? "Failed to update booking." : "Failed to create booking.");
      setFormError(m);
      showToast("error", m);
    } finally {
      if (mounted.current) setSaving(false);
    }
  };

  const handleDeleteClick = (row) => setPendingDelete(row);

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleteLoading(true);
    try {
      await APICall.deleteT(`/hotel/room_booking/${pendingDelete.id}`);
      showToast("success", "Booking deleted.");
      setPendingDelete(null);
      loadBookings();
    } catch (err) {
      showToast("error", errMsg(err, "Failed to delete booking."));
    } finally {
      if (mounted.current) setDeleteLoading(false);
    }
  };

  const handleExportCsv = () => {
    const list = Array.isArray(data) ? data : [];
    if (list.length === 0) {
      showToast("error", "No bookings to export.");
      return;
    }
    const header = [
      "Booking ID", "First Name", "Last Name", "Phone", "Email",
      "Arrival", "Departure", "Nights", "Rooms", "Adults", "Children",
    ];
    const rows = list.map((r) => [
      r.room_booking_id ?? r.id,
      r.first_name ?? "",
      r.last_name ?? "",
      r.phone_number ?? "",
      r.email ?? "",
      r.arrival_date ?? "",
      r.departure_date ?? "",
      r.no_of_nights ?? "",
      r.no_of_rooms ?? "",
      r.no_of_adults ?? "",
      r.no_of_children ?? "",
    ]);
    const csv = [header, ...rows]
      .map((row) => row.map((cell) => {
        const s = String(cell ?? "");
        return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
      }).join(","))
      .join("\r\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bookings-${isoDay(new Date().toISOString())}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isView = mode === "view";
  const isLoading = data === null;
  const tableData = Array.isArray(data) ? data : [];
  const modalTitle = mode === "add" ? "Add Booking" : mode === "edit" ? "Edit Booking" : "View Booking";

  return (
    <>
      {error && (
        <div className="reservation-alert" role="alert">
          <span>{error}</span>
          <button
            type="button"
            className="reservation-alert-action"
            onClick={() => setRefreshTick((n) => n + 1)}
          >
            Retry
          </button>
        </div>
      )}

      {isLoading && (
        <div className="reservation-loading" role="status" aria-live="polite">
          Loading bookings…
        </div>
      )}

      {!isLoading && (
        <TableTemplate
          title="Booking List"
          hasActionButton
          searchable
          pagination
          exportable
          actionButton={{
            label: "Add Booking",
            onClick: openAddModal,
            variant: "primary",
          }}
          columns={[
            { key: "room_booking_id", title: "Booking ID", align: "center" },
            { key: "first_name", title: "First Name", align: "center" },
            { key: "last_name", title: "Last Name", align: "center" },
            { key: "phone_number", title: "Phone", align: "center" },
            { key: "no_of_rooms", title: "Rooms", align: "center" },
            { key: "arrival_date", title: "Arrival", align: "center" },
            { key: "departure_date", title: "Departure", align: "center" },
            {
              key: "actions",
              title: "Actions",
              align: "center",
              type: "custom",
              render: (row) => (
                <div className="table-actions">
                  <button
                    type="button"
                    className="table-action-btn view"
                    title="View"
                    aria-label={`View booking ${row.room_booking_id || row.id}`}
                    onClick={() => openViewModal(row)}
                  >
                    <Eye size={16} />
                  </button>
                  <button
                    type="button"
                    className="table-action-btn edit"
                    title="Edit"
                    aria-label={`Edit booking ${row.room_booking_id || row.id}`}
                    onClick={() => openEditModal(row)}
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    type="button"
                    className="table-action-btn delete"
                    title="Delete"
                    aria-label={`Delete booking ${row.room_booking_id || row.id}`}
                    onClick={() => handleDeleteClick(row)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ),
            },
          ]}
          data={tableData}
        />
      )}

      {!isLoading && tableData.length === 0 && !error && (
        <div className="reservation-empty">
          No bookings yet. Use "Add Booking" to create the first one.
        </div>
      )}

      {/* Export bar shown alongside the table when data is present */}
      {!isLoading && tableData.length > 0 && (
        <div className="bkg-export-bar">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleExportCsv}
            aria-label="Export bookings as CSV"
          >
            <Download size={16} aria-hidden="true" />
            <span>Export CSV</span>
          </button>
        </div>
      )}

      {/* CRUD modal */}
      {showModal && (
        <div
          className="modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="booking-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget && !saving) closeModal(); }}
        >
          <div className="modal-card">
            <div className="modal-header">
              <h3 id="booking-modal-title">{modalTitle}</h3>
              <button
                type="button"
                onClick={closeModal}
                aria-label="Close booking dialog"
                disabled={saving}
              >
                <X size={18} />
              </button>
            </div>

            {formError && (
              <div className="reservation-alert inline" role="alert">
                {formError}
              </div>
            )}

            <div className="modal-body grid">
              <div className="form-group">
                <label htmlFor="bkg-salutation">Salutation</label>
                <select
                  id="bkg-salutation"
                  name="salutation"
                  value={formData.salutation}
                  onChange={handleChange}
                  disabled={isView}
                >
                  {SALUTATIONS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="bkg-first-name">First Name *</label>
                <input
                  id="bkg-first-name"
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  disabled={isView}
                  required
                  maxLength={100}
                  autoComplete="given-name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-last-name">Last Name *</label>
                <input
                  id="bkg-last-name"
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  disabled={isView}
                  required
                  maxLength={100}
                  autoComplete="family-name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-email">Email</label>
                <input
                  id="bkg-email"
                  type="email"
                  inputMode="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={isView}
                  maxLength={100}
                  autoComplete="email"
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-phone">Phone Number *</label>
                <input
                  id="bkg-phone"
                  type="tel"
                  inputMode="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  disabled={isView}
                  required
                  maxLength={20}
                  autoComplete="tel"
                />
              </div>

              <div className="form-group">
                <label>Room Types *</label>
                <div className="bkg-chip-tray" data-view={isView ? "true" : "false"}>
                  {formData.room_type.length > 0 ? (
                    formData.room_type.map((id) => {
                      const room = roomTypes.find((r) => r.id === id);
                      return (
                        <span key={id} className="bkg-chip">
                          {room?.room_type_name || `#${id}`}
                          {!isView && (
                            <button
                              type="button"
                              className="bkg-chip-remove"
                              aria-label={`Remove room type ${room?.room_type_name || id}`}
                              onClick={() =>
                                setFormData((prev) => ({
                                  ...prev,
                                  room_type: prev.room_type.filter((x) => x !== id),
                                }))
                              }
                            >
                              ×
                            </button>
                          )}
                        </span>
                      );
                    })
                  ) : (
                    <span className="bkg-chip-placeholder">Select room types…</span>
                  )}
                </div>
                {!isView && (
                  <select
                    className="bkg-chip-picker"
                    aria-label="Add room type"
                    onChange={(e) => {
                      const id = Number(e.target.value);
                      if (!id) return;
                      if (formData.room_type.includes(id)) return;
                      setFormData((prev) => ({
                        ...prev,
                        room_type: [...prev.room_type, id],
                      }));
                      e.target.value = "";
                    }}
                  >
                    <option value="">+ Add Room Type</option>
                    {roomTypes.map((room) => (
                      <option key={room.id} value={room.id}>
                        {room.room_type_name}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="bkg-arrival">Arrival Date *</label>
                <input
                  id="bkg-arrival"
                  type="date"
                  name="arrival_date"
                  value={formData.arrival_date}
                  onChange={handleChange}
                  disabled={isView}
                  required
                  min={isView ? undefined : isoDay(new Date().toISOString())}
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-departure">Departure Date *</label>
                <input
                  id="bkg-departure"
                  type="date"
                  name="departure_date"
                  value={formData.departure_date}
                  onChange={handleChange}
                  disabled={isView}
                  required
                  min={formData.arrival_date || undefined}
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-nights">No. of Nights</label>
                <input
                  id="bkg-nights"
                  type="number"
                  value={totalNights}
                  readOnly
                  aria-readonly="true"
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-no-rooms">No. of Rooms *</label>
                <input
                  id="bkg-no-rooms"
                  type="number"
                  name="no_of_rooms"
                  value={formData.no_of_rooms}
                  onChange={handleChange}
                  disabled={isView}
                  min="1"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-no-adults">No. of Adults *</label>
                <input
                  id="bkg-no-adults"
                  type="number"
                  name="no_of_adults"
                  value={formData.no_of_adults}
                  onChange={handleChange}
                  disabled={isView}
                  min="1"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="bkg-no-children">No. of Children</label>
                <input
                  id="bkg-no-children"
                  type="number"
                  name="no_of_children"
                  value={formData.no_of_children}
                  onChange={handleChange}
                  disabled={isView}
                  min="0"
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn secondary"
                onClick={closeModal}
                disabled={saving}
              >
                {isView ? "Close" : "Cancel"}
              </button>
              {!isView && (
                <button
                  type="button"
                  className="btn primary"
                  onClick={handleSave}
                  disabled={saving}
                  aria-busy={saving}
                >
                  {saving ? "Saving…" : "Save"}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete booking"
        body={
          pendingDelete
            ? `Delete booking ${pendingDelete.room_booking_id || pendingDelete.id} for ${pendingDelete.first_name || "guest"}? This action cannot be undone.`
            : ""
        }
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() => setPendingDelete(null)}
        loading={deleteLoading}
      />

      <Toast toast={toast} onClose={() => setToast(null)} />
    </>
  );
};

export default Booking;
