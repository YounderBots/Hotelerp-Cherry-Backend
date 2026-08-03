// RepeatableRowEditor.stories.jsx
import React, { useState } from 'react';
import RepeatableRowEditor from './RepeatableRowEditor';

export default {
  title: 'Components/RepeatableRowEditor',
  component: RepeatableRowEditor,
};

export const Variants = () => {
  const [rows, setRows] = useState([{ variant_name: 'Small', price: '180' }]);
  return (
    <RepeatableRowEditor
      rows={rows}
      fields={[
        { key: 'variant_name', placeholder: 'Variant name (e.g. Large)' },
        { key: 'price', placeholder: 'Price', type: 'number' },
      ]}
      onFieldChange={(i, key, value) => setRows((r) => r.map((row, idx) => (idx === i ? { ...row, [key]: value } : row)))}
      onAdd={() => setRows((r) => [...r, { variant_name: '', price: '' }])}
      onRemove={(i) => setRows((r) => r.filter((_, idx) => idx !== i))}
      addLabel="+ Add Variant"
      emptyLabel="No variants — this item will use the single price above."
    />
  );
};

export const ModifiersWithType = () => {
  const [rows, setRows] = useState([{ modifier_name: 'Extra Cheese', price: '20', modifier_type: 'Add-on' }]);
  return (
    <RepeatableRowEditor
      rows={rows}
      fields={[
        { key: 'modifier_name', placeholder: 'Modifier name (e.g. Extra Cheese)' },
        { key: 'price', placeholder: 'Price', type: 'number' },
        { key: 'modifier_type', placeholder: 'Type', type: 'select', options: ['Add-on', 'Remove'] },
      ]}
      onFieldChange={(i, key, value) => setRows((r) => r.map((row, idx) => (idx === i ? { ...row, [key]: value } : row)))}
      onAdd={() => setRows((r) => [...r, { modifier_name: '', price: '', modifier_type: '' }])}
      onRemove={(i) => setRows((r) => r.filter((_, idx) => idx !== i))}
      addLabel="+ Add Modifier"
      emptyLabel="No modifiers for this item."
    />
  );
};
