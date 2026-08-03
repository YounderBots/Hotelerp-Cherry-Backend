import React, { useCallback, useEffect, useRef, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import {
  Download,
  Eye,
  Pencil,
  Printer,
  Trash2,
  Check,
  X,
  LogOut,
  AlertCircle,
  CheckCircle,
  CreditCard,
  HandCoins,
} from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./Reservation.css";

// reservation_status is master-data-driven (see /masterdata/reservation_status);
// checkin flips Booked → Checked-In, checkout flips Checked-In → Checked-Out.
const CAN_CHECKIN = new Set(["Booked"]);
const CAN_CHECKOUT = new Set(["Checked-In"]);
const LOCKED_STATUSES = new Set(["Checked-Out", "Cancelled", "No Show"]);

const RESERVATION_TYPES = ["RESERVATION", "GROUP_RESERVATION", "CHECKIN"];
const SALUTATIONS = ["Mr.", "Mrs.", "Ms.", "Mx.", "Dr.", "Prof."];

const isoDay = (v) => (typeof v === "string" ? v.slice(0, 10) : "");

const escapeHtml = (v) =>
  String(v ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

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

const readList = (res) => {
  if (Array.isArray(res?.data)) return res.data;
  if (Array.isArray(res?.data?.data)) return res.data.data;
  return [];
};

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

const getStatusBadgeClass = (status) => {
  const s = String(status || "").toLowerCase();
  if (s === "booked" || s === "pending") return "status-pending";
  if (s === "confirmed") return "status-confirmed";
  if (s === "checked-in" || s === "arrived") return "status-checked-in";
  if (s === "checked-out" || s === "departures") return "status-checked-out";
  if (s === "cancelled" || s === "canceled" || s === "no show" || s === "no-show") return "status-cancelled";
  return "status-pending";
};

// -------------------------------------------------------------------------
// Toast
// -------------------------------------------------------------------------
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

// -------------------------------------------------------------------------
// Confirm dialog
// -------------------------------------------------------------------------
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
      aria-labelledby="confirm-modal-title"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel(); }}
    >
      <div className="modal-content confirm-modal">
        <div className="modal-header">
          <h2 className="modal-title" id="confirm-modal-title">{title}</h2>
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
        <div className="modal-body">
          <p>{body}</p>
        </div>
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

