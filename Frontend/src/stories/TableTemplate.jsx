import React, { useState, useMemo } from 'react';
import './TableTemplate.css';
import InputField from './InputField'; // Assuming you have this component
import Button from './Button';
import { ClipboardPaste, FileDown, Printer, Settings, FileSpreadsheet, Plus, Inbox } from 'lucide-react';

// Import existing cell components
const AvatarCell = ({ src, name, email }) => (
  <div className="table-cell-avatar">
    <img src={src} alt={name} className="avatar" />
    <div>
      <div style={{ fontWeight: 600 }}>{name}</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{email}</div>
    </div>
  </div>
);

// Status vocabulary is matched case-insensitively. The lookup used to be an
// exact match on lower-case keys only, so the values the app actually stores
// ("Yes", "No", "Working", "Not Working", "Available") all missed and fell
// through to badge-info — every badge in the app was the same blue whatever
// it meant.
const BADGE_CONFIGS = {
  status: {
    active: { label: 'Active', class: 'badge-success' },
    inactive: { label: 'Inactive', class: 'badge-error' },
    pending: { label: 'Pending', class: 'badge-warning' },
    completed: { label: 'Completed', class: 'badge-success' },
    cancelled: { label: 'Cancelled', class: 'badge-error' },
    yes: { label: 'Yes', class: 'badge-success' },
    no: { label: 'No', class: 'badge-neutral' },
    working: { label: 'Working', class: 'badge-success' },
    'not working': { label: 'Not Working', class: 'badge-error' },
    // Housekeeping vocabulary as the rooms table actually stores it
    // (CommonWords.WORK_STATUS is the misspelled 'Not Assigne').
    ready: { label: 'Ready', class: 'badge-success' },
    'not ready': { label: 'Not Ready', class: 'badge-warning' },
    'not assigne': { label: 'Unassigned', class: 'badge-neutral' },
    'not assigned': { label: 'Unassigned', class: 'badge-neutral' },
    reserved: { label: 'Reserved', class: 'badge-info' },
    // Staff shift lifecycle (restaurant_staff_assignment.shift_status /
    // bar_staff_assignment.shift_status), plus the synthetic "Not Scheduled"
    // the roster screens show for an employee with no assignment today.
    scheduled: { label: 'Scheduled', class: 'badge-info' },
    'on shift': { label: 'On Shift', class: 'badge-success' },
    'on break': { label: 'On Break', class: 'badge-warning' },
    closed: { label: 'Closed', class: 'badge-neutral' },
    // Service state of a floor / station (`is_open`). 'closed' above is the
    // other half, shared with the staff shift lifecycle.
    open: { label: 'Open', class: 'badge-success' },
    'not scheduled': { label: 'Not Scheduled', class: 'badge-neutral' },
    unblocking: { label: 'Unblocked', class: 'badge-neutral' },
    blocking: { label: 'Blocked', class: 'badge-error' },
    // housekeeper_task.task_status stores the hyphenated "In-Progress";
    // hotel.inquiry.inquiry_status stores the spaced "In Progress". Both
    // spellings are listed so either renders as the same amber badge rather
    // than falling through to a grey one with the raw string as its label.
    // 'completed' above is the other half of the enquiry pair.
    'in-progress': { label: 'In Progress', class: 'badge-warning' },
    'in progress': { label: 'In Progress', class: 'badge-warning' },
    available: { label: 'Available', class: 'badge-success' },
    // Inventory levels (restaurant + bar Stock screens).
    'in stock': { label: 'In Stock', class: 'badge-success' },
    'low stock': { label: 'Low Stock', class: 'badge-warning' },
    'out of stock': { label: 'Out of Stock', class: 'badge-error' },
    occupied: { label: 'Occupied', class: 'badge-warning' },
    maintenance: { label: 'Maintenance', class: 'badge-error' },
    // The rest of restaurant_table.table_status / bar_table.table_status:
    // 'available', 'occupied' and 'reserved' are already listed, while these
    // two fell through to a grey chip carrying the raw string as its label.
    cleaning: { label: 'Cleaning', class: 'badge-info' },
    blocked: { label: 'Blocked', class: 'badge-error' },
    // Reservation lifecycle, exactly as masterdata.reservation_status spells
    // it (Confirmed / Checked-In / Checked-Out / Cancelled / No-Show /
    // Pending / On Hold). 'pending' and 'cancelled' above are shared with
    // other modules. Both hyphenations of no-show are listed because the
    // label is free text a property can retype.
    confirmed: { label: 'Confirmed', class: 'badge-success' },
    'checked-in': { label: 'Checked-In', class: 'badge-info' },
    'checked-out': { label: 'Checked-Out', class: 'badge-neutral' },
    'no-show': { label: 'No-Show', class: 'badge-warning' },
    'no show': { label: 'No-Show', class: 'badge-warning' },
    'on hold': { label: 'On Hold', class: 'badge-warning' },
    // Restaurant / bar order lifecycle (order_status_enum) and its payment
    // state (order_payment_status_enum). 'in progress', 'ready', 'completed'
    // and 'cancelled' are already listed above and shared with other modules;
    // 'new', 'served' and 'partial' fell through to a grey chip.
    new: { label: 'New', class: 'badge-info' },
    served: { label: 'Served', class: 'badge-success' },
    partial: { label: 'Partial', class: 'badge-warning' },
    // Kitchen / bar ticket lifecycle (kot_status_enum, bot_status_enum) and
    // its per-item preparation state (kot_item_prep_status_enum). 'new',
    // 'in progress', 'ready', 'completed', 'cancelled' and 'pending' are
    // already listed; these two were the gap.
    acknowledged: { label: 'Acknowledged', class: 'badge-info' },
    preparing: { label: 'Preparing', class: 'badge-warning' },
    // Derived payment state on a reservation (API `payment_state`).
    unpaid: { label: 'Unpaid', class: 'badge-error' },
    'partly paid': { label: 'Partly Paid', class: 'badge-warning' },
    paid: { label: 'Paid', class: 'badge-success' },
  },
  priority: {
    // hsk_room_incident.severity uses this vocabulary, so Critical sits above
    // High rather than sharing its badge.
    critical: { label: 'Critical', class: 'badge-error' },
    high: { label: 'High', class: 'badge-error' },
    medium: { label: 'Medium', class: 'badge-warning' },
    low: { label: 'Low', class: 'badge-info' },
    // kot_priority_enum / bot_priority_enum. The kitchen screens asked for a
    // 'status' badge for this column, so ASAP and Normal both fell through to
    // a grey chip and a rush ticket looked like an ordinary one.
    asap: { label: 'ASAP', class: 'badge-error' },
    normal: { label: 'Normal', class: 'badge-neutral' },
  },
};

