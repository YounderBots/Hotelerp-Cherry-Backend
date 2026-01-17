// Button.stories.jsx
import React from 'react';
import Button from './Button';

export default {
  title: 'Components/Button',
  component: Button,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'outline', 'ghost', 'danger', 'success'],
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large'],
    },
    onClick: { action: 'clicked' },
  },
};

const Template = (args) => <Button {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  variant: 'primary',
  children: 'Primary Button',
};

export const Secondary = Template.bind({});
Secondary.args = {
  variant: 'secondary',
  children: 'Secondary Button',
};

export const Outline = Template.bind({});
Outline.args = {
  variant: 'outline',
  children: 'Outline Button',
};

export const Ghost = Template.bind({});
Ghost.args = {
  variant: 'ghost',
  children: 'Ghost Button',
};

export const Danger = Template.bind({});
Danger.args = {
  variant: 'danger',
  children: 'Danger Button',
};

export const Success = Template.bind({});
Success.args = {
  variant: 'success',
  children: 'Success Button',
};

export const Sizes = () => (
  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
    <Button size="small">Small Button</Button>
    <Button size="medium">Medium Button</Button>
    <Button size="large">Large Button</Button>
  </div>
);

export const States = () => (
  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
    <Button>Normal</Button>
    <Button disabled>Disabled</Button>
    <Button loading>Loading</Button>
  </div>
);

export const WithIcons = () => (
  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
    <Button>
      <span style={{ marginRight: '0.5rem' }}>→</span>
      Button with Icon
    </Button>
    <Button iconOnly aria-label="Settings">
      ⚙️
    </Button>
    <Button size="small" iconOnly aria-label="Search">
      🔍
    </Button>
  </div>
);

export const FullWidth = () => (
  <div style={{ maxWidth: '400px' }}>
    <Button fullWidth>Full Width Button</Button>
  </div>
);

export const AllVariants = () => (
  <div style={{ display: 'grid', gap: '1rem', maxWidth: '400px' }}>
    {['primary', 'secondary', 'outline', 'ghost', 'danger', 'success'].map((variant) => (
      <div key={variant} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <Button variant={variant} size="small">
          {variant.charAt(0).toUpperCase() + variant.slice(1)} Small
        </Button>
        <Button variant={variant} size="medium">
          {variant.charAt(0).toUpperCase() + variant.slice(1)}
        </Button>
        <Button variant={variant} size="large">
          {variant.charAt(0).toUpperCase() + variant.slice(1)} Large
        </Button>
      </div>
    ))}
  </div>
);