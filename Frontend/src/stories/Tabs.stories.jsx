import React, { useState } from 'react';
import Tabs, { Tab } from './Tabs';
import './Tabs.css';

export default {
  title: 'Components/Tabs',
  component: Tabs,
  subcomponents: { Tab },
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'filled', 'pills', 'underline'],
    },
    size: {
      control: { type: 'select' },
      options: ['default', 'sm', 'lg'],
    },
    orientation: {
      control: { type: 'select' },
      options: ['horizontal', 'vertical'],
    },
    scrollable: { control: 'boolean' },
    addable: { control: 'boolean' },
    removable: { control: 'boolean' },
  },
};

// Template for basic stories
const Template = (args) => (
  <Tabs {...args}>
    <Tab label="Profile">
      <div>
        <h3>Profile Information</h3>
        <p>This is the profile tab content. You can add user information here.</p>
      </div>
    </Tab>
    <Tab label="Settings">
      <div>
        <h3>Settings Panel</h3>
        <p>Configure your application settings in this tab.</p>
      </div>
    </Tab>
    <Tab label="Notifications">
      <div>
        <h3>Notification Preferences</h3>
        <p>Manage your notification settings and preferences.</p>
      </div>
    </Tab>
  </Tabs>
);

// Basic Tabs
export const Basic = Template.bind({});
Basic.args = {
  variant: 'default',
};

// Filled Variant
export const Filled = Template.bind({});
Filled.args = {
  variant: 'filled',
};

// Pills Variant
export const Pills = Template.bind({});
Pills.args = {
  variant: 'pills',
};

// Underline Variant
export const Underline = Template.bind({});
Underline.args = {
  variant: 'underline',
};

// Different Sizes
export const Sizes = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
    <div>
      <h4>Small Tabs</h4>
      <Tabs size="sm">
        <Tab label="Small Tab 1">Content for small tab 1</Tab>
        <Tab label="Small Tab 2">Content for small tab 2</Tab>
      </Tabs>
    </div>
    
    <div>
      <h4>Default Tabs</h4>
      <Tabs size="default">
        <Tab label="Default Tab 1">Content for default tab 1</Tab>
        <Tab label="Default Tab 2">Content for default tab 2</Tab>
      </Tabs>
    </div>
    
    <div>
      <h4>Large Tabs</h4>
      <Tabs size="lg">
        <Tab label="Large Tab 1">Content for large tab 1</Tab>
        <Tab label="Large Tab 2">Content for large tab 2</Tab>
      </Tabs>
    </div>
  </div>
);

// Vertical Tabs
export const Vertical = () => (
  <div style={{ height: '400px' }}>
    <Tabs orientation="vertical" variant="filled">
      <Tab label="Dashboard" icon="📊">
        <div>
          <h3>Dashboard Overview</h3>
          <p>Welcome to your dashboard. Here's an overview of your metrics.</p>
        </div>
      </Tab>
      <Tab label="Messages" icon="💬" badge="5">
        <div>
          <h3>Messages</h3>
          <p>You have 5 unread messages.</p>
        </div>
      </Tab>
      <Tab label="Files" icon="📁">
        <div>
          <h3>File Manager</h3>
          <p>Manage your files and documents here.</p>
        </div>
      </Tab>
      <Tab label="Settings" icon="⚙️">
        <div>
          <h3>Settings</h3>
          <p>Configure your application settings.</p>
        </div>
      </Tab>
    </Tabs>
  </div>
);

// Tabs with Icons and Badges
export const WithIconsAndBadges = Template.bind({});
WithIconsAndBadges.args = {
  children: [
    <Tab key="1" label="Inbox" icon="📥" badge="12">
      <div>
        <h3>Inbox</h3>
        <p>You have 12 new messages in your inbox.</p>
      </div>
    </Tab>,
    <Tab key="2" label="Sent" icon="📤">
      <div>
        <h3>Sent Items</h3>
        <p>View your sent messages and emails.</p>
      </div>
    </Tab>,
    <Tab key="3" label="Drafts" icon="📝" badge="3">
      <div>
        <h3>Drafts</h3>
        <p>You have 3 unsaved drafts.</p>
      </div>
    </Tab>,
    <Tab key="4" label="Archived" icon="📦">
      <div>
        <h3>Archived Items</h3>
        <p>Browse through your archived content.</p>
      </div>
    </Tab>
  ]
};

