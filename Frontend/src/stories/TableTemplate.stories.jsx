import React from 'react';
import TableTemplate, { TableActionButton } from './TableTemplate';
import './TableTemplate.css';
import { Plus, UserPlus, Download, Edit } from 'lucide-react';

export default {
  title: 'Components/TableTemplate',
  component: TableTemplate,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'striped', 'bordered', 'hover'],
    },
    size: {
      control: { type: 'select' },
      options: ['default', 'sm', 'lg'],
    },
    pagination: { control: 'boolean' },
    searchable: { control: 'boolean' },
    exportable: { control: 'boolean' },
    loading: { control: 'boolean' },
    hasActionButton: { control: 'boolean' },
  },
};

// Sample data
const sampleUsers = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Admin',
    status: 'active',
    lastLogin: '2024-01-15',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    role: 'User',
    status: 'pending',
    lastLogin: '2024-01-10',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=32&h=32&fit=crop&crop=face'
  },
  {
    id: 3,
    name: 'Mike Johnson',
    email: 'mike@example.com',
    role: 'Moderator',
    status: 'inactive',
    lastLogin: '2024-01-05',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=32&h=32&fit=crop&crop=face'
  },
  {
    id: 4,
    name: 'Sarah Wilson',
    email: 'sarah@example.com',
    role: 'User',
    status: 'active',
    lastLogin: '2024-01-14',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=32&h=32&fit=crop&crop=face'
  },
  {
    id: 5,
    name: 'Alex Chen',
    email: 'alex@example.com',
    role: 'Developer',
    status: 'active',
    lastLogin: '2024-01-12',
    avatar: 'https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=32&h=32&fit=crop&crop=face'
  },
];

// Generate more sample data
const generateSampleData = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    role: ['Admin', 'User', 'Moderator', 'Developer'][i % 4],
    status: ['active', 'pending', 'inactive'][i % 3],
    lastLogin: `2024-01-${(i % 28) + 1}`,
    avatar: `https://i.pravatar.cc/32?img=${i + 1}`
  }));
};

const Template = (args) => <TableTemplate {...args} />;

