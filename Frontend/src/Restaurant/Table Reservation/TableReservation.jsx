import React, { useState } from "react";
import { Check, CheckCheck, XCircle } from "lucide-react";
import TableTemplate from "../../stories/TableTemplate";
import Modal, { ConfirmModal } from "../../stories/Modal";
import RowActions from "../../stories/RowActions";
import IconButton from "../../stories/IconButton";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import Textarea from "../../stories/Form/Textarea";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { formatDate, todayIso } from "../../functions/formatters";
import { useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";

/**
 * Table bookings for the restaurant floor.
 *
 * There is no Edit: the update endpoint accepts only a status transition
 * (`ReservationUpdate` carries reservation_status and the two timestamps), and
 * moving the booking's status is what the row actions do. A booking made for
 * the wrong table or time is cancelled and re-made, which is also what keeps
 * the table's own status honest — update_reservation frees or holds the table
 * as the status moves.
 */
const RESERVATION_SOURCES = ["Walk-In", "Phone", "Online", "Hotel Guest"];

const initialForm = {
  table_id: "",
  guest_name: "",
  guest_mobile: "",
  guest_email: "",
  reservation_date: "",
  start_time: "",
  end_time: "",
  no_of_guests: "",
  reservation_type: "Walk-In",
  occasion: "",
  special_requests: "",
};

// The two status moves that lose the booking, so both are confirmed. Checking
// a guest in and completing a seated booking are not: they are the ordinary
// path, and both are reversible by the next transition.
const CONFIRMED_MOVES = {
  "No-Show": {
    title: "Mark as No-Show",
    confirm: "Mark no-show",
    body: (row) =>
      `Mark ${row?.guest_name || "this booking"} as a no-show? The table is released for other guests.`,
  },
  Cancelled: {
    title: "Cancel Reservation",
    confirm: "Cancel booking",
    body: (row) =>
      `Cancel ${row?.guest_name || "this booking"}? The table is released for other guests.`,
  },
};

const TableReservation = () => {
  const perms = usePagePermissions("/table_reservation");

  const {
    data: [data, tables],
    loading,
    error,
    reload: load,
  } = useApiResources([
    {
      fetch: () => APICall.getT("/restaurant/table_reservation"),
      select: readList,
      fallback: "Failed to load reservations.",
    },
    { fetch: () => APICall.getT("/restaurant/table"), select: readList },
  ]);

  const { toast, showToast } = useToast();

  const [showModal, setShowModal] = useState(false);
  const [viewData, setViewData] = useState(null);
  const [pendingMove, setPendingMove] = useState(null); // { row, status }
  const [saving, setSaving] = useState(false);
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState(null);
  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setFormData({ ...initialForm, reservation_date: todayIso() });
    setFormError(null);
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setFormData(initialForm);
    setFormError(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = async () => {
    if (saving) return;
    if (
      !formData.table_id ||
      !formData.guest_name.trim() ||
      !formData.guest_mobile.trim() ||
      !formData.reservation_date ||
      !formData.start_time ||
      !formData.no_of_guests
    ) {
      setFormError("Table, guest name, mobile, date, start time and guest count are required.");
      return;
    }
    if (Number(formData.no_of_guests) < 1) {
      setFormError("A booking needs at least one guest.");
      return;
    }
    // An end before the start would be stored as-is and then read as a
    // zero-or-negative sitting on the floor plan.
    if (formData.end_time && formData.end_time <= formData.start_time) {
      setFormError("End time must be after the start time.");
      return;
    }

    setFormError(null);
    setSaving(true);
    try {
      await APICall.postT("/restaurant/table_reservation", {
        table_id: Number(formData.table_id),
        guest_name: formData.guest_name.trim(),
        guest_mobile: formData.guest_mobile.trim(),
        guest_email: formData.guest_email.trim() || null,
        reservation_date: formData.reservation_date,
        start_time: formData.start_time,
        end_time: formData.end_time || null,
        no_of_guests: Number(formData.no_of_guests),
        reservation_type: formData.reservation_type,
        occasion: formData.occasion.trim() || null,
        special_requests: formData.special_requests.trim() || null,
      });
      showToast("Reservation added successfully", "success");
      setShowModal(false);
      setFormData(initialForm);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to create reservation."));
    } finally {
      setSaving(false);
    }
  };

  const applyStatus = async (row, reservation_status) => {
    if (busy) return;
    setBusy(true);
    try {
      await APICall.putT(`/restaurant/table_reservation/${row.id}`, { reservation_status });
      showToast(`Reservation marked ${reservation_status.toLowerCase()}`, "update");
      load();
    } catch (err) {
      showToast(errMsg(err, "Failed to update reservation."), "error");
    } finally {
      setBusy(false);
    }
  };

  // A move that loses the booking asks first; the rest apply straight away.
  const moveStatus = (row, status) => {
    if (CONFIRMED_MOVES[status]) {
      setPendingMove({ row, status });
      return;
    }
    applyStatus(row, status);
  };

  const confirmMove = async () => {
    const move = pendingMove;
    setPendingMove(null);
    setViewData(null);
    await applyStatus(move.row, move.status);
  };

  /* ================= UI ================= */

  const tableOptions = tables.map((t) => ({
    value: t.id,
    label: `${t.table_name} (${t.table_code})`,
  }));

  const confirmCopy = pendingMove ? CONFIRMED_MOVES[pendingMove.status] : null;

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Table Reservations"
        loading={loading}
        emptyMessage="No table reservations yet. Add the first one to get started."
        hasActionButton={perms.add}
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Reservation",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "reservation_code", title: "Code", align: "left" },
          { key: "guest_name", title: "Guest Name", align: "left" },
          { key: "guest_mobile", title: "Contact", align: "left" },
          {
            key: "reservation_date",
            title: "Date",
            align: "left",
            type: "custom",
            render: (row) => formatDate(row.reservation_date),
            exportValue: (row) => formatDate(row.reservation_date),
          },
          { key: "start_time", title: "Start", align: "left" },
          // table_label is resolved by the API. This was joined in the browser
          // and fell back to the raw table id when the list had not loaded.
          { key: "table_label", title: "Table", align: "left" },
          { key: "no_of_guests", title: "Guests", align: "right" },
          { key: "reservation_type", title: "Source", align: "left" },
          { key: "reservation_status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            excludeFromExport: true,
            render: (row) => (
              <RowActions
                label={`reservation for ${row.guest_name || ""}`.trim()}
                onView={() => setViewData(row)}
              >
                {row.reservation_status === "Reserved" && perms.edit && (
                  <>
                    <IconButton
                      variant="action-edit"
                      size="action"
                      icon={<Check size={16} />}
                      onClick={() => moveStatus(row, "Checked-In")}
                      disabled={busy}
                      title="Check in"
                      ariaLabel={`Check in ${row.guest_name || "guest"}`}
                    />
                    <IconButton
                      variant="action-delete"
                      size="action"
                      icon={<XCircle size={16} />}
                      onClick={() => moveStatus(row, "No-Show")}
                      disabled={busy}
                      title="Mark as no-show"
                      ariaLabel={`Mark ${row.guest_name || "guest"} as a no-show`}
                    />
                  </>
                )}
                {row.reservation_status === "Checked-In" && perms.edit && (
                  <IconButton
                    variant="action-edit"
                    size="action"
                    icon={<CheckCheck size={16} />}
                    onClick={() => moveStatus(row, "Completed")}
                    disabled={busy}
                    title="Mark completed"
                    ariaLabel={`Mark ${row.guest_name || "booking"} completed`}
                  />
                )}
              </RowActions>
            ),
          },
        ]}
        data={data}
      />

      {/* ================= VIEW ================= */}
      <Modal
        isOpen={!!viewData}
        title="Reservation Details"
        onClose={() => setViewData(null)}
        size="large"
        viewMode
        showFooter
        actions={[
          ...(viewData?.reservation_status === "Reserved" && perms.delete
            ? [
                {
                  label: "Cancel Reservation",
                  variant: "error",
                  onClick: () => moveStatus(viewData, "Cancelled"),
                },
              ]
            : []),
          { label: "Close", variant: "secondary", onClick: () => setViewData(null) },
        ]}
      >
        {/* Was `Object.entries(viewData).map(...)` into disabled <Input>s,
            which printed every column on the row — id, company_id, branch_id,
            status, created_by, created_at — as a greyed-out form field. */}
        <ViewSection title="Booking">
          <DetailList columns={3}>
            <DetailItem label="Code" value={viewData?.reservation_code} />
            <DetailItem label="Table" value={viewData?.table_label} />
            <DetailItem label="Status" value={viewData?.reservation_status} />
            <DetailItem label="Date" value={formatDate(viewData?.reservation_date)} />
            <DetailItem label="Start Time" value={viewData?.start_time} />
            <DetailItem label="End Time" value={viewData?.end_time} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Guest">
          <DetailList columns={3}>
            <DetailItem label="Name" value={viewData?.guest_name} />
            <DetailItem label="Contact" value={viewData?.guest_mobile} />
            <DetailItem label="Email" value={viewData?.guest_email} />
            <DetailItem label="Guests" value={viewData?.no_of_guests} />
            <DetailItem label="Source" value={viewData?.reservation_type} />
            <DetailItem label="Occasion" value={viewData?.occasion} />
          </DetailList>
        </ViewSection>

        <ViewSection title="Service">
          <DetailList columns={2}>
            <DetailItem label="Checked In" value={viewData?.check_in_time} />
            <DetailItem label="Checked Out" value={viewData?.check_out_time} />
            <DetailItem label="Order" value={viewData?.order_number} />
            <DetailItem label="Special Requests" value={viewData?.special_requests} />
          </DetailList>
        </ViewSection>
      </Modal>

      {/* ================= ADD ================= */}
      <Modal
        isOpen={showModal}
        title="Add Reservation"
        onClose={closeModal}
        size="large"
        bodyLayout="grid"
        showFooter
        actions={[
          { label: "Cancel", variant: "secondary", onClick: closeModal, disabled: saving },
          {
            label: saving ? "Saving…" : "Submit",
            variant: "primary",
            onClick: handleSave,
            disabled: saving,
          },
        ]}
      >
        <ErrorAlert message={formError} className="field-full" />

        <Select
          label="Table"
          required
          name="table_id"
          value={formData.table_id}
          onChange={handleChange}
          placeholder="— select —"
          options={tableOptions}
        />
        <Input
          label="Guest Name"
          required
          name="guest_name"
          value={formData.guest_name}
          onChange={handleChange}
        />
        <Input
          label="Contact Number"
          required
          type="tel"
          name="guest_mobile"
          value={formData.guest_mobile}
          onChange={handleChange}
        />
        <Input
          label="Email"
          type="email"
          name="guest_email"
          value={formData.guest_email}
          onChange={handleChange}
        />
        <Input
          label="Reservation Date"
          required
          type="date"
          name="reservation_date"
          min={todayIso()}
          value={formData.reservation_date}
          onChange={handleChange}
        />
        <Input
          label="Start Time"
          required
          type="time"
          name="start_time"
          value={formData.start_time}
          onChange={handleChange}
        />
        <Input
          label="End Time"
          type="time"
          name="end_time"
          value={formData.end_time}
          onChange={handleChange}
        />
        <Input
          label="No. of Guests"
          required
          type="number"
          min="1"
          name="no_of_guests"
          value={formData.no_of_guests}
          onChange={handleChange}
        />
        <Select
          label="Source"
          name="reservation_type"
          value={formData.reservation_type}
          onChange={handleChange}
          options={RESERVATION_SOURCES}
        />
        <Input
          label="Occasion"
          name="occasion"
          placeholder="Birthday, Anniversary…"
          value={formData.occasion}
          onChange={handleChange}
        />
        <div className="field-full">
          <Textarea
            label="Special Requests"
            name="special_requests"
            rows={3}
            placeholder="Anything the floor should set up before the guests arrive."
            value={formData.special_requests}
            onChange={handleChange}
          />
        </div>
      </Modal>

      {/* ================= CONFIRM A LOSING MOVE ================= */}
      <ConfirmModal
        isOpen={!!pendingMove}
        onClose={() => setPendingMove(null)}
        onConfirm={confirmMove}
        title={confirmCopy?.title || "Confirm"}
        confirmText={confirmCopy?.confirm || "Confirm"}
        cancelText="Keep booking"
        size="small"
        destructive
      >
        {confirmCopy ? confirmCopy.body(pendingMove.row) : ""}
      </ConfirmModal>

      <Toast {...toast} />
    </>
  );
};

export default TableReservation;
