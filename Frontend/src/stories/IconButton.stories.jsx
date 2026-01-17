// IconButton.stories.jsx
import React from 'react';
import IconButton, { IconButtonGroup } from './IconButton';

// Common icons for demonstration
const SettingsIcon = () => <span>⚙️</span>;
const SearchIcon = () => <span>🔍</span>;
const HeartIcon = () => <span>❤️</span>;
const StarIcon = () => <span>⭐</span>;
const BellIcon = () => <span>🔔</span>;
const PlusIcon = () => <span>➕</span>;
const EditIcon = () => <span>✏️</span>;
const DeleteIcon = () => <span>🗑️</span>;
const CheckIcon = () => <span>✅</span>;

export default {
  title: 'Components/IconButton',
  component: IconButton,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: [
        'solid', 'solid-secondary', 'outline', 'ghost', 'subtle', 
        'text', 'minimal', 'danger', 'danger-ghost', 'success', 'float'
      ],
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large', 'xlarge'],
    },
    onClick: { action: 'clicked' },
    icon: { control: false },
  },
  parameters: {
    layout: 'centered',
  },
};

const Template = (args) => <IconButton {...args} />;

export const Default = Template.bind({});
Default.args = {
  icon: <SettingsIcon />,
  ariaLabel: 'Settings',
};

export const AllVariants = () => (
  <div style={{ 
    display: 'grid', 
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
    gap: '2rem',
    padding: '2rem',
    background: 'var(--bg-primary)',
    borderRadius: 'var(--border-radius-lg)'
  }}>
    {[
      { variant: 'solid', label: 'Solid', icon: <StarIcon /> },
      { variant: 'solid-secondary', label: 'Solid Secondary', icon: <StarIcon /> },
      { variant: 'outline', label: 'Outline', icon: <StarIcon /> },
      { variant: 'ghost', label: 'Ghost', icon: <StarIcon /> },
      { variant: 'subtle', label: 'Subtle', icon: <StarIcon /> },
      { variant: 'text', label: 'Text', icon: <StarIcon /> },
      { variant: 'minimal', label: 'Minimal', icon: <StarIcon /> },
      { variant: 'danger', label: 'Danger', icon: <DeleteIcon /> },
      { variant: 'danger-ghost', label: 'Danger Ghost', icon: <DeleteIcon /> },
      { variant: 'success', label: 'Success', icon: <CheckIcon /> },
      { variant: 'float', label: 'Float', icon: <PlusIcon /> },
    ].map(({ variant, label, icon }) => (
      <div key={variant} style={{ textAlign: 'center' }}>
        <p style={{ marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          {label}
        </p>
        <IconButton variant={variant} icon={icon} ariaLabel={label} />
      </div>
    ))}
  </div>
);

export const Sizes = () => (
  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
    {['small', 'medium', 'large', 'xlarge'].map((size) => (
      <IconButton
        key={size}
        size={size}
        icon={<SettingsIcon />}
        ariaLabel={`${size} settings`}
      />
    ))}
  </div>
);

export const WithBadges = () => (
  <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', flexWrap: 'wrap' }}>
    <IconButton icon={<BellIcon />} badge={3} ariaLabel="Notifications" />
    <IconButton icon={<HeartIcon />} badge="♥" badgeColor="var(--error-color)" ariaLabel="Favorites" />
    <IconButton variant="solid" icon={<BellIcon />} badge={12} ariaLabel="Notifications" />
    <IconButton variant="outline" icon={<HeartIcon />} badge={99} ariaLabel="Likes" />
  </div>
);

export const States = () => (
  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
    <IconButton icon={<EditIcon />} ariaLabel="Edit" />
    <IconButton icon={<EditIcon />} disabled ariaLabel="Edit disabled" />
    <IconButton icon={<EditIcon />} loading ariaLabel="Edit loading" />
    <IconButton icon={<EditIcon />} variant="solid" ariaLabel="Edit solid" />
    <IconButton icon={<EditIcon />} variant="solid" disabled ariaLabel="Edit solid disabled" />
  </div>
);

export const CommonActions = () => (
  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
    <IconButton icon={<SearchIcon />} variant="minimal" ariaLabel="Search" />
    <IconButton icon={<SettingsIcon />} variant="minimal" ariaLabel="Settings" />
    <IconButton icon={<EditIcon />} variant="outline" ariaLabel="Edit" />
    <IconButton icon={<DeleteIcon />} variant="danger-ghost" ariaLabel="Delete" />
    <IconButton icon={<CheckIcon />} variant="success" ariaLabel="Confirm" />
    <IconButton icon={<PlusIcon />} variant="float" size="large" ariaLabel="Add" />
  </div>
);

export const ButtonGroupExample = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
    <div>
      <h4 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Horizontal Group</h4>
      <IconButtonGroup direction="horizontal" gap="md">
        <IconButton icon={<EditIcon />} variant="minimal" ariaLabel="Edit" />
        <IconButton icon={<DeleteIcon />} variant="minimal" ariaLabel="Delete" />
        <IconButton icon={<CheckIcon />} variant="minimal" ariaLabel="Check" />
        <IconButton icon={<SettingsIcon />} variant="minimal" ariaLabel="Settings" />
      </IconButtonGroup>
    </div>
    
    <div>
      <h4 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Toolbar Example</h4>
      <IconButtonGroup direction="horizontal" gap="sm">
        <IconButton icon="B" variant="text" ariaLabel="Bold" />
        <IconButton icon="I" variant="text" ariaLabel="Italic" />
        <IconButton icon="U" variant="text" ariaLabel="Underline" />
        <div style={{ width: '1px', background: 'var(--border-color)', margin: '0 0.5rem' }} />
        <IconButton icon="🔤" variant="text" ariaLabel="Font" />
        <IconButton icon="🎨" variant="text" ariaLabel="Color" />
      </IconButtonGroup>
    </div>
  </div>
);

export const DarkModeCompatible = () => (
  <div style={{ 
    padding: '2rem', 
    background: 'var(--bg-secondary)', 
    borderRadius: 'var(--border-radius-lg)',
    display: 'flex',
    gap: '1rem',
    flexWrap: 'wrap'
  }}>
    <IconButton icon={<StarIcon />} variant="solid" ariaLabel="Star" />
    <IconButton icon={<StarIcon />} variant="outline" ariaLabel="Star" />
    <IconButton icon={<StarIcon />} variant="ghost" ariaLabel="Star" />
    <IconButton icon={<StarIcon />} variant="subtle" ariaLabel="Star" />
    <IconButton icon={<StarIcon />} variant="text" ariaLabel="Star" />
  </div>
);

// Interactive story for testing
export const Playground = Template.bind({});
Playground.args = {
  icon: <SettingsIcon />,
  variant: 'ghost',
  size: 'medium',
  ariaLabel: 'Settings button',
  disabled: false,
  loading: false,
};