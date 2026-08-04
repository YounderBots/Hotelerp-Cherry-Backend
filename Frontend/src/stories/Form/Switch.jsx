// Switch.jsx
import React, { useId } from 'react';
import './Switch.css';

const Switch = ({
  label,
  checked,
  onChange,
  disabled = false,
  error = false,
  helperText,
  size = 'medium',
  className = '',
  ...props
}) => {
  // See Checkbox.jsx: a render-time random id breaks the label association.
  const switchId = `switch-${useId()}`;

  const sliderClasses = [
    'switch-slider',
    `switch-slider--${size}`,
    error && 'switch-slider--error',
    disabled && 'switch-slider--disabled',
    className
  ].filter(Boolean).join(' ');

  const labelClasses = [
    'switch-label',
    disabled && 'switch-label--disabled'
  ].filter(Boolean).join(' ');

  const textClasses = [
    'switch-text',
    disabled && 'switch-text--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className="switch-group">
      <label className={labelClasses} htmlFor={switchId}>
        <input
          type="checkbox"
          id={switchId}
          className="switch-input"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          {...props}
        />
        <span className={sliderClasses} />
        {label && <span className={textClasses}>{label}</span>}
      </label>
      {helperText && (
        <span className={`switch-helper ${error ? 'switch-helper--error' : ''}`}>
          {helperText}
        </span>
      )}
    </div>
  );
};

export default Switch;