import React, { useCallback, useMemo, useState } from "react";
import {
    AlertTriangle,
    CalendarClock,
    CheckCircle2,
    History,
    Moon,
    RefreshCw,
    XCircle,
} from "lucide-react";

import TableTemplate from "../../stories/TableTemplate";
import Tabs, { Tab } from "../../stories/Tabs";
import Modal, { ConfirmModal } from "../../stories/Modal";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import Button from "../../stories/Button";
import RowActions from "../../stories/RowActions";
import APICall from "../../APICalls/APICalls";
import { useApiResource } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import { usePagePermissions } from "../../hooks/usePagePermissions";
import {
    AUDIT_LISTS,
    AUDIT_STATUS_CLASS,
    formatCount,
    formatCurrency,
    formatDate,
    formatDateTime,
    formatPercent,
    formatPrecise,
} from "./nightAuditShared";
import "./NightAudit.css";

/**
 * The Night Audit process screen.
 *
 * WHAT THIS PAGE IS FOR
 * Closing one hotel day. It is the only screen in the module that writes
 * anything; the other three are reports.
 *
 * WHY IT IS NOT JUST A BUTTON
 * Running the audit marks unarrived reservations as No-Show and moves the
 * property's business date, and neither is undoable from the UI. So the page
 * shows the operator exactly what the run will act on -- the night's occupancy,
 * its revenue, the money still owed, every reservation in each category --
 * before offering to run it. The confirm step restates the two consequences in
 * words.
 *
 * EVERY NUMBER ON THIS PAGE COMES FROM THE SERVER
 * Nothing here is summed in the browser. The totals rendered are the same ones
 * `compute_position` produces and `run_audit` snapshots, so what the operator
 * approves is what gets recorded. A frontend that re-derived its own totals
 * could show a figure the audit never stored, which for a financial control is
 * worse than showing nothing.
 */

const readData = (res) => res?.data ?? null;

const StatTile = ({ label, value, hint, tone = "default" }) => (
    <div className={`na-stat na-stat--${tone}`}>
        <span className="na-stat__label">{label}</span>
        <strong className="na-stat__value">{value}</strong>
        {hint ? <span className="na-stat__hint">{hint}</span> : null}
    </div>
);

const ReadinessRow = ({ tone, title, detail, count }) => {
    const Icon = tone === "blocker" ? XCircle : AlertTriangle;
    return (
        <li className={`na-readiness__item na-readiness__item--${tone}`}>
            <Icon size={16} aria-hidden="true" />
            <div>
                <b>
                    {title}
                    {typeof count === "number" ? ` (${count})` : ""}
                </b>
                <span>{detail}</span>
            </div>
        </li>
    );
};

