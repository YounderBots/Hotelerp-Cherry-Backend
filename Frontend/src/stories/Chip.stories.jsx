// Chip.stories.jsx
import React from 'react';
import { Chip, ChipGroup } from './Chip';

export default {
  title: 'Components/Chip',
  component: Chip,
};

export const Single = () => <Chip label="Vegetarian" />;

export const Removable = () => <Chip label="Vegetarian" onRemove={() => {}} />;

export const Group = () => (
  <ChipGroup items={['Veg', 'Non-Veg', 'Contains Nuts']} onRemove={() => {}} />
);
