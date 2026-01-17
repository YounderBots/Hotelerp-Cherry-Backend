import React, { useMemo } from 'react';
import ReactSelect from 'react-select';
import './Select.css';

const Select = ({
    id,
    label,
    required = false,
    size = 'medium',
    options = [],
    value,
    onChange,
    disabled = false,
    error = false,
    success = false,
    helperText,
    placeholder = 'Select an option',
    multiple = false,
    fullWidth = true,
    className = '',
    ...props
}) => {
    const selectId = id || `select-${Math.random().toString(36).slice(2, 9)}`;

    /** Normalize options */
    const normalizedOptions = useMemo(() => {
        return options.map(opt =>
            typeof opt === 'object'
                ? { value: opt.value, label: opt.label, disabled: opt.disabled }
                : { value: opt, label: opt }
        );
    }, [options]);

    /** MULTI SELECT DERIVED STATE */
    const { reactSelectValue, selectedLabels } = useMemo(() => {
        if (!multiple || !Array.isArray(value)) {
            return { reactSelectValue: [], selectedLabels: [] };
        }

        const selected = normalizedOptions.filter(opt =>
            value.includes(opt.value)
        );

        return {
            reactSelectValue: selected,
            selectedLabels: selected.map(opt => opt.label),
        };
    }, [multiple, value, normalizedOptions]);

    /** Unified change handler */
    const handleMultiChange = selected => {
        onChange?.({
            target: {
                value: Array.isArray(selected)
                    ? selected.map(s => s.value)
                    : [],
            },
        });
    };

    const stateClass = error
        ? 'select-control--error'
        : success
            ? 'select-control--success'
            : '';

    const selectClasses = [
        'select-control',
        `select-control--${size}`,
        stateClass,
        className,
    ]
        .filter(Boolean)
        .join(' ');

    const handleRemoveValue = removedValue => {
        if (!Array.isArray(value)) return;

        onChange?.({
            target: {
                value: value.filter(v => v !== removedValue),
            },
        });
    };

    /** MULTI SELECT */
    if (multiple) {
        return (
            <div className="form-group" style={{ width: fullWidth ? '100%' : 'auto' }}>
                {label && (
                    <label
                        className={`form-label ${required ? 'form-label--required' : ''}`}
                    >
                        {label}
                    </label>
                )}

                <ReactSelect
                    inputId={selectId}
                    isMulti
                    options={normalizedOptions}
                    value={reactSelectValue}
                    onChange={handleMultiChange}
                    isDisabled={disabled}
                    placeholder={placeholder}
                    classNamePrefix="react-select"
                    closeMenuOnSelect={false}
                    isClearable
                    menuPortalTarget={
                        typeof window !== 'undefined' ? document.body : null
                    }
                    menuPosition="fixed"
                    aria-invalid={error}
                    aria-required={required}
                    {...props}
                />

                {helperText && (
                    <span
                        className={`form-helper ${error ? 'form-helper--error' : success ? 'form-helper--success' : ''
                            }`}
                    >
                        {helperText}
                    </span>
                )}

               

            </div>
        );
    }

    /** SINGLE SELECT */
    return (
        <div className="form-group" style={{ width: fullWidth ? '100%' : 'auto' }}>
            {label && (
                <label
                    htmlFor={selectId}
                    className={`form-label ${required ? 'form-label--required' : ''}`}
                >
                    {label}
                </label>
            )}

            <select
                id={selectId}
                className={selectClasses}
                value={value ?? ''}
                onChange={onChange}
                disabled={disabled}
                required={required}
                aria-invalid={error}
                {...props}
            >
                {!normalizedOptions.some(
                    o => o.disabled && o.value === ''
                ) && <option value="">{placeholder}</option>}

                {normalizedOptions.map(opt => (
                    <option
                        key={opt.value}
                        value={opt.value}
                        disabled={opt.disabled}
                    >
                        {opt.label}
                    </option>
                ))}
            </select>

            {helperText && (
                <span
                    className={`form-helper ${error ? 'form-helper--error' : success ? 'form-helper--success' : ''
                        }`}
                >
                    {helperText}
                </span>
            )}
        </div>
    );
};

export default Select;
