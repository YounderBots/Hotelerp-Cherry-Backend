import React from 'react';
import TableTemplate from './TableTemplate';
import './TableTemplate.css';

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

// Advanced Table with Avatars
export const AdvancedUsers = Template.bind({});
AdvancedUsers.args = {
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
  pageSize: 3
};

// Large Dataset with Search
export const LargeDataset = Template.bind({});
LargeDataset.args = {
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
  pageSize: 10
};

// Without Export Features
export const Minimal = Template.bind({});
Minimal.args = {
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
};

// Loading State
export const LoadingState = Template.bind({});
LoadingState.args = {
  title: 'User Management',
  columns: [
    { key: 'name', title: 'Name' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role' },
  ],
  data: [],
  loading: true,
};

// Empty State
export const EmptyState = Template.bind({});
EmptyState.args = {
  title: 'User Management',
  columns: [
    { key: 'name', title: 'Name' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role' },
  ],
  data: [],
  emptyMessage: 'No users found. Please add some users to get started.',
};

// Interactive Demo
export const InteractiveDemo = (args) => {
  const [currentVariant, setCurrentVariant] = React.useState('default');
  const [currentSize, setCurrentSize] = React.useState('default');
  const [enablePagination, setEnablePagination] = React.useState(true);
  const [enableSearch, setEnableSearch] = React.useState(true);
  const [enableExport, setEnableExport] = React.useState(true);

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
      />
    </div>
  );
};

InteractiveDemo.args = {
  title: 'Interactive Table Demo',
  columns: [
    { key: 'name', title: 'Name' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Role' },
    { key: 'status', title: 'Status', type: 'badge' },
  ],
  data: generateSampleData(25),
};