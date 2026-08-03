// InputField.jsx (React JS, no TypeScript)
// Presentation-only: parent should manage value and onChange (controlled pattern).
import React, { useState, useEffect } from 'react';
import './InputField.css';

const IconSearch = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden>
    <path d="M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16z" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M21 21l-4.35-4.35" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const IconClear = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden>
    <path d="M18 6L6 18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M6 6l12 12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

/**
 * Props:
 *  - size: 'small' | 'medium' | 'large' | 'full' | 'custom'
 *  - customWidth: string (e.g. '40%' or '320px') used when size === 'custom' 
 *  - placeholder: string
 *  - value: string (controlled)
 *  - onChange: function(event)  <-- parent handles search state
 *  - onClear: function()       <-- called when clear button clicked
 *  - aria-label: string
 *  - disabled: boolean
 *
 * NOTE: component does NOT fetch; it only emits onChange/onClear.
 */
export default function InputField({
  size = 'medium',
  customWidth = '',
  placeholder = 'Search',
  value,
  onChange,
  onClear,
  disabled = false,
  style={},
  className = '',

  'aria-label': ariaLabel = 'Search input',
}) {
  // For safety we support an optional uncontrolled fallback but recommend controlled usage.
  const isControlled = value !== undefined && typeof onChange === 'function';
  const [internal, setInternal] = useState(value ?? '');

  useEffect(() => {
    if (isControlled) {
      setInternal(value);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const handleChange = (e) => {
    if (disabled) return;
    if (isControlled) {
      onChange(e); // parent handles the data
    } else {
      setInternal(e.target.value);
      onChange && onChange(e); // optional callback
    }
  };

  const handleClear = () => {
    if (disabled) return;
    if (isControlled) {
      // parent should react to this clear event (we call onChange with empty value)
      onChange({ target: { value: '' } });
    } else {
      setInternal('');
      onChange && onChange({ target: { value: '' } });
    }
    onClear && onClear();
  };

  const currentValue = isControlled ? value : internal;

  // A custom width applies to the field itself, not the wrapper. This used to
  // assign to `style.width`, which mutated the caller's own style object — the
  // width leaked back into the parent and persisted across renders — while
  // `innerStyle` was built and then never populated, so the field never
  // actually resized.
  const innerStyle = size === 'custom' && customWidth ? { width: customWidth } : undefined;

  // class for percent widths
  const sizeClass = size === 'custom' ? '' : `InputField--${size}`;

  return (
    <div className={`InputField-wrapper ${className}`} style={{ opacity: disabled ? 0.6 : 1,...style }}>
      <div className={`InputField ${sizeClass}`} style={innerStyle} role="search" aria-label={ariaLabel}>
        <span className="InputField__icon" aria-hidden>
          <IconSearch />
        </span>

        <input
          className="InputField__input"
          type="search"
          value={currentValue}
          onChange={handleChange}
          placeholder={placeholder}
          aria-label={ariaLabel}
          disabled={disabled}
        />

        {/* The clear affordance was never rendered: IconClear, the documented
            `onClear` prop and handleClear all existed, but nothing invoked
            them, so onClear never fired for any consumer. */}
        {currentValue && !disabled && (
          <button
            type="button"
            className="InputField__clear"
            onClick={handleClear}
            aria-label="Clear search"
            title="Clear"
          >
            <IconClear />
          </button>
        )}

      </div>
    </div>
  );
}