const BadgeCell = ({ status, type = 'status' }) => {
  if (status === null || status === undefined || status === '') return '—';

  const key = String(status).trim().toLowerCase();
  const { label, class: badgeClass } =
    BADGE_CONFIGS[type]?.[key] || { label: String(status), class: 'badge-neutral' };

  return <span className={`table-cell-badge ${badgeClass}`}>{label}</span>;
};

/** Colour swatch cell — one definition instead of an inline-styled span
 *  re-implemented on each screen that stores a colour. */
export const ColorSwatchCell = ({ color, label }) => (
  <span className="table-cell-swatch">
    <span
      className="table-cell-swatch__dot"
      style={{ backgroundColor: color || 'transparent' }}
      aria-hidden="true"
    />
    {label ?? color ?? '—'}
  </span>
);

// Toolbar Icons Component
const TableToolbar = ({
  onSearch,
  onCopyJSON,
  onDownloadCSV,
  onDownloadPDF,
  onPrint,
  onFilter,
  searchValue,
  searchPlaceholder = "Search...",
  // `searchable` and `exportable` were accepted by TableTemplate and never read,
  // so a caller passing searchable={false} still got a search box and the export
  // buttons could not be hidden at all. They are honoured here.
  searchable = true,
  exportable = true,
  // Business filters (status, date range, ...) supplied by the screen. Kept as
  // a slot rather than a prop schema: what is worth filtering is a per-screen
  // decision, while where the row sits and how it collapses is not.
  filters = null,
}) => {
  return (
    <div className="table-toolbar">
      <div className="toolbar-left">
        {searchable && (
          <InputField
            placeholder={searchPlaceholder}
            size="small"
            value={searchValue}
            onChange={(e) => onSearch(e.target.value)}
            aria-label={searchPlaceholder}
          />
        )}
      </div>
      {filters && <div className="toolbar-filters">{filters}</div>}
      <div className="toolbar-right">
        <div className="toolbar-actions">
          {exportable && (
            <>
              <button
                type="button"
                className="toolbar-btn nav-icon"
                title="Copy as JSON"
                aria-label="Copy table as JSON"
                onClick={onCopyJSON}
              >
                <ClipboardPaste aria-hidden="true" />
              </button>
              <button
                type="button"
                className="toolbar-btn nav-icon"
                title="Download CSV"
                aria-label="Download table as CSV"
                onClick={onDownloadCSV}
              >
                <FileSpreadsheet aria-hidden="true" />
              </button>
              <button
                type="button"
                className="toolbar-btn nav-icon"
                title="Download PDF"
                aria-label="Download table as PDF"
                onClick={onDownloadPDF}
              >
                <FileDown aria-hidden="true" />
              </button>
              <button
                type="button"
                className="toolbar-btn nav-icon"
                title="Print Table"
                aria-label="Print table"
                onClick={onPrint}
              >
                <Printer aria-hidden="true" />
              </button>
            </>
          )}
          <button
            type="button"
            className="toolbar-btn nav-icon"
            title="Filter Columns"
            aria-label="Choose which columns are visible"
            onClick={onFilter}
          >
            <Settings aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
};

const FilterModal = ({ columns, visibleColumns, onColumnToggle, onClose, isOpen, onReset }) => {
  if (!isOpen) return null;

  return (
    <div className="filter-modal-overlay" onClick={onClose}>
      <div className="filter-modal" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="filter-modal-header">
          <div>
            <h3>Column Visibility</h3>
            <p>Select which columns should be visible</p>
          </div>
          <button className="filter-modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        {/* Content */}
        <div className="filter-modal-content">
          {columns.map(column => (
            <label key={column.key} className="filter-item">
              <input
                type="checkbox"
                checked={visibleColumns.includes(column.key)}
                onChange={() => onColumnToggle(column.key)}
              />
              <span className="filter-label">{column.title}</span>
            </label>
          ))}
        </div>

        {/* Footer */}
        <div className="filter-modal-footer">
          <button className="btn-secondary" onClick={onReset}>
            Reset
          </button>
          <button className="btn-primary" onClick={onClose}>
            Apply
          </button>
        </div>
      </div>
    </div>
  );
};

// Action Button Variant Component — delegates to the shared Storybook Button
// so every "Add X" button in the app renders identically to Submit/Cancel
// buttons elsewhere (same color, padding, height, focus/disabled states).
const TableActionButton = ({
  onClick,
  label = "Add New",
  icon = <Plus size={18} />,
  variant = "primary",
  size = "medium",
}) => (
  <Button variant={variant} size={size} onClick={onClick} className="table-action-button">
    {icon}
    {label && <span>{label}</span>}
  </Button>
);

// Main TableTemplate Component
const TableTemplate = ({
  title,
  columns = [],
  data = [],
  variant = 'default',
  size = 'default',
  pagination = true,
  pageSize = 10,
  loading = false,
  emptyMessage = 'No data available',
  searchable = true,
  exportable = true,
  filters = null,
  className = '',
  onRowClick,
  // New props for action button variant
  actionButton = null, // Object: { onClick, label, icon, variant, size }
  hasActionButton = false,
  ...props
}) => {
  // The page the user asked for. The page actually rendered is this clamped
  // to the current page count (see `currentPage` below) — deleting the only
  // row on the last page, or any reload that shrinks the set, used to leave
  // this pointing past the end and render an empty table.
  const [requestedPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [searchTerm, setSearchTerm] = useState('');

  // Sorting already reset to page 1; searching did not. Filtering down to a
  // single page while on page 3 showed an empty table with no explanation.
  const handleSearch = (term) => {
    setSearchTerm(term);
    setCurrentPage(1);
  };
  const [visibleColumns, setVisibleColumns] = useState(columns.map(col => col.key));
  const [showFilterModal, setShowFilterModal] = useState(false);
  // Transient feedback for the "Copy as JSON" action (this component has no
  // shared Toast of its own).
  const [copyToast, setCopyToast] = useState(null); // { type: 'success'|'error', message }

  const flashCopyToast = (type, message) => {
    setCopyToast({ type, message });
    setTimeout(() => setCopyToast(null), 2000);
  };
  
  const formatCellValue = (value, colKey) => {
    if (value === null || value === undefined) return "";

    // If object
    if (typeof value === "object") {
      // Special handling for known objects
      if (colKey === "user") {
        return `${value.name} (${value.email})`;
      }

      // Fallback for unknown objects
      return JSON.stringify(value);
    }

    return String(value);
  };
  
  const resolveExportValue = (row, column) => {
    const value = row[column.key];

    // Highest priority → column-controlled export
    if (column.exportValue) {
      return column.exportValue(row);
    }

    // Handle known column types
    switch (column.type) {
      case "avatar":
        return value?.name || value?.email || "";

      case "badge": {
        const shown = column.render ? column.render(row) : value;
        return typeof shown === "string"
          ? shown.charAt(0).toUpperCase() + shown.slice(1)
          : "";
      }

      case "custom":
        // Custom JSX cannot be exported → fallback
        return formatCellValue(value, column.key);

      default:
        return formatCellValue(value, column.key);
    }
  };

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm) return data;

    const term = searchTerm.toLowerCase();

    return data.filter(row =>
      columns.some(column => {
        const value = resolveExportValue(row, column);
        return (
          value &&
          String(value).toLowerCase().includes(term)
        );
      })
    );
  }, [data, searchTerm, columns]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortConfig]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

  // Clamped at render time rather than corrected in an effect, so there is
  // never a pass that paints an out-of-range page.
  const currentPage = Math.min(requestedPage, Math.max(totalPages, 1));

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, currentPage, pageSize, pagination]);

  // Handle sort with cycle: none -> asc -> desc -> asc...
  const handleSort = (key) => {
    let direction = 'asc';

    if (sortConfig.key === key) {
      if (sortConfig.direction === 'asc') {
        direction = 'desc';
      } else if (sortConfig.direction === 'desc') {
        direction = 'asc';
      }
    }

    setSortConfig({ key, direction });
    setCurrentPage(1); // Reset to first page when sorting
  };

  // Export functions
  const handleCopyJSON = async () => {
    const json = JSON.stringify(getExportRows(), null, 2);

    // The Clipboard API is only available in secure contexts (https or
    // localhost). Over plain http on a LAN IP navigator.clipboard is
    // undefined, so fall back to the legacy execCommand('copy') path.
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(json);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = json;
        // Keep it out of view and non-disruptive to scroll position.
        textarea.style.position = 'fixed';
        textarea.style.top = '-9999px';
        textarea.setAttribute('readonly', '');
        document.body.appendChild(textarea);
        textarea.select();
        const ok = document.execCommand('copy');
        document.body.removeChild(textarea);
        if (!ok) throw new Error('execCommand copy failed');
      }
      flashCopyToast('success', 'Table copied as JSON');
    } catch {
      flashCopyToast('error', 'Copy failed — clipboard unavailable');
    }
  };

  const handleDownloadCSV = () => {
    if (sortedData.length === 0) return;

    // Mirrors the PDF export: current column visibility, resolved values and
    // an absolute S.No. This used to read `row[col.key]` off every column,
    // including the visibility-hidden ones and the render-only Actions
    // column, so the file carried an always-empty Actions field and rendered
    // every custom cell as a blank.
    const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const headers = ['"S.No"', ...exportColumnsData.map(col => escape(col.title))].join(',');
    const csvData = sortedData
      .map((row, i) =>
        [i + 1, ...exportColumnsData.map(col => resolveExportValue(row, col))]
          .map(escape)
          .join(','),
      )
      .join('\n');

    const csv = `${headers}\n${csvData}`;
    // BOM so Excel opens a UTF-8 CSV without mangling non-ASCII names.
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title || 'table'}-data.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getExportRows = () =>
    sortedData.map(row =>
      exportColumnsData.reduce((acc, col) => {
        acc[col.key] = resolveExportValue(row, col);
        return acc;
      }, {}),
    );

  // Generate a real PDF (jsPDF + autotable) rather than opening the browser's
  // print dialog. Columns follow the current visibility selection; rows use the
  // same resolved export values as CSV, with an absolute S.No.
  //
  // jspdf + jspdf-autotable are ~444 kB and this component is shared by 54
  // pages, so they are imported dynamically here rather than at module scope.
  // Statically imported they were the largest chunk in the app -- larger than
  // the entry bundle -- and every table page paid for them even when nobody
  // exported anything.
  const handleDownloadPDF = async () => {
    if (sortedData.length === 0) return;

    let jsPDF;
    let autoTable;
    try {
      [{ jsPDF }, { default: autoTable }] = await Promise.all([
        import('jspdf'),
        import('jspdf-autotable'),
      ]);
    } catch {
      // A chunk that fails to load (offline, cache miss after a deploy) must
      // not take the page down with it.
      flashCopyToast('error', 'Could not load the PDF exporter. Please try again.');
      return;
    }

    const head = [['S.No', ...exportColumnsData.map(col => col.title)]];
    const body = sortedData.map((row, i) => [
      i + 1,
      ...exportColumnsData.map(col => resolveExportValue(row, col)),
    ]);

    const doc = new jsPDF({ orientation: 'landscape' });

    if (title) {
      doc.setFontSize(14);
      doc.text(title, 14, 16);
    }

    autoTable(doc, {
      head,
      body,
      startY: title ? 22 : 14,
      styles: { fontSize: 9, cellPadding: 3, overflow: 'linebreak' },
      headStyles: { fillColor: [193, 18, 50], textColor: 255, fontStyle: 'bold' },
      alternateRowStyles: { fillColor: [248, 245, 247] },
    });

    doc.save(`${title || 'table'}-data.pdf`);
  };

  // Print ONLY the clean data table — reuse the off-screen export table so the
  // printout never includes the toolbar (Add button / search) or a duplicated
  // on-screen heading. The title is rendered exactly once here.
  const handlePrint = () => {
    const table = document.getElementById('export-table-full');
    if (!table) return;

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>${title || 'Table Data'}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: middle; }
            th { background-color: #c11232; color: #fff; }
            img { max-width: 32px; max-height: 32px; border-radius: 50%; display: block; }
            @media print { body { margin: 0; } }
          </style>
        </head>
        <body>
          ${title ? `<h2>${title}</h2>` : ''}
          ${table.outerHTML}
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 300);
  };

  const handleColumnToggle = (columnKey) => {
    setVisibleColumns(prev =>
      prev.includes(columnKey)
        ? prev.filter(key => key !== columnKey)
        : [...prev, columnKey]
    );
  };

  // Reset column visibility to the default: every column visible.
  const handleResetColumns = () => {
    setVisibleColumns(columns.map(col => col.key));
  };

  // Render cell content based on column type
  const renderCell = (item, column) => {
    const value = item[column.key];

    switch (column.type) {
      case 'avatar':
        return <AvatarCell {...value} />;
      case 'badge':
        // `render` lets a column map a raw value into the badge vocabulary
        // below — a boolean `below_minimum` into "Low Stock" / "In Stock",
        // say. Without it a screen had to fall back to type:'custom' and
        // hand-roll a <span className="badge">, which is how an unstyled chip
        // that was the same colour for every state ended up on the Stock
        // screens. Absent `render`, behaviour is unchanged.
        return <BadgeCell status={column.render ? column.render(item) : value} type={column.badgeType} />;
      case 'custom':
        return column.render ? column.render(item) : value;
      default:
        return value;
    }
  };

  // Filter visible columns
  const visibleColumnsData = columns.filter(col => visibleColumns.includes(col.key));

  // Columns that carry no data worth exporting — the render-only Actions
  // column above all — opt out with `excludeFromExport`. Without it every
  // CSV/PDF/JSON/print carried a blank "Actions" column.
  const exportColumnsData = visibleColumnsData.filter(col => !col.excludeFromExport);
  
  const tableClass = `
    table-template
    ${variant !== 'default' ? `table-${variant}` : ''}
    ${size !== 'default' ? `table-${size}` : ''}
    ${loading ? 'table-loading' : ''}
    ${className}
  `.trim();

  return (
    <div className={tableClass} {...props}>
      {/* Title Section with optional action button */}
      {title && (
        <div className="table-title-section">
          <div className="table-title-wrapper">
            <h2 className="table-title">{title}</h2>
            {hasActionButton && actionButton && (
              <TableActionButton
                onClick={actionButton.onClick}
                label={actionButton.label}
                icon={actionButton.icon}
                variant={actionButton.variant}
                size={actionButton.size}
              />
            )}
          </div>
        </div>
      )}

      {/* Toolbar Section */}
      <div className="table-toolbar-section">
        <TableToolbar
          onSearch={handleSearch}
          onCopyJSON={handleCopyJSON}
          onDownloadCSV={handleDownloadCSV}
          onDownloadPDF={handleDownloadPDF}
          onPrint={handlePrint}
          onFilter={() => setShowFilterModal(true)}
          searchValue={searchTerm}
          searchPlaceholder={`Search ${filteredData.length} records...`}
          searchable={searchable}
          exportable={exportable}
          filters={filters}
        />
      </div>

      {/* Table Section */}
      <div className="table-container">
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th >  
                  S.No
                </th>
                {visibleColumnsData.map((column) => (
                  <th
                    key={column.key}
                    className="sortable"
                    onClick={() => handleSort(column.key)}
                    style={{
                      width: column.width,
                      textAlign: column.align || 'left',
                      cursor: 'pointer'
                    }}  
                  >
                    {column.title}
                    {sortConfig.key === column.key && (
                      <span className={`sort-indicator ${sortConfig.direction}`}>
                        {sortConfig.direction === 'asc' ? ' ↑' : ' ↓'}
                      </span>
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                /* colSpan must cover the S.No column too. It counted only the
                   data columns, so the loading and empty rows stopped one
                   column short and left a stray cell on the right. The
                   full-width class opts this cell out of the sticky
                   last-column treatment further down. */
                <tr className="table-message-row">
                  <td colSpan={visibleColumnsData.length + 1} className="table-empty">
                    <div className="table-loading-spinner" role="status" aria-label="Loading" />
                    <div className="table-empty-text">Loading…</div>
                  </td>
                </tr>
              ) : paginatedData.length === 0 ? (
                <tr className="table-message-row">
                  <td colSpan={visibleColumnsData.length + 1} className="table-empty">
                    <div className="table-empty-icon" aria-hidden="true">
                      <Inbox strokeWidth={1.25} />
                    </div>
                    <div className="table-empty-text">
                      {searchTerm ? 'No results match your search.' : emptyMessage}
                    </div>
                    {searchTerm && (
                      <button
                        type="button"
                        className="table-empty-action"
                        onClick={() => handleSearch('')}
                      >
                        Clear search
                      </button>
                    )}
                  </td>
                </tr>
              ) : (
                paginatedData.map((item, index) => (
                  <tr
                    key={item.id || index}
                    onClick={() => onRowClick?.(item)}
                    style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                  >
                    <td data-label="S.No">
                      {pagination ? (currentPage - 1) * pageSize + index + 1 : index + 1}
                    </td>
                    {visibleColumnsData.map((column) => (
                      <td
                        key={column.key}
                        // Read by the stacked card layout on narrow screens,
                        // where the header row is hidden and each cell has to
                        // carry its own label.
                        data-label={column.title}
                        style={{ textAlign: column.align || 'left' }}
                        className={[column.cellClass?.(item), column.key === 'actions' && 'table-cell-actions']
                          .filter(Boolean)
                          .join(' ')}
                      >
                        {renderCell(item, column)}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Section */}
      {pagination && totalPages > 1 && (
        <div className="table-pagination">
          <div className="pagination-info">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, filteredData.length)} of {filteredData.length} entries
            {searchTerm && ` (filtered from ${data.length} total)`}
          </div>
          <div className="pagination-controls">
            <button
              className="pagination-btn"
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
            >
              First
            </button>
            <button
              className="pagination-btn"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <div className="pagination-pages">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                return (
                  <button
                    key={pageNum}
                    className={`pagination-page ${currentPage === pageNum ? 'active' : ''}`}
                    onClick={() => setCurrentPage(pageNum)}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>
            <button
              className="pagination-btn"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
            <button
              className="pagination-btn"
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
            >
              Last
            </button>
          </div>
        </div>
      )}

      {/* Filter Modal */}
      <FilterModal
        columns={columns}
        visibleColumns={visibleColumns}
        onColumnToggle={handleColumnToggle}
        onClose={() => setShowFilterModal(false)}
        onReset={handleResetColumns}
        isOpen={showFilterModal}
      />

      {/* Copy-to-JSON feedback */}
      {copyToast && (
        <div className={`table-copy-toast table-copy-toast--${copyToast.type}`} role="status">
          {copyToast.message}
        </div>
      )}
      {/* Off-screen full table used only as a source for CSV/PDF export. It is
          hidden from assistive tech (aria-hidden) so screen readers don't
          encounter a duplicate of the visible table. */}
      <div aria-hidden="true" style={{ position: 'absolute', left: '-9999px', top: 0 }}>
        <table id="export-table-full">
          <thead>
            <tr>
              <th>S.No</th>
              {exportColumnsData.map(column => (
                <th key={column.key}>{column.title}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((item, index) => (
              <tr key={item.id || index}>
                <td style={{ width: '200px' }}>{index + 1}</td>
                {exportColumnsData.map(column => (
                  <td key={column.key}>
                    {renderCell(item, column)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TableTemplate;
export { AvatarCell, BadgeCell, TableActionButton };