import React, { useMemo, useState } from "react";

import TableTemplate from "../../stories/TableTemplate";
import TableFilters, { FilterDate } from "../../stories/TableFilters";
import Tabs, { Tab } from "../../stories/Tabs";
import Modal from "../../stories/Modal";
import DetailList, { DetailItem } from "../../stories/DetailList";
import ViewSection from "../../stories/ViewSection";
import ErrorAlert from "../../stories/ErrorAlert";
import RowActions from "../../stories/RowActions";
import APICall from "../../APICalls/APICalls";
import { useApiResources } from "../../hooks/useApiResource";
import { formatCount, formatDate } from "./nightAuditShared";
import "./NightAudit.css";

/**
 * User Reserved Details -- what happened on the property over a date range.
 *
 * WHAT CHANGED
 * This screen called `/hotel/room_reservation` and `/hotel/housekeeper_tasks`
 * and listed everything both returned, unfiltered. Meanwhile
 * `/hotel/user_activity_log` -- an endpoint written for exactly this screen,
 * which takes a date range and returns both halves already scoped and shaped --
 * sat unused. The RBAC map still lists it as belonging to `/dashboard`, because
 * the generator could only see who actually called it.
 *
 * It now uses that endpoint, with the range defaulting to the two days ending
 * at the current business date (the server's own default when no dates are
 * sent), so the report opens on the window a night auditor cares about instead
 * of on the entire history of the hotel.
 */

const readActivity = (res) => res?.data ?? { room_activity: [], housekeeping_activity: [] };
const readTasks = (res) => (Array.isArray(res?.data) ? res.data : []);

