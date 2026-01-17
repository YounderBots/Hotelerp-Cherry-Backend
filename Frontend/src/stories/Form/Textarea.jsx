// Textarea.jsx
import React from 'react';
import './Textarea.css';

const Textarea = ({
  label,
  required = false,
  placeholder,
  value,
  onChange,
  disabled = false,
  error = false,
  success = false,
  helperText,
  maxLength,
  rows = 3,
  fullWidth = true,
  className = '',
  ...props
}) => {
  const characterCount = value?.length || 0;

  const getStateClass = () => {
    if (error) return 'textarea-control--error';
    if (success) return 'textarea-control--success';
    return '';
  };

  const getCounterClass = () => {
    if (!maxLength) return '';
    const ratio = characterCount / maxLength;
    if (ratio >= 1) return 'textarea-counter--error';
    if (ratio >= 0.9) return 'textarea-counter--warning';
    return '';
  };

  const textareaClasses = [
    'textarea-control',
    getStateClass(),
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-group" style={{ width: fullWidth ? '100%' : 'auto' }}>
      {label && (
        <label className={`form-label ${required ? 'form-label--required' : ''}`}>
          {label}
        </label>
      )}
      <textarea
        className={textareaClasses}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        rows={rows}
        maxLength={maxLength}
        {...props}
      />
      {helperText && (
        <span className={`form-helper ${error ? 'form-helper--error' : ''}`}>
          {helperText}
        </span>
      )}
      {maxLength && (
        <div className={`textarea-counter ${getCounterClass()}`}>
          {characterCount} / {maxLength}
        </div>
      )}
    </div>
  );
};

export default Textarea;