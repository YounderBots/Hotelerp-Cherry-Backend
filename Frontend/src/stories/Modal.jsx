// Modal.jsx - Enhanced with better UX
import React, { useEffect, useRef, useState, useCallback } from 'react';
import Button from './Button'
import PropTypes from 'prop-types';
import './Modal.css';

const Modal = ({
  // Core props
  isOpen = false,
  onClose,
  onConfirm,

  // Content
  title,
  children,
  icon,

  // Variants
  variant = 'default',
  size = 'medium',
  type = 'modal',

  // Header
  showHeader = true,
  showCloseButton = true,
  headerBorder = true,

  // Footer
  showFooter = false,
  footerAlign = 'right',
  footerBorder = true,
  actions = [],

  // Body
  bodyPadding = true,
  compact = false,
  showGradients = true,

  // Behavior
  closeOnBackdropClick = true,
  closeOnEscape = true,
  preventScroll = true,
  autoFocus = true,

  // Accessibility
  ariaLabel,
  ariaDescribedBy,
  role = 'dialog',

  // CSS
  className = '',
  overlayClassName = '',
  style = {},

  ...props
}) => {
  const modalRef = useRef(null);
  const backdropRef = useRef(null);
  const previousActiveElement = useRef(null);
  const [isExiting, setIsExiting] = useState(false);
  const [isActive, setIsActive] = useState(false);

  // Handle entrance animation
  useEffect(() => {
    if (isOpen && !isExiting) {
      requestAnimationFrame(() => {
        setIsActive(true);
      });
    } else {
      setIsActive(false);
    }
  }, [isOpen, isExiting]);

  // Handle escape key with debounce
  const handleEscape = useCallback((e) => {
    if (e.key === 'Escape' && closeOnEscape && onClose && !isExiting) {
      e.preventDefault();
      handleClose();
    }
  }, [closeOnEscape, onClose, isExiting]);

  useEffect(() => {
    if (isOpen && closeOnEscape) {
      document.addEventListener('keydown', handleEscape, { passive: false });
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, closeOnEscape, handleEscape]);

  // Handle body scroll prevention with iOS support
  useEffect(() => {
    if (isOpen && preventScroll) {
      const scrollY = window.scrollY;
      const originalOverflow = document.body.style.overflow;
      const originalPosition = document.body.style.position;
      const originalWidth = document.body.style.width;
      const originalTop = document.body.style.top;

      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.width = '100%';
      document.body.style.top = `-${scrollY}px`;

      return () => {
        document.body.style.overflow = originalOverflow;
        document.body.style.position = originalPosition;
        document.body.style.width = originalWidth;
        document.body.style.top = originalTop;
        window.scrollTo(0, scrollY);
      };
    }
  }, [isOpen, preventScroll]);

  // Focus management with improved trap
  useEffect(() => {
    if (isOpen && !isExiting) {
      previousActiveElement.current = document.activeElement;

      if (autoFocus) {
        const timer = setTimeout(() => {
          const focusableElements = modalRef.current?.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );

          if (focusableElements && focusableElements.length > 0) {
            focusableElements[0]?.focus();
          } else {
            modalRef.current?.focus();
          }
        }, 100);

        return () => clearTimeout(timer);
      }
    } else if (!isOpen && previousActiveElement.current) {
      previousActiveElement.current?.focus();
    }
  }, [isOpen, isExiting, autoFocus]);

  // Handle close with smooth animation
  const handleClose = useCallback(() => {
    if (!onClose || isExiting) return;

    setIsExiting(true);
    setIsActive(false);

    // Match animation duration
    setTimeout(() => {
      setIsExiting(false);
      onClose();
    }, 200);
  }, [onClose, isExiting]);

  const handleConfirm = useCallback(() => {
    if (onConfirm) {
      onConfirm();
    } else {
      handleClose();
    }
  }, [onConfirm, handleClose]);

  const handleBackdropClick = useCallback((e) => {
    if (
      backdropRef.current &&
      e.target === backdropRef.current &&
      closeOnBackdropClick &&
      !isExiting
    ) {
      handleClose();
    }
  }, [closeOnBackdropClick, isExiting, handleClose]);

  // Handle click outside for drawer and sheet
  const handleClickOutside = useCallback((e) => {
    if (
      modalRef.current &&
      !modalRef.current.contains(e.target) &&
      closeOnBackdropClick &&
      !isExiting
    ) {
      handleClose();
    }
  }, [closeOnBackdropClick, isExiting, handleClose]);

  useEffect(() => {
    if (isOpen && (type === 'drawer' || type === 'sheet')) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, type, handleClickOutside]);

  if (!isOpen && !isExiting) return null;

  // Build CSS classes
  const backdropClasses = [
    'modal-backdrop',
    isActive && 'modal-backdrop--active',
    isExiting && 'modal-backdrop--exiting',
    overlayClassName
  ].filter(Boolean).join(' ');

  const modalClasses = [
    'modal',
    `modal--${size}`,
    variant !== 'default' && `modal--${variant}`,
    type !== 'modal' && `modal--${type}`,
    isActive && 'modal--active',
    isExiting && 'modal--exiting',
    className
  ].filter(Boolean).join(' ');

  const headerClasses = [
    'modal__header',
    !headerBorder && 'modal__header--no-border'
  ].filter(Boolean).join(' ');

  const bodyClasses = [
    'modal__body',
    !bodyPadding && 'modal__body--no-padding',
    compact && 'modal__body--compact'
  ].filter(Boolean).join(' ');

  const footerClasses = [
    'modal__footer',
    `modal__footer--${footerAlign}`,
    !footerBorder && 'modal__footer--no-border'
  ].filter(Boolean).join(' ');

  // Render icon with enhanced styling
  const renderIcon = () => {
    if (!icon) return null;

    if (typeof icon === 'string') {
      return (
        <div className={`modal__icon modal__icon--${variant}`} aria-hidden="true">
          {icon}
        </div>
      );
    }

    return React.cloneElement(icon, {
      className: `modal__icon modal__icon--${variant} ${icon.props.className || ''}`,
      'aria-hidden': 'true'
    });
  };

  // Generate default actions if none provided but footer is shown
  const getActions = () => {
    if (actions.length > 0) return actions;
    if (!showFooter) return [];

    return [
      {
        label: 'Cancel',
        variant: 'ghost',
        onClick: handleClose,
        type: 'button'
      },
      {
        label: 'Confirm',
        variant: 'primary',
        onClick: handleConfirm,
        type: 'button',
        autoFocus: true
      }
    ];
  };

  const modalActions = getActions();

  return (
    <div
      ref={backdropRef}
      className={backdropClasses}
      onClick={handleBackdropClick}
      role="presentation"
      aria-hidden={!isOpen}
      data-testid="modal-backdrop"
    >
      <div
        ref={modalRef}
        className={modalClasses}
        role={role}
        aria-modal="true"
        aria-label={ariaLabel || title}
        aria-describedby={ariaDescribedBy}
        tabIndex={-1}
        style={style}
        data-testid="modal"
        {...props}
      >
     

        {/* Header */}
        {showHeader && (
          <header className={headerClasses}>
            <h2 className="modal__title" id="modal-title">
              {title}
            </h2>
            {showCloseButton && (
              <button
                className="modal__close"
                onClick={handleClose}
                aria-label="Close modal"
                type="button"
                disabled={isExiting}
                data-testid="modal-close"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            )}
          </header>
        )}

        {/* Body */}
        <main className={bodyClasses} id={ariaDescribedBy || 'modal-body'}>
          {renderIcon()}
          {children}
        </main>

        {/* Footer */}
        {showFooter && modalActions.length > 0 && (
          <footer className={footerClasses}>
            <div className="modal-actions">
              {modalActions.map((action, index) => (
                <Button
                  variant="primary"
                  onClick={action.onClick}
                  disabled={action.disabled || isExiting}
                  autoFocus={action.autoFocus}
                  type={action.type || 'button'}
                  aria-label={action.ariaLabel}
                  data-testid={`modal-action-${index}`}
                >
                  {action.icon && <span className="btn__icon">{action.icon}</span>} {action.label} 
                </Button>
                // <button
                //                 key={action.key || index}
                //                 className={`btn btn--${action.variant || 'primary'} ${action.size ? `btn--${action.size}` : ''}`}
                //                 onClick={action.onClick}
                //                 disabled={action.disabled || isExiting}
                //                 autoFocus={action.autoFocus}
                //                 type={action.type || 'button'}
                //                 aria-label={action.ariaLabel}
                //                 data-testid={`modal-action-${index}`}
                //               >
                //                 {action.icon && <span className="btn__icon">{action.icon}</span>}
                //                 {action.label} 
                //               </button>


              ))}
            </div>
          </footer>
        )}
      </div>
    </div>
  );
};

