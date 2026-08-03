// Toast.jsx
import React from 'react';
import { CheckCircle, Pencil, Trash2, AlertTriangle } from 'lucide-react';
import './Toast.css';

const ICONS = {
  success: CheckCircle,
  update: Pencil,
  delete: Trash2,
  error: AlertTriangle,
};

const Toast = ({ show, message, type = 'success', exiting = false, className = '' }) => {
  if (!show) return null;

  const Icon = ICONS[type] || CheckCircle;
  const toastClasses = ['toast', `toast--${type}`, exiting && 'toast--exit', className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={toastClasses} role="status" aria-live="polite">
      <span className="toast__icon">
        <Icon size={18} aria-hidden="true" />
      </span>
      <span className="toast__message">{message}</span>
    </div>
  );
};

export default Toast;
