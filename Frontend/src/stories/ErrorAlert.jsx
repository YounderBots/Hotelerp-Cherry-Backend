// ErrorAlert.jsx
import React from 'react';
import { AlertTriangle } from 'lucide-react';
import './ErrorAlert.css';

const ErrorAlert = ({ message, className = '' }) => {
  if (!message) return null;
  return (
    <div className={['error-alert', className].filter(Boolean).join(' ')} role="alert">
      <AlertTriangle size={16} aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
};

export default ErrorAlert;
