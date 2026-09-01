import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Check, CreditCard, Download, HandCoins, LogOut } from "lucide-react";

import TableTemplate from "../../stories/TableTemplate";
import TableFilters, { FilterDate, FilterSelect } from "../../stories/TableFilters";
import Modal, { ConfirmModal } from "../../stories/Modal";
import Input from "../../stories/Form/Input";
import RowActions from "../../stories/RowActions";
import IconButton from "../../stories/IconButton";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { printDocument, printHeading, printRow } from "../../functions/printDocument";
import { formatAmount, isoDay, num } from "./reservationShared";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import "./Reservation.css";

/**
 * Reservation list.
 *
 * WHAT THIS SCREEN NO LONGER DECIDES
 *   Which actions a row offers used to be a set of status literals kept here
 *   ("Booked" for check-in, "No Show" for locked). Neither matched the
 *   property's actual vocabulary, which is Master Data and reads Confirmed /
 *   Checked-In / Checked-Out / Cancelled / No-Show / Pending / On Hold. The
 *   check-in button was therefore drawn for a status no reservation could ever
 *   hold, and the endpoint behind it refused every request for the same
 *   reason. Each row now carries `can_check_in` / `can_check_out` /
 *   `can_cancel` / `can_mark_no_show` from the API, derived from the same
 *   transition table the API enforces, so a button can never offer something
 *   the server would refuse.
 *
 *   The edit form no longer decides money either. Total, tax, discount,
 *   overall and balance were free-text number inputs posted straight to the
 *   database; they are now priced by /hotel/room_reservation_quote and shown
 *   read-only.
 */

// `isoDay`, `num`, `money` and `escapeHtml` used to be declared here as well
// as in reservationShared.js, which exists to hold exactly these. The local
// `money` also disagreed with the shared `formatAmount` on a null: "—" here,
// "0.00" there, on two screens showing the same folio.
const money = formatAmount;

const nightsBetween = (start, end) => {
  if (!start || !end) return 0;
  const a = new Date(start);
  const d = new Date(end);
  if (Number.isNaN(a.getTime()) || Number.isNaN(d.getTime())) return 0;
  const ms = d.getTime() - a.getTime();
  return ms <= 0 ? 0 : Math.round(ms / (1000 * 60 * 60 * 24));
};

// Compact date for table cells. A receptionist reads "07 Aug 26" faster than
// "2026-08-07", and two of them fit the column where two ISO strings did not.
// The View modal and the printed receipt keep the unambiguous ISO form.
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const shortDate = (v) => {
  const day = isoDay(v);
  if (day.length !== 10) return day || "—";
  const [y, m, d] = day.split("-");
  const month = MONTHS[Number(m) - 1];
  return month ? `${d} ${month} ${y.slice(2)}` : day;
};

const guestName = (r) =>
  [r?.first_name, r?.last_name].filter(Boolean).join(" ").trim() || "—";

const joinList = (values) =>
  Array.isArray(values) && values.length ? values.join(", ") : "—";

// Common cancellation reasons, as one-tap presets. Free text on purpose:
// there is no cancellation-reason master table, and inventing one would put a
// Master Data change inside a Reservation change. If these settle into a fixed
// vocabulary the property wants to manage, that is when they earn a table.
const CANCELLATION_PRESETS = [
  "Guest request",
  "Guest did not confirm",
  "Duplicate booking",
  "Overbooking resolved",
  "Payment not received",
  "Room unavailable",
];

const PAYMENT_STATES = ["Unpaid", "Partly paid", "Paid"];
// GROUP_RESERVATION is deliberately NOT offered. The API accepts it and the
// column stores it, but nothing behaves differently for a group: there is no
// linked-booking concept, no shared folio, no group rate. Offering it in a
// dropdown promises a feature that does not exist, and a booking saved with it
// is indistinguishable from a normal one. It stays in the backend vocabulary
// so any row already carrying it still reads back correctly -- see
// reservation_rules.RESERVATION_TYPES -- and returns to this list when group
// handling is actually built.
const RESERVATION_TYPES = ["RESERVATION", "CHECKIN"];
const SALUTATIONS = ["Mr.", "Mrs.", "Ms.", "Mx.", "Dr.", "Prof."];

const EMPTY_FILTERS = {
  reservation_status: "",
  reservation_type: "",
  payment_state: "",
  from_date: "",
  to_date: "",
};