// Disabled Tabs
export const DisabledTabs = Template.bind({});
DisabledTabs.args = {
  children: [
    <Tab key="1" label="Active Tab">This tab is active and functional.</Tab>,
    <Tab key="2" label="Disabled Tab" disabled>
      This tab is disabled and cannot be accessed.
    </Tab>,
    <Tab key="3" label="Another Active Tab">This is another active tab.</Tab>,
  ]
};

// Scrollable Tabs
export const Scrollable = () => (
  <Tabs scrollable variant="filled">
    {Array.from({ length: 15 }, (_, i) => (
      <Tab key={i} label={`Tab ${i + 1}`}>
        <div>
          <h3>Tab {i + 1} Content</h3>
          <p>This is the content for tab number {i + 1}.</p>
        </div>
      </Tab>
    ))}
  </Tabs>
);

// Dynamic Tabs (Add/Remove)
export const DynamicTabs = () => {
  const [tabs, setTabs] = useState([
    { id: 1, label: 'Tab 1', content: 'Initial tab content' },
    { id: 2, label: 'Tab 2', content: 'Second tab content' },
  ]);

  const handleAddTab = () => {
    const newId = tabs.length + 1;
    setTabs([...tabs, { 
      id: newId, 
      label: `Tab ${newId}`, 
      content: `Dynamic content for tab ${newId}` 
    }]);
  };

  const handleRemoveTab = (index) => {
    if (tabs.length <= 1) return;
    setTabs(tabs.filter((_, i) => i !== index));
  };

  return (
    <div>
      <Tabs addable removable onTabAdd={handleAddTab} onTabRemove={handleRemoveTab}>
        {tabs.map((tab, index) => (
          <Tab key={tab.id} label={tab.label}>
            <div>
              <h3>{tab.label}</h3>
              <p>{tab.content}</p>
            </div>
          </Tab>
        ))}
      </Tabs>
    </div>
  );
};

// Loading States
export const LoadingStates = () => (
  <Tabs>
    <Tab label="Normal Tab">
      <div>
        <h3>Normal Content</h3>
        <p>This tab loads normally.</p>
      </div>
    </Tab>
    <Tab label="Loading Tab" loading>
      {/* Content will be replaced by loading spinner */}
    </Tab>
    <Tab label="Another Tab">
      <div>
        <h3>More Content</h3>
        <p>This tab also loads normally.</p>
      </div>
    </Tab>
  </Tabs>
);

// Animated Transitions
export const Animated = () => (
  <Tabs>
    <Tab label="Slide Left" animation="slide-left">
      <div>
        <h3>Slide Left Animation</h3>
        <p>This tab content slides in from the right.</p>
      </div>
    </Tab>
    <Tab label="Slide Right" animation="slide-right">
      <div>
        <h3>Slide Right Animation</h3>
        <p>This tab content slides in from the left.</p>
      </div>
    </Tab>
    <Tab label="Zoom" animation="zoom">
      <div>
        <h3>Zoom Animation</h3>
        <p>This tab content zooms in smoothly.</p>
      </div>
    </Tab>
  </Tabs>
);

