// Textarea.jsx
import React, { useRef, useEffect } from 'react';
import './Textarea.css';

const Textarea = ({
  // Core props
  value = '',
  onChange,
  placeholder = '',
  disabled = false,
  readOnly = false,
  required = false,
  
  // Variants
  variant = 'default',
  size = 'medium',
  resize = 'vertical',
  
  // Layout
  fullWidth = true,
  autoExpand = false,
  floatingLabel = false,
  
  // Validation
  error = false,
  warning = false,
  success = false,
  maxLength,
  
  // Icons
  icon,
  
  // Labels
  label,
  helperText,
  showCharCount = false,
  
  // CSS
  className = '',
  style,
  
  ...props
}) => {
  const textareaRef = useRef(null);
  
  // Auto-expand functionality
  useEffect(() => {
    if (autoExpand && textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [value, autoExpand]);
  
  const handleChange = (e) => {
    if (onChange) {
      onChange(e);
    }
    
    // Auto-expand on change
    if (autoExpand && textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };
  
  // Character count status
  const getCharCountStatus = () => {
    if (!maxLength) return null;
    
    const currentLength = value?.length || 0;
    const percentage = (currentLength / maxLength) * 100;
    
    if (percentage >= 100) return 'error';
    if (percentage >= 90) return 'warning';
    return null;
  };
  
  const charCountStatus = getCharCountStatus();
  const currentLength = value?.length || 0;
  
  // Base textarea classes
  const textareaClasses = [
    'textarea',
    `textarea--${size}`,
    `textarea--${variant}`,
    `textarea--resize-${resize}`,
    autoExpand && 'textarea--auto-expand',
    error && 'textarea--error',
    warning && 'textarea--warning',
    success && 'textarea--success',
    disabled && 'textarea--disabled',
    readOnly && 'textarea--read-only',
    className
  ].filter(Boolean).join(' ');
  
  // Wrapper classes for icon and floating label
  const wrapperClasses = [
    'textarea-wrapper',
    icon && 'textarea-wrapper--with-icon',
    floatingLabel && 'textarea-wrapper--floating',
    `textarea-wrapper--${size}`,
    error && 'textarea-wrapper--error',
    fullWidth && 'textarea-wrapper--full-width'
  ].filter(Boolean).join(' ');
  
  // Render the textarea with appropriate wrapper
  const renderTextarea = () => (
    <div className={wrapperClasses} style={style}>
      {icon && (
        <span className="textarea__icon">
          {typeof icon === 'string' ? icon : icon}
        </span>
      )}
      
      <textarea
        ref={textareaRef}
        className={textareaClasses}
        value={value}
        onChange={handleChange}
        placeholder={floatingLabel ? ' ' : placeholder} // Space for floating label
        disabled={disabled}
        readOnly={readOnly}
        required={required}
        maxLength={maxLength}
        {...props}
      />
      
      {floatingLabel && label && (
        <label className={`textarea-label ${required ? 'textarea-label--required' : ''}`}>
          {label}
        </label>
      )}
    </div>
  );
  
  return (
    <div className="textarea-container" style={{ width: fullWidth ? '100%' : 'auto' }}>
      {/* Standard Label */}
      {label && !floatingLabel && (
        <label className={`textarea-label ${required ? 'textarea-label--required' : ''}`}>
          {label}
        </label>
      )}
      
      {/* Textarea */}
      {renderTextarea()}
      
      {/* Helper Text and Character Count */}
      {(helperText || showCharCount) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'var(--spacing-xs)' }}>
          {helperText && (
            <span className={`textarea-helper ${
              error ? 'textarea-helper--error' : 
              warning ? 'textarea-helper--warning' : 
              success ? 'textarea-helper--success' : ''
            }`}>
              {helperText}
            </span>
          )}
          
          {showCharCount && maxLength && (
            <span className={`textarea__count ${
              charCountStatus === 'warning' ? 'textarea__count--warning' :
              charCountStatus === 'error' ? 'textarea__count--error' : ''
            }`}>
              {currentLength} / {maxLength}
            </span>
          )}
        </div>
      )}
      
      {/* Character Count Only */}
      {showCharCount && !helperText && maxLength && (
        <span className={`textarea__count ${
          charCountStatus === 'warning' ? 'textarea__count--warning' :
          charCountStatus === 'error' ? 'textarea__count--error' : ''
        }`}>
          {currentLength} / {maxLength}
        </span>
      )}
    </div>
  );
};

export default Textarea;