const NightAuditDashboard = () => {
    const perms = usePagePermissions("/night_audit");
    const { toast, showToast } = useToast();

    const [running, setRunning] = useState(false);
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [markNoShows, setMarkNoShows] = useState(true);
    const [resultAudit, setResultAudit] = useState(null);
    const [historyDetail, setHistoryDetail] = useState(null);
    const [runError, setRunError] = useState(null);

    const {
        data: preview,
        loading,
        error,
        reload,
    } = useApiResource(() => APICall.getT("/hotel/night_audit/preview"), {
        select: readData,
        initial: null,
        fallback: "Failed to load the night audit position.",
    });

    const {
        data: history,
        loading: historyLoading,
        error: historyError,
        reload: reloadHistory,
    } = useApiResource(() => APICall.getT("/hotel/night_audit/history"), {
        select: (res) => (Array.isArray(res?.data) ? res.data : []),
        fallback: "Failed to load audit history.",
    });

    const businessDate = preview?.business_date ?? null;
    const readiness = preview?.readiness ?? { ready: false, blockers: [], warnings: [] };
    const movement = preview?.movement ?? {};
    const revenue = preview?.revenue ?? {};
    const settlement = preview?.settlement ?? {};
    const occupancy = preview?.occupancy ?? {};
    const lists = preview?.lists ?? {};
    const daysBehind = preview?.days_behind ?? 0;

    const noShowCount = movement.no_show_candidates ?? 0;

    const refreshAll = useCallback(() => {
        setRunError(null);
        reload();
        reloadHistory();
    }, [reload, reloadHistory]);

    const handleRun = async () => {
        // Guarded here as well as by the disabled button: a double click can
        // dispatch twice before React re-renders, and this run is not
        // idempotent from the user's point of view even though the server
        // makes it so.
        if (running) return;
        setConfirmOpen(false);
        setRunning(true);
        setRunError(null);
        try {
            const res = await APICall.postT("/hotel/night_audit/run", {
                // Naming the date is what stops a stale page from closing the
                // wrong night; the server refuses the run if it has moved on.
                business_date: businessDate,
                mark_no_shows: markNoShows,
            });
            setResultAudit(res?.data?.audit ?? null);
            showToast(
                `Night audit completed for ${formatDate(businessDate)}`,
                "success",
            );
            refreshAll();
        } catch (err) {
            // Shown as a persistent alert, not just a toast: a failed audit is
            // something the operator has to act on, and a banner that
            // disappears after two seconds is the wrong affordance for it.
            setRunError(err?.message || "The night audit could not be completed.");
            showToast("Night audit failed", "error");
            refreshAll();
        } finally {
            setRunning(false);
        }
    };

    // Every column carrying a `render` is typed "custom": TableTemplate's
    // renderCell dispatches on `type` and ignores `render` for anything else,
    // so an untyped column silently shows the raw database value.
    const listColumns = useMemo(
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
            {
                key: "departure_date",
                title: "Departure",
                align: "center",
                width: "100px",
                type: "custom",
                render: (row) => formatDate(row.departure_date),
                exportValue: (row) => row.departure_date ?? "",
            },
            { key: "reservation_status", title: "Status", align: "center", width: "110px", type: "badge" },
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
        ],
        [],
    );

    const historyColumns = useMemo(
        () => [
            {
                key: "business_date",
                title: "Business Date",
                align: "center",
                width: "115px",
                type: "custom",
                render: (row) => formatDate(row.business_date),
                exportValue: (row) => row.business_date ?? "",
            },
            { key: "night_audit_id", title: "Reference", align: "left", width: "150px" },
            {
                key: "audit_status",
                title: "Result",
                align: "center",
                width: "100px",
                type: "custom",
                render: (row) => (
                    <span className={`na-badge ${AUDIT_STATUS_CLASS[row.audit_status] || ""}`}>
                        {row.audit_status}
                    </span>
                ),
                exportValue: (row) => row.audit_status ?? "",
            },
            {
                key: "completed_at",
                title: "Completed",
                align: "center",
                width: "150px",
                type: "custom",
                render: (row) => formatDateTime(row.completed_at),
                exportValue: (row) => row.completed_at ?? "",
            },
            {
                key: "gross_revenue",
                title: "Gross Revenue",
                align: "right",
                width: "120px",
                type: "custom",
                render: (row) => formatCurrency(row.revenue?.gross_revenue),
                exportValue: (row) => row.revenue?.gross_revenue ?? 0,
            },
            {
                key: "payments_collected",
                title: "Collected",
                align: "right",
                width: "115px",
                type: "custom",
                render: (row) => formatCurrency(row.settlement?.payments_collected),
                exportValue: (row) => row.settlement?.payments_collected ?? 0,
            },
            {
                key: "no_shows",
                title: "No-Shows",
                align: "center",
                width: "90px",
                type: "custom",
                render: (row) => formatCount(row.movement?.no_shows_marked),
                exportValue: (row) => row.movement?.no_shows_marked ?? 0,
            },
            {
                key: "actions",
                title: "Actions",
                align: "center",
                width: "80px",
                type: "custom",
                excludeFromExport: true,
                render: (row) => (
                    <RowActions label="audit" onView={() => setHistoryDetail(row)} />
                ),
            },
        ],
        [],
    );

    const canRun = perms.add && readiness.ready && !running && !loading;

    return (
        <div className="na-page">
            <ErrorAlert message={error} />
            <ErrorAlert message={runError} />

            {/* ---------------- Business date + run control ---------------- */}
            <section className="na-hero" aria-label="Business date">
                <div className="na-hero__date">
                    <span className="na-hero__eyebrow">
                        <Moon size={14} aria-hidden="true" /> Current business date
                    </span>
                    <strong className="na-hero__value">
                        {loading ? "…" : formatDate(businessDate)}
                    </strong>
                    <span className="na-hero__meta">
                        {preview?.last_audit_at
                            ? `Last audit ${formatDateTime(preview.last_audit_at)}`
                            : "No audit has been run yet"}
                    </span>
                    {daysBehind > 1 && (
                        <span className="na-hero__behind">
                            <CalendarClock size={13} aria-hidden="true" />
                            {daysBehind} nights behind the calendar
                        </span>
                    )}
                </div>

                <div className="na-hero__actions">
                    {/* Button renders `children` only -- it has no `icon` prop, so
                        the glyph goes inside rather than being spread onto the
                        DOM node as an unknown attribute. */}
                    <Button
                        variant="outline"
                        size="medium"
                        onClick={refreshAll}
                        disabled={loading}
                    >
                        <RefreshCw size={16} aria-hidden="true" />
                        Refresh
                    </Button>
                    <Button
                        variant="primary"
                        size="medium"
                        onClick={() => setConfirmOpen(true)}
                        disabled={!canRun}
                        loading={running}
                        title={
                            !perms.add
                                ? "Your role cannot run the night audit"
                                : readiness.ready
                                    ? undefined
                                    : readiness.blockers[0]?.detail
                        }
                    >
                        <Moon size={16} aria-hidden="true" />
                        {running ? "Running…" : "Run Night Audit"}
                    </Button>
                </div>
            </section>

            {/* ---------------- Readiness ---------------- */}
            <section className="na-readiness" aria-label="Audit readiness">
                {loading ? (
                    <p className="na-readiness__loading">Checking readiness…</p>
                ) : readiness.ready && readiness.warnings.length === 0 ? (
                    <p className="na-readiness__clear">
                        <CheckCircle2 size={16} aria-hidden="true" />
                        Ready to close {formatDate(businessDate)}. Nothing outstanding.
                    </p>
                ) : (
                    <>
                        <h3 className="na-readiness__title">
                            {readiness.ready
                                ? "Ready to run, with things to be aware of"
                                : "Cannot run yet"}
                        </h3>
                        <ul className="na-readiness__list">
                            {readiness.blockers.map((b) => (
                                <ReadinessRow
                                    key={b.code}
                                    tone="blocker"
                                    title={b.label}
                                    detail={b.detail}
                                />
                            ))}
                            {readiness.warnings.map((w) => (
                                <ReadinessRow
                                    key={w.code}
                                    tone="warning"
                                    title={w.label}
                                    detail={w.detail}
                                    count={w.count}
                                />
                            ))}
                        </ul>
                    </>
                )}
            </section>

            {/* ---------------- The night's position ---------------- */}
            <section className="na-stats" aria-label="Position for this night">
                <StatTile
                    label="Room revenue"
                    value={formatCurrency(revenue.room_revenue)}
                    hint="Accrued for this night"
                />
                <StatTile label="Tax" value={formatCurrency(revenue.tax_amount)} />
                <StatTile label="Discount" value={formatCurrency(revenue.discount_amount)} />
                <StatTile
                    label="Gross revenue"
                    value={formatCurrency(revenue.gross_revenue)}
                    tone="primary"
                />
                <StatTile
                    label="Collected"
                    value={formatCurrency(settlement.payments_collected)}
                    hint="Payments dated this day"
                    tone="success"
                />
                <StatTile
                    label="Outstanding"
                    value={formatCurrency(settlement.outstanding_balance)}
                    hint="Owed by arrived guests"
                    tone={settlement.outstanding_balance > 0 ? "warning" : "default"}
                />
                <StatTile
                    label="Occupancy"
                    value={formatCount(occupancy.rooms_occupied)}
                    hint={`${formatCount(occupancy.room_nights)} room nights`}
                />
                <StatTile
                    label="In house"
                    value={formatCount(movement.in_house)}
                    hint={`${formatCount(movement.arrivals_expected)} due in · ${formatCount(
                        movement.departures_expected,
                    )} due out`}
                />
            </section>

            {/* ---------------- What the audit will act on ---------------- */}
            <Tabs variant="default">
                {AUDIT_LISTS.map((list) => {
                    const rows = Array.isArray(lists[list.key]) ? lists[list.key] : [];
                    return (
                        <Tab
                            key={list.key}
                            label={`${list.label}${rows.length ? ` (${rows.length})` : ""}`}
                        >
                            <p className="na-list__description">{list.description}</p>
                            <TableTemplate
                                title={`${list.label} · ${formatDate(businessDate)}`}
                                loading={loading}
                                emptyMessage={list.emptyMessage}
                                columns={listColumns}
                                data={rows}
                                variant="striped"
                                pagination
                                pageSize={10}
                                searchable
                                exportable
                            />
                        </Tab>
                    );
                })}
            </Tabs>

            {/* ---------------- History ---------------- */}
            <section className="na-history" aria-label="Audit history">
                <ErrorAlert message={historyError} />
                <TableTemplate
                    title="Audit History"
                    loading={historyLoading}
                    emptyMessage="No night audit has been run for this property yet."
                    columns={historyColumns}
                    data={history}
                    variant="striped"
                    pagination
                    pageSize={10}
                    searchable
                    exportable
                />
            </section>

            {/* ---------------- Confirm ---------------- */}
            <ConfirmModal
                isOpen={confirmOpen}
                onClose={() => setConfirmOpen(false)}
                onConfirm={handleRun}
                title={`Close ${formatDate(businessDate)}?`}
                confirmText={running ? "Running…" : "Run Night Audit"}
                size="medium"
            >
                <div className="na-confirm">
                    <p>
                        This records the night's figures permanently and moves the business
                        date to <b>{formatDate(preview?.next_business_date)}</b>.
                    </p>

                    <ul className="na-confirm__effects">
                        <li>
                            <b>{formatCurrency(revenue.gross_revenue)}</b> gross revenue and{" "}
                            <b>{formatCurrency(settlement.payments_collected)}</b> collected
                            will be snapshotted.
                        </li>
                        <li>
                            <b>{formatCount(occupancy.rooms_occupied)}</b> occupied rooms and{" "}
                            <b>{formatCount(movement.in_house)}</b> in-house guests recorded.
                        </li>
                        {settlement.outstanding_balance > 0 && (
                            <li>
                                <b>{formatCurrency(settlement.outstanding_balance)}</b> stays
                                outstanding — the audit records it, it does not collect it.
                            </li>
                        )}
                    </ul>

                    {noShowCount > 0 ? (
                        <label className="na-confirm__option">
                            <input
                                type="checkbox"
                                checked={markNoShows}
                                onChange={(e) => setMarkNoShows(e.target.checked)}
                            />
                            <span>
                                Mark the <b>{noShowCount}</b> reservation
                                {noShowCount === 1 ? "" : "s"} that never checked in as{" "}
                                <b>No-Show</b>
                                <em>
                                    This changes those reservations. The audit stores which ones,
                                    so it can be undone by hand if a guest arrived late.
                                </em>
                            </span>
                        </label>
                    ) : (
                        <p className="na-confirm__note">
                            Every arrival due on this date was checked in — no reservation will
                            be changed.
                        </p>
                    )}

                    {readiness.warnings.length > 0 && (
                        <p className="na-confirm__warn">
                            <AlertTriangle size={14} aria-hidden="true" />
                            {readiness.warnings.length} warning
                            {readiness.warnings.length === 1 ? "" : "s"} above will not stop the
                            audit.
                        </p>
                    )}
                </div>
            </ConfirmModal>

            {/* ---------------- Result ---------------- */}
            <Modal
                isOpen={!!resultAudit}
                title={`Night Audit · ${formatDate(resultAudit?.business_date)}`}
                onClose={() => setResultAudit(null)}
                size="large"
                viewMode
                showFooter
                actions={[
                    { label: "Close", variant: "secondary", onClick: () => setResultAudit(null) },
                ]}
            >
                <AuditDetail audit={resultAudit} />
            </Modal>

            {/* ---------------- History detail ---------------- */}
            <Modal
                isOpen={!!historyDetail}
                title={`Night Audit · ${formatDate(historyDetail?.business_date)}`}
                onClose={() => setHistoryDetail(null)}
                size="large"
                viewMode
                showFooter
                actions={[
                    {
                        label: "Close",
                        variant: "secondary",
                        onClick: () => setHistoryDetail(null),
                    },
                ]}
            >
                <AuditDetail audit={historyDetail} />
            </Modal>

            <Toast {...toast} />
        </div>
    );
};

