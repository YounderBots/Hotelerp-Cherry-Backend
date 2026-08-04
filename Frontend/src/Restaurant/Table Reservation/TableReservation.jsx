import React, { useCallback, useEffect, useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import Modal from "../../stories/Modal";
import IconButton from "../../stories/IconButton";
import Input from "../../stories/Form/Input";
import Select from "../../stories/Form/Select";
import ErrorAlert from "../../stories/ErrorAlert";
import { Eye, Check, XCircle, CheckCheck } from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";

const errMsg = (err, fallback) => (err instanceof ApiError && err.message ? err.message : fallback);
const readList = (res) => (Array.isArray(res?.data) ? res.data : []);

const TableReservation = () => {
  const [data, setData] = useState([]);
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewData, setViewData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);

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
  const [formData, setFormData] = useState(initialForm);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([APICall.getT("/restaurant/table_reservation"), APICall.getT("/restaurant/table")]).then(([rRes, tRes]) => {
      setData(rRes.status === "fulfilled" ? readList(rRes.value) : []);
      setTables(tRes.status === "fulfilled" ? readList(tRes.value) : []);
      if (rRes.status === "rejected") setError(errMsg(rRes.reason, "Failed to load reservations."));
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const tableLabel = (tableId) => {
    const t = tables.find((x) => x.id === tableId);
    return t ? `${t.table_name} (${t.table_code})` : tableId;
  };

  const openAddModal = () => {
    setFormData(initialForm);
    setFormError(null);
    setShowModal(true);
  };

  const openViewModal = (row) => {
    setViewData({ ...row, table: tableLabel(row.table_id) });
    setShowViewModal(true);
  };
  const closeViewModal = () => {
    setViewData(null);
    setShowViewModal(false);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = async () => {
    if (!formData.table_id || !formData.guest_name.trim() || !formData.guest_mobile.trim() || !formData.reservation_date || !formData.start_time || !formData.no_of_guests) {
      setFormError("Table, guest name, mobile, date, start time and guest count are required.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      await APICall.postT("/restaurant/table_reservation", {
        table_id: Number(formData.table_id),
        guest_name: formData.guest_name.trim(),
        guest_mobile: formData.guest_mobile.trim(),
        guest_email: formData.guest_email || null,
        reservation_date: formData.reservation_date,
        start_time: formData.start_time,
        end_time: formData.end_time || null,
        no_of_guests: Number(formData.no_of_guests),
        reservation_type: formData.reservation_type,
        occasion: formData.occasion || null,
        special_requests: formData.special_requests || null,
      });
      setShowModal(false);
      load();
    } catch (err) {
      setFormError(errMsg(err, "Failed to create reservation."));
    } finally {
      setSaving(false);
    }
  };

  const updateStatus = async (row, reservation_status) => {
    try {
      await APICall.putT(`/restaurant/table_reservation/${row.id}`, { reservation_status });
      load();
    } catch (err) {
      setError(errMsg(err, "Failed to update reservation."));
    }
  };

  return (
    <>
      <ErrorAlert message={error} />

      <TableTemplate
        title="Table Reservation"
        hasActionButton
        searchable
        pagination
        exportable
        loading={loading}
        actionButton={{
          label: "Add Reservation",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "reservation_code", title: "Reservation Code", align: "center" },
          { key: "guest_name", title: "Guest Name", align: "center" },
          { key: "guest_mobile", title: "Contact", align: "center" },
          { key: "reservation_date", title: "Date", align: "center" },
          { key: "start_time", title: "Start", align: "center" },
          { key: "table_id", title: "Table", align: "center", type: "custom", render: (row) => tableLabel(row.table_id) },
          { key: "no_of_guests", title: "Guests", align: "center" },
          { key: "reservation_type", title: "Source", align: "center" },
          { key: "reservation_status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <IconButton variant="ghost" size="small" icon={<Eye size={16} />} ariaLabel="View" onClick={() => openViewModal(row)} />
                {row.reservation_status === "Reserved" && (
                  <>
                    <IconButton variant="subtle" size="small" icon={<Check size={16} />} ariaLabel="Check in" onClick={() => updateStatus(row, "Checked-In")} />
                    <IconButton variant="danger-ghost" size="small" icon={<XCircle size={16} />} ariaLabel="Mark as no-show" onClick={() => updateStatus(row, "No-Show")} />
                  </>
                )}
                {row.reservation_status === "Checked-In" && (
                  <IconButton variant="subtle" size="small" icon={<CheckCheck size={16} />} ariaLabel="Mark completed" onClick={() => updateStatus(row, "Completed")} />
                )}
              </div>
            ),
          },
        ]}
        data={data}
      />

      {showViewModal && viewData && (
        <Modal
          isOpen
          title="View Reservation"
          onClose={closeViewModal}
          size="large"
          bodyLayout="grid"
          viewMode
          showFooter
          actions={[
            ...(viewData.reservation_status === "Reserved"
              ? [{ label: "Cancel Reservation", variant: "secondary", onClick: () => { updateStatus(viewData, "Cancelled"); closeViewModal(); } }]
              : []),
            { label: "Close", variant: "primary", onClick: closeViewModal },
          ]}
        >
          {Object.entries(viewData).map(([key, value]) => (
            <Input key={key} label={key.replace(/_/g, " ")} value={value ?? "-"} disabled />
          ))}
        </Modal>
      )}

      {showModal && (
        <Modal
          isOpen
          title="Add Reservation"
          onClose={closeModal}
          size="large"
          bodyLayout="grid"
          showFooter
          actions={[
            { label: "Close", variant: "secondary", onClick: closeModal, disabled: saving },
            { label: saving ? "Saving…" : "Submit", variant: "primary", onClick: handleSave, disabled: saving },
          ]}
        >
          <ErrorAlert message={formError} />

          <Select
            label="Table"
            required
            name="table_id"
            value={formData.table_id}
            onChange={handleChange}
            placeholder="— select —"
            options={tables.map((t) => ({ value: t.id, label: `${t.table_name} (${t.table_code})` }))}
          />
          <Input label="Guest Name" required name="guest_name" value={formData.guest_name} onChange={handleChange} />
          <Input label="Contact Number" required name="guest_mobile" value={formData.guest_mobile} onChange={handleChange} />
          <Input label="Email" type="email" name="guest_email" value={formData.guest_email} onChange={handleChange} />
          <Input label="Reservation Date" required type="date" name="reservation_date" value={formData.reservation_date} onChange={handleChange} />
          <Input label="Start Time" required type="time" name="start_time" value={formData.start_time} onChange={handleChange} />
          <Input label="End Time" type="time" name="end_time" value={formData.end_time} onChange={handleChange} />
          <Input label="No. of Guests" required type="number" name="no_of_guests" value={formData.no_of_guests} onChange={handleChange} />
          <Input label="Occasion" name="occasion" value={formData.occasion} onChange={handleChange} placeholder="Birthday, Anniversary…" />
          <Select
            label="Source"
            name="reservation_type"
            value={formData.reservation_type}
            onChange={handleChange}
            options={[
              { value: "Walk-In", label: "Walk-In" },
              { value: "Phone", label: "Phone" },
              { value: "Online", label: "Online" },
              { value: "Hotel Guest", label: "Hotel Guest" },
            ]}
          />
          <Input label="Special Requests" name="special_requests" value={formData.special_requests} onChange={handleChange} />
        </Modal>
      )}
    </>
  );
};

export default TableReservation;
