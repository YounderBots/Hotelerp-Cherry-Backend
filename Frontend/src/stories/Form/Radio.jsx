// Radio.jsx
import React from 'react';
import './Radio.css';

const Radio = ({
  label,
  checked,
  onChange,
  disabled = false,
  error = false,
  helperText,
  name,
  value,
  className = '',
  ...props
}) => {
  const radioId = `radio-${Math.random().toString(36).substr(2, 9)}`;

  const radioClasses = [
    'radio-custom',
    error && 'radio-custom--error',
    disabled && 'radio-custom--disabled',
    className
  ].filter(Boolean).join(' ');

  const labelClasses = [
    'radio-label',
    disabled && 'radio-label--disabled'
  ].filter(Boolean).join(' ');

  const textClasses = [
    'radio-text',
    disabled && 'radio-text--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className="radio-group">
      <label className={labelClasses} htmlFor={radioId}>
        <input
          type="radio"
          id={radioId}
          className="radio-input"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          name={name}
          value={value}
          {...props}
        />
        <span className={radioClasses} />
        {label && <span className={textClasses}>{label}</span>}
      </label>
      {helperText && (
        <span className={`radio-helper ${error ? 'radio-helper--error' : ''}`}>
          {helperText}
        </span>
      )}
    </div>
  );
};

export const RadioGroup = ({
  label,
  required = false,
  options = [],
  value,
  onChange,
  disabled = false,
  error = false,
  helperText,
  layout = 'vertical',
  name,
  className = '',
}) => {
  const groupName = name || `radio-group-${Math.random().toString(36).substr(2, 9)}`;

  const containerClasses = [
    layout === 'horizontal' ? 'radio-group-horizontal' : 'radio-group-container',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-group">
      {label && (
        <label className={`radio-group-label ${required ? 'radio-group-label--required' : ''}`}>
          {label}
        </label>
      )}
      <div className={containerClasses}>
        {options.map((option) => {
          const optionLabel = typeof option === 'object' ? option.label : option;
          const optionValue = typeof option === 'object' ? option.value : option;
          
          return (
            <Radio
              key={optionValue}
              label={optionLabel}
              checked={value === optionValue}
              onChange={() => onChange(optionValue)}
              disabled={disabled}
              error={error}
              name={groupName}
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

export default Radio;