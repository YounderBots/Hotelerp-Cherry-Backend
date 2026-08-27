import React, { useMemo, useState } from "react";

import TableTemplate from "../../stories/TableTemplate";
import TableFilters, { FilterDate } from "../../stories/TableFilters";
import Modal from "../../stories/Modal";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import RowActions from "../../stories/RowActions";
import Tabs, { Tab } from "../../stories/Tabs";
import APICall from "../../APICalls/APICalls";
import { useApiResource } from "../../hooks/useApiResource";
import {
    formatCount,
    formatCurrency,
    formatDate,
    formatPrecise,
} from "./nightAuditShared";
import "./NightAudit.css";

/**
 * Settlement Summary -- the money position for one night.
 *
 * WHAT CHANGED, AND WHY IT MATTERS
 * The previous version fetched every reservation in the database and then added
 * the columns up IN THE BROWSER to produce its totals. Two problems, both real:
 *
 *   * The totals covered every reservation ever taken, not a night. The
 *     "Total paid" figure was the hotel's lifetime takings.
 *   * A total computed in the browser is a number the backend never agreed to.
 *     When the same figure appeared on the dashboard and here, nothing made
 *     them match, and for a settlement report that is the whole job.
 *
 * Now every figure comes from the server's position for the chosen business
 * date -- the same calculation the night audit snapshots. The screen formats
 * numbers; it does not compute them.
 *
 * "Collected" and "Outstanding" answer different questions on purpose:
 * collected is cash that moved ON this date, outstanding is what arrived guests
 * still owe AS OF this date. They are not two views of one number and should
 * not be expected to reconcile against each other.
 */

const readData = (res) => res?.data ?? null;