// Basic Table Template
export const Basic = Template.bind({});
Basic.args = {
  title: 'User Management',
  columns: [
    { key: 'name', title: 'Name', width: '200px' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role', align: 'center' },
    { key: 'status', title: 'Status', type: 'badge', align: 'center' },
    { key: 'lastLogin', title: 'Last Login', align: 'center' },
  ],
  data: sampleUsers,
  pagination: true,
  searchable: true,
  exportable: true,
};

// Table with Action Button
export const WithActionButton = Template.bind({});
WithActionButton.args = {
  title: 'User Management',
  columns: [
    { key: 'name', title: 'Name', width: '200px' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role', align: 'center' },
    { key: 'status', title: 'Status', type: 'badge', align: 'center' },
    { key: 'lastLogin', title: 'Last Login', align: 'center' },
  ],
  data: sampleUsers,
  pagination: true,
  searchable: true,
  exportable: true,
  hasActionButton: true,
  actionButton: {
    onClick: () => alert('Add New User clicked!'),
    label: 'Add New User',
    icon: <UserPlus size={18} />,
    variant: 'primary',
    size: 'medium'
  }
};

// Advanced Table with Avatars and Action Button
export const AdvancedWithAction = Template.bind({});
AdvancedWithAction.args = {
  title: 'Team Members',
  columns: [
    { 
      key: 'user', 
      title: 'User',
      type: 'avatar',
      width: '250px'
    },
    { 
      key: 'role', 
      title: 'Role',
      align: 'center'
    },
    { 
      key: 'status', 
      title: 'Status',
      type: 'badge',
      align: 'center'
    },
    { 
      key: 'lastLogin', 
      title: 'Last Login',
      align: 'center'
    },
  ],
  data: sampleUsers.map(user => ({
    ...user,
    user: { src: user.avatar, name: user.name, email: user.email }
  })),
  variant: 'striped',
  pagination: true,
  pageSize: 3,
  hasActionButton: true,
  actionButton: {
    onClick: () => console.log('Export team data'),
    label: 'Export Team',
    icon: <Download size={18} />,
    variant: 'outline',
    size: 'small'
  }
};

// Large Dataset with Custom Action Button
export const LargeDatasetWithAction = Template.bind({});
LargeDatasetWithAction.args = {
  title: 'User Directory (50 Users)',
  columns: [
    { key: 'id', title: 'ID', width: '80px', align: 'center' },
    { key: 'name', title: 'Full Name', width: '200px' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role', align: 'center' },
    { key: 'status', title: 'Status', type: 'badge', align: 'center' },
  ],
  data: generateSampleData(50),
  variant: 'hover',
  pagination: true,
  pageSize: 10,
  hasActionButton: true,
  actionButton: {
    onClick: () => console.log('Bulk edit users'),
    label: 'Bulk Edit',
    icon: <Edit size={18} />,
    variant: 'secondary',
    size: 'medium'
  }
};

// Without Export Features but with Action Button
export const MinimalWithAction = Template.bind({});
MinimalWithAction.args = {
  title: 'Simple User List',
  columns: [
    { key: 'name', title: 'Name' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role' },
  ],
  data: sampleUsers,
  exportable: false,
  searchable: false,
  pagination: false,
  hasActionButton: true,
  actionButton: {
    onClick: () => alert('Quick action!'),
    label: 'Quick Action',
    variant: 'primary',
    size: 'small'
  }
};

// Interactive Demo with Action Button
export const InteractiveDemoWithAction = (args) => {
  const [currentVariant, setCurrentVariant] = React.useState('default');
  const [currentSize, setCurrentSize] = React.useState('default');
  const [enablePagination, setEnablePagination] = React.useState(true);
  const [enableSearch, setEnableSearch] = React.useState(true);
  const [enableExport, setEnableExport] = React.useState(true);
  const [hasActionBtn, setHasActionBtn] = React.useState(true);
  const [buttonVariant, setButtonVariant] = React.useState('primary');

  const handleActionClick = () => {
    alert('Action button clicked! This could open a modal, navigate, or perform any action.');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ 
        display: 'flex', 
        gap: '15px', 
        padding: '15px', 
        background: 'var(--gray-50)',
        borderRadius: 'var(--border-radius)',
        flexWrap: 'wrap'
      }}>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Variant:</label>
          <select 
            value={currentVariant} 
            onChange={(e) => setCurrentVariant(e.target.value)}
            style={{ padding: '8px', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}
          >
            <option value="default">Default</option>
            <option value="striped">Striped</option>
            <option value="bordered">Bordered</option>
            <option value="hover">Hover</option>
          </select>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Size:</label>
          <select 
            value={currentSize} 
            onChange={(e) => setCurrentSize(e.target.value)}
            style={{ padding: '8px', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}
          >
            <option value="default">Default</option>
            <option value="sm">Small</option>
            <option value="lg">Large</option>
          </select>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input 
            type="checkbox" 
            id="actionBtn" 
            checked={hasActionBtn} 
            onChange={(e) => setHasActionBtn(e.target.checked)}
          />
          <label htmlFor="actionBtn">Action Button</label>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Button Style:</label>
          <select 
            value={buttonVariant} 
            onChange={(e) => setButtonVariant(e.target.value)}
            style={{ padding: '8px', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}
          >
            <option value="primary">Primary</option>
            <option value="secondary">Secondary</option>
            <option value="outline">Outline</option>
          </select>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input 
            type="checkbox" 
            id="pagination" 
            checked={enablePagination} 
            onChange={(e) => setEnablePagination(e.target.checked)}
          />
          <label htmlFor="pagination">Pagination</label>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input 
            type="checkbox" 
            id="search" 
            checked={enableSearch} 
            onChange={(e) => setEnableSearch(e.target.checked)}
          />
          <label htmlFor="search">Search</label>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input 
            type="checkbox" 
            id="export" 
            checked={enableExport} 
            onChange={(e) => setEnableExport(e.target.checked)}
          />
          <label htmlFor="export">Export</label>
        </div>
      </div>

      <TableTemplate
        {...args}
        variant={currentVariant}
        size={currentSize}
        pagination={enablePagination}
        searchable={enableSearch}
        exportable={enableExport}
        hasActionButton={hasActionBtn}
        actionButton={hasActionBtn ? {
          onClick: handleActionClick,
          label: 'Add New Item',
          icon: <Plus size={18} />,
          variant: buttonVariant,
          size: 'medium'
        } : null}
      />
    </div>
  );
};

InteractiveDemoWithAction.args = {
  title: 'Interactive Table Demo with Action Button',
  columns: [
    { key: 'name', title: 'Name' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role' },
    { key: 'status', title: 'Status', type: 'badge' },
  ],
  data: generateSampleData(25),
};

// Example of using TableActionButton component standalone
export const ActionButtonDemo = () => {
  const handlePrimaryClick = () => alert('Primary button clicked!');
  const handleSecondaryClick = () => alert('Secondary button clicked!');
  const handleOutlineClick = () => alert('Outline button clicked!');

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <h3>Action Button Variants</h3>
      <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
        <TableActionButton
          onClick={handlePrimaryClick}
          label="Primary Button"
          icon={<Plus size={18} />}
          variant="primary"
        />
        <TableActionButton
          onClick={handleSecondaryClick}
          label="Secondary Button"
          icon={<Download size={18} />}
          variant="secondary"
        />
        <TableActionButton
          onClick={handleOutlineClick}
          label="Outline Button"
          icon={<Edit size={18} />}
          variant="outline"
        />
      </div>
      
      <h3>Different Sizes</h3>
      <div style={{ display: 'flex', gap: '15px', alignItems: 'center', flexWrap: 'wrap' }}>
        <TableActionButton
          onClick={handlePrimaryClick}
          label="Small"
          variant="primary"
          size="small"
        />
        <TableActionButton
          onClick={handlePrimaryClick}
          label="Medium"
          variant="primary"
          size="medium"
        />
        <TableActionButton
          onClick={handlePrimaryClick}
          label="Large"
          variant="primary"
          size="large"
        />
      </div>
      
      <h3>Icon Only</h3>
      <div style={{ display: 'flex', gap: '15px' }}>
        <TableActionButton
          onClick={handlePrimaryClick}
          icon={<Plus size={18} />}
          variant="primary"
        />
        <TableActionButton
          onClick={handleSecondaryClick}
          icon={<Download size={18} />}
          variant="secondary"
        />
      </div>
    </div>
  );
};