Modal.propTypes = {
  // Core props
  isOpen: PropTypes.bool,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func,

  // Content
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  icon: PropTypes.oneOfType([PropTypes.string, PropTypes.element]),

  // Variants
  variant: PropTypes.oneOf([
    'default', 'elevated', 'bordered', 'subtle',
    'alert', 'success', 'warning', 'info'
  ]),
  size: PropTypes.oneOf(['small', 'medium', 'large', 'xlarge', 'fullscreen']),
  type: PropTypes.oneOf(['modal', 'dialog', 'sheet', 'drawer']),

  // Header
  showHeader: PropTypes.bool,
  showCloseButton: PropTypes.bool,
  headerBorder: PropTypes.bool,

  // Footer
  showFooter: PropTypes.bool,
  footerAlign: PropTypes.oneOf(['left', 'center', 'right', 'space-between']),
  footerBorder: PropTypes.bool,
  actions: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
    variant: PropTypes.string,
    size: PropTypes.string,
    disabled: PropTypes.bool,
    autoFocus: PropTypes.bool,
    icon: PropTypes.element,
    key: PropTypes.string,
    ariaLabel: PropTypes.string
  })),

  // Body
  bodyPadding: PropTypes.bool,
  compact: PropTypes.bool,
  showGradients: PropTypes.bool,

  // Behavior
  closeOnBackdropClick: PropTypes.bool,
  closeOnEscape: PropTypes.bool,
  preventScroll: PropTypes.bool,
  autoFocus: PropTypes.bool,

  // Accessibility
  ariaLabel: PropTypes.string,
  ariaDescribedBy: PropTypes.string,
  role: PropTypes.string,

  // CSS
  className: PropTypes.string,
  overlayClassName: PropTypes.string,
  style: PropTypes.object
};