/**
 * One audit record, exactly as it was stored.
 *
 * Deliberately reads from the audit row and never from live reservations: this
 * is a statement of the property's position on a past night, and recomputing it
 * from today's data would give a different answer every time somebody edited an
 * old booking.
 */
const AuditDetail = ({ audit }) => {
    if (!audit) return null;
    const { occupancy = {}, movement = {}, revenue = {}, settlement = {} } = audit;

    return (
        <>
            {audit.audit_status === "Failed" && (
                <ErrorAlert
                    message={
                        audit.error_message
                            ? `This audit failed and was rolled back. ${audit.error_message}`
                            : "This audit failed and was rolled back. No changes were applied."
                    }
                />
            )}

            <ViewSection title="Run">
                <DetailList columns={3}>
                    <DetailItem label="Reference" value={audit.night_audit_id} />
                    <DetailItem label="Business date" value={formatDate(audit.business_date)} />
                    <DetailItem
                        label="Rolled to"
                        value={formatDate(audit.next_business_date)}
                    />
                    <DetailItem
                        label="Result"
                        value={
                            <span className={`na-badge ${AUDIT_STATUS_CLASS[audit.audit_status] || ""}`}>
                                {audit.audit_status}
                            </span>
                        }
                    />
                    <DetailItem label="Started" value={formatDateTime(audit.started_at)} />
                    <DetailItem label="Completed" value={formatDateTime(audit.completed_at)} />
                </DetailList>
            </ViewSection>

            <ViewSection title="Revenue accrued for this night">
                <DetailList columns={3}>
                    <DetailItem label="Room revenue" value={formatPrecise(revenue.room_revenue)} />
                    <DetailItem label="Extra charges" value={formatPrecise(revenue.extra_charges)} />
                    <DetailItem label="Tax" value={formatPrecise(revenue.tax_amount)} />
                    <DetailItem label="Discount" value={formatPrecise(revenue.discount_amount)} />
                    <DetailItem label="Gross revenue" value={formatPrecise(revenue.gross_revenue)} />
                </DetailList>
            </ViewSection>

            <ViewSection title="Settlement">
                <DetailList columns={3}>
                    <DetailItem
                        label="Payments collected"
                        value={formatPrecise(settlement.payments_collected)}
                    />
                    <DetailItem
                        label="Outstanding balance"
                        value={formatPrecise(settlement.outstanding_balance)}
                    />
                </DetailList>
                {Array.isArray(settlement.payment_breakdown) &&
                    settlement.payment_breakdown.length > 0 && (
                        <ul className="na-breakdown">
                            {settlement.payment_breakdown.map((p) => (
                                <li key={p.payment_method}>
                                    <span>{p.payment_method}</span>
                                    <b>{formatPrecise(p.amount)}</b>
                                </li>
                            ))}
                        </ul>
                    )}
            </ViewSection>

            <ViewSection title="Occupancy">
                <DetailList columns={4}>
                    <DetailItem label="Rooms occupied" value={formatCount(occupancy.rooms_occupied)} />
                    <DetailItem
                        label="Rooms in inventory"
                        value={
                            occupancy.rooms_total === null || occupancy.rooms_total === undefined
                                ? "Not recorded"
                                : formatCount(occupancy.rooms_total)
                        }
                    />
                    <DetailItem
                        label="Occupancy"
                        value={
                            occupancy.occupancy_percent === null ||
                                occupancy.occupancy_percent === undefined
                                ? "—"
                                : formatPercent(occupancy.occupancy_percent)
                        }
                    />
                    <DetailItem label="Room nights" value={formatCount(occupancy.room_nights)} />
                </DetailList>
            </ViewSection>

            <ViewSection title="Guest movement">
                <DetailList columns={4}>
                    <DetailItem label="Arrivals due" value={formatCount(movement.arrivals_expected)} />
                    <DetailItem
                        label="Arrivals completed"
                        value={formatCount(movement.arrivals_completed)}
                    />
                    <DetailItem
                        label="Departures due"
                        value={formatCount(movement.departures_expected)}
                    />
                    <DetailItem
                        label="Departures completed"
                        value={formatCount(movement.departures_completed)}
                    />
                    <DetailItem label="In house" value={formatCount(movement.in_house)} />
                    <DetailItem
                        label="Marked No-Show"
                        value={formatCount(movement.no_shows_marked)}
                    />
                </DetailList>
                {Array.isArray(movement.no_show_reservation_ids) &&
                    movement.no_show_reservation_ids.length > 0 && (
                        <p className="na-detail__note">
                            <History size={13} aria-hidden="true" />
                            Reservation IDs changed by this run:{" "}
                            {movement.no_show_reservation_ids.join(", ")}
                        </p>
                    )}
            </ViewSection>
        </>
    );
};

export default NightAuditDashboard;
