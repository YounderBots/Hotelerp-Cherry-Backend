// RowActions.jsx
//
// THE single action-control set for table rows. Every View / Edit / Delete
// affordance in the app renders through this component so the icon, its size,
// the chip background, colour, radius, hover state, tooltip and the spacing
// between buttons are identical on every screen.
//
// Before this existed each screen hand-rolled three <IconButton>s with a
// different variant each (ghost / subtle / danger-ghost), so View and Delete
// were flat while Edit carried a grey box — the same three actions read as
// three unrelated controls. Reach for this instead of composing IconButtons
// by hand; add a new action here rather than inventing one per screen.
import React from 'react';
import { Eye, Pencil, Trash2 } from 'lucide-react';
import IconButton from './IconButton';
import './RowActions.css';

// One icon, one size, one label per action — imported by name so a screen
// cannot accidentally pick a different glyph for the same verb.
export const ACTION_ICON_SIZE = 16;

const RowActions = ({
  onView,
  onEdit,
  onDelete,
  // Per-row overrides for the rare screen where one action is conditional.
  canView = true,
  canEdit = true,
  canDelete = true,
  // Names the thing being acted on, so tooltips and screen-reader labels read
  // "Edit room type" rather than a bare "Edit" repeated down the column.
  label = '',
  children,
  className = '',
}) => {
  const suffix = label ? ` ${label}` : '';

  return (
    <div className={['row-actions', className].filter(Boolean).join(' ')}>
      {onView && canView && (
        <IconButton
          variant="action-view"
          size="action"
          icon={<Eye size={ACTION_ICON_SIZE} />}
          onClick={onView}
          title={`View${suffix}`}
          ariaLabel={`View${suffix}`}
        />
      )}
      {onEdit && canEdit && (
        <IconButton
          variant="action-edit"
          size="action"
          icon={<Pencil size={ACTION_ICON_SIZE} />}
          onClick={onEdit}
          title={`Edit${suffix}`}
          ariaLabel={`Edit${suffix}`}
        />
      )}
      {onDelete && canDelete && (
        <IconButton
          variant="action-delete"
          size="action"
          icon={<Trash2 size={ACTION_ICON_SIZE} />}
          onClick={onDelete}
          title={`Delete${suffix}`}
          ariaLabel={`Delete${suffix}`}
        />
      )}
      {children}
    </div>
  );
};

export default RowActions;
