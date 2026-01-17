// IconButton.jsx
import React from 'react';
import './IconButton.css';

const IconButton = ({
  variant = 'ghost',
  size = 'medium',
  icon,
  onClick,
  disabled = false,
  loading = false,
  type = 'button',
  badge,
  badgeColor,
  ariaLabel,
  className = '',
  children,
  ...props
}) => {
  const buttonClasses = [
    'icon-btn',
    `icon-btn--${variant}`,
    `icon-btn--${size}`,
    loading && 'icon-btn--loading',
    badge && 'icon-btn--with-badge',
    className
  ]
    .filter(Boolean)
    .join(' ');

  // Render icon - can be string (emoji), React component, or SVG
  const renderIcon = () => {
    if (typeof icon === 'string') {
      return <span className="icon-btn__icon">{icon}</span>;
    }
    return React.cloneElement(icon, { className: 'icon-btn__icon' });
  };

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      {...props}
    >
      {renderIcon()}
      {children}
      {badge && (
        <span 
          className="icon-btn__badge" 
          style={badgeColor ? { backgroundColor: badgeColor } : {}}
        >
          {badge}
        </span>
      )}
    </button>
  );
};

// Convenience component for common icon buttons
export const IconButtonGroup = ({ children, direction = 'horizontal', gap = 'sm' }) => {
  const gapClass = `gap-${gap}`;
  return (
    <div className={`icon-btn-group icon-btn-group--${direction} ${gapClass}`}>
      {children}
    </div>
  );
};

export default IconButton;