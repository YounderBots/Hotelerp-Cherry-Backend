import React, { useState, useMemo } from 'react';
import './TableTemplate.css';
import InputField from './InputField'; // Assuming you have this component
import { ClipboardPaste, FileText, Printer, Settings, Table2 } from 'lucide-react';


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

const BadgeCell = ({ status, type = 'status' }) => {
  const getBadgeConfig = () => {
    const configs = {
      status: {
        active: { label: 'Active', class: 'badge-success' },
        pending: { label: 'Pending', class: 'badge-warning' },
        inactive: { label: 'Inactive', class: 'badge-error' },
        completed: { label: 'Completed', class: 'badge-success' },
        cancelled: { label: 'Cancelled', class: 'badge-error' }
      },
      priority: {
        high: { label: 'High', class: 'badge-error' },
        medium: { label: 'Medium', class: 'badge-warning' },
        low: { label: 'Low', class: 'badge-info' }
      }
    };

    return configs[type]?.[status] || { label: status, class: 'badge-info' };
  };

  const { label, class: badgeClass } = getBadgeConfig();

  return <span className={`table-cell-badge ${badgeClass}`}>{label}</span>;
};

// Toolbar Icons Component
const TableToolbar = ({
  onSearch,
  onCopyJSON,
  onDownloadCSV,
  onDownloadPDF,
  onPrint,
  onFilter,
  searchValue,
  searchPlaceholder = "Search..."
}) => {
  return (
    <div className="table-toolbar">
      <div className="toolbar-left">
        <InputField
          placeholder={searchPlaceholder}
          size="small"
          value={searchValue}
          onChange={(e) => onSearch(e.target.value)}
          style={{ width: '250px' }}
        />
      </div>
      <div className="toolbar-right">
        <div className="toolbar-actions">
          <button
            className="toolbar-btn nav-icon"
            title="Copy as JSON"
            onClick={onCopyJSON}
          >
            <ClipboardPaste />
          </button>
          <button
            className="toolbar-btn nav-icon"
            title="Download CSV"
            onClick={onDownloadCSV}
          >
            <Table2 />
          </button>
          <button
            className="toolbar-btn nav-icon"
            title="Download PDF"
            onClick={onDownloadPDF}
          >
            <FileText />
          </button>
          <button
            className="toolbar-btn nav-icon"
            title="Print Table"
            onClick={onPrint}
          >
            <Printer />
          </button>
          <button
            className="toolbar-btn nav-icon"
            title="Filter Columns"
            onClick={onFilter}
          >
            <Settings />
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
  className = '',
  onRowClick,
  ...props
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [searchTerm, setSearchTerm] = useState('');
  const [visibleColumns, setVisibleColumns] = useState(columns.map(col => col.key));
  const [showFilterModal, setShowFilterModal] = useState(false);
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

      case "badge":
        return typeof value === "string"
          ? value.charAt(0).toUpperCase() + value.slice(1)
          : "";

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

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, currentPage, pageSize, pagination]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

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
    const rows = getExportRows();
    await navigator.clipboard.writeText(JSON.stringify(rows, null, 2));
  };

  const handleDownloadCSV = () => {
    if (sortedData.length === 0) return;

    const headers = columns.map(col => `"${col.title}"`).join(',');
    const csvData = sortedData.map(row =>
      columns.map(col => `"${row[col.key] || ''}"`).join(',')
    ).join('\n');

    const csv = `${headers}\n${csvData}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title || 'table'}-data.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };


  const getExportRows = () => {
    return sortedData.map(row =>
      visibleColumns
        .map(key => columns.find(c => c.key === key))
        .reduce((acc, col) => {
          acc[col.key] = resolveExportValue(row, col);
          return acc;
        }, {})
    );
  };


  const handleDownloadPDF = () => {
    const table = document.getElementById('export-table-full');
    if (!table) return;
    const printWindow = window.open('', '_blank', 'width=1200,height=800');
    printWindow.document.write(`
    <html>
      <head>
        <title>${title || 'Table Export'}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 20px;
          }

          table {
            width: 100%;
            border-collapse: collapse;
          }

          th, td {
            border: 1px solid #ddd;
            padding: 8px;
            vertical-align: middle;
            text-align: left;
          }

          th {
            background: #2f80ed;
            color: #fff;
          }

          img {
            max-width: 32px;
            max-height: 32px;
            border-radius: 50%;
            display: block;
          }

          @media print {
            body {
              margin: 0;
            }
          }
        </style>
      </head>
      <body>
        <h2>${title || ''}</h2>
        ${table.outerHTML}
      </body>
    </html>
  `);

    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 500);
  };




  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    const tableHtml = document.querySelector('.table-template').innerHTML;
    printWindow.document.write(`
      <html>
        <head>
          <title>Print Table</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
          </style>
        </head>
        <body>
          <h2>${title || 'Table Data'}</h2>
          ${tableHtml}
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const handleColumnToggle = (columnKey) => {
    setVisibleColumns(prev =>
      prev.includes(columnKey)
        ? prev.filter(key => key !== columnKey)
        : [...prev, columnKey]
    );
  };

  // Render cell content based on column type
  const renderCell = (item, column) => {
    const value = item[column.key];

    switch (column.type) {
      case 'avatar':
        return <AvatarCell {...value} />;
      case 'badge':
        return <BadgeCell status={value} type={column.badgeType} />;
      case 'custom':
        return column.render ? column.render(item) : value;
      default:
        return value;
    }
  };

  // Filter visible columns
  const visibleColumnsData = columns.filter(col => visibleColumns.includes(col.key));
  const tableClass = `
    table-template
    ${variant !== 'default' ? `table-${variant}` : ''}
    ${size !== 'default' ? `table-${size}` : ''}
    ${loading ? 'table-loading' : ''}
    ${className}
  `.trim();
  return (
    <div className={tableClass} {...props}>
      {/* Title Section */}
      {title && (
        <div className="table-title-section">
          <h2 className="table-title">{title}</h2>
        </div>
      )}

      {/* Toolbar Section */}
      <div className="table-toolbar-section">
        <TableToolbar
          onSearch={setSearchTerm}
          onCopyJSON={handleCopyJSON}
          onDownloadCSV={handleDownloadCSV}
          onDownloadPDF={handleDownloadPDF}
          onPrint={handlePrint}
          onFilter={() => setShowFilterModal(true)}
          searchValue={searchTerm}
          searchPlaceholder={`Search ${filteredData.length} records...`}
        />
      </div>

      {/* Table Section */}
      <div className="table-container">
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: '15px' }} >
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
                <tr>
                  <td colSpan={visibleColumnsData.length} className="table-empty">
                    <div className="table-loading-spinner"></div>
                  </td>
                </tr>
              ) : paginatedData.length === 0 ? (
                <tr>
                  <td colSpan={visibleColumnsData.length} className="table-empty">
                    <div className="table-empty-icon">📊</div>
                    {searchTerm ? 'No results found for your search.' : emptyMessage}
                  </td>
                </tr>
              ) : (
                paginatedData.map((item, index) => (
                  <tr
                    key={item.id || index}
                    onClick={() => onRowClick?.(item)}
                    style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                  >
                    <td>{index + 1}</td>
                    {visibleColumnsData.map((column) => (
                      <td
                        key={column.key}
                        style={{ textAlign: column.align || 'left' }}
                        className={column.cellClass?.(item) || ''}
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
        isOpen={showFilterModal}
      />
      {/* Hidden full table for PDF export */}
      <div style={{ position: 'absolute', left: '-9999px', top: 0 }}>
        <table id="export-table-full">
          <thead>
            <tr>
              <th>S.No</th>
              {visibleColumnsData.map(column => (
                <th key={column.key}>{column.title}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((item, index) => (
              <tr key={item.id || index}>
                <td>{index + 1}</td>
                {visibleColumnsData.map(column => (
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
export { AvatarCell, BadgeCell };