// -------------------------------------------------------------------------
// Reservation page
// -------------------------------------------------------------------------
const Reservation = () => {
  const [data, setData] = useState(null); // null = loading
  const [error, setError] = useState(null);
  const [refreshTick, setRefreshTick] = useState(0);

  const [selectedReservation, setSelectedReservation] = useState(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({});
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState(null);

  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [rowLocks, setRowLocks] = useState({});
  const [toast, setToast] = useState(null);

  const [identityTypes, setIdentityTypes] = useState([]);
  const [roomTypes, setRoomTypes] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [taxTypes, setTaxTypes] = useState([]);
  const [discountTypes, setDiscountTypes] = useState([]);
  const [reservationStatuses, setReservationStatuses] = useState([]);

  const [paymentHistory, setPaymentHistory] = useState([]);

  const [payModal, setPayModal] = useState(null); // { row, amount, method }
  const [paySaving, setPaySaving] = useState(false);
  const [payError, setPayError] = useState(null);

  const [refundModal, setRefundModal] = useState(null); // { row, amount, method }
  const [refundSaving, setRefundSaving] = useState(false);
  const [refundError, setRefundError] = useState(null);

  const mounted = useRef(true);

  const showToast = useCallback((kind, text) => {
    setToast({ kind, text, at: Date.now() });
  }, []);

  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  const loadReservations = useCallback(async () => {
    try {
      const res = await APICall.getT("/hotel/room_reservation");
      if (!mounted.current) return;
      setData(Array.isArray(res?.data) ? res.data : []);
      setError(null);
    } catch (err) {
      if (!mounted.current) return;
      setData([]);
      setError(errMsg(err, "Failed to load reservations."));
    }
  }, []);

  useEffect(() => {
    mounted.current = true;
    setData(null);
    loadReservations();

    Promise.allSettled([
      APICall.getT("/masterdata/identity_proof"),
      APICall.getT("/masterdata/room_types"),
      APICall.getT("/masterdata/room"),
      APICall.getT("/masterdata/payment_methods"),
      APICall.getT("/masterdata/tax"),
      APICall.getT("/masterdata/discount"),
      APICall.getT("/masterdata/reservation_status"),
    ]).then((results) => {
      if (!mounted.current) return;
      const [rIdent, rRT, rRoom, rPM, rTax, rDisc, rStatus] = results;
      setIdentityTypes(rIdent.status === "fulfilled" ? readList(rIdent.value) : []);
      setRoomTypes(rRT.status === "fulfilled" ? readList(rRT.value) : []);
      setRooms(rRoom.status === "fulfilled" ? readList(rRoom.value) : []);
      setPaymentMethods(rPM.status === "fulfilled" ? readList(rPM.value) : []);
      setTaxTypes(rTax.status === "fulfilled" ? readList(rTax.value) : []);
      setDiscountTypes(rDisc.status === "fulfilled" ? readList(rDisc.value) : []);
      setReservationStatuses(rStatus.status === "fulfilled" ? readList(rStatus.value) : []);
    });

    return () => {
      mounted.current = false;
    };
  }, [loadReservations, refreshTick]);

  // Escape closes the topmost modal.
  useEffect(() => {
    if (!isViewModalOpen && !isEditModalOpen) return undefined;
    const onKey = (e) => {
      if (e.key !== "Escape") return;
      if (isEditModalOpen && !editSaving) setIsEditModalOpen(false);
      else if (isViewModalOpen) setIsViewModalOpen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [isViewModalOpen, isEditModalOpen, editSaving]);

  // Lock body scroll while a modal is open.
  useEffect(() => {
    const anyOpen = isViewModalOpen || isEditModalOpen || Boolean(pendingDelete);
    if (!anyOpen) return undefined;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, [isViewModalOpen, isEditModalOpen, pendingDelete]);

  // -----------------------------------------------------------------------
  // Row action handlers
  // -----------------------------------------------------------------------
  const handleApprove = async (id) => {
    setRowLocks((m) => ({ ...m, [id]: "checkin" }));
    try {
      await APICall.postT(`/hotel/room_reservation_checkin/${id}`);
      showToast("success", "Guest checked in.");
      loadReservations();
    } catch (err) {
      showToast("error", errMsg(err, "Check-in failed."));
    } finally {
      // Guarded with `if (mounted)` rather than an early `return`: returning
      // from a finally block discards any exception still propagating, so a
      // throw inside the catch above would vanish silently.
      if (mounted.current) {
        setRowLocks((m) => {
          const next = { ...m };
          delete next[id];
          return next;
        });
      }
    }
  };

  const handleCheckout = async (id, token) => {
    if (!token) {
      showToast("error", "This reservation has no checkout token — please refresh.");
      return;
    }
    setRowLocks((m) => ({ ...m, [id]: "checkout" }));
    try {
      await APICall.postT(`/hotel/room_reservation_checkout/${encodeURIComponent(token)}`);
      showToast("success", "Guest checked out.");
      loadReservations();
    } catch (err) {
      showToast("error", errMsg(err, "Check-out failed."));
    } finally {
      // Guarded with `if (mounted)` rather than an early `return`: returning
      // from a finally block discards any exception still propagating, so a
      // throw inside the catch above would vanish silently.
      if (mounted.current) {
        setRowLocks((m) => {
          const next = { ...m };
          delete next[id];
          return next;
        });
      }
    }
  };

  const openPayModal = (row) => {
    setPayError(null);
    setPayModal({ row, amount: "", method: "" });
  };
  const closePayModal = () => { if (!paySaving) setPayModal(null); };

  const submitPay = async () => {
    if (!payModal?.row?.token) {
      setPayError("This reservation has no payment token — please refresh.");
      return;
    }
    const amount = num(payModal.amount);
    if (amount <= 0) {
      setPayError("Enter an amount greater than 0.");
      return;
    }
    if (amount > num(payModal.row.balance_amount)) {
      setPayError("Amount cannot exceed the outstanding balance.");
      return;
    }
    if (!payModal.method) {
      setPayError("Select a payment method.");
      return;
    }
    setPaySaving(true);
    setPayError(null);
    try {
      await APICall.postT(`/hotel/room_reservation_pay/${encodeURIComponent(payModal.row.token)}`, {
        paying_amount: amount,
        payment_method: payModal.method,
      });
      showToast("success", "Payment recorded.");
      setPayModal(null);
      loadReservations();
    } catch (err) {
      setPayError(errMsg(err, "Failed to record payment."));
    } finally {
      if (mounted.current) setPaySaving(false);
    }
  };

  const openRefundModal = (row) => {
    setRefundError(null);
    setRefundModal({ row, amount: "", method: "" });
  };
  const closeRefundModal = () => { if (!refundSaving) setRefundModal(null); };

  const submitRefund = async () => {
    if (!refundModal?.row?.token) {
      setRefundError("This reservation has no refund token — please refresh.");
      return;
    }
    const amount = num(refundModal.amount);
    if (amount <= 0) {
      setRefundError("Enter an amount greater than 0.");
      return;
    }
    if (amount > num(refundModal.row.extra_amount)) {
      setRefundError("Amount cannot exceed the refundable amount.");
      return;
    }
    if (!refundModal.method) {
      setRefundError("Select a refund method.");
      return;
    }
    setRefundSaving(true);
    setRefundError(null);
    try {
      await APICall.postT(`/hotel/room_reservation_refund/${encodeURIComponent(refundModal.row.token)}`, {
        refund_amount: amount,
        refund_method: refundModal.method,
      });
      showToast("success", "Refund processed.");
      setRefundModal(null);
      loadReservations();
    } catch (err) {
      setRefundError(errMsg(err, "Failed to process refund."));
    } finally {
      if (mounted.current) setRefundSaving(false);
    }
  };

  const handleDelete = (row) => setPendingDelete(row);

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleteLoading(true);
    try {
      await APICall.deleteT(`/hotel/room_reservation/${pendingDelete.id}`);
      showToast("success", "Reservation deleted.");
      setPendingDelete(null);
      loadReservations();
    } catch (err) {
      showToast("error", errMsg(err, "Failed to delete reservation."));
    } finally {
      if (mounted.current) setDeleteLoading(false);
    }
  };

  const handleView = (row) => {
    setSelectedReservation(row);
    setIsViewModalOpen(true);
    setPaymentHistory([]);
    if (row?.token) {
      APICall.getT(`/hotel/room_reservation_payments/${encodeURIComponent(row.token)}`)
        .then((res) => {
          if (mounted.current) setPaymentHistory(readList(res));
        })
        .catch(() => { /* history is best-effort; view still works without it */ });
    }
  };

  const handleEdit = (row) => {
    setSelectedReservation(row);
    setEditFormData({
      ...row,
      room_type_ids: parseArr(row.room_type_ids),
      room_ids: parseArr(row.room_ids),
      rate_type: parseArr(row.rate_type),
      arrival_date: isoDay(row.arrival_date),
      departure_date: isoDay(row.departure_date),
    });
    setEditError(null);
    setIsEditModalOpen(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSingleIdChange = (name) => (e) => {
    const v = e.target.value;
    setEditFormData((prev) => ({ ...prev, [name]: v ? [Number(v)] : [] }));
  };

  const handleRateTypeChange = (index, value) => {
    setEditFormData((prev) => {
      const next = [...(prev.rate_type || [])];
      next[index] = value;
      return { ...prev, rate_type: next };
    });
  };

  const validateEdit = (form) => {
    if (!form.first_name?.trim()) return "First name is required.";
    if (!form.phone_number?.trim()) return "Phone number is required.";
    if (!form.arrival_date || !form.departure_date) return "Arrival and departure dates are required.";
    if (isoDay(form.arrival_date) > isoDay(form.departure_date)) return "Departure date must be on or after arrival.";
    if (num(form.no_of_nights) < 1) return "Number of nights must be at least 1.";
    if (num(form.no_of_adults) < 1) return "At least one adult is required.";
    if (num(form.no_of_rooms) < 1) return "At least one room is required.";
    if (!form.identity_type_id) return "Identity type is required.";
    const statusLabels = reservationStatuses.map((s) => s.reservation_status);
    if (!form.reservation_status || (statusLabels.length > 0 && !statusLabels.includes(form.reservation_status))) {
      return `Reservation status must be one of: ${statusLabels.join(", ")}`;
    }
    if (num(form.overall_amount) < 0) return "Overall amount cannot be negative.";
    if (num(form.total_amount) < 0) return "Total amount cannot be negative.";
    if (num(form.tax_percentage) < 0 || num(form.tax_percentage) > 100) return "Tax percentage must be between 0 and 100.";
    if (num(form.discount_percentage) < 0 || num(form.discount_percentage) > 100) return "Discount percentage must be between 0 and 100.";
    return null;
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    const v = validateEdit(editFormData);
    if (v) {
      setEditError(v);
      return;
    }
    if (!selectedReservation?.id) {
      setEditError("Missing reservation id.");
      return;
    }

    setEditSaving(true);
    setEditError(null);
    try {
      const fd = new FormData();
      const put = (k, val) => {
        if (val === undefined || val === null) return;
        fd.append(k, typeof val === "object" ? JSON.stringify(val) : String(val));
      };
      Object.keys(editFormData).forEach((k) => put(k, editFormData[k]));

      const numeric = {
        no_of_nights: num(editFormData.no_of_nights),
        no_of_rooms: num(editFormData.no_of_rooms) || 1,
        no_of_adults: num(editFormData.no_of_adults) || 1,
        no_of_children: num(editFormData.no_of_children),
        extra_bed_count: num(editFormData.extra_bed_count),
        extra_bed_cost: num(editFormData.extra_bed_cost),
        total_amount: num(editFormData.total_amount),
        tax_percentage: num(editFormData.tax_percentage),
        tax_amount: num(editFormData.tax_amount),
        discount_percentage: num(editFormData.discount_percentage),
        discount_amount: num(editFormData.discount_amount),
        extra_charges: num(editFormData.extra_charges),
        overall_amount: num(editFormData.overall_amount),
        paid_amount: num(editFormData.paid_amount),
        balance_amount: num(editFormData.balance_amount),
        extra_amount: num(editFormData.extra_amount),
        payment_method_id: num(editFormData.payment_method_id) || 1,
        booking_status_id: num(editFormData.booking_status_id) || 1,
        identity_type_id: num(editFormData.identity_type_id) || 1,
      };
      Object.entries(numeric).forEach(([k, val]) => fd.set(k, String(val)));
      fd.set("room_type_ids", JSON.stringify(editFormData.room_type_ids || []));
      fd.set("room_ids", JSON.stringify(editFormData.room_ids || []));
      fd.set("rate_type", JSON.stringify((editFormData.rate_type || []).filter(Boolean)));
      fd.set("id", String(selectedReservation.id));

      await APICall.putT("/hotel/room_reservation", fd);
      showToast("success", "Reservation updated.");
      setIsEditModalOpen(false);
      loadReservations();
    } catch (err) {
      setEditError(errMsg(err, "Failed to update reservation."));
    } finally {
      if (mounted.current) setEditSaving(false);
    }
  };

  // -----------------------------------------------------------------------
  // Print — HTML-escapes every user-controlled field.
  // -----------------------------------------------------------------------
  const handlePrint = (row) => {
    const printWindow = window.open("", "_blank", "noopener,noreferrer");
    if (!printWindow) {
      showToast("error", "The print window was blocked. Please allow pop-ups for this site.");
      return;
    }
    const content = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>Reservation Receipt ${escapeHtml(row.room_reservation_id)}</title>
<style>
  body { font-family: Arial, sans-serif; margin: 40px; color: #111827; }
  .header { text-align: center; margin-bottom: 30px; }
  .section { margin-bottom: 20px; }
  .section h3 { border-bottom: 2px solid #000; padding-bottom: 5px; }
  .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .detail-item { margin-bottom: 8px; }
  .label { font-weight: bold; color: #555; }
  .total { font-size: 18px; font-weight: bold; margin-top: 20px; }
</style>
</head>
<body>
  <div class="header">
    <h1>Reservation Receipt</h1>
    <p>Reservation ID: ${escapeHtml(row.room_reservation_id)}</p>
    <p>Date: ${escapeHtml(new Date().toLocaleDateString())}</p>
  </div>
  <div class="section">
    <h3>Guest Information</h3>
    <div class="grid">
      <div class="detail-item"><span class="label">Name:</span> ${escapeHtml(`${row.first_name || ""} ${row.last_name || ""}`.trim() || "—")}</div>
      <div class="detail-item"><span class="label">Phone:</span> ${escapeHtml(row.phone_number || "—")}</div>
      <div class="detail-item"><span class="label">Email:</span> ${escapeHtml(row.email || "N/A")}</div>
      <div class="detail-item"><span class="label">Reservation Type:</span> ${escapeHtml(row.reservation_type || "")}</div>
      <div class="detail-item"><span class="label">Status:</span> ${escapeHtml(row.reservation_status || "")}</div>
      <div class="detail-item"><span class="label">Confirmation Code:</span> ${escapeHtml(row.confirmation_code || "N/A")}</div>
    </div>
  </div>
  <div class="section">
    <h3>Stay Information</h3>
    <div class="grid">
      <div class="detail-item"><span class="label">Arrival Date:</span> ${escapeHtml(row.arrival_date || "")}</div>
      <div class="detail-item"><span class="label">Departure Date:</span> ${escapeHtml(row.departure_date || "")}</div>
      <div class="detail-item"><span class="label">Nights:</span> ${escapeHtml(row.no_of_nights ?? "")}</div>
      <div class="detail-item"><span class="label">Rooms:</span> ${escapeHtml(row.no_of_rooms ?? "")}</div>
      <div class="detail-item"><span class="label">Adults:</span> ${escapeHtml(row.no_of_adults ?? "")}</div>
      <div class="detail-item"><span class="label">Children:</span> ${escapeHtml(row.no_of_children ?? 0)}</div>
      <div class="detail-item"><span class="label">Extra Beds:</span> ${escapeHtml(row.extra_bed_count ?? 0)}</div>
      <div class="detail-item"><span class="label">Payment Method:</span> ${escapeHtml(row.payment_method_id ?? "")}</div>
    </div>
  </div>
  <div class="section">
    <h3>Payment Summary</h3>
    <div class="detail-item"><span class="label">Total Amount:</span> ${escapeHtml(row.total_amount ?? 0)}</div>
    <div class="detail-item"><span class="label">Tax Amount:</span> ${escapeHtml(row.tax_amount ?? 0)}</div>
    <div class="detail-item"><span class="label">Discount Amount:</span> ${escapeHtml(row.discount_amount ?? 0)}</div>
    <div class="detail-item"><span class="label">Extra Charges:</span> ${escapeHtml(row.extra_charges ?? 0)}</div>
    <div class="detail-item"><span class="label">Paid Amount:</span> ${escapeHtml(row.paid_amount ?? 0)}</div>
    <div class="detail-item"><span class="label">Balance Amount:</span> ${escapeHtml(row.balance_amount ?? 0)}</div>
    <div class="detail-item total"><span class="label">Overall Amount:</span> ${escapeHtml(row.overall_amount ?? 0)}</div>
  </div>
  <script>window.addEventListener("load", function(){ window.print(); });</script>
</body>
</html>`;
    printWindow.document.write(content);
    printWindow.document.close();
  };

  // -----------------------------------------------------------------------
  // CSV export
  // -----------------------------------------------------------------------
  const handleExportCsv = () => {
    const list = Array.isArray(data) ? data : [];
    if (list.length === 0) {
      showToast("error", "No reservations to export.");
      return;
    }
    const header = [
      "Reservation ID", "Type", "Name", "Phone", "Email",
      "Arrival", "Departure", "Nights", "Rooms", "Adults", "Children",
      "Status", "Overall Amount", "Paid", "Balance",
    ];
    const rows = list.map((r) => [
      r.room_reservation_id ?? "",
      r.reservation_type ?? "",
      `${r.first_name || ""} ${r.last_name || ""}`.trim(),
      r.phone_number ?? "",
      r.email ?? "",
      r.arrival_date ?? "",
      r.departure_date ?? "",
      r.no_of_nights ?? "",
      r.no_of_rooms ?? "",
      r.no_of_adults ?? "",
      r.no_of_children ?? "",
      r.reservation_status ?? "",
      r.overall_amount ?? "",
      r.paid_amount ?? "",
      r.balance_amount ?? "",
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
    a.download = `reservations-${isoDay(new Date().toISOString())}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isLoading = data === null;
  const tableData = Array.isArray(data) ? data : [];

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------
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
          Loading reservations…
        </div>
      )}

      {!isLoading && (
        <TableTemplate
          title="Reservation List"
          variant="striped"
          pagination
          pageSize={5}
          searchable
          exportable
          hasActionButton
          actionButton={{
            icon: <Download size={18} />,
            label: "Export CSV",
            onClick: handleExportCsv,
            size: "small",
            variant: "outline",
          }}
          columns={[
            { key: "room_reservation_id", title: "Reservation ID", align: "center", width: "160px" },
            { key: "reservation_type", title: "Reservation Type", align: "center" },
            {
              key: "first_name",
              title: "Name",
              align: "center",
              render: (row) => `${row.first_name || ""} ${row.last_name || ""}`.trim() || "—",
            },
            { key: "phone_number", title: "Phone", align: "center" },
            { key: "arrival_date", title: "Arrival Date", align: "center" },
            { key: "departure_date", title: "Departure Date", align: "center" },
            { key: "reservation_status", title: "Reservation Status", align: "center", type: "badge" },
            {
              key: "actions",
              title: "Actions",
              align: "center",
              type: "custom",
              render: (row) => {
                const lock = rowLocks[row.id];
                const status = row.reservation_status;
                const isLocked = LOCKED_STATUSES.has(status);
                return (
                  <div className="table-actions">
                    <button
                      type="button"
                      className="table-action-btn print"
                      title="Print receipt"
                      aria-label={`Print reservation ${row.room_reservation_id}`}
                      onClick={() => handlePrint(row)}
                    >
                      <Printer size={16} />
                    </button>

                    {CAN_CHECKIN.has(status) && (
                      <button
                        type="button"
                        className="table-action-btn approve"
                        title="Check in"
                        aria-label={`Check in ${row.first_name || "guest"}`}
                        onClick={() => handleApprove(row.id)}
                        disabled={lock === "checkin"}
                        aria-busy={lock === "checkin"}
                      >
                        <Check size={16} />
                      </button>
                    )}

                    {CAN_CHECKOUT.has(status) && (
                      <button
                        type="button"
                        className="table-action-btn checkout"
                        title="Check out"
                        aria-label={`Check out ${row.first_name || "guest"}`}
                        onClick={() => handleCheckout(row.id, row.token)}
                        disabled={lock === "checkout"}
                        aria-busy={lock === "checkout"}
                      >
                        <LogOut size={16} />
                      </button>
                    )}

                    <button
                      type="button"
                      className="table-action-btn view"
                      title="View details"
                      aria-label={`View reservation ${row.room_reservation_id}`}
                      onClick={() => handleView(row)}
                    >
                      <Eye size={16} />
                    </button>

                    {!isLocked && (
                      <button
                        type="button"
                        className="table-action-btn edit"
                        title="Edit"
                        aria-label={`Edit reservation ${row.room_reservation_id}`}
                        onClick={() => handleEdit(row)}
                      >
                        <Pencil size={16} />
                      </button>
                    )}

                    {!isLocked && (
                      <button
                        type="button"
                        className="table-action-btn delete"
                        title="Delete"
                        aria-label={`Delete reservation ${row.room_reservation_id}`}
                        onClick={() => handleDelete(row)}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}

                    {num(row.balance_amount) > 0 && (
                      <button
                        type="button"
                        className="table-action-btn pay"
                        title="Record payment"
                        aria-label={`Record payment for ${row.first_name || "guest"}`}
                        onClick={() => openPayModal(row)}
                      >
                        <CreditCard size={16} />
                      </button>
                    )}

                    {num(row.extra_amount) > 0 && (
                      <button
                        type="button"
                        className="table-action-btn refund"
                        title="Refund"
                        aria-label={`Refund ${row.first_name || "guest"}`}
                        onClick={() => openRefundModal(row)}
                      >
                        <HandCoins size={16} />
                      </button>
                    )}
                  </div>
                );
              },
            },
          ]}
          data={tableData}
        />
      )}

      {!isLoading && tableData.length === 0 && !error && (
        <div className="reservation-empty">
          No reservations yet. Use “Add New Reservation” to create the first one.
        </div>
      )}

      {/* -------------------------------------------------------------- */}
      {/* View Modal                                                     */}
      {/* -------------------------------------------------------------- */}
      {isViewModalOpen && selectedReservation && (
        <div
          className="modal-container"
          role="dialog"
          aria-modal="true"
          aria-labelledby="view-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget) setIsViewModalOpen(false); }}
        >
          <div className="modal-content view-modal">
            <div className="modal-header">
              <h2 className="modal-title" id="view-modal-title">
                Reservation Details
                <span className="reservation-id">#{selectedReservation.room_reservation_id}</span>
              </h2>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setIsViewModalOpen(false)}
                aria-label="Close reservation details"
              >
                <X size={24} />
              </button>
            </div>

            <div className="modal-body">
              <div className="view-modal-grid">
                <div className="view-section">
                  <h3 className="section-title">Guest Information</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Salutation</span>
                      <span className="field-value">{selectedReservation.salutation || "N/A"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">First Name</span>
                      <span className="field-value">{selectedReservation.first_name || "—"}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Last Name</span>
                      <span className="field-value">{selectedReservation.last_name || "—"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Email</span>
                      <span className="field-value email-value">{selectedReservation.email || "N/A"}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Phone Number</span>
                      <span className="field-value phone-value">{selectedReservation.phone_number || "—"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Reservation Status</span>
                      <span className={`field-value status-badge ${getStatusBadgeClass(selectedReservation.reservation_status)}`}>
                        {selectedReservation.reservation_status || "—"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="view-section">
                  <h3 className="section-title">Stay Information</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Arrival Date</span>
                      <span className="field-value">{selectedReservation.arrival_date || "—"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Departure Date</span>
                      <span className="field-value">{selectedReservation.departure_date || "—"}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">No. of Nights</span>
                      <span className="field-value">{selectedReservation.no_of_nights ?? "—"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">No. of Rooms</span>
                      <span className="field-value">{selectedReservation.no_of_rooms ?? "—"}</span>
                    </div>
                  </div>
                </div>

                <div className="view-section">
                  <h3 className="section-title">Room Details</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Room Type</span>
                      <span className="field-value json-value">
                        {parseArr(selectedReservation.room_type_ids)
                          .map((id) => roomTypes.find((rt) => rt.id === id)?.room_type_name)
                          .filter(Boolean)
                          .join(", ") || "N/A"}
                      </span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Room Number</span>
                      <span className="field-value json-value">
                        {parseArr(selectedReservation.room_ids)
                          .map((id) => rooms.find((r) => r.id === id)?.room_no)
                          .filter(Boolean)
                          .join(", ") || "N/A"}
                      </span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Rate Types</span>
                      <span className="field-value json-value">
                        {parseArr(selectedReservation.rate_type).join(", ") || "N/A"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="view-section">
                  <h3 className="section-title">Occupancy</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">No. of Adults</span>
                      <span className="field-value">{selectedReservation.no_of_adults ?? "—"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">No. of Children</span>
                      <span className="field-value">{selectedReservation.no_of_children ?? 0}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Extra Bed Count</span>
                      <span className="field-value">{selectedReservation.extra_bed_count ?? 0}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Extra Bed Cost</span>
                      <span className="field-value">{selectedReservation.extra_bed_cost ?? 0}</span>
                    </div>
                  </div>
                </div>

                <div className="view-section">
                  <h3 className="section-title">Complementary</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Room Complementary</span>
                      <span className="field-value">{selectedReservation.room_complementary || "None"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Common Complementary</span>
                      <span className="field-value">{selectedReservation.common_complementary || "None"}</span>
                    </div>
                  </div>
                </div>

                <div className="view-section">
                  <h3 className="section-title">Payment Details</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Total Amount</span>
                      <span className="field-value amount">{selectedReservation.total_amount ?? 0}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Tax Percentage</span>
                      <span className="field-value">{selectedReservation.tax_percentage ?? 0}%</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Tax Amount</span>
                      <span className="field-value amount">{selectedReservation.tax_amount ?? 0}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Tax Type</span>
                      <span className="field-value">
                        {taxTypes.find((t) => t.id === selectedReservation.tax_type_id)?.tax_name || "N/A"}
                      </span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Discount Percentage</span>
                      <span className="field-value">{selectedReservation.discount_percentage ?? 0}%</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Discount Amount</span>
                      <span className="field-value amount discount">
                        {selectedReservation.discount_amount ? `-${selectedReservation.discount_amount}` : 0}
                      </span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Discount Type</span>
                      <span className="field-value">
                        {discountTypes.find((d) => d.id === selectedReservation.discount_type_id)?.discount_name
                          || discountTypes.find((d) => d.id === selectedReservation.discount_type_id)?.name
                          || "N/A"}
                      </span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Extra Charges</span>
                      <span className="field-value amount">{selectedReservation.extra_charges ?? 0}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Room Amount</span>
                      <span className="field-value amount">{selectedReservation.room_amount ?? 0}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Overall Amount</span>
                      <span className="field-value amount total">{selectedReservation.overall_amount ?? 0}</span>
                    </div>
                  </div>
                </div>

                <div className="view-section">
                  <h3 className="section-title">Payment Status</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Payment Method</span>
                      <span className="field-value">
                        {paymentMethods.find((p) => p.id === selectedReservation.payment_method_id)?.payment_method
                          || selectedReservation.payment_method_id
                          || "N/A"}
                      </span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Paying Amount</span>
                      <span className="field-value amount">{selectedReservation.paying_amount ?? 0}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Paid Amount</span>
                      <span className="field-value amount paid">{selectedReservation.paid_amount ?? 0}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Balance Amount</span>
                      <span className="field-value amount balance">{selectedReservation.balance_amount ?? 0}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Extra Amount</span>
                      <span className="field-value amount">{selectedReservation.extra_amount ?? 0}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Identity Type</span>
                      <span className="field-value">
                        {identityTypes.find((i) => i.id === selectedReservation.identity_type_id)?.proof_name
                          || "N/A"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="view-section">
                  <h3 className="section-title">Payment History</h3>
                  {paymentHistory.length === 0 ? (
                    <div className="rmv-empty inline">No payments recorded yet.</div>
                  ) : (
                    <table className="payment-history-table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Method</th>
                          <th>Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paymentHistory.map((p) => (
                          <tr key={p.id}>
                            <td>{p.paid_date}</td>
                            <td>{p.payment_method}</td>
                            <td>{p.amount}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>

                <div className="view-section">
                  <h3 className="section-title">Additional Information</h3>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Booking Status</span>
                      <span className="field-value">{selectedReservation.booking_status_id || "N/A"}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Reservation Type</span>
                      <span className="field-value">{selectedReservation.reservation_type || "N/A"}</span>
                    </div>
                  </div>
                  <div className="field-pair">
                    <div className="field-group">
                      <span className="field-label">Confirmation Code</span>
                      <span className="field-value code">{selectedReservation.confirmation_code || "N/A"}</span>
                    </div>
                    <div className="field-group full-width">
                      <span className="field-label">Proof Document</span>
                      <span className="field-value">{selectedReservation.proof_document || "No document uploaded"}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <div className="footer-actions">
                <button
                  type="button"
                  className="btn btn-icon"
                  onClick={() => handlePrint(selectedReservation)}
                  title="Print receipt"
                >
                  <Printer size={18} />
                  Print Receipt
                </button>
                <div className="action-buttons">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setIsViewModalOpen(false)}
                  >
                    Close
                  </button>
                  {!LOCKED_STATUSES.has(selectedReservation.reservation_status) && (
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => {
                        setIsViewModalOpen(false);
                        handleEdit(selectedReservation);
                      }}
                    >
                      Edit Reservation
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* -------------------------------------------------------------- */}
      {/* Edit Modal                                                     */}
      {/* -------------------------------------------------------------- */}
      {isEditModalOpen && selectedReservation && (
        <div
          className="modal-container"
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget && !editSaving) setIsEditModalOpen(false); }}
        >
          <div className="modal-content edit-modal">
            <div className="modal-header">
              <h2 className="modal-title" id="edit-modal-title">Edit Reservation</h2>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setIsEditModalOpen(false)}
                aria-label="Close edit reservation"
                disabled={editSaving}
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="edit-modal-form" noValidate>
              {editError && (
                <div className="reservation-alert inline" role="alert">
                  {editError}
                </div>
              )}

              <div className="modal-body edit-modal-body">
                <div className="modal-body-content">
                  {/* Guest Information */}
                  <div className="modal-section">
                    <h3 className="section-title">Guest Information</h3>
                    <div className="form-grid">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-salutation">Salutation</label>
                        <select
                          id="edit-salutation"
                          name="salutation"
                          value={editFormData.salutation || ""}
                          onChange={handleInputChange}
                          className="form-select"
                        >
                          <option value="">Select</option>
                          {SALUTATIONS.map((s) => (
                            <option key={s} value={s}>{s}</option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-first-name">First Name *</label>
                        <input
                          id="edit-first-name"
                          type="text"
                          name="first_name"
                          value={editFormData.first_name || ""}
                          onChange={handleInputChange}
                          required
                          maxLength={100}
                          autoComplete="given-name"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-last-name">Last Name</label>
                        <input
                          id="edit-last-name"
                          type="text"
                          name="last_name"
                          value={editFormData.last_name || ""}
                          onChange={handleInputChange}
                          maxLength={100}
                          autoComplete="family-name"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-phone">Phone Number *</label>
                        <input
                          id="edit-phone"
                          type="tel"
                          name="phone_number"
                          inputMode="tel"
                          value={editFormData.phone_number || ""}
                          onChange={handleInputChange}
                          required
                          maxLength={20}
                          autoComplete="tel"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-email">Email</label>
                        <input
                          id="edit-email"
                          type="email"
                          name="email"
                          inputMode="email"
                          value={editFormData.email || ""}
                          onChange={handleInputChange}
                          maxLength={100}
                          autoComplete="email"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-identity-type">
                          Identity Type <span className="required">*</span>
                        </label>
                        <select
                          id="edit-identity-type"
                          style={{ height: "40px" }}
                          value={editFormData.identity_type_id || ""}
                          onChange={handleInputChange}
                          name="identity_type_id"
                          required
                        >
                          <option value="">— select —</option>
                          {identityTypes.map((identity) => (
                            <option key={identity.id} value={identity.id}>
                              {identity.proof_name}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Stay Information */}
                  <div className="modal-section">
                    <h3 className="section-title">Stay Information</h3>
                    <div className="form-grid">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-arrival">Arrival Date *</label>
                        <input
                          id="edit-arrival"
                          type="date"
                          name="arrival_date"
                          value={editFormData.arrival_date || ""}
                          onChange={handleInputChange}
                          required
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-departure">Departure Date *</label>
                        <input
                          id="edit-departure"
                          type="date"
                          name="departure_date"
                          value={editFormData.departure_date || ""}
                          onChange={handleInputChange}
                          required
                          min={editFormData.arrival_date || undefined}
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-nights">Number of Nights *</label>
                        <input
                          id="edit-nights"
                          type="number"
                          name="no_of_nights"
                          value={editFormData.no_of_nights ?? ""}
                          onChange={handleInputChange}
                          required
                          min="1"
                          className="form-input"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Room Information */}
                  <div className="modal-section">
                    <h3 className="section-title">Room Information</h3>
                    <div className="form-grid">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-room-type">
                          Room Type <span className="required">*</span>
                        </label>
                        <select
                          id="edit-room-type"
                          style={{ height: "40px" }}
                          value={(editFormData.room_type_ids && editFormData.room_type_ids[0]) || ""}
                          onChange={handleSingleIdChange("room_type_ids")}
                          name="room_type_ids"
                          required
                        >
                          <option value="">— select —</option>
                          {roomTypes.map((roomType) => (
                            <option key={roomType.id} value={roomType.id}>
                              {roomType.room_type_name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-room-number">Room Number</label>
                        <input
                          id="edit-room-number"
                          className="form-input"
                          type="text"
                          readOnly
                          aria-readonly="true"
                          title="Room assignment is managed under Booking / Room View"
                          name="room_ids_display"
                          value={
                            (editFormData?.room_ids?.length > 0
                              ? editFormData.room_ids
                                  .map((id) => rooms.find((rt) => rt.id === id)?.room_no)
                                  .filter(Boolean)
                                  .join(", ")
                              : "—")
                          }
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-rate-type">Rate Type</label>
                        <input
                          id="edit-rate-type"
                          type="text"
                          name="rate_type_input"
                          value={(editFormData.rate_type && editFormData.rate_type[0]) || ""}
                          onChange={(e) => handleRateTypeChange(0, e.target.value)}
                          placeholder="e.g. STANDARD"
                          maxLength={50}
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-no-rooms">Number of Rooms *</label>
                        <input
                          id="edit-no-rooms"
                          type="number"
                          name="no_of_rooms"
                          value={editFormData.no_of_rooms ?? ""}
                          onChange={handleInputChange}
                          required
                          min="1"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-adults">Adults *</label>
                        <input
                          id="edit-adults"
                          type="number"
                          name="no_of_adults"
                          value={editFormData.no_of_adults ?? ""}
                          onChange={handleInputChange}
                          required
                          min="1"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-children">Children</label>
                        <input
                          id="edit-children"
                          type="number"
                          name="no_of_children"
                          value={editFormData.no_of_children ?? ""}
                          onChange={handleInputChange}
                          min="0"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-extra-bed-count">Extra Bed Count</label>
                        <input
                          id="edit-extra-bed-count"
                          type="number"
                          name="extra_bed_count"
                          value={editFormData.extra_bed_count ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-extra-bed-cost">Extra Bed Cost</label>
                        <input
                          id="edit-extra-bed-cost"
                          type="number"
                          name="extra_bed_cost"
                          value={editFormData.extra_bed_cost ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Reservation Details */}
                  <div className="modal-section">
                    <h3 className="section-title">Reservation Details</h3>
                    <div className="form-grid">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-payment-method">Payment Method *</label>
                        <select
                          id="edit-payment-method"
                          name="payment_method_id"
                          value={editFormData.payment_method_id || ""}
                          onChange={handleInputChange}
                          required
                          className="form-select"
                        >
                          <option value="">— select —</option>
                          {paymentMethods.map((pm) => (
                            <option key={pm.id} value={pm.id}>{pm.payment_method}</option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-booking-status">Booking Status *</label>
                        <input
                          id="edit-booking-status"
                          type="number"
                          name="booking_status_id"
                          value={editFormData.booking_status_id ?? 1}
                          onChange={handleInputChange}
                          required
                          min="1"
                          className="form-input"
                          title="Booking status ID — dropdown pending master-data endpoint"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-reservation-type">Reservation Type *</label>
                        <select
                          id="edit-reservation-type"
                          name="reservation_type"
                          value={editFormData.reservation_type || ""}
                          onChange={handleInputChange}
                          required
                          className="form-select"
                        >
                          <option value="">— select —</option>
                          {RESERVATION_TYPES.map((rt) => (
                            <option key={rt} value={rt}>{rt}</option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-reservation-status">Reservation Status *</label>
                        <select
                          id="edit-reservation-status"
                          name="reservation_status"
                          value={editFormData.reservation_status || ""}
                          onChange={handleInputChange}
                          required
                          className="form-select"
                        >
                          <option value="">— select —</option>
                          {reservationStatuses.map((s) => (
                            <option key={s.id} value={s.reservation_status}>{s.reservation_status}</option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-room-comp">Room Complementary</label>
                        <input
                          id="edit-room-comp"
                          type="text"
                          name="room_complementary"
                          value={editFormData.room_complementary || ""}
                          onChange={handleInputChange}
                          maxLength={200}
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-common-comp">Common Complementary</label>
                        <input
                          id="edit-common-comp"
                          type="text"
                          name="common_complementary"
                          value={editFormData.common_complementary || ""}
                          onChange={handleInputChange}
                          maxLength={200}
                          className="form-input"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Payment Information */}
                  <div className="modal-section">
                    <h3 className="section-title">Payment Information</h3>
                    <div className="form-grid">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-total-amount">Total Amount *</label>
                        <input
                          id="edit-total-amount"
                          type="number"
                          name="total_amount"
                          value={editFormData.total_amount ?? ""}
                          onChange={handleInputChange}
                          required
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-tax-type">Tax Type</label>
                        <select
                          id="edit-tax-type"
                          name="tax_type_id"
                          value={editFormData.tax_type_id || ""}
                          onChange={handleInputChange}
                          className="form-select"
                        >
                          <option value="">— select —</option>
                          {taxTypes.map((t) => (
                            <option key={t.id} value={t.id}>
                              {t.tax_name} ({t.tax_percentage}%)
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-tax-percentage">Tax Percentage</label>
                        <input
                          id="edit-tax-percentage"
                          type="number"
                          name="tax_percentage"
                          value={editFormData.tax_percentage ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          max="100"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-tax-amount">Tax Amount</label>
                        <input
                          id="edit-tax-amount"
                          type="number"
                          name="tax_amount"
                          value={editFormData.tax_amount ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-discount-type">Discount Type</label>
                        <select
                          id="edit-discount-type"
                          name="discount_type_id"
                          value={editFormData.discount_type_id || ""}
                          onChange={handleInputChange}
                          className="form-select"
                        >
                          <option value="">— select —</option>
                          {discountTypes.map((d) => (
                            <option key={d.id} value={d.id}>
                              {d.discount_name || d.name || `#${d.id}`}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-discount-percentage">Discount Percentage</label>
                        <input
                          id="edit-discount-percentage"
                          type="number"
                          name="discount_percentage"
                          value={editFormData.discount_percentage ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          max="100"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-discount-amount">Discount Amount</label>
                        <input
                          id="edit-discount-amount"
                          type="number"
                          name="discount_amount"
                          value={editFormData.discount_amount ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-extra-charges">Extra Charges</label>
                        <input
                          id="edit-extra-charges"
                          type="number"
                          name="extra_charges"
                          value={editFormData.extra_charges ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-overall">Overall Amount *</label>
                        <input
                          id="edit-overall"
                          type="number"
                          name="overall_amount"
                          value={editFormData.overall_amount ?? ""}
                          onChange={handleInputChange}
                          required
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-paid">Paid Amount</label>
                        <input
                          id="edit-paid"
                          type="number"
                          name="paid_amount"
                          value={editFormData.paid_amount ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-balance">Balance Amount</label>
                        <input
                          id="edit-balance"
                          type="number"
                          name="balance_amount"
                          value={editFormData.balance_amount ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-extra-amount">Extra Amount</label>
                        <input
                          id="edit-extra-amount"
                          type="number"
                          name="extra_amount"
                          value={editFormData.extra_amount ?? 0}
                          onChange={handleInputChange}
                          min="0"
                          step="0.01"
                          className="form-input"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsEditModalOpen(false)}
                  disabled={editSaving}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={editSaving}
                  aria-busy={editSaving}
                >
                  {editSaving ? "Updating…" : "Update Reservation"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete confirmation */}
      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete reservation"
        body={
          pendingDelete
            ? `Delete reservation ${pendingDelete.room_reservation_id} for ${pendingDelete.first_name || "guest"}? This action cannot be undone.`
            : ""
        }
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() => setPendingDelete(null)}
        loading={deleteLoading}
      />

      {/* Pay due amount */}
      {payModal && (
        <div
          className="modal-container"
          role="dialog"
          aria-modal="true"
          aria-labelledby="pay-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget) closePayModal(); }}
        >
          <div className="modal-content confirm-modal">
            <div className="modal-header">
              <h2 className="modal-title" id="pay-modal-title">Record Payment</h2>
              <button type="button" className="modal-close-btn" onClick={closePayModal} aria-label="Close" disabled={paySaving}>
                <X size={22} />
              </button>
            </div>
            <div className="modal-body">
              {payError && <div className="reservation-alert inline" role="alert">{payError}</div>}
              <div className="form-group">
                <label className="form-label">Due Amount</label>
                <input className="form-input" type="text" value={payModal.row?.balance_amount ?? 0} readOnly />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="pay-amount">Paying Amount</label>
                <input
                  id="pay-amount"
                  className="form-input"
                  type="number"
                  min="0"
                  step="0.01"
                  value={payModal.amount}
                  onChange={(e) => setPayModal((m) => ({ ...m, amount: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="pay-method">Payment Method</label>
                <select
                  id="pay-method"
                  className="form-select"
                  value={payModal.method}
                  onChange={(e) => setPayModal((m) => ({ ...m, method: e.target.value }))}
                >
                  <option value="">— select —</option>
                  {paymentMethods.map((pm) => (
                    <option key={pm.id} value={pm.payment_method}>{pm.payment_method}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={closePayModal} disabled={paySaving}>Cancel</button>
              <button type="button" className="btn btn-primary" onClick={submitPay} disabled={paySaving} aria-busy={paySaving}>
                {paySaving ? "Saving…" : "Submit"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Refund */}
      {refundModal && (
        <div
          className="modal-container"
          role="dialog"
          aria-modal="true"
          aria-labelledby="refund-modal-title"
          onClick={(e) => { if (e.target === e.currentTarget) closeRefundModal(); }}
        >
          <div className="modal-content confirm-modal">
            <div className="modal-header">
              <h2 className="modal-title" id="refund-modal-title">Refund Amount</h2>
              <button type="button" className="modal-close-btn" onClick={closeRefundModal} aria-label="Close" disabled={refundSaving}>
                <X size={22} />
              </button>
            </div>
            <div className="modal-body">
              {refundError && <div className="reservation-alert inline" role="alert">{refundError}</div>}
              <div className="form-group">
                <label className="form-label">Refundable Amount</label>
                <input className="form-input" type="text" value={refundModal.row?.extra_amount ?? 0} readOnly />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="refund-amount">Refund Amount</label>
                <input
                  id="refund-amount"
                  className="form-input"
                  type="number"
                  min="0"
                  step="0.01"
                  value={refundModal.amount}
                  onChange={(e) => setRefundModal((m) => ({ ...m, amount: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="refund-method">Refund Method</label>
                <select
                  id="refund-method"
                  className="form-select"
                  value={refundModal.method}
                  onChange={(e) => setRefundModal((m) => ({ ...m, method: e.target.value }))}
                >
                  <option value="">— select —</option>
                  {paymentMethods.map((pm) => (
                    <option key={pm.id} value={pm.payment_method}>{pm.payment_method}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={closeRefundModal} disabled={refundSaving}>Cancel</button>
              <button type="button" className="btn btn-primary" onClick={submitRefund} disabled={refundSaving} aria-busy={refundSaving}>
                {refundSaving ? "Saving…" : "Submit"}
              </button>
            </div>
          </div>
        </div>
      )}

      <Toast toast={toast} onClose={() => setToast(null)} />
    </>
  );
};

export default Reservation;
