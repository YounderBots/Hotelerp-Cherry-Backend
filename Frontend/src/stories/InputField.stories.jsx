// InputField.stories.jsx
import React, { useState } from 'react';
import InputField from './InputField';

export default {
  title: 'Components/InputField',
  component: InputField,
  argTypes: {
    size: { control: { type: 'select' }, options: ['small', 'medium', 'large', 'full', 'custom'] },
    customWidth: { control: 'text' },
    placeholder: { control: 'text' },
    disabled: { control: 'boolean' },
  },
};

const ControlledTemplate = (args) => {
  // Parent manages the search data manually (controlled)
  const [query, setQuery] = useState('');
  const handleChange = (e) => setQuery(e.target.value);
  const handleClear = () => setQuery('');

  return (
 
      <InputField
        {...args}
        value={query} 
      />
      
    
  );
};

// Stories showing percent-based presets
export const Small = ControlledTemplate.bind({});
Small.args = { size: 'small', placeholder: 'Search (25%)' };

export const Medium = ControlledTemplate.bind({});
Medium.args = { size: 'medium', placeholder: 'Search (50%)' };

export const Large = ControlledTemplate.bind({});
Large.args = { size: 'large', placeholder: 'Search (75%)' };

export const Full = ControlledTemplate.bind({});
Full.args = { size: 'full', placeholder: 'Search (100%)' };

// CustomWidth: show passing percentage string or pixel value
export const CustomWidthPercent = ControlledTemplate.bind({});
CustomWidthPercent.args = { size: 'custom', customWidth: '40%', placeholder: 'Custom 40%' };

export const CustomWidthPixels = ControlledTemplate.bind({});
CustomWidthPixels.args = { size: 'custom', customWidth: '420px', placeholder: 'Custom 420px' };

// Disabled example (still presentational)
export const Disabled = ControlledTemplate.bind({});
Disabled.args = { size: 'medium', placeholder: 'Disabled', disabled: true };
