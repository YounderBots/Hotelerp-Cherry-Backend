// Form.jsx
import React, { useState } from 'react';
import './Form.css';
import Button from '../Button';

const Form = ({
  title,
  subtitle,
  children,
  onSubmit,
  submitLabel = 'Submit',
  cancelLabel = 'Cancel',
  onCancel,
  loading = false,
  disabled = false,
  className = '',
  ...props
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formClasses = [
    'form',
    loading && 'form--loading',
    disabled && 'form--disabled',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-container">
      <form className={formClasses} onSubmit={handleSubmit} {...props}>
        {(title || subtitle) && (
          <div className="form-header">
            {title && <h2 className="form-title">{title}</h2>}
            {subtitle && <p className="form-subtitle">{subtitle}</p>}
          </div>
        )}
        
        <div className="form-body">
          {children}
        </div>
        
        <div className="form-actions">
          {onCancel && (
            <Button
              type="button"
              variant="ghost"
              onClick={onCancel}
              disabled={disabled || isSubmitting}
            >
              {cancelLabel}
            </Button>
          )}
          <Button
            type="submit"
            variant="primary"
            loading={isSubmitting || loading}
            disabled={disabled}
          >
            {submitLabel}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default Form;