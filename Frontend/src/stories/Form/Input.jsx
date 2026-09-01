// Input.jsx
import React, { useId, useState } from 'react';
// Shared field metrics first, input-specific chrome second, so Input.css can
// build on the tokens FormField.css defines.
import './FormField.css';
import './Input.css';
// EyeClosed / EyeClosedIcon and react-icons' RxEyeOpen were imported and never
// used — the react-icons one pulled a second icon library into the bundle for
// a button that renders lucide's Eye/EyeOff.
import { Eye, EyeOff } from 'lucide-react';

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

  // WHY THIS COMPONENT GENERATES AN ID
  //
  // The label was rendered as a bare <label> with no `htmlFor`, and the input
  // as its SIBLING rather than nested inside it -- so nothing connected the
  // two. Every Input in the product therefore had a visible label and no
  // accessible one: a screen reader announced "edit text, blank", and clicking
  // the label did not focus the field. Select next to it did this correctly,
  // which is why the two behaved differently in the same form.
  //
  // A caller-supplied `id` still wins, so an existing `htmlFor` or a test
  // selecting by id keeps working.
  const generatedId = useId();
  const inputId = props.id || `input-${generatedId}`;

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
        id={inputId}
        type={getInputType()}
        className={inputClasses}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        aria-describedby={helperText ? `${inputId}-helper` : undefined}
        aria-invalid={error || undefined}
        aria-required={required || undefined}
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
        <label
          htmlFor={inputId}
          className={`form-label ${required ? 'form-label--required' : ''}`}
        >
          {label}
        </label>
      )}
      {renderWithGroup()}
      {helperText && (
        <span id={`${inputId}-helper`} className={`form-helper ${getHelperClass()}`}>
          {helperText}
        </span>
      )}
    </div>
  );
};

export default Input;