const UserReserved = () => {
    const [fromDate, setFromDate] = useState("");
    const [toDate, setToDate] = useState("");
    const [viewRoom, setViewRoom] = useState(null);
    const [viewTask, setViewTask] = useState(null);

    // Both dates or neither: the endpoint treats a lone bound as "no range
    // given" and quietly falls back to its default, which would look like the
    // filter had silently done nothing.
    const rangeReady = Boolean(fromDate && toDate);
    const rangeParams = rangeReady ? { from_date: fromDate, to_date: toDate } : {};

    const {
        data: [activity, tasks],
        loading,
        error,
    } = useApiResources(
        [
            {
                fetch: () => APICall.getT("/hotel/user_activity_log", rangeParams),
                select: readActivity,
                initial: { room_activity: [], housekeeping_activity: [] },
                fallback: "Failed to load user activity.",
            },
            {
                // The activity log carries the housekeeping summary, but not
                // the per-task detail (schedule time, room status, special
                // instructions) the View modal shows. Loaded alongside rather
                // than widening the log's response for one screen.
                fetch: () => APICall.getT("/hotel/housekeeper_tasks"),
                select: readTasks,
                initial: [],
            },
        ],
        { deps: [fromDate, toDate, rangeReady] },
    );

    const roomActivity = Array.isArray(activity?.room_activity)
        ? activity.room_activity
        : [];
    const housekeeping = Array.isArray(activity?.housekeeping_activity)
        ? activity.housekeeping_activity
        : [];

    // The log returns the task's summary fields only; the full row is matched
    // back by id for the detail view.
    const taskById = useMemo(() => {
        const map = new Map();
        for (const t of tasks || []) map.set(t.id, t);
        return map;
    }, [tasks]);

    const roomColumns = useMemo(
        () => [
            { key: "reservation_id", title: "Reservation", align: "left", width: "130px" },
            {
                key: "first_name",
                title: "Guest",
                align: "left",
                width: "150px",
                // `type: "custom"` is what makes `render` run at all -- see the
                // note in RoomBooked.jsx.
                type: "custom",
                render: (row) =>
                    [row.first_name, row.last_name].filter(Boolean).join(" ") || "—",
                exportValue: (row) =>
                    [row.first_name, row.last_name].filter(Boolean).join(" "),
            },
            { key: "room_no", title: "Room", align: "center", width: "70px" },
            { key: "phone", title: "Phone", align: "center", width: "115px" },
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
            { key: "booking_status", title: "Status", align: "center", width: "110px", type: "badge" },
            {
                key: "actions",
                title: "Actions",
                align: "center",
                width: "80px",
                type: "custom",
                excludeFromExport: true,
                render: (row) => (
                    <RowActions label="reservation" onView={() => setViewRoom(row)} />
                ),
            },
        ],
        [],
    );

    const taskColumns = useMemo(
        () => [
            { key: "employee_id", title: "Employee ID", align: "center", width: "105px" },
            { key: "employee_name", title: "Employee", align: "left", width: "150px" },
            { key: "room_no", title: "Room", align: "center", width: "70px" },
            { key: "task_type", title: "Task Type", align: "left", width: "140px" },
            { key: "task_status", title: "Status", align: "center", width: "110px", type: "badge" },
            {
                key: "actions",
                title: "Actions",
                align: "center",
                width: "80px",
                type: "custom",
                excludeFromExport: true,
                render: (row) => (
                    <RowActions
                        label="task"
                        onView={() => setViewTask({ ...row, ...(taskById.get(row.id) || {}) })}
                    />
                ),
            },
        ],
        [taskById],
    );

    // Rendered ONCE, above the tabs, rather than handed to each tab's
    // TableTemplate. Tabs mounts every panel and hides the inactive ones with
    // CSS, so a filter row inside two panels would put two elements with
    // id="ur-from" in the document -- and a <label for> binds to the first
    // match, so clicking the visible tab's label would focus the hidden one.
    // One range across both tabs is also the correct behaviour: they are two
    // views of the same window.
    const filters = (
        <TableFilters
            isActive={Boolean(fromDate || toDate)}
            onClear={() => {
                setFromDate("");
                setToDate("");
            }}
        >
            <FilterDate
                id="ur-from"
                label="From"
                value={fromDate}
                max={toDate || undefined}
                onChange={(e) => setFromDate(e.target.value)}
            />
            <FilterDate
                id="ur-to"
                label="To"
                value={toDate}
                min={fromDate || undefined}
                onChange={(e) => setToDate(e.target.value)}
            />
        </TableFilters>
    );

    const rangeLabel = rangeReady
        ? `${formatDate(fromDate)} – ${formatDate(toDate)}`
        : "Default range";

    return (
        <div className="na-page">
            <ErrorAlert message={error} />

            <header className="na-report__header">
                <div className="na-report__context">
                    <h2 className="na-report__title">User Reserved Details</h2>
                    <span className="na-report__subtitle">
                        Reservation and housekeeping activity · <b>{rangeLabel}</b>
                        {!rangeReady && fromDate
                            ? " · pick a To date to apply the range"
                            : ""}
                    </span>
                </div>
            </header>

            <section className="na-stats" aria-label="Activity summary">
                <div className="na-stat na-stat--primary">
                    <span className="na-stat__label">Reservation activity</span>
                    <strong className="na-stat__value">
                        {loading ? "…" : formatCount(roomActivity.length)}
                    </strong>
                </div>
                <div className="na-stat">
                    <span className="na-stat__label">Housekeeping tasks</span>
                    <strong className="na-stat__value">
                        {loading ? "…" : formatCount(housekeeping.length)}
                    </strong>
                </div>
            </section>

            {filters}

            <Tabs variant="default">
                <Tab label={`User Activity (${roomActivity.length})`}>
                    <p className="na-list__description">
                        Reservations whose arrival falls in this range.
                    </p>
                    <TableTemplate
                        title="User Activity Log"
                        loading={loading}
                        emptyMessage="No reservation activity in this range."
                        columns={roomColumns}
                        data={roomActivity}
                        variant="striped"
                        pagination
                        pageSize={10}
                        searchable
                        exportable
                    />
                </Tab>

                <Tab label={`House Keeper (${housekeeping.length})`}>
                    <p className="na-list__description">
                        Housekeeping tasks scheduled in this range.
                    </p>
                    <TableTemplate
                        title="House Keeper Tasks"
                        loading={loading}
                        emptyMessage="No housekeeping tasks in this range."
                        columns={taskColumns}
                        data={housekeeping}
                        variant="striped"
                        pagination
                        pageSize={10}
                        searchable
                        exportable
                    />
                </Tab>
            </Tabs>

            <Modal
                isOpen={!!viewRoom}
                title="Reservation Activity"
                onClose={() => setViewRoom(null)}
                size="medium"
                viewMode
                showFooter
                actions={[
                    { label: "Close", variant: "secondary", onClick: () => setViewRoom(null) },
                ]}
            >
                {viewRoom && (
                    <ViewSection title="Reservation">
                        <DetailList columns={2}>
                            <DetailItem label="Reservation" value={viewRoom.reservation_id} />
                            <DetailItem
                                label="Guest"
                                value={[viewRoom.first_name, viewRoom.last_name]
                                    .filter(Boolean)
                                    .join(" ")}
                            />
                            <DetailItem label="Room" value={viewRoom.room_no} />
                            <DetailItem label="Phone" value={viewRoom.phone} />
                            <DetailItem label="Email" value={viewRoom.email} />
                            <DetailItem label="Status" value={viewRoom.booking_status} />
                            <DetailItem label="Arrival" value={formatDate(viewRoom.arrival_date)} />
                            <DetailItem
                                label="Departure"
                                value={formatDate(viewRoom.departure_date)}
                            />
                        </DetailList>
                    </ViewSection>
                )}
            </Modal>

            <Modal
                isOpen={!!viewTask}
                title="House Keeper Task"
                onClose={() => setViewTask(null)}
                size="medium"
                viewMode
                showFooter
                actions={[
                    { label: "Close", variant: "secondary", onClick: () => setViewTask(null) },
                ]}
            >
                {viewTask && (
                    <>
                        <ViewSection title="Assignment">
                            <DetailList columns={2}>
                                <DetailItem label="Employee ID" value={viewTask.employee_id} />
                                <DetailItem label="Employee" value={viewTask.employee_name} />
                                <DetailItem label="Room" value={viewTask.room_no} />
                                <DetailItem label="Task type" value={viewTask.task_type} />
                                <DetailItem label="Task status" value={viewTask.task_status} />
                                <DetailItem label="Room status" value={viewTask.room_status} />
                                <DetailItem
                                    label="Scheduled"
                                    value={
                                        viewTask.schedule_date
                                            ? `${formatDate(viewTask.schedule_date)}${viewTask.schedule_time
                                                ? ` · ${viewTask.schedule_time}`
                                                : ""
                                            }`
                                            : null
                                    }
                                />
                            </DetailList>
                        </ViewSection>

                        {viewTask.special_instructions ? (
                            <ViewSection title="Special Instructions">
                                <DetailList columns={1}>
                                    <DetailItem
                                        label="Instructions"
                                        value={viewTask.special_instructions}
                                        span={1}
                                    />
                                </DetailList>
                            </ViewSection>
                        ) : null}
                    </>
                )}
            </Modal>
        </div>
    );
};

export default UserReserved;
