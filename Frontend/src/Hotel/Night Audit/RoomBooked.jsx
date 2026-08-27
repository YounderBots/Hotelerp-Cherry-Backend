import React, { useMemo, useState } from "react";

import TableTemplate from "../../stories/TableTemplate";
import TableFilters, { FilterDate, FilterSelect } from "../../stories/TableFilters";
import Modal from "../../stories/Modal";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import RowActions from "../../stories/RowActions";
import APICall from "../../APICalls/APICalls";
import { useApiResource } from "../../hooks/useApiResource";
import {
    RESERVATION_STATUSES,
    formatCount,
    formatCurrency,
    formatDate,
    formatPrecise,
} from "./nightAuditShared";
import "./NightAudit.css";

/**
 * Room Booked Details -- which rooms were sold on one night, and what each
 * earned.
 *
 * WHAT THIS SCREEN USED TO DO
 * It fetched `/hotel/room_reservation` -- every reservation ever taken, with no
 * date filter at all -- and listed them under the heading "Room Booked". It was
 * not a night audit report; it was an unfiltered dump of the reservations
 * table, and the number of rows it showed had no relationship to any night.
 *
 * WHAT IT DOES NOW
 * Asks the server for the position on one business date and lists the
 * reservations that actually held a room that night. The nightly revenue column
 * is the same per-night accrual the audit records, so the rows on screen sum to
 * the night's room revenue exactly -- an operator can reconcile the total by
 * reading the table instead of taking it on trust.
 */

const readData = (res) => res?.data ?? null;