// Complex Content Tabs
export const ComplexContent = () => (
  <Tabs variant="filled">
    <Tab label="User Management" icon="👥">
      <div>
        <h3>User Management System</h3>
        <div style={{ display: 'grid', gap: '15px', marginTop: '15px' }}>
          <div style={{ padding: '15px', background: 'var(--gray-50)', borderRadius: '8px' }}>
            <h4>Active Users: 1,234</h4>
            <p>Manage user permissions and access levels.</p>
          </div>
          <button style={{ padding: '10px 15px', background: 'var(--primary-color)', color: 'white', border: 'none', borderRadius: '5px' }}>
            Add New User
          </button>
        </div>
      </div>
    </Tab>
    
    <Tab label="Analytics" icon="📈" badge="New">
      <div>
        <h3>Analytics Dashboard</h3>
        <div style={{ display: 'flex', gap: '15px', marginTop: '15px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '200px', padding: '15px', background: 'var(--success-light)', borderRadius: '8px' }}>
            <h4>Revenue: $12.5K</h4>
            <p style={{ color: 'var(--success-color)' }}>↑ 15% from last month</p>
          </div>
          <div style={{ flex: 1, minWidth: '200px', padding: '15px', background: 'var(--info-light)', borderRadius: '8px' }}>
            <h4>Users: 5,678</h4>
            <p style={{ color: 'var(--info-color)' }}>↑ 8% from last week</p>
          </div>
        </div>
      </div>
    </Tab>
    
    <Tab label="Settings" icon="⚙️">
      <div>
        <h3>Application Settings</h3>
        <div style={{ marginTop: '15px' }}>
          <label style={{ display: 'block', marginBottom: '10px' }}>
            <input type="checkbox" /> Enable notifications
          </label>
          <label style={{ display: 'block', marginBottom: '10px' }}>
            <input type="checkbox" /> Dark mode
          </label>
          <label style={{ display: 'block', marginBottom: '10px' }}>
            <input type="checkbox" /> Auto-save
          </label>
        </div>
      </div>
    </Tab>
  </Tabs>
);

// Interactive Demo
export const InteractiveDemo = (args) => {
  const [activeVariant, setActiveVariant] = useState('default');
  const [activeSize, setActiveSize] = useState('default');
  const [activeOrientation, setActiveOrientation] = useState('horizontal');
  const [enableScroll, setEnableScroll] = useState(false);
  const [enableAddRemove, setEnableAddRemove] = useState(false);

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
            value={activeVariant} 
            onChange={(e) => setActiveVariant(e.target.value)}
            style={{ padding: '8px', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}
          >
            <option value="default">Default</option>
            <option value="filled">Filled</option>
            <option value="pills">Pills</option>
            <option value="underline">Underline</option>
          </select>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Size:</label>
          <select 
            value={activeSize} 
            onChange={(e) => setActiveSize(e.target.value)}
            style={{ padding: '8px', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}
          >
            <option value="default">Default</option>
            <option value="sm">Small</option>
            <option value="lg">Large</option>
          </select>
        </div>
        
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Orientation:</label>
          <select 
            value={activeOrientation} 
            onChange={(e) => setActiveOrientation(e.target.value)}
            style={{ padding: '8px', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}
          >
            <option value="horizontal">Horizontal</option>
            <option value="vertical">Vertical</option>
          </select>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input 
            type="checkbox" 
            id="scrollable" 
            checked={enableScroll} 
            onChange={(e) => setEnableScroll(e.target.checked)}
          />
          <label htmlFor="scrollable">Scrollable</label>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input 
            type="checkbox" 
            id="addremove" 
            checked={enableAddRemove} 
            onChange={(e) => setEnableAddRemove(e.target.checked)}
          />
          <label htmlFor="addremove">Add/Remove</label>
        </div>
      </div>

      <div style={activeOrientation === 'vertical' ? { height: '400px' } : {}}>
        <Tabs
          {...args}
          variant={activeVariant}
          size={activeSize}
          orientation={activeOrientation}
          scrollable={enableScroll}
          addable={enableAddRemove}
          removable={enableAddRemove}
        />
      </div>
    </div>
  );
};

InteractiveDemo.args = {
  children: [
    <Tab key="1" label="Interactive Tab 1" icon="🎮">
      <div>
        <h3>Interactive Demo</h3>
        <p>This tab demonstrates the interactive capabilities of the tabs component.</p>
      </div>
    </Tab>,
    <Tab key="2" label="Interactive Tab 2" icon="⚡">
      <div>
        <h3>Real-time Updates</h3>
        <p>Change the controls above to see the tabs update in real-time.</p>
      </div>
    </Tab>,
    <Tab key="3" label="Interactive Tab 3" icon="🌟" badge="New">
      <div>
        <h3>Customization</h3>
        <p>Explore different variants, sizes, and configurations.</p>
      </div>
    </Tab>
  ]
};