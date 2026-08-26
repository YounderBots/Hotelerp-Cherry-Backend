// DetailList.jsx
//
// Read-only presentation for View modals. Every View modal in the app used to
// render its data as a grid of `<Input disabled>` — controls the user could
// tab into, with a dashed "you can't edit this" border, which read as a form
// that had been switched off rather than as a record.
//
// DetailList renders the same data as label/value pairs: no form controls, no
// tab stops, values selectable for copy/paste, and long values wrap instead of
// being clipped by an input's single line.
import React from 'react';
import './DetailList.css';

/** A labelled value. `span` widens an item across the grid for long text. */
export const DetailItem = ({ label, value, span = 1, children }) => {
  const content = children ?? value;
  const isEmpty =
    content === null ||
    content === undefined ||
    content === '' ||
    (typeof content === 'number' && Number.isNaN(content));

  return (
    <div
      className={`detail-item${span > 1 ? ' detail-item--wide' : ''}`}
      style={span > 1 ? { gridColumn: `span ${span}` } : undefined}
    >
      <dt className="detail-item__label">{label}</dt>
      <dd className={`detail-item__value${isEmpty ? ' detail-item__value--empty' : ''}`}>
        {isEmpty ? '—' : content}
      </dd>
    </div>
  );
};

/**
 * Grid of DetailItems. `columns` is a maximum, not a fixed count — the grid
 * auto-fits, so the same list is 3-up in a large modal, 2-up in a medium one
 * and 1-up on a phone without any per-screen breakpoint work.
 */
const DetailList = ({ columns = 2, children, className = '' }) => (
  <dl
    className={['detail-list', `detail-list--${columns}`, className]
      .filter(Boolean)
      .join(' ')}
  >
    {children}
  </dl>
);

export default DetailList;
