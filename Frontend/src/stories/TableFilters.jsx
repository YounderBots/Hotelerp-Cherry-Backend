// TableFilters.jsx
//
// The business-filter row that sits in a TableTemplate toolbar, beside the
// search box.
//
// TableTemplate already ships free-text search, sorting and a column-visibility
// picker, but nothing for "show me only the enquiries still in progress" — the
// filtering a screen needs when the distinction is a value in a column rather
// than a substring anywhere in the row. Screens that wanted it would otherwise
// each hand-roll a `<select>` above the table, and the control heights, label
// casing and clear affordance would drift apart immediately.
//
// The controls deliberately reuse `.select-control` / `.form-control` and their
// `--small` size from FormField.css rather than defining their own chrome, so a
// filter input is the same object as a form input, one size down.
import React from 'react';
import { FilterX } from 'lucide-react';
import './TableFilters.css';

/** Label + control pair. Use directly when a filter needs a custom control. */
export const FilterField = ({ label, htmlFor, children, className = '' }) => (
  <div className={['table-filter', className].filter(Boolean).join(' ')}>
    <label className="table-filter__label" htmlFor={htmlFor}>
      {label}
    </label>
    {children}
  </div>
);

/**
 * A single-choice filter. The empty value is always "no filter", so a screen
 * never has to model "all" as a sentinel of its own.
 *
 * `options` takes plain strings or {value, label} objects, matching Select.
 */
export const FilterSelect = ({
  id,
  label,
  value,
  onChange,
  options = [],
  allLabel = 'All',
  disabled = false,
}) => (
  <FilterField label={label} htmlFor={id}>
    <select
      id={id}
      className="select-control select-control--small table-filter__control"
      value={value ?? ''}
      onChange={onChange}
      disabled={disabled}
    >
      <option value="">{allLabel}</option>
      {options.map((opt) => {
        const optValue = typeof opt === 'object' ? opt.value : opt;
        const optLabel = typeof opt === 'object' ? opt.label : opt;
        return (
          <option key={optValue} value={optValue}>
            {optLabel}
          </option>
        );
      })}
    </select>
  </FilterField>
);

/** A date bound. Pair two of them for a range. */
export const FilterDate = ({
  id,
  label,
  value,
  onChange,
  min,
  max,
  disabled = false,
}) => (
  <FilterField label={label} htmlFor={id}>
    <input
      id={id}
      type="date"
      className="form-control form-control--small table-filter__control"
      value={value ?? ''}
      onChange={onChange}
      min={min || undefined}
      max={max || undefined}
      disabled={disabled}
    />
  </FilterField>
);

/**
 * Container for a row of filters.
 *
 * `isActive` drives the Clear button rather than the component inspecting its
 * children: only the screen knows what "no filter applied" means for its own
 * state, and a Clear button that is always enabled invites a click that does
 * nothing.
 */
const TableFilters = ({ children, onClear, isActive = false, className = '' }) => (
  <div
    className={['table-filters', className].filter(Boolean).join(' ')}
    role="group"
    aria-label="Filters"
  >
    {children}
    {onClear && (
      <button
        type="button"
        className="table-filters__clear"
        onClick={onClear}
        disabled={!isActive}
        title="Clear all filters"
      >
        <FilterX size={14} aria-hidden="true" />
        <span>Clear</span>
      </button>
    )}
  </div>
);

export default TableFilters;