const RoomBooked = () => {
    // Empty means "the current business date", which the server resolves. The
    // screen deliberately does not default this to the browser's today: the
    // hotel's date and the calendar date are different things, and this module
    // exists because of that difference.
    const [date, setDate] = useState("");
    const [statusFilter, setStatusFilter] = useState("");
    const [viewRow, setViewRow] = useState(null);

    const { data, loading, error } = useApiResource(
        () =>
            APICall.getT(
                "/hotel/night_audit/preview",
                date ? { business_date: date } : {},
            ),
        {
            select: readData,
            initial: null,
            fallback: "Failed to load room bookings for this night.",
            deps: [date],
        },
    );

    const auditedDate = data?.audited_date ?? null;
    const occupancy = data?.occupancy ?? {};
    const revenue = data?.revenue ?? {};
    const rows = useMemo(() => {
        const list = Array.isArray(data?.lists?.occupying) ? data.lists.occupying : [];
        return statusFilter
            ? list.filter((r) => r.reservation_status === statusFilter)
            : list;
    }, [data, statusFilter]);

    // NOTE ON `type: "custom"`
    // TableTemplate's renderCell only calls `column.render` when the column is
    // typed "custom"; any other column falls through to the raw value and the
    // render function is silently ignored. Leaving it off is why these dates
    // first rendered as "2026-07-29" instead of "29 Jul 2026".
    //
    // Columns are kept to eight. Eleven of them squeezed "Night Revenue" down
    // to a clipped "NIGH" and pushed "Night Tax" off the edge entirely; the
    // fields dropped here (nights, tax, discount, extra charges) are all in
    // the View modal, which is the right home for detail.
    // Widths are set because the browser's automatic distribution gave every
    // column an equal share, which broke "Mr. Rohan Mehta" over three lines
    // and "29 Jul 2026" over two while leaving the numeric columns half empty.
    // They are hints, not hard limits -- the table keeps its own 600px
    // min-width and scrolls inside its wrapper on a narrow screen.
    const columns = useMemo(
        () => [
            { key: "reservation_id", title: "Reservation", align: "left", width: "130px" },
            { key: "guest_name", title: "Guest", align: "left", width: "150px" },
            { key: "room_no", title: "Room", align: "center", width: "70px" },
            {
                key: "arrival_date",
                title: "Arrival",
                align: "center",
                width: "100px",
                type: "custom",
                render: (row) => formatDate(row.arrival_date),
                exportValue: (row) => row.arrival_date ?? "",
            },
            // Departure is deliberately absent. With nowrap the nine-column
            // version measured 1159px inside a 1060px wrapper, which pushed
            // Actions off the right edge at 1440. Departure is the least
            // load-bearing column on a report about one night -- it is in the
            // View modal, and the dashboard has a Departures Due tab of its
            // own -- so it is the one that goes.
            {
                key: "reservation_status",
                title: "Status",
                align: "center",
                width: "110px",
                type: "badge",
            },
            {
                key: "night_room_revenue",
                title: "Night Revenue",
                align: "right",
                width: "120px",
                type: "custom",
                render: (row) => formatPrecise(row.night_room_revenue),
                exportValue: (row) => row.night_room_revenue ?? 0,
            },
            {
                key: "actions",
                title: "Actions",
                align: "center",
                width: "80px",
                type: "custom",
                excludeFromExport: true,
                render: (row) => (
                    <RowActions label="booking" onView={() => setViewRow(row)} />
                ),
            },
        ],
        [],
    );

    const filtersActive = Boolean(date || statusFilter);

    return (
        <div className="na-page">
            <ErrorAlert message={error} />

            <header className="na-report__header">
                <div className="na-report__context">
                    <h2 className="na-report__title">Room Booked Details</h2>
                    <span className="na-report__subtitle">
                        Rooms held on the night of{" "}
                        <b>{loading ? "…" : formatDate(auditedDate)}</b>
                        {data && !data.is_current_business_date
                            ? " · past night"
                            : " · current business date"}
                    </span>
                </div>
            </header>

            <section className="na-stats" aria-label="Night summary">
                <div className="na-stat na-stat--primary">
                    <span className="na-stat__label">Rooms sold</span>
                    <strong className="na-stat__value">
                        {formatCount(occupancy.rooms_occupied)}
                    </strong>
                    <span className="na-stat__hint">
                        {formatCount(occupancy.room_nights)} room nights
                    </span>
                </div>
                <div className="na-stat">
                    <span className="na-stat__label">Room revenue</span>
                    <strong className="na-stat__value">
                        {formatCurrency(revenue.room_revenue)}
                    </strong>
                    <span className="na-stat__hint">Accrued for this night</span>
                </div>
                <div className="na-stat">
                    <span className="na-stat__label">Tax</span>
                    <strong className="na-stat__value">
                        {formatCurrency(revenue.tax_amount)}
                    </strong>
                </div>
                <div className="na-stat">
                    <span className="na-stat__label">Gross</span>
                    <strong className="na-stat__value">
                        {formatCurrency(revenue.gross_revenue)}
                    </strong>
                </div>
            </section>

            <TableTemplate
                title={`Rooms Held · ${formatDate(auditedDate)}`}
                loading={loading}
                emptyMessage={
                    statusFilter
                        ? `No ${statusFilter} reservations held a room on this night.`
                        : "No rooms were held on this night."
                }
                columns={columns}
                data={rows}
                variant="striped"
                pagination
                pageSize={10}
                searchable
                exportable
                filters={
                    <TableFilters
                        isActive={filtersActive}
                        onClear={() => {
                            setDate("");
                            setStatusFilter("");
                        }}
                    >
                        <FilterDate
                            id="rb-date"
                            label="Business date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                        />
                        <FilterSelect
                            id="rb-status"
                            label="Status"
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            options={RESERVATION_STATUSES}
                        />
                    </TableFilters>
                }
            />

            <Modal
                isOpen={!!viewRow}
                title="Booking Details"
                onClose={() => setViewRow(null)}
                size="large"
                viewMode
                showFooter
                actions={[
                    { label: "Close", variant: "secondary", onClick: () => setViewRow(null) },
                ]}
            >
                {viewRow && (
                    <>
                        <ViewSection title="Guest & Stay">
                            <DetailList columns={3}>
                                <DetailItem label="Reservation" value={viewRow.reservation_id} />
                                <DetailItem label="Guest" value={viewRow.guest_name} />
                                <DetailItem label="Phone" value={viewRow.phone_number} />
                                <DetailItem label="Room" value={viewRow.room_no} />
                                <DetailItem label="Arrival" value={formatDate(viewRow.arrival_date)} />
                                <DetailItem
                                    label="Departure"
                                    value={formatDate(viewRow.departure_date)}
                                />
                                <DetailItem label="Nights" value={viewRow.no_of_nights} />
                                <DetailItem label="Status" value={viewRow.reservation_status} />
                            </DetailList>
                        </ViewSection>

                        <ViewSection title={`Accrued for ${formatDate(auditedDate)}`}>
                            <DetailList columns={4}>
                                <DetailItem
                                    label="Room revenue"
                                    value={formatPrecise(viewRow.night_room_revenue)}
                                />
                                <DetailItem label="Tax" value={formatPrecise(viewRow.night_tax)} />
                                <DetailItem
                                    label="Discount"
                                    value={formatPrecise(viewRow.night_discount)}
                                />
                                <DetailItem
                                    label="Extra charges"
                                    value={formatPrecise(viewRow.night_extra_charges)}
                                />
                            </DetailList>
                        </ViewSection>

                        <ViewSection title="Whole stay">
                            <DetailList columns={3}>
                                <DetailItem
                                    label="Total billed"
                                    value={formatPrecise(viewRow.overall_amount)}
                                />
                                <DetailItem label="Paid" value={formatPrecise(viewRow.paid_amount)} />
                                <DetailItem
                                    label="Balance"
                                    value={formatPrecise(viewRow.balance_amount)}
                                />
                            </DetailList>
                        </ViewSection>
                    </>
                )}
            </Modal>
        </div>
    );
};

export default RoomBooked;
