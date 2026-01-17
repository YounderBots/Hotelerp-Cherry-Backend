// Button.jsx
import React from 'react';
import './Button.css';

const Button = ({
  variant = 'primary',
  size = 'medium',
  children,
  onClick,
  disabled = false,
  loading = false,
  type = 'button',
  fullWidth = false,
  iconOnly = false,
  className = '',
  ...props
}) => {
  const buttonClasses = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    loading && 'btn--loading',
    fullWidth && 'btn--full-width',
    iconOnly && 'btn--icon-only',
    className
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;