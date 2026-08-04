// RepeatableRowEditor.jsx
// Config-driven editor for a list of small multi-field rows with add/remove
// (menu variants / modifiers / combo items).
import React from 'react';
import { X } from 'lucide-react';
import './RepeatableRowEditor.css';

const RepeatableRowEditor = ({
  rows = [],
  fields,
  onFieldChange,
  onAdd,
  onRemove,
  renderRowExtra,
  addLabel = '+ Add Row',
  emptyLabel = 'No rows added yet.',
  rowKey,
}) => {
  const rowStyle = { gridTemplateColumns: `repeat(${fields.length}, minmax(0, 1fr)) auto` };

  return (
    <div className="repeatable-editor">
      {rows.length === 0 && <span className="repeatable-empty">{emptyLabel}</span>}

      {rows.map((row, index) => (
        <div className="repeatable-row" style={rowStyle} key={rowKey ? rowKey(row, index) : index}>
          {fields.map((field) => {
            const value = row[field.key] ?? '';
            const handleChange = (e) => onFieldChange(index, field.key, e.target.value, row);

            if (field.type === 'select') {
              return (
                <select key={field.key} value={value} onChange={handleChange}>
                  <option value="">{field.placeholder}</option>
                  {(field.options || []).map((opt) => (
                    <option key={opt.value ?? opt} value={opt.value ?? opt}>
                      {opt.label ?? opt}
                    </option>
                  ))}
                </select>
              );
            }

            return (
              <input
                key={field.key}
                type={field.type === 'number' ? 'number' : 'text'}
                placeholder={field.placeholder}
                value={value}
                list={field.listId}
                onChange={handleChange}
              />
            );
          })}

          <div className="repeatable-row__actions">
            {renderRowExtra && renderRowExtra(row, index)}
            {onRemove && (
              <button type="button" className="repeatable-row-remove" onClick={() => onRemove(index, row)}>
                <X size={14} aria-hidden="true" />
              </button>
            )}
          </div>
        </div>
      ))}

      {onAdd && (
        <button type="button" className="repeatable-add-btn" onClick={onAdd}>
          {addLabel}
        </button>
      )}
    </div>
  );
};

export default RepeatableRowEditor;