const SettlementSummary = () => {
    const [date, setDate] = useState("");
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
            fallback: "Failed to load settlement data for this night.",
            deps: [date],
        },
    );

    const auditedDate = data?.audited_date ?? null;
    const settlement = data?.settlement ?? {};
    const revenue = data?.revenue ?? {};
    const breakdown = Array.isArray(settlement.payment_breakdown)
        ? settlement.payment_breakdown
        : [];
    const unsettled = Array.isArray(data?.lists?.unsettled_folios)
        ? data.lists.unsettled_folios
        : [];
    const occupying = Array.isArray(data?.lists?.occupying) ? data.lists.occupying : [];

    // `type: "custom"` is required for `render` to be called at all -- see the
    // note in RoomBooked.jsx. Arrival/departure are left to the View modal so
    // the three money columns, which are the point of this report, get the
    // width they need.
    const folioColumns = useMemo(
        () => [
            { key: "reservation_id", title: "Reservation", align: "left", width: "130px" },
            { key: "guest_name", title: "Guest", align: "left", width: "150px" },
            { key: "room_no", title: "Room", align: "center", width: "70px" },
            { key: "reservation_status", title: "Status", align: "center", width: "110px", type: "badge" },
            {
                // "Billed", not "Total Billed": headers are uppercased with
                // 0.06em letter-spacing, so the label -- not the value -- sets
                // this column's width, and the longer wording was the last
                // 42px keeping this table from fitting 1280.
                key: "overall_amount",
                title: "Billed",
                align: "right",
                width: "115px",
                type: "custom",
                render: (row) => formatPrecise(row.overall_amount),
                exportValue: (row) => row.overall_amount ?? 0,
            },
            {
                key: "paid_amount",
                title: "Paid",
                align: "right",
                width: "105px",
                type: "custom",
                render: (row) => formatPrecise(row.paid_amount),
                exportValue: (row) => row.paid_amount ?? 0,
            },
            {
                key: "balance_amount",
                title: "Balance",
                align: "right",
                width: "105px",
                type: "custom",
                render: (row) => (
                    <span className={row.balance_amount > 0 ? "na-amount--due" : ""}>
                        {formatPrecise(row.balance_amount)}
                    </span>
                ),
                exportValue: (row) => row.balance_amount ?? 0,
            },
            {
                key: "actions",
                title: "Actions",
                align: "center",
                width: "80px",
                type: "custom",
                excludeFromExport: true,
                render: (row) => (
                    <RowActions label="settlement" onView={() => setViewRow(row)} />
                ),
            },
        ],
        [],
    );

    const paymentColumns = useMemo(
        () => [
            { key: "payment_method", title: "Payment Method", align: "left", width: "200px" },
            {
                key: "amount",
                title: "Amount Collected",
                align: "right",
                width: "150px",
                type: "custom",
                render: (row) => formatPrecise(row.amount),
                exportValue: (row) => row.amount ?? 0,
            },
        ],
        [],
    );

    return (
        <div className="na-page">
            <ErrorAlert message={error} />

            <header className="na-report__header">
                <div className="na-report__context">
                    <h2 className="na-report__title">Settlement Summary</h2>
                    <span className="na-report__subtitle">
                        Money position for <b>{loading ? "…" : formatDate(auditedDate)}</b>
                        {data && !data.is_current_business_date
                            ? " · past night"
                            : " · current business date"}
                    </span>
                </div>
            </header>

            <section className="na-stats" aria-label="Settlement summary">
                <div className="na-stat na-stat--success">
                    <span className="na-stat__label">Collected</span>
                    <strong className="na-stat__value">
                        {formatCurrency(settlement.payments_collected)}
                    </strong>
                    <span className="na-stat__hint">Payments dated this day</span>
                </div>
                <div
                    className={`na-stat ${settlement.outstanding_balance > 0 ? "na-stat--warning" : ""
                        }`}
                >
                    <span className="na-stat__label">Outstanding</span>
                    <strong className="na-stat__value">
                        {formatCurrency(settlement.outstanding_balance)}
                    </strong>
                    <span className="na-stat__hint">
                        {formatCount(unsettled.length)} unsettled folio
                        {unsettled.length === 1 ? "" : "s"}
                    </span>
                </div>
                <div className="na-stat na-stat--primary">
                    <span className="na-stat__label">Gross revenue</span>
                    <strong className="na-stat__value">
                        {formatCurrency(revenue.gross_revenue)}
                    </strong>
                    <span className="na-stat__hint">Accrued for this night</span>
                </div>
                <div className="na-stat">
                    <span className="na-stat__label">Room revenue</span>
                    <strong className="na-stat__value">
                        {formatCurrency(revenue.room_revenue)}
                    </strong>
                </div>
                <div className="na-stat">
                    <span className="na-stat__label">Tax</span>
                    <strong className="na-stat__value">
                        {formatCurrency(revenue.tax_amount)}
                    </strong>
                </div>
                <div className="na-stat">
                    <span className="na-stat__label">Discount</span>
                    <strong className="na-stat__value">
                        {formatCurrency(revenue.discount_amount)}
                    </strong>
                </div>
            </section>

            <TableFilters
                isActive={Boolean(date)}
                onClear={() => setDate("")}
            >
                <FilterDate
                    id="ss-date"
                    label="Business date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                />
            </TableFilters>

            <Tabs variant="default">
                <Tab label={`Unsettled (${unsettled.length})`}>
                    <p className="na-list__description">
                        Guests who have arrived on or before this date and still owe money.
                        The night audit records these balances; it does not collect them.
                    </p>
                    <TableTemplate
                        title={`Unsettled Folios · ${formatDate(auditedDate)}`}
                        loading={loading}
                        emptyMessage="Every arrived reservation is settled for this night."
                        columns={folioColumns}
                        data={unsettled}
                        variant="striped"
                        pagination
                        pageSize={10}
                        searchable
                        exportable
                    />
                </Tab>

                <Tab label={`Payments (${breakdown.length})`}>
                    <p className="na-list__description">
                        Cash that moved on this date, grouped by the method it was taken on.
                        Read from the payment history, so a guest who paid in two instalments
                        on different days appears against each day separately.
                    </p>
                    <TableTemplate
                        title={`Payments Collected · ${formatDate(auditedDate)}`}
                        loading={loading}
                        emptyMessage="No payments were recorded on this date."
                        columns={paymentColumns}
                        data={breakdown}
                        variant="striped"
                        pagination={false}
                        searchable={false}
                        exportable
                    />
                </Tab>

                <Tab label={`All Folios (${occupying.length})`}>
                    <p className="na-list__description">
                        Every reservation holding a room on this night, settled or not.
                    </p>
                    <TableTemplate
                        title={`Folios · ${formatDate(auditedDate)}`}
                        loading={loading}
                        emptyMessage="No rooms were held on this night."
                        columns={folioColumns}
                        data={occupying}
                        variant="striped"
                        pagination
                        pageSize={10}
                        searchable
                        exportable
                    />
                </Tab>
            </Tabs>

            <Modal
                isOpen={!!viewRow}
                title="Settlement Details"
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

                        <ViewSection title="Folio (whole stay)">
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
                    </>
                )}
            </Modal>
        </div>
    );
};

export default SettlementSummary;
