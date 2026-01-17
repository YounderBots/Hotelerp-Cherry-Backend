// Input.jsx
import React, { useState } from 'react';
import './Input.css';
import { Eye, EyeClosed, EyeClosedIcon, EyeOff } from 'lucide-react';
import { RxEyeOpen } from 'react-icons/rx';

const Input = ({
  label,
  required = false,
  size = 'medium',
  type = 'text',
  placeholder,
  value,
  onChange,
  disabled = false,
  error = false,
  success = false,
  warning = false,
  helperText,
  fullWidth = true,
  icon,
  prepend,
  append,
  className = '',
  ...props
}) => {
  const [showPassword, setShowPassword] = useState(false);

  const getInputType = () => {
    if (type === 'password' && showPassword) return 'text';
    return type;
  };

  const getStateClass = () => {
    if (error) return 'form-control--error';
    if (success) return 'form-control--success';
    if (warning) return 'form-control--warning';
    return '';
  };

  const getHelperClass = () => {
    if (error) return 'form-helper--error';
    if (success) return 'form-helper--success';
    if (warning) return 'form-helper--warning';
    return '';
  };

  const inputClasses = [
    'form-control',
    `form-control--${size}`,
    getStateClass(),
    className
  ].filter(Boolean).join(' ');

  const inputWrapperClass = icon ? 'input-with-icon' : '';

  const renderInput = () => {
    const baseInput = (
      <input
        type={getInputType()}
        className={inputClasses}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        {...props}
      />
    );

    if (icon || type === 'password') {
      return (
        <div className={`${inputWrapperClass} passwordClass`}>
          {icon && <span className="input-icon">{icon}</span>}
          {baseInput}
          {type === 'password' && (
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              tabIndex={-1}
            >
              {showPassword ? <Eye/> : <EyeOff />}
            </button>
          )}
        </div>
      );
    }

    return baseInput;
  };

  const renderWithGroup = () => {
    if (prepend || append) {
      return (
        <div className="input-group">
          {prepend && <div className="input-group-prepend">{prepend}</div>}
          {renderInput()}
          {append && <div className="input-group-append">{append}</div>}
        </div>
      );
    }
    return renderInput();
  };

  if (!label && !helperText) {
    return renderWithGroup();
  }

  return (
    <div className="form-group" style={{ width: fullWidth ? '100%' : 'auto' }}>
      {label && (
        <label className={`form-label ${required ? 'form-label--required' : ''}`}>
          {label}
        </label>
      )}
      {renderWithGroup()}
      {helperText && (
        <span className={`form-helper ${getHelperClass()}`}>
          {helperText}
        </span>
      )}
    </div>
  );
};

export default Input;