const Reservation = () => {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const filtersActive = Object.values(filters).some(Boolean);

  // Filtering happens on the server so it applies to the whole book, not just
  // the page already downloaded.
  const query = useMemo(() => {
    const params = {};
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params[key] = value;
    });
    return params;
  }, [filters]);
  const queryKey = JSON.stringify(query);

  const {
    data: [reservationPage, statuses, rooms, paymentMethods, taxTypes, discountTypes],
    loading,
    error,
    reload,
  } = useApiResources(
    [
      {
        fetch: () => APICall.getT("/hotel/room_reservation", query),
        // The whole envelope: the response is capped, and `total` is the only
        // way this screen can tell that what it is showing is a page rather
        // than the book. Rows are unwrapped immediately below, so everything
        // downstream sees exactly what it saw before.
        select: (res) => res || null,
        initial: null,
        fallback: "Failed to load reservations.",
      },
      { fetch: () => APICall.getT("/masterdata/reservation_status"), select: readList },
      // Room *types* are not fetched here: the reservation payload already
      // carries `room_type_names`, so this screen no longer re-joins ids to
      // names against a second endpoint.
      { fetch: () => APICall.getT("/masterdata/room"), select: readList },
      { fetch: () => APICall.getT("/masterdata/payment_methods"), select: readList },
      { fetch: () => APICall.getT("/masterdata/tax"), select: readList },
      { fetch: () => APICall.getT("/masterdata/discount"), select: readList },
    ],
    { deps: [queryKey] },
  );

  // Rows for the table, plus an honest signal when the book is larger than the
  // page. The list endpoint caps what it returns; showing 200 of 5,000 rows and
  // letting the user search only those 200 would be a quietly wrong answer.
  const reservations = useMemo(() => readList(reservationPage), [reservationPage]);
  const totalReservations = Number(reservationPage?.total) || reservations.length;
  const listTruncated = totalReservations > reservations.length;

  const { toast, showToast } = useToast();

  const [viewRow, setViewRow] = useState(null);
  const [paymentHistory, setPaymentHistory] = useState([]);

  const [editRow, setEditRow] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState(null);
  const [editQuote, setEditQuote] = useState(null);
  const [editQuoteError, setEditQuoteError] = useState(null);
  const [editAvailability, setEditAvailability] = useState(null);

  const [deleteRow, setDeleteRow] = useState(null);
  const [cancelRow, setCancelRow] = useState(null);
  const [cancelReason, setCancelReason] = useState("");
  const [cancelError, setCancelError] = useState(null);
  const [cancelSaving, setCancelSaving] = useState(false);
  const [noShowRow, setNoShowRow] = useState(null);
  const [checkoutModal, setCheckoutModal] = useState(null); // { row, position, adjust }
  const [checkoutSaving, setCheckoutSaving] = useState(false);
  const [checkoutError, setCheckoutError] = useState(null);
  const [rowBusy, setRowBusy] = useState({});

  const [payModal, setPayModal] = useState(null);
  const [paySaving, setPaySaving] = useState(false);
  const [payError, setPayError] = useState(null);

  const [refundModal, setRefundModal] = useState(null);
  const [refundSaving, setRefundSaving] = useState(false);
  const [refundError, setRefundError] = useState(null);

  const statusOptions = useMemo(
    () => statuses.map((s) => s.reservation_status).filter(Boolean),
    [statuses],
  );

  const lockRow = (id, what) => setRowBusy((m) => ({ ...m, [id]: what }));
  const unlockRow = (id) =>
    setRowBusy((m) => {
      const next = { ...m };
      delete next[id];
      return next;
    });

  /* ======================= Row lifecycle actions ======================= */

  // Takes a thunk rather than a URL string, so every endpoint this screen
  // POSTs to is spelled out at its own call site.
  //
  // THIS IS NOT A STYLE CHOICE. Backend/tools/build_rbac_map.py derives the
  // gateway permission map from these call sites. Its pass B treats a verb
  // dispatched through a variable as evidence that the page might POST to any
  // endpoint literal in the same file. This file names /masterdata/room,
  // /masterdata/tax, /masterdata/discount, /masterdata/payment_methods and
  // /masterdata/reservation_status because it READS them, so a single
  // variable-dispatched POST silently granted the Reservation page write
  // access to five master-data tables. Keeping the literal at the call site
  // keeps the generated permissions honest.
  const runRowAction = useCallback(
    async (row, action, request, successText) => {
      if (rowBusy[row.id]) return;
      lockRow(row.id, action);
      try {
        await request();
        showToast(successText, "success");
        reload();
      } catch (err) {
        showToast(errMsg(err, `${action} failed.`), "error");
      } finally {
        unlockRow(row.id);
      }
    },
    [rowBusy, reload, showToast],
  );

  const handleCheckIn = (row) =>
    runRowAction(
      row,
      "check-in",
      () =>
        APICall.postT(
          `/hotel/room_reservation_checkin/${encodeURIComponent(row.token)}`,
        ),
      `${guestName(row)} checked in.`,
    );

  // Check-out asks the server what it would do before doing it. A guest
  // leaving on their booked departure date goes straight through; one leaving
  // early opens a dialog showing both bills, because which one applies is a
  // policy this system has no rate-plan configuration to decide from.
  const handleCheckOut = async (row) => {
    if (rowBusy[row.id]) return;
    lockRow(row.id, "check-out");
    try {
      const res = await APICall.getT(
        `/hotel/room_reservation_checkout_preview/${encodeURIComponent(row.token)}`,
      );
      const position = res?.data || null;
      if (position?.is_early && position?.repriced) {
        setCheckoutModal({ row, position, adjust: false });
        return;
      }
      await APICall.postT(
        `/hotel/room_reservation_checkout/${encodeURIComponent(row.token)}`,
        { adjust_stay: false },
      );
      showToast(`${guestName(row)} checked out.`, "success");
      reload();
    } catch (err) {
      showToast(errMsg(err, "Check-out failed."), "error");
    } finally {
      unlockRow(row.id);
    }
  };

  const submitCheckout = async () => {
    if (!checkoutModal || checkoutSaving) return;
    const { row, adjust } = checkoutModal;
    setCheckoutSaving(true);
    setCheckoutError(null);
    try {
      const res = await APICall.postT(
        `/hotel/room_reservation_checkout/${encodeURIComponent(row.token)}`,
        { adjust_stay: adjust },
      );
      const refund = num(res?.data?.extra_amount);
      showToast(
        refund > 0
          ? `${guestName(row)} checked out. ${money(refund)} is refundable.`
          : `${guestName(row)} checked out.`,
        "success",
      );
      setCheckoutModal(null);
      reload();
    } catch (err) {
      setCheckoutError(errMsg(err, "Check-out failed."));
    } finally {
      setCheckoutSaving(false);
    }
  };

  const openCancel = (row) => {
    setCancelReason("");
    setCancelError(null);
    setCancelRow(row);
  };

  const confirmCancel = async () => {
    const row = cancelRow;
    if (!row || cancelSaving) return;
    const reason = cancelReason.trim();
    if (!reason) {
      setCancelError("Please say why this reservation is being cancelled.");
      return;
    }
    setCancelSaving(true);
    setCancelError(null);
    try {
      const res = await APICall.postT(
        `/hotel/room_reservation_cancel/${encodeURIComponent(row.token)}`,
        { cancellation_reason: reason },
      );
      setCancelRow(null);
      const paid = num(res?.data?.amount_already_paid);
      showToast(
        paid > 0
          ? `Reservation cancelled. ${money(paid)} already paid — refund it from the folio if your policy allows.`
          : "Reservation cancelled.",
        "success",
      );
      reload();
    } catch (err) {
      setCancelError(errMsg(err, "Cancellation failed."));
    } finally {
      setCancelSaving(false);
    }
  };

  const confirmNoShow = async () => {
    const row = noShowRow;
    setNoShowRow(null);
    if (!row) return;
    try {
      await APICall.postT(
        `/hotel/room_reservation_no_show/${encodeURIComponent(row.token)}`,
      );
      showToast("Reservation marked as no-show.", "success");
      reload();
    } catch (err) {
      showToast(errMsg(err, "Could not mark as no-show."), "error");
    }
  };

  const confirmDelete = async () => {
    const row = deleteRow;
    setDeleteRow(null);
    if (!row) return;
    try {
      await APICall.deleteT(`/hotel/room_reservation/${row.id}`);
      showToast("Reservation deleted.", "delete");
      reload();
    } catch (err) {
      showToast(errMsg(err, "Delete failed."), "error");
    }
  };

  /* ============================== View ============================== */

  const openView = (row) => {
    setViewRow(row);
    setPaymentHistory([]);
    if (row?.token) {
      APICall.getT(`/hotel/room_reservation_payments/${encodeURIComponent(row.token)}`)
        .then((res) => setPaymentHistory(readList(res)))
        .catch(() => {
          /* history is best-effort; the rest of the view still stands */
        });
    }
  };

  /* ============================== Edit ============================== */

  const openEdit = (row) => {
    setEditRow(row);
    setEditError(null);
    setEditQuote(null);
    setEditQuoteError(null);
    setEditAvailability(null);
    setEditForm({
      salutation: row.salutation || "",
      first_name: row.first_name || "",
      last_name: row.last_name || "",
      phone_number: row.phone_number || "",
      email: row.email || "",
      arrival_date: isoDay(row.arrival_date),
      departure_date: isoDay(row.departure_date),
      room_ids: Array.isArray(row.room_ids) ? row.room_ids : [],
      rate_type: Array.isArray(row.rate_type) ? row.rate_type : [],
      no_of_adults: row.no_of_adults ?? 1,
      no_of_children: row.no_of_children ?? 0,
      payment_method_id: row.payment_method_id || "",
      tax_type_id: row.tax_type_id || "",
      discount_type_id: row.discount_type_id || "",
      extra_charges: row.extra_charges ?? 0,
      extra_bed_count: row.extra_bed_count ?? 0,
      room_amount: "",
      // Upper-cased to match the canonical vocabulary the options are built
      // from. The API normalises this on write, but rows created before it did
      // still hold title-case "Reservation", and a controlled <select> whose
      // value matches no <option> shows the first one while state holds
      // something else -- so editing a legacy booking looked like it had
      // silently changed type.
      reservation_type: (row.reservation_type || "RESERVATION").toUpperCase(),
      reservation_status: row.reservation_status || "",
      room_complementary: row.room_complementary || "",
      common_complementary: row.common_complementary || "",
    });
  };

  const closeEdit = () => {
    if (editSaving) return;
    setEditRow(null);
    setEditForm({});
  };

  const setField = (field) => (e) =>
    setEditForm((prev) => ({ ...prev, [field]: e.target.value }));

  // Nights are derived, never typed. The old form had a Number of Nights input
  // that was posted as-is, so it could disagree with the dates beside it.
  const editNights = nightsBetween(editForm.arrival_date, editForm.departure_date);

  const editQuoteRequest = useMemo(
    () => ({
      arrival_date: editForm.arrival_date,
      departure_date: editForm.departure_date,
      room_ids: editForm.room_ids || [],
      rate_type: editForm.rate_type || [],
      tax_type_id: editForm.tax_type_id || null,
      discount_type_id: editForm.discount_type_id || null,
      extra_charges: num(editForm.extra_charges),
      extra_bed_count: num(editForm.extra_bed_count),
      room_amount: editForm.room_amount === "" ? null : num(editForm.room_amount),
      paying_amount: num(editRow?.paid_amount),
    }),
    [editForm, editRow],
  );
  const editQuoteKey = JSON.stringify(editQuoteRequest);

  // Re-price and re-check availability whenever the amendment changes either.
  // Editing a booking is booking it again: moving the dates has to prove the
  // room is still free, which the old form never asked.
  useEffect(() => {
    if (!editRow) return undefined;
    let cancelled = false;
    const timer = setTimeout(() => {
      if (cancelled) return;
      if (!editForm.arrival_date || !editForm.departure_date || editNights < 1) {
        setEditQuote(null);
        return;
      }

      APICall.postT("/hotel/room_reservation_quote", editQuoteRequest)
        .then((res) => {
          if (!cancelled) {
            setEditQuote(res?.data || null);
            setEditQuoteError(null);
          }
        })
        .catch((err) => {
          if (!cancelled) {
            setEditQuote(null);
            setEditQuoteError(errMsg(err, "Could not price this stay."));
          }
        });

      APICall.getT("/hotel/room_availability", {
        arrival_date: editForm.arrival_date,
        departure_date: editForm.departure_date,
        // Without this the reservation collides with itself the moment the
        // guest so much as reopens the form.
        exclude_reservation_id: editRow.id,
      })
        .then((res) => {
          if (cancelled) return;
          const taken = new Set((res?.data?.booked_room_ids || []).map(Number));
          const clashing = (editForm.room_ids || []).filter((id) => taken.has(Number(id)));
          setEditAvailability(
            clashing.length
              ? `Room ${clashing
                  .map((id) => rooms.find((r) => r.id === Number(id))?.room_no || id)
                  .join(", ")} is not free for these dates.`
              : null,
          );
        })
        .catch(() => {
          if (!cancelled) setEditAvailability(null);
        });
    }, 300);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editQuoteKey, editRow, editNights]);

  const validateEdit = () => {
    if (!editForm.first_name?.trim()) return "First name is required.";
    if (!editForm.phone_number?.trim()) return "Phone number is required.";
    if (!editForm.arrival_date || !editForm.departure_date)
      return "Arrival and departure dates are required.";
    if (editNights < 1) return "Departure must be at least one night after arrival.";
    if (!editForm.payment_method_id) return "Payment method is required.";
    if (!editForm.reservation_status) return "Reservation status is required.";
    if (editAvailability) return editAvailability;
    if (editQuoteError) return editQuoteError;
    return null;
  };

  const submitEdit = async (e) => {
    e.preventDefault();
    if (editSaving) return;

    const problem = validateEdit();
    if (problem) {
      setEditError(problem);
      return;
    }

    setEditSaving(true);
    setEditError(null);
    try {
      const fd = new FormData();
      fd.set("id", String(editRow.id));
      fd.set("salutation", editForm.salutation || "");
      fd.set("first_name", editForm.first_name.trim());
      fd.set("last_name", (editForm.last_name || "").trim());
      fd.set("phone_number", editForm.phone_number.trim());
      fd.set("email", (editForm.email || "").trim());
      fd.set("arrival_date", editForm.arrival_date);
      fd.set("departure_date", editForm.departure_date);
      fd.set("room_ids", JSON.stringify(editForm.room_ids || []));
      fd.set("rate_type", JSON.stringify((editForm.rate_type || []).filter(Boolean)));
      fd.set("no_of_adults", String(num(editForm.no_of_adults) || 1));
      fd.set("no_of_children", String(num(editForm.no_of_children)));
      fd.set("payment_method_id", String(num(editForm.payment_method_id)));
      if (editForm.tax_type_id) fd.set("tax_type_id", String(num(editForm.tax_type_id)));
      if (editForm.discount_type_id) {
        fd.set("discount_type_id", String(num(editForm.discount_type_id)));
      }
      fd.set("extra_charges", String(num(editForm.extra_charges)));
      fd.set("extra_bed_count", String(num(editForm.extra_bed_count)));
      if (editForm.room_amount !== "") {
        fd.set("room_amount", String(num(editForm.room_amount)));
      }
      fd.set("reservation_type", editForm.reservation_type);
      fd.set("reservation_status", editForm.reservation_status);
      fd.set("room_complementary", editForm.room_complementary || "");
      fd.set("common_complementary", editForm.common_complementary || "");

      await APICall.putT("/hotel/room_reservation", fd);
      showToast("Reservation updated.", "update");
      setEditRow(null);
      reload();
    } catch (err) {
      setEditError(errMsg(err, "Failed to update reservation."));
    } finally {
      setEditSaving(false);
    }
  };

  /* ============================ Payments ============================ */

  const submitPay = async () => {
    if (paySaving) return;
    const amount = num(payModal?.amount);
    if (amount <= 0) {
      setPayError("Enter an amount greater than 0.");
      return;
    }
    if (!payModal.method) {
      setPayError("Select a payment method.");
      return;
    }
    setPaySaving(true);
    setPayError(null);
    try {
      await APICall.postT(
        `/hotel/room_reservation_pay/${encodeURIComponent(payModal.row.token)}`,
        { paying_amount: amount, payment_method: payModal.method },
      );
      showToast("Payment recorded.", "success");
      setPayModal(null);
      reload();
    } catch (err) {
      setPayError(errMsg(err, "Failed to record payment."));
    } finally {
      setPaySaving(false);
    }
  };

  const submitRefund = async () => {
    if (refundSaving) return;
    const amount = num(refundModal?.amount);
    if (amount <= 0) {
      setRefundError("Enter an amount greater than 0.");
      return;
    }
    if (!refundModal.method) {
      setRefundError("Select a refund method.");
      return;
    }
    setRefundSaving(true);
    setRefundError(null);
    try {
      await APICall.postT(
        `/hotel/room_reservation_refund/${encodeURIComponent(refundModal.row.token)}`,
        { refund_amount: amount, refund_method: refundModal.method },
      );
      showToast("Refund processed.", "success");
      setRefundModal(null);
      reload();
    } catch (err) {
      setRefundError(errMsg(err, "Failed to process refund."));
    } finally {
      setRefundSaving(false);
    }
  };

  /* ============================== Print ============================== */

  const handlePrint = (row) => {
    // Was a hand-written document with its own inline stylesheet, one of three
    // near-identical copies in the app. printDocument owns the boilerplate.
    const ok = printDocument({
      title: `Reservation ${row.room_reservation_id}`,
      heading: "Reservation Receipt",
      subtitle: `${row.room_reservation_id} · ${new Date().toLocaleDateString()}`,
      body:
        printHeading("Guest") +
        printRow("Name", guestName(row)) +
        printRow("Phone", row.phone_number || "—") +
        printRow("Email", row.email || "—") +
        printRow("Confirmation code", row.confirmation_code || "—") +
        printRow("Status", row.reservation_status || "—") +
        printHeading("Stay") +
        printRow("Arrival", isoDay(row.arrival_date)) +
        printRow("Departure", isoDay(row.departure_date)) +
        printRow("Nights", row.no_of_nights ?? "—") +
        printRow("Rooms", joinList(row.room_nos)) +
        printRow("Room types", joinList(row.room_type_names)) +
        printRow(
          "Guests",
          `${row.no_of_adults ?? 0} adult(s), ${row.no_of_children ?? 0} child(ren)`,
        ) +
        printHeading("Charges") +
        printRow("Room amount", money(row.room_amount)) +
        printRow("Extra charges", money(row.extra_charges)) +
        printRow(
          `Tax${row.tax_name ? ` (${row.tax_name} ${row.tax_percentage}%)` : ""}`,
          money(row.tax_amount),
        ) +
        printRow(
          `Discount${row.discount_name ? ` (${row.discount_name} ${row.discount_percentage}%)` : ""}`,
          `-${money(row.discount_amount)}`,
        ) +
        printRow("Total", money(row.overall_amount), { total: true }) +
        printRow("Paid", money(row.paid_amount)) +
        printRow("Balance", money(row.balance_amount)) +
        printRow("Payment method", row.payment_method || "—") +
        (row.cancellation_reason
          ? printHeading("Cancellation") +
            printRow("Reason", row.cancellation_reason) +
            printRow("Cancelled on", isoDay(row.cancelled_at))
          : ""),
    });

    if (!ok) {
      showToast("The print window was blocked. Please allow pop-ups for this site.", "error");
    }
  };

  /* ============================== Export ============================== */

  const handleExportCsv = () => {
    if (!reservations.length) {
      showToast("No reservations to export.", "error");
      return;
    }
    const header = [
      "Reservation ID", "Confirmation", "Type", "Guest", "Phone", "Email",
      "Arrival", "Departure", "Nights", "Rooms", "Room Types",
      "Adults", "Children", "Status", "Total", "Paid", "Balance", "Payment",
      "Cancellation Reason", "Cancelled On",
    ];
    const rows = reservations.map((r) => [
      r.room_reservation_id, r.confirmation_code, r.reservation_type,
      guestName(r), r.phone_number, r.email,
      isoDay(r.arrival_date), isoDay(r.departure_date), r.no_of_nights,
      (r.room_nos || []).join(" / "), (r.room_type_names || []).join(" / "),
      r.no_of_adults, r.no_of_children, r.reservation_status,
      r.overall_amount, r.paid_amount, r.balance_amount, r.payment_state,
      r.cancellation_reason ?? "", isoDay(r.cancelled_at),
    ]);
    const csv = [header, ...rows]
      .map((row) =>
        row
          .map((cell) => {
            const s = String(cell ?? "");
            return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
          })
          .join(","),
      )
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

  /* =============================== UI =============================== */

  return (
    <>
      <ErrorAlert message={error} />

      {/*
        Search and paging inside the table are client-side, over the rows that
        came back. That is the whole book until a property outgrows one page --
        past that, saying so is the only honest option, because a search box
        that silently covers 200 of 5,000 reservations reports "not found" for
        bookings that exist. Narrowing with the filters above re-queries the
        server, so they still reach the whole book.
      */}
      {listTruncated && (
        <div className="res-truncation-note" role="status">
          Showing {reservations.length} of {totalReservations} reservations. Search
          and sort below cover these {reservations.length}; use the filters above to
          narrow the whole book.
        </div>
      )}

      <TableTemplate
        title="Reservations"
        className="reservation-table"
        loading={loading}
        emptyMessage={
          filtersActive
            ? "No reservations match these filters."
            : "No reservations yet. Use Add New Reservation to create the first one."
        }
        variant="striped"
        pagination
        pageSize={10}
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
        filters={
          <TableFilters
            onClear={() => setFilters(EMPTY_FILTERS)}
            isActive={filtersActive}
          >
            <FilterSelect
              id="res-filter-status"
              label="Status"
              value={filters.reservation_status}
              onChange={(e) =>
                setFilters((f) => ({ ...f, reservation_status: e.target.value }))
              }
              options={statusOptions}
            />
            <FilterSelect
              id="res-filter-type"
              label="Type"
              value={filters.reservation_type}
              onChange={(e) =>
                setFilters((f) => ({ ...f, reservation_type: e.target.value }))
              }
              options={RESERVATION_TYPES}
            />
            <FilterSelect
              id="res-filter-payment"
              label="Payment"
              value={filters.payment_state}
              onChange={(e) =>
                setFilters((f) => ({ ...f, payment_state: e.target.value }))
              }
              options={PAYMENT_STATES}
            />
            <FilterDate
              id="res-filter-from"
              label="Staying from"
              value={filters.from_date}
              onChange={(e) => setFilters((f) => ({ ...f, from_date: e.target.value }))}
              max={filters.to_date || undefined}
            />
            <FilterDate
              id="res-filter-to"
              label="Staying to"
              value={filters.to_date}
              onChange={(e) => setFilters((f) => ({ ...f, to_date: e.target.value }))}
              min={filters.from_date || undefined}
            />
          </TableFilters>
        }
        columns={[
          { key: "room_reservation_id", title: "Reservation ID", align: "left", width: "150px" },
          {
            key: "first_name",
            title: "Guest",
            align: "left",
            width: "150px",
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
            width: "115px",
            type: "custom",
            exportValue: (row) => `${isoDay(row.arrival_date)} to ${isoDay(row.departure_date)}`,
            render: (row) => (
              <div className="res-stay-cell">
                <span className="res-stay-dates">{shortDate(row.arrival_date)}</span>
                <span className="res-stay-dates">{shortDate(row.departure_date)}</span>
                <span className="res-stay-nights">
                  {row.no_of_nights} night{row.no_of_nights === 1 ? "" : "s"}
                </span>
              </div>
            ),
          },
          {
            // Room numbers and type names, never the foreign keys they used to
            // be. The list payload carries both so no screen has to join by
            // hand against seven master endpoints.
            key: "room_nos",
            title: "Room",
            align: "left",
            width: "130px",
            type: "custom",
            exportValue: (row) => (row.room_nos || []).join(" / "),
            render: (row) => (
              <div className="res-room-cell">
                <span className="res-room-no">{joinList(row.room_nos)}</span>
                <span className="res-room-type">{joinList(row.room_type_names)}</span>
              </div>
            ),
          },
          {
            // Total, what is still owed, and the payment state in one column.
            // As three separate columns the table needed more width than a
            // laptop has, and Status -- the thing a receptionist scans for --
            // ended up off the right edge behind a horizontal scroll.
            key: "overall_amount",
            title: "Amount",
            align: "right",
            width: "130px",
            type: "custom",
            exportValue: (row) => row.overall_amount ?? "",
            render: (row) => {
              const due = num(row.balance_amount);
              return (
                <div className="res-amount-cell">
                  <span className="res-amount">{money(row.overall_amount)}</span>
                  <span
                    className={
                      due > 0 ? "res-amount-sub res-amount--due" : "res-amount-sub"
                    }
                  >
                    {due > 0 ? `${money(due)} due` : row.payment_state}
                  </span>
                </div>
              );
            },
          },
          { key: "reservation_status", title: "Status", align: "center", width: "120px", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => {
              const busy = rowBusy[row.id];
              // Deliberately short. Nine icons per row did not fit beside the
              // data columns, and a row of nine same-sized chips is unreadable
              // anyway. What stays here is the everyday work: look at it,
              // change it, arrive or depart the guest, take money. Cancel,
              // no-show and print are one deliberate step further in, in the
              // View modal, which is the right distance for two irreversible
              // actions and one that opens a print dialog.
              return (
                <RowActions
                  label={`reservation ${row.room_reservation_id}`}
                  onView={() => openView(row)}
                  onEdit={() => openEdit(row)}
                  onDelete={() => setDeleteRow(row)}
                  canEdit={!row.is_terminal}
                  canDelete={!row.is_terminal && num(row.paid_amount) === 0}
                >
                  {row.can_check_in && (
                    <IconButton
                      variant="action-view"
                      size="action"
                      icon={<Check size={16} />}
                      onClick={() => handleCheckIn(row)}
                      disabled={Boolean(busy)}
                      title="Check in"
                      ariaLabel={`Check in ${guestName(row)}`}
                    />
                  )}
                  {row.can_check_out && (
                    <IconButton
                      variant="action-view"
                      size="action"
                      icon={<LogOut size={16} />}
                      onClick={() => handleCheckOut(row)}
                      disabled={Boolean(busy)}
                      title="Check out"
                      ariaLabel={`Check out ${guestName(row)}`}
                    />
                  )}
                  {num(row.balance_amount) > 0 && !row.is_terminal && (
                    <IconButton
                      variant="action-edit"
                      size="action"
                      icon={<CreditCard size={16} />}
                      onClick={() => {
                        setPayError(null);
                        setPayModal({ row, amount: "", method: "" });
                      }}
                      title="Record payment"
                      ariaLabel={`Record payment for ${guestName(row)}`}
                    />
                  )}
                  {num(row.extra_amount) > 0 && (
                    <IconButton
                      variant="action-edit"
                      size="action"
                      icon={<HandCoins size={16} />}
                      onClick={() => {
                        setRefundError(null);
                        setRefundModal({ row, amount: "", method: "" });
                      }}
                      title="Refund"
                      ariaLabel={`Refund ${guestName(row)}`}
                    />
                  )}
                </RowActions>
              );
            },
          },
        ]}
        data={reservations}
      />

      {/* ============================== VIEW ============================== */}
      <Modal
        isOpen={Boolean(viewRow)}
        title={`Reservation ${viewRow?.room_reservation_id || ""}`}
        onClose={() => setViewRow(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          {
            label: "Print receipt",
            variant: "secondary",
            onClick: () => viewRow && handlePrint(viewRow),
          },
          ...(viewRow?.can_mark_no_show
            ? [{
                label: "Mark no-show",
                variant: "secondary",
                onClick: () => {
                  const row = viewRow;
                  setViewRow(null);
                  setNoShowRow(row);
                },
              }]
            : []),
          ...(viewRow?.can_cancel
            ? [{
                label: "Cancel reservation",
                variant: "error",
                onClick: () => {
                  const row = viewRow;
                  setViewRow(null);
                  openCancel(row);
                },
              }]
            : []),
          // Secondary, not primary. When "Cancel reservation" is present the
          // footer would otherwise hold two filled red buttons side by side —
          // the destructive one and the dismissal — differing only in shade.
          // Closing a read-only dialog is not the primary action anyway.
          { label: "Close", variant: "secondary", onClick: () => setViewRow(null) },
        ]}
      >
        <ViewSection title="Reservation">
          <DetailList columns={3}>
            <DetailItem label="Reservation ID" value={viewRow?.room_reservation_id} />
            <DetailItem label="Confirmation code" value={viewRow?.confirmation_code} />
            <DetailItem label="Status" value={viewRow?.reservation_status} />
            <DetailItem label="Type" value={viewRow?.reservation_type} />
            <DetailItem label="Booked on" value={isoDay(viewRow?.created_at)} />
            <DetailItem label="Last updated" value={isoDay(viewRow?.updated_at)} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Guest">
          <DetailList columns={3}>
            <DetailItem label="Name" value={guestName(viewRow)} />
            <DetailItem label="Salutation" value={viewRow?.salutation} />
            <DetailItem label="Phone" value={viewRow?.phone_number} />
            <DetailItem label="Email" value={viewRow?.email} span={2} />
            <DetailItem label="Identity type" value={viewRow?.identity_type} />
            <DetailItem label="Identity document" value={viewRow?.proof_document} span={3} />
          </DetailList>
        </ViewSection>

        {viewRow?.is_terminal &&
          String(viewRow?.reservation_status || "").toLowerCase().includes("cancel") && (
            <ViewSection title="Cancellation">
              <DetailList columns={3}>
                {/* A booking cancelled before the reason was recorded shows
                    "Not recorded" rather than an empty cell — the difference
                    between "nobody wrote it down" and "there was no reason"
                    matters when somebody is auditing a released room. */}
                <DetailItem
                  label="Reason"
                  value={viewRow?.cancellation_reason || "Not recorded"}
                  span={3}
                />
                <DetailItem label="Cancelled on" value={isoDay(viewRow?.cancelled_at)} />
                <DetailItem label="Cancelled by" value={viewRow?.cancelled_by} />
                <DetailItem label="Amount paid" value={money(viewRow?.paid_amount)} />
              </DetailList>
            </ViewSection>
          )}

        <ViewSection title="Stay">
          <DetailList columns={3}>
            <DetailItem label="Arrival" value={isoDay(viewRow?.arrival_date)} />
            <DetailItem label="Departure" value={isoDay(viewRow?.departure_date)} />
            <DetailItem label="Nights" value={viewRow?.no_of_nights} />
            <DetailItem label="Rooms" value={joinList(viewRow?.room_nos)} />
            <DetailItem label="Room types" value={joinList(viewRow?.room_type_names)} />
            <DetailItem
              label="Rate types"
              value={joinList((viewRow?.rate_type || []).map((r) => String(r).replace(/_/g, " ")))}
            />
            <DetailItem label="Adults" value={viewRow?.no_of_adults} />
            <DetailItem label="Children" value={viewRow?.no_of_children ?? 0} />
            <DetailItem label="Extra beds" value={viewRow?.extra_bed_count ?? 0} />
            <DetailItem label="Room complementary" value={viewRow?.room_complementary} />
            <DetailItem label="Common complementary" value={viewRow?.common_complementary} span={2} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Charges">
          <DetailList columns={3}>
            <DetailItem label="Room amount" value={money(viewRow?.room_amount)} />
            <DetailItem label="Extra charges" value={money(viewRow?.extra_charges)} />
            <DetailItem
              label="Extra bed cost"
              value={`${money(viewRow?.extra_bed_cost)} × ${viewRow?.extra_bed_count ?? 0}`}
            />
            <DetailItem
              label={`Tax${viewRow?.tax_name ? ` — ${viewRow.tax_name}` : ""}`}
              value={`${money(viewRow?.tax_amount)} (${viewRow?.tax_percentage ?? 0}%)`}
            />
            <DetailItem
              label={`Discount${viewRow?.discount_name ? ` — ${viewRow.discount_name}` : ""}`}
              value={`-${money(viewRow?.discount_amount)} (${viewRow?.discount_percentage ?? 0}%)`}
            />
            <DetailItem label="Total" value={money(viewRow?.overall_amount)} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Payment">
          <DetailList columns={3}>
            <DetailItem label="Method" value={viewRow?.payment_method} />
            <DetailItem label="Paid" value={money(viewRow?.paid_amount)} />
            <DetailItem label="Balance" value={money(viewRow?.balance_amount)} />
            <DetailItem label="Refundable" value={money(viewRow?.extra_amount)} />
            <DetailItem label="State" value={viewRow?.payment_state} span={2} />
          </DetailList>

          {paymentHistory.length > 0 && (
            <div className="res-history-scroll">
              <table className="payment-history-table">
                <thead>
                  <tr>
                    <th scope="col">Date</th>
                    <th scope="col">Kind</th>
                    <th scope="col">Method</th>
                    <th scope="col" className="num">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {paymentHistory.map((p) => (
                    <tr key={p.id}>
                      <td>{isoDay(p.paid_date)}</td>
                      <td>{p.kind}</td>
                      <td>{p.payment_method}</td>
                      <td className="num">{money(p.amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </ViewSection>
      </Modal>

      {/* ============================ ADD / EDIT ============================ */}
      <Modal
        isOpen={Boolean(editRow)}
        title={`Edit Reservation ${editRow?.room_reservation_id || ""}`}
        onClose={closeEdit}
        size="large"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeEdit, disabled: editSaving },
          {
            label: editSaving ? "Saving…" : "Save changes",
            variant: "primary",
            onClick: submitEdit,
            disabled: editSaving,
          },
        ]}
      >
        <form onSubmit={submitEdit} noValidate>
          <ErrorAlert message={editError} />
          <ErrorAlert message={editAvailability} />

          <ViewSection title="Guest">
            <div className="res-form-grid">
              <div className="form-group">
                <label className="form-label" htmlFor="edit-salutation">
                  Salutation
                </label>
                <select
                  id="edit-salutation"
                  className="select-control"
                  value={editForm.salutation || ""}
                  onChange={setField("salutation")}
                >
                  <option value="">—</option>
                  {SALUTATIONS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <Input
                label="First Name"
                required
                value={editForm.first_name || ""}
                onChange={setField("first_name")}
                maxLength={100}
              />
              <Input
                label="Last Name"
                value={editForm.last_name || ""}
                onChange={setField("last_name")}
                maxLength={100}
              />
              <Input
                label="Phone Number"
                required
                type="tel"
                value={editForm.phone_number || ""}
                onChange={setField("phone_number")}
                maxLength={20}
              />
              <Input
                label="Email"
                type="email"
                value={editForm.email || ""}
                onChange={setField("email")}
                maxLength={100}
              />
            </div>
          </ViewSection>

          <ViewSection title="Stay">
            <div className="res-form-grid">
              <Input
                label="Arrival Date"
                required
                type="date"
                value={editForm.arrival_date || ""}
                onChange={setField("arrival_date")}
              />
              <Input
                label="Departure Date"
                required
                type="date"
                value={editForm.departure_date || ""}
                onChange={setField("departure_date")}
                min={editForm.arrival_date || undefined}
              />
              <Input
                label="Nights"
                type="number"
                value={editNights}
                readOnly
                helperText="Calculated from the dates"
              />
              <Input
                label="Rooms"
                value={
                  (editForm.room_ids || [])
                    .map((id) => rooms.find((r) => r.id === Number(id))?.room_no || id)
                    .join(", ") || "—"
                }
                readOnly
                helperText="Room assignment is managed under Room View"
              />
              <Input
                label="Adults"
                required
                type="number"
                min="1"
                value={editForm.no_of_adults ?? 1}
                onChange={setField("no_of_adults")}
              />
              <Input
                label="Children"
                type="number"
                min="0"
                value={editForm.no_of_children ?? 0}
                onChange={setField("no_of_children")}
              />
            </div>
          </ViewSection>

          <ViewSection title="Reservation">
            <div className="res-form-grid">
              <div className="form-group">
                <label className="form-label form-label--required" htmlFor="edit-status">
                  Status
                </label>
                <select
                  id="edit-status"
                  className="select-control"
                  value={editForm.reservation_status || ""}
                  onChange={setField("reservation_status")}
                  required
                >
                  <option value="">— select —</option>
                  {statusOptions.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="edit-type">
                  Type
                </label>
                <select
                  id="edit-type"
                  className="select-control"
                  value={editForm.reservation_type || ""}
                  onChange={setField("reservation_type")}
                >
                  {RESERVATION_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label form-label--required" htmlFor="edit-payment-method">
                  Payment Method
                </label>
                <select
                  id="edit-payment-method"
                  className="select-control"
                  value={editForm.payment_method_id || ""}
                  onChange={setField("payment_method_id")}
                  required
                >
                  <option value="">— select —</option>
                  {paymentMethods.map((pm) => (
                    <option key={pm.id} value={pm.id}>{pm.payment_method}</option>
                  ))}
                </select>
              </div>
              <Input
                label="Room Complementary"
                value={editForm.room_complementary || ""}
                onChange={setField("room_complementary")}
                maxLength={100}
              />
              <Input
                label="Common Complementary"
                value={editForm.common_complementary || ""}
                onChange={setField("common_complementary")}
                maxLength={100}
              />
            </div>
          </ViewSection>

          {/* Charges: the inputs are the desk's decisions, everything below
              them is the server's answer. This section used to be twelve
              editable number boxes including the total itself. */}
          <ViewSection title="Charges">
            <ErrorAlert message={editQuoteError} />
            <div className="res-form-grid">
              <div className="form-group">
                <label className="form-label" htmlFor="edit-tax-type">
                  Tax Type
                </label>
                <select
                  id="edit-tax-type"
                  className="select-control"
                  value={editForm.tax_type_id || ""}
                  onChange={setField("tax_type_id")}
                >
                  <option value="">No tax</option>
                  {taxTypes.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.tax_name} ({t.tax_percentage}%)
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="edit-discount-type">
                  Discount Type
                </label>
                <select
                  id="edit-discount-type"
                  className="select-control"
                  value={editForm.discount_type_id || ""}
                  onChange={setField("discount_type_id")}
                >
                  <option value="">No discount</option>
                  {discountTypes.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.discount_name} ({d.discount_percentage}%)
                    </option>
                  ))}
                </select>
              </div>
              <Input
                label="Extra Charges"
                type="number"
                min="0"
                step="0.01"
                value={editForm.extra_charges ?? 0}
                onChange={setField("extra_charges")}
              />
              <Input
                label="Extra Bed Count"
                type="number"
                min="0"
                value={editForm.extra_bed_count ?? 0}
                onChange={setField("extra_bed_count")}
              />
              <Input
                label="Room Amount"
                type="number"
                min="0"
                step="0.01"
                placeholder={String(editQuote?.computed_room_amount ?? "")}
                value={editForm.room_amount}
                onChange={setField("room_amount")}
                helperText="Leave blank to use the rate card"
              />
            </div>

            <DetailList columns={3}>
              <DetailItem label="Room amount" value={money(editQuote?.room_amount)} />
              <DetailItem
                label="Tax"
                value={`${money(editQuote?.tax_amount)} (${editQuote?.tax_percentage ?? 0}%)`}
              />
              <DetailItem
                label="Discount"
                value={`-${money(editQuote?.discount_amount)} (${editQuote?.discount_percentage ?? 0}%)`}
              />
              <DetailItem label="New total" value={money(editQuote?.overall_amount)} />
              <DetailItem label="Already paid" value={money(editRow?.paid_amount)} />
              <DetailItem label="Balance after change" value={money(editQuote?.balance_amount)} />
            </DetailList>
          </ViewSection>
        </form>
      </Modal>

      {/* ============================ CONFIRMATIONS ============================ */}
      <ConfirmModal
        isOpen={Boolean(deleteRow)}
        onClose={() => setDeleteRow(null)}
        onConfirm={confirmDelete}
        title="Delete reservation"
        confirmText="Delete"
        size="small"
        destructive
      >
        Delete {deleteRow?.room_reservation_id} for {guestName(deleteRow)}? This removes
        it from the book entirely. To keep the record and free the room, cancel it instead.
      </ConfirmModal>

      {/* An early departure puts two bills on screen and makes the desk pick.
          Defaulting to either would be this screen choosing a refund policy:
          re-pricing silently gives away nights the property may be entitled
          to charge for, and keeping the charge silently bills for nights
          nobody slept. The pre-selected option is "no change", so a reduction
          only ever happens because somebody asked for one. */}
      <Modal
        isOpen={Boolean(checkoutModal)}
        title="Check out early"
        onClose={() => !checkoutSaving && setCheckoutModal(null)}
        size="medium"
        showFooter
        actions={[
          {
            label: "Cancel",
            variant: "secondary",
            onClick: () => setCheckoutModal(null),
            disabled: checkoutSaving,
          },
          {
            label: checkoutSaving ? "Checking out…" : "Check out",
            variant: "primary",
            onClick: submitCheckout,
            disabled: checkoutSaving,
          },
        ]}
      >
        <ErrorAlert message={checkoutError} />

        <p className="res-cancel-summary">
          <strong>{guestName(checkoutModal?.row)}</strong> is leaving{" "}
          <strong>{checkoutModal?.position?.nights_unused}</strong> night
          {checkoutModal?.position?.nights_unused === 1 ? "" : "s"} early —
          booked {checkoutModal?.position?.booked_nights} night
          {checkoutModal?.position?.booked_nights === 1 ? "" : "s"} to{" "}
          {isoDay(checkoutModal?.position?.booked_departure_date)}, staying{" "}
          {checkoutModal?.position?.actual_nights}.{" "}
          {joinList(checkoutModal?.row?.room_nos)} is released either way.
        </p>

        <div className="res-checkout-options" role="radiogroup" aria-label="Billing">
          {[
            {
              adjust: false,
              title: "Keep the original charge",
              amount: checkoutModal?.position?.current_total,
              note: `Billed for all ${checkoutModal?.position?.booked_nights} booked nights.`,
            },
            {
              adjust: true,
              title: "Re-price to nights stayed",
              amount: checkoutModal?.position?.repriced?.overall_amount,
              note:
                num(checkoutModal?.position?.repriced?.refund_due) > 0
                  ? `${money(checkoutModal?.position?.repriced?.refund_due)} becomes refundable.`
                  : `Billed for ${checkoutModal?.position?.actual_nights} night(s).`,
            },
          ].map((opt) => (
            <button
              key={String(opt.adjust)}
              type="button"
              role="radio"
              aria-checked={checkoutModal?.adjust === opt.adjust}
              className={
                checkoutModal?.adjust === opt.adjust
                  ? "res-checkout-option res-checkout-option--on"
                  : "res-checkout-option"
              }
              onClick={() =>
                setCheckoutModal((m) => ({ ...m, adjust: opt.adjust }))
              }
              disabled={checkoutSaving}
            >
              <span className="res-checkout-option-title">{opt.title}</span>
              <span className="res-checkout-option-amount">{money(opt.amount)}</span>
              <span className="res-checkout-option-note">{opt.note}</span>
            </button>
          ))}
        </div>

        <DetailList columns={3}>
          <DetailItem label="Already paid" value={money(checkoutModal?.position?.paid_amount)} />
          <DetailItem
            label="Balance after"
            value={money(
              checkoutModal?.adjust
                ? checkoutModal?.position?.repriced?.balance_amount
                : checkoutModal?.position?.balance_amount,
            )}
          />
          <DetailItem
            label="Refundable after"
            value={money(
              checkoutModal?.adjust ? checkoutModal?.position?.repriced?.refund_due : 0,
            )}
          />
        </DetailList>
      </Modal>

      {/* Cancelling asks WHY, because that is the only moment somebody knows.
          A reason recorded here is what answers "why was 304 free that night?"
          six weeks later; reconstructed afterwards it is a guess. The presets
          cover the common cases in one tap and stay editable, so the required
          field costs a click rather than a sentence. */}
      <Modal
        isOpen={Boolean(cancelRow)}
        title="Cancel reservation"
        onClose={() => !cancelSaving && setCancelRow(null)}
        size="medium"
        showFooter
        actions={[
          {
            label: "Keep it",
            variant: "secondary",
            onClick: () => setCancelRow(null),
            disabled: cancelSaving,
          },
          {
            label: cancelSaving ? "Cancelling…" : "Cancel reservation",
            variant: "error",
            onClick: confirmCancel,
            disabled: cancelSaving,
          },
        ]}
      >
        <ErrorAlert message={cancelError} />

        <p className="res-cancel-summary">
          Cancel <strong>{cancelRow?.room_reservation_id}</strong> for{" "}
          <strong>{guestName(cancelRow)}</strong>?{" "}
          {joinList(cancelRow?.room_nos)} becomes available for those dates
          immediately.
          {num(cancelRow?.paid_amount) > 0 && (
            <>
              {" "}
              <strong>{money(cancelRow?.paid_amount)}</strong> has already been
              paid and stays on the record.
            </>
          )}
        </p>

        <div className="res-reason-presets" role="group" aria-label="Common reasons">
          {CANCELLATION_PRESETS.map((preset) => (
            <button
              key={preset}
              type="button"
              className={
                cancelReason === preset
                  ? "res-reason-chip res-reason-chip--on"
                  : "res-reason-chip"
              }
              onClick={() => {
                setCancelReason(preset);
                setCancelError(null);
              }}
              disabled={cancelSaving}
            >
              {preset}
            </button>
          ))}
        </div>

        <Input
          label="Reason"
          required
          value={cancelReason}
          onChange={(e) => {
            setCancelReason(e.target.value);
            if (cancelError) setCancelError(null);
          }}
          maxLength={500}
          placeholder="Pick one above, or describe what happened"
          helperText="Recorded against the booking and shown on the reservation."
          disabled={cancelSaving}
        />
      </Modal>

      <ConfirmModal
        isOpen={Boolean(noShowRow)}
        onClose={() => setNoShowRow(null)}
        onConfirm={confirmNoShow}
        title="Mark as no-show"
        confirmText="Mark no-show"
        size="small"
        destructive
      >
        Mark {noShowRow?.room_reservation_id} for {guestName(noShowRow)} as a no-show?
        The room is released, and the booking stays on record as chargeable.
      </ConfirmModal>

      {/* ============================ PAYMENT ============================ */}
      <Modal
        isOpen={Boolean(payModal)}
        title="Record Payment"
        onClose={() => !paySaving && setPayModal(null)}
        size="small"
        showFooter
        actions={[
          {
            label: "Cancel",
            variant: "secondary",
            onClick: () => setPayModal(null),
            disabled: paySaving,
          },
          {
            label: paySaving ? "Saving…" : "Record payment",
            variant: "primary",
            onClick: submitPay,
            disabled: paySaving,
          },
        ]}
      >
        <ErrorAlert message={payError} />
        <Input
          label="Outstanding balance"
          value={money(payModal?.row?.balance_amount)}
          readOnly
        />
        <Input
          label="Paying now"
          type="number"
          min="0"
          step="0.01"
          value={payModal?.amount ?? ""}
          onChange={(e) => setPayModal((m) => ({ ...m, amount: e.target.value }))}
        />
        <div className="form-group">
          <label className="form-label" htmlFor="pay-method-select">
            Payment method
          </label>
          <select
            id="pay-method-select"
            className="select-control"
            value={payModal?.method ?? ""}
            onChange={(e) => setPayModal((m) => ({ ...m, method: e.target.value }))}
          >
            <option value="">— select —</option>
            {paymentMethods.map((pm) => (
              <option key={pm.id} value={pm.payment_method}>{pm.payment_method}</option>
            ))}
          </select>
        </div>
      </Modal>

      {/* ============================ REFUND ============================ */}
      <Modal
        isOpen={Boolean(refundModal)}
        title="Refund Overpayment"
        onClose={() => !refundSaving && setRefundModal(null)}
        size="small"
        showFooter
        actions={[
          {
            label: "Cancel",
            variant: "secondary",
            onClick: () => setRefundModal(null),
            disabled: refundSaving,
          },
          {
            label: refundSaving ? "Saving…" : "Refund",
            variant: "primary",
            onClick: submitRefund,
            disabled: refundSaving,
          },
        ]}
      >
        <ErrorAlert message={refundError} />
        <Input
          label="Refundable amount"
          value={money(refundModal?.row?.extra_amount)}
          readOnly
        />
        <Input
          label="Refund amount"
          type="number"
          min="0"
          step="0.01"
          value={refundModal?.amount ?? ""}
          onChange={(e) => setRefundModal((m) => ({ ...m, amount: e.target.value }))}
        />
        <div className="form-group">
          <label className="form-label" htmlFor="refund-method-select">
            Refund method
          </label>
          <select
            id="refund-method-select"
            className="select-control"
            value={refundModal?.method ?? ""}
            onChange={(e) => setRefundModal((m) => ({ ...m, method: e.target.value }))}
          >
            <option value="">— select —</option>
            {paymentMethods.map((pm) => (
              <option key={pm.id} value={pm.payment_method}>{pm.payment_method}</option>
            ))}
          </select>
        </div>
      </Modal>

      <Toast {...toast} />
    </>
  );
};

export default Reservation;
