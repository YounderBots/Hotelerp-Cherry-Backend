
import React, { useEffect, useState } from 'react';
import './Card.css';

const COLOR_MAP = {
    primary: 'var(--primary-color)',
    success: 'var(--success-color)',
    warning: 'var(--warning-color)',
    error: 'var(--error-color)',
    info: 'var(--info-color)',
    white: 'var(--white)',
    muted: 'var(--bg-secondary)',
};

function resolveColor(input) {
    if (!input) return undefined;
    if (typeof input !== 'string') return undefined;
    const trimmed = input.trim();
    // if it looks like a css var, hex or rgb, return as is
    if (/^(var\(|#|rgba?\(|hsla?\(|[a-zA-Z]+)/.test(trimmed)) {
        // a named token (like 'primary') will be handled below
        // try to map named tokens
        const lower = trimmed.toLowerCase();
        if (COLOR_MAP[lower]) return COLOR_MAP[lower];
        // otherwise return the raw input (supports 'red', '#fff', 'var(--my-color)')
        return trimmed;
    }
    return trimmed;
}

function renderIcon(icon) {
    if (!icon) return null;
    if (React.isValidElement(icon)) return icon;
    if (typeof icon === 'function') {
        const IconComp = icon;
        return <IconComp />;
    }
    // fallback: if string, you might map it in stories, but default return null
    return null;
}


/**
 * Props:
 *  - bgColor: string  (e.g. 'var(--primary-color)' - Refer index.css for color)
 *  - textColor: string (optional override for text, e.g. 'var(--primary-color)')
 *  - icon: React element OR React component  (e.g. <FaUser/> or FaUser)
 *  - label: string
 *  - value: string | number
 *  - fluid: boolean (if true, card gets class card--fluid -> width:100%)
 *  - className, style, ...rest
 *
 */

export default function Card({
    bgColor = 'var(--bg-primary)',
    textColor = 'var(--primary-color)',
    icon,
    iconBg='',
    width='',
    value,
    label,
    labelColor = textColor,
    fluid = false,
    className = '',
    style = {},
    ...rest
}) {

    // 🔹 Count-up animation logic
    const [displayValue, setDisplayValue] = useState(
        typeof value === 'number' ? 0 : value
    );


    useEffect(() => {
        if (typeof value === 'number') {
            let startTimestamp = null;
            const duration = 500; // total animation time in ms

            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);

                // 🔥 easing (easeOutQuad)
                const easedProgress = 1 - (1 - progress) * (1 - progress);

                const currentValue = Math.floor(easedProgress * value);
                setDisplayValue(currentValue);

                if (progress < 1) {
                    requestAnimationFrame(step);
                }
            };

            requestAnimationFrame(step);
        } else {
            setDisplayValue(value); // fallback for string values
        }
    }, [value]);




    const resolvedBg = resolveColor(bgColor);
    const cssVars = {
        ...(resolvedBg ? { '--card-bg': resolvedBg } : {}),
        ...(textColor ? { '--card-text': textColor } : {}),
        ...style,
        width
    };

    return (
        <>
            <div
                className={`card shine-overlay ${fluid ? 'card--fluid' : ''} ${className}`}
                style={cssVars}
                role="group"
                aria-label={label || 'dashboard card'}
                {...rest}
            >
                {icon ? <div className="card__icon" style={{ ...(iconBg ? { '--card-iconBg': iconBg } : {})}} aria-hidden>{renderIcon(icon)}</div> : null}
                <div className="card__content">
                    <div className="card__value">{displayValue}</div>
                    {label ? <div className="card__label">{label}</div> : null}
                </div>
                <div className="shine"></div>
            </div>
        </>
    );
}
