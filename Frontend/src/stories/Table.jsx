import React, { useState, useMemo } from 'react';
import './Table.css';

// Custom cell components
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

const ActionsCell = ({ actions, onAction }) => (
  <div className="table-cell-actions">
    {actions.map((action, index) => (
      <button
        key={index}
        className="action-btn"
        onClick={() => onAction(action.type, action.data)}
        title={action.label}
      >
        {action.icon || action.label}
      </button>
    ))}
  </div>
);

// Main Table Component
const Table = ({
  columns = [],
  data = [],
  variant = 'default',
  size = 'default',
  sortable = false,
  pagination = false,
  pageSize = 10,
  loading = false,
  emptyMessage = 'No data available',
  onSort,
  onRowClick,
  className = '',
  ...props
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig.key || !sortable) return data;
    
    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig, sortable]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;
    
    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, currentPage, pageSize, pagination]);

  const totalPages = Math.ceil(data.length / pageSize);

  // Handle sort
  const handleSort = (key) => {
    if (!sortable) return;
    
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    
    const newSortConfig = { key, direction };
    setSortConfig(newSortConfig);
    onSort?.(newSortConfig);
  };

  // Render cell content based on column type
  const renderCell = (item, column) => {
    const value = item[column.key];
    
    switch (column.type) {
      case 'avatar':
        return <AvatarCell {...value} />;
      case 'badge':
        return <BadgeCell status={value} type={column.badgeType} />;
      case 'actions':
        return <ActionsCell actions={column.actions} onAction={column.onAction} />;
      case 'custom':
        return column.render ? column.render(item) : value;
      default:
        return value;
    }
  };

  // Table classes
  const tableClass = `
    table 
    ${variant !== 'default' ? `table-${variant}` : ''}
    ${size !== 'default' ? `table-${size}` : ''}
    ${loading ? 'table-loading' : ''}
    ${className}
  `.trim();

  return (
    <div className="table-container" {...props}>
      <div className="table-wrapper">
        <table className={tableClass}>
          <thead>
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={sortable ? 'sortable' : ''}
                  onClick={() => handleSort(column.key)}
                  style={{ width: column.width, textAlign: column.align || 'left' }}
                >
                  {column.title}
                  {sortable && sortConfig.key === column.key && (
                    <span className={`sort-${sortConfig.direction}`}></span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="table-empty">
                  <div className="table-loading-spinner"></div>
                </td>
              </tr>
            ) : paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="table-empty">
                  <div className="table-empty-icon">📊</div>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((item, index) => (
                <tr 
                  key={item.id || index}
                  onClick={() => onRowClick?.(item)}
                  style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                >
                  {columns.map((column) => (
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

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="table-pagination">
          <div className="pagination-info">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, data.length)} of {data.length} entries
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
    </div>
  );
};

export default Table;
export { AvatarCell, BadgeCell, ActionsCell };