// Enhanced specialized modal components
export const AlertModal = ({
  type = 'info',
  confirmText = 'OK',
  confirmVariant,
  onConfirm,
  showCloseButton = false,
  icon,
  ...props
}) => {
  const defaultIcons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️'
  };

  return (
    <Modal
      {...props}
      variant={type}
      showFooter={true}
      showCloseButton={showCloseButton}
      icon={icon || defaultIcons[type]}
      actions={[
        {
          label: confirmText,
          variant: confirmVariant || (type === 'error' ? 'danger' : 'primary'),
          onClick: onConfirm || props.onClose,
          autoFocus: true
        }
      ]}
    />
  );
};

AlertModal.propTypes = {
  type: PropTypes.oneOf(['success', 'warning', 'error', 'info']),
  confirmText: PropTypes.string,
  confirmVariant: PropTypes.string,
  onConfirm: PropTypes.func,
  showCloseButton: PropTypes.bool,
  icon: PropTypes.oneOfType([PropTypes.string, PropTypes.element])
};

export const ConfirmModal = ({
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'primary',
  cancelVariant = 'ghost',
  onConfirm,
  destructive = false,
  ...props
}) => (
  <Modal
    {...props}
    showFooter={true}
    variant={destructive ? 'alert' : props.variant}
    actions={[
      {
        label: cancelText,
        variant: cancelVariant,
        onClick: props.onClose
      },
      {
        label: confirmText,
        variant: destructive ? 'danger' : confirmVariant,
        onClick: onConfirm,
        autoFocus: true
      }
    ]}
  />
);

ConfirmModal.propTypes = {
  confirmText: PropTypes.string,
  cancelText: PropTypes.string,
  confirmVariant: PropTypes.string,
  cancelVariant: PropTypes.string,
  onConfirm: PropTypes.func.isRequired,
  destructive: PropTypes.bool
};

export const DialogModal = ({
  showCloseButton = false,
  variant = 'dialog',
  ...props
}) => (
  <Modal
    {...props}
    type="dialog"
    variant={variant}
    showCloseButton={showCloseButton}
    headerBorder={false}
  />
);

export const SheetModal = ({
  closeOnBackdropClick = true,
  size = 'medium',
  showGradients = false,
  ...props
}) => (
  <Modal
    {...props}
    type="sheet"
    size={size}
    showGradients={showGradients}
    closeOnBackdropClick={closeOnBackdropClick}
  />
);

export const DrawerModal = ({
  closeOnBackdropClick = true,
  size = 'medium',
  showGradients = false,
  ...props
}) => (
  <Modal
    {...props}
    type="drawer"
    size={size}
    showGradients={showGradients}
    closeOnBackdropClick={closeOnBackdropClick}
  />
);

// Additional utility components
export const LoadingModal = ({
  title = 'Loading...',
  message = 'Please wait while we process your request.',
  showSpinner = true,
  ...props
}) => (
  <Modal
    {...props}
    title={title}
    showCloseButton={false}
    showFooter={false}
    closeOnBackdropClick={false}
    closeOnEscape={false}
  >
    <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>
      {showSpinner && (
        <div
          style={{
            width: '48px',
            height: '48px',
            border: '3px solid var(--border-light)',
            borderTopColor: 'var(--primary-color)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto var(--spacing-lg)'
          }}
          aria-hidden="true"
        />
      )}
      <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{message}</p>
    </div>
  </Modal>
);

LoadingModal.propTypes = {
  title: PropTypes.string,
  message: PropTypes.string,
  showSpinner: PropTypes.bool
};

export default Modal;