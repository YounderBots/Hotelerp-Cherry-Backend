// Textarea.stories.jsx
import React, { useState } from 'react';
import Textarea from './Textarea';

export default {
  title: 'Components/Textarea',
  component: Textarea,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'primary', 'success', 'warning', 'error'],
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large'],
    },
    resize: {
      control: { type: 'select' },
      options: ['none', 'both', 'horizontal', 'vertical'],
    },
    onChange: { action: 'changed' },
  },
  parameters: {
    layout: 'padded',
  },
};

const Template = (args) => {
  const [value, setValue] = useState(args.value || '');
  return <Textarea {...args} value={value} onChange={(e) => setValue(e.target.value)} />;
};

export const Default = Template.bind({});
Default.args = {
  placeholder: 'Enter your message here...',
};

export const Sizes = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '400px' }}>
    <Textarea size="small" placeholder="Small textarea" />
    <Textarea size="medium" placeholder="Medium textarea" />
    <Textarea size="large" placeholder="Large textarea" />
  </div>
);

export const Variants = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '400px' }}>
    <Textarea variant="default" placeholder="Default variant" />
    <Textarea variant="primary" placeholder="Primary variant" />
    <Textarea variant="success" placeholder="Success variant" value="This looks good!" />
    <Textarea variant="warning" placeholder="Warning variant" value="Please check this..." />
    <Textarea variant="error" placeholder="Error variant" value="Something went wrong!" />
  </div>
);

export const States = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '400px' }}>
    <Textarea placeholder="Normal textarea" />
    <Textarea placeholder="Disabled textarea" disabled />
    <Textarea placeholder="Read-only textarea" readOnly value="This content cannot be edited" />
    <Textarea placeholder="Required field" required value="This field is required" />
  </div>
);

export const WithLabels = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '400px' }}>
    <Textarea 
      label="Description" 
      placeholder="Enter a description..." 
      helperText="This will be displayed on your profile" 
    />
    
    <Textarea 
      label="Bio" 
      required 
      placeholder="Tell us about yourself..." 
      helperText="Required field" 
    />
    
    <Textarea 
      label="Feedback" 
      variant="error"
      placeholder="What went wrong?"
      helperText="Please describe the issue in detail"
      error
    />
  </div>
);

export const WithCharacterCount = () => {
  const [value, setValue] = useState('');
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '400px' }}>
      <Textarea 
        label="Tweet"
        placeholder="What's happening?"
        maxLength={280}
        showCharCount
        value={value}
        onChange={(e) => setValue(e.target.value)}
        helperText="Maximum 280 characters"
      />
      
      <Textarea 
        label="Short Description"
        placeholder="Brief description..."
        maxLength={100}
        showCharCount
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </div>
  );
};

export const ResizeOptions = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '400px' }}>
    <Textarea resize="none" placeholder="No resize" />
    <Textarea resize="vertical" placeholder="Vertical resize (default)" />
    <Textarea resize="horizontal" placeholder="Horizontal resize" />
    <Textarea resize="both" placeholder="Both directions" />
  </div>
);

export const AutoExpand = () => {
  const [value, setValue] = useState('');
  return (
    <div style={{ maxWidth: '400px' }}>
      <Textarea 
        autoExpand
        placeholder="Start typing... This textarea will expand automatically as you type more content. Try adding multiple lines of text to see the effect."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        helperText="Auto-expanding textarea"
      />
    </div>
  );
};

export const FloatingLabel = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '400px' }}>
    <Textarea 
      floatingLabel
      label="Comments"
      placeholder=" "
      helperText="Floating label variant"
    />
    
    <Textarea 
      floatingLabel
      label="Email Content"
      placeholder=" "
      variant="primary"
      helperText="With primary variant"
    />
    
    <Textarea 
      floatingLabel
      label="Error Field"
      placeholder=" "
      variant="error"
      error
      helperText="This field has an error"
    />
  </div>
);

export const ValidationStates = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '400px' }}>
    <Textarea 
      label="Valid Input"
      variant="success"
      success
      value="This input is valid"
      helperText="Everything looks good!"
    />
    
    <Textarea 
      label="Warning Input"
      variant="warning"
      warning
      value="This needs attention"
      helperText="Please review this input"
    />
    
    <Textarea 
      label="Error Input"
      variant="error"
      error
      value="This has an error"
      helperText="Please fix this error"
    />
  </div>
);

export const FullWidth = () => (
  <div style={{ width: '100%' }}>
    <Textarea 
      fullWidth
      label="Full Width Textarea"
      placeholder="This textarea spans the full width of its container"
      helperText="Useful for forms and layouts that need to fill available space"
    />
  </div>
);

export const InFormContext = () => {
  const [formData, setFormData] = useState({
    description: '',
    feedback: '',
    notes: ''
  });

  const handleChange = (field) => (e) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  return (
    <div style={{ maxWidth: '600px', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <Textarea 
        label="Project Description"
        placeholder="Describe your project..."
        value={formData.description}
        onChange={handleChange('description')}
        helperText="Provide a detailed description of your project"
      />
      
      <Textarea 
        label="User Feedback"
        placeholder="What feedback do you have?"
        value={formData.feedback}
        onChange={handleChange('feedback')}
        maxLength={500}
        showCharCount
        helperText="Maximum 500 characters"
      />
      
      <Textarea 
        label="Additional Notes"
        placeholder="Any additional notes..."
        value={formData.notes}
        onChange={handleChange('notes')}
        size="small"
        resize="none"
        helperText="Optional notes"
      />
    </div>
  );
};

export const Playground = Template.bind({});
Playground.args = {
  label: 'Playground Textarea',
  placeholder: 'Experiment with different props...',
  variant: 'default',
  size: 'medium',
  resize: 'vertical',
  disabled: false,
  readOnly: false,
  required: false,
  error: false,
  warning: false,
  success: false,
  helperText: 'This is a helper text',
  showCharCount: false,
  maxLength: 200,
};