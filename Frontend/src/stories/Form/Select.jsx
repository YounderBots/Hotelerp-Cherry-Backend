import React, { useId, useMemo } from 'react';
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
    const generatedId = useId();
    const selectId = id || `select-${generatedId}`;

    /** Normalize options */
    const normalizedOptions = useMemo(() => {
        return options.map(opt =>
            typeof opt === 'object'
                ? { value: opt.value, label: opt.label, disabled: opt.disabled }
                : { value: opt, label: opt }
        );
    }, [options]);

    /** MULTI SELECT DERIVED STATE
     *  `selectedLabels` used to be derived alongside this and never read —
     *  react-select renders its own chips from `value`. */
    const reactSelectValue = useMemo(() => {
        if (!multiple || !Array.isArray(value)) return [];
        return normalizedOptions.filter(opt => value.includes(opt.value));
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
