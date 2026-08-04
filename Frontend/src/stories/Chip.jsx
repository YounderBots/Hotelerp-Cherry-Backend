// Chip.jsx
import React from 'react';
import { X } from 'lucide-react';
import './Chip.css';

export const Chip = ({ label, onRemove, className = '' }) => (
  <span className={['chip', className].filter(Boolean).join(' ')}>
    {label}
    {onRemove && (
      <button type="button" className="chip__remove" onClick={onRemove} aria-label={`Remove ${label}`}>
        <X size={12} aria-hidden="true" />
      </button>
    )}
  </span>
);

export const ChipGroup = ({ items = [], onRemove, className = '' }) => {
  if (items.length === 0) return null;
  return (
    <div className={['chip-list', className].filter(Boolean).join(' ')}>
      {items.map((item, index) => {
        const label = typeof item === 'string' ? item : item.label;
        const key = typeof item === 'string' ? item : item.key ?? item.label ?? index;
        return <Chip key={key} label={label} onRemove={onRemove ? () => onRemove(item, index) : undefined} />;
      })}
    </div>
  );
};

export default Chip;
