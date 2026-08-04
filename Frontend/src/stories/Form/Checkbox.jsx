// Checkbox.jsx
import React, { useId } from 'react';
import './Checkbox.css';

const Checkbox = ({
  label,
  checked,
  onChange,
  disabled = false,
  error = false,
  helperText,
  required = false,
  name,
  value,
  className = '',
  ...props
}) => {
  // useId() rather than Math.random(): a random id is impure during render
  // and changes on every re-render, so the label's htmlFor stops matching the
  // input and clicking the label no longer toggles it.
  const checkboxId = `checkbox-${useId()}`;

  const checkboxClasses = [
    'checkbox-custom',
    error && 'checkbox-custom--error',
    disabled && 'checkbox-custom--disabled',
    className
  ].filter(Boolean).join(' ');

  const labelClasses = [
    'checkbox-label',
    disabled && 'checkbox-label--disabled'
  ].filter(Boolean).join(' ');

  const textClasses = [
    'checkbox-text',
    disabled && 'checkbox-text--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className="checkbox-group">
      <label className={labelClasses} htmlFor={checkboxId}>
        <input
          type="checkbox"
          id={checkboxId}
          className="checkbox-input"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          required={required}
          name={name}
          value={value}
          {...props}
        />
        <span className={checkboxClasses} />
        {label && <span className={textClasses}>{label}</span>}
      </label>
      {helperText && (
        <span className={`checkbox-helper ${error ? 'checkbox-helper--error' : ''}`}>
          {helperText}
        </span>
      )}
    </div>
  );
};

export const CheckboxGroup = ({
  label,
  required = false,
  options = [],
  value = [],
  onChange,
  disabled = false,
  error = false,
  helperText,
  className = '',
}) => {
  // `className` was accepted and then dropped, so callers could not style the
  // group at all.
  const handleCheckboxChange = (optionValue, isChecked) => {
    let newValue;
    if (isChecked) {
      newValue = [...value, optionValue];
    } else {
      newValue = value.filter(v => v !== optionValue);
    }
    onChange(newValue);
  };

  return (
    <div className={`form-group ${className}`.trim()}>
      {label && (
        <label className={`checkbox-group-label ${required ? 'checkbox-group-label--required' : ''}`}>
          {label}
        </label>
      )}
      <div className="checkbox-group-container">
        {options.map((option) => {
          const optionLabel = typeof option === 'object' ? option.label : option;
          const optionValue = typeof option === 'object' ? option.value : option;
          
          return (
            <Checkbox
              key={optionValue}
              label={optionLabel}
              checked={value.includes(optionValue)}
              onChange={(e) => handleCheckboxChange(optionValue, e.target.checked)}
              disabled={disabled}
              error={error}
              name={optionValue}
              value={optionValue}
            />
          );
        })}
      </div>
      {helperText && (
        <span className={`form-helper ${error ? 'form-helper--error' : ''}`}>
          {helperText}
        </span>
      )}
    </div>
  );
};

export default Checkbox;