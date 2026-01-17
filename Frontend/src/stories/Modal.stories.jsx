// Modal.stories.jsx
import React, { useState } from 'react';
import Modal, { 
  AlertModal, 
  ConfirmModal, 
  DialogModal, 
  SheetModal, 
  DrawerModal 
} from './Modal';

// Mock Button component for the story
const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'medium',
  className = '',
  ...props 
}) => (
  <button
    className={`btn btn--${variant} btn--${size} ${className}`}
    onClick={onClick}
    {...props}
    style={{
      padding: size === 'small' ? '0.5rem 1rem' : '0.75rem 1.5rem',
      borderRadius: 'var(--border-radius)',
      cursor: 'pointer',
      fontWeight: '500',
      fontSize: size === 'small' ? '0.875rem' : '1rem',
      transition: 'all var(--transition-fast)',
      backgroundColor: variant === 'primary' ? 'var(--primary-color)' : 
                      variant === 'ghost' ? 'transparent' :
                      variant === 'outline' ? 'transparent' : 'var(--gray-200)',
      color: variant === 'primary' ? 'var(--text-white)' :
             variant === 'ghost' ? 'var(--text-primary)' :
             variant === 'outline' ? 'var(--primary-color)' : 'var(--text-primary)',
      border: variant === 'outline' ? '1px solid var(--primary-color)' : 'none',
      ...props.style
    }}
  >
    {children}
  </button>
);

export default {
  title: 'Components/Modal',
  component: Modal,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'elevated', 'bordered', 'subtle', 'alert', 'success', 'warning', 'info'],
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large', 'xlarge', 'fullscreen'],
    },
    type: {
      control: { type: 'select' },
      options: ['modal', 'dialog', 'sheet', 'drawer'],
    },
    footerAlign: {
      control: { type: 'select' },
      options: ['left', 'center', 'right', 'space-between'],
    },
  },
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'A versatile modal component with multiple variants, sizes, and behaviors. Supports accessibility features, animations, and responsive design.'
      }
    }
  },
};

const Template = (args) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div style={{ padding: '2rem' }}>
      <Button onClick={() => setIsOpen(true)}>Open Modal</Button>
      
      <Modal
        {...args}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      >
        {args.children}
      </Modal>
    </div>
  );
};

// Basic Modal Story
export const Basic = Template.bind({});
Basic.args = {
  title: 'Basic Modal',
  children: (
    <div>
      <p>This is a basic modal with default styling and behavior.</p>
      <p>It includes proper focus management, keyboard navigation, and accessibility features.</p>
    </div>
  ),
  showFooter: true,
};

// Modal Sizes
export const Sizes = () => {
  const [activeSize, setActiveSize] = useState(null);
  
  const sizes = [
    { size: 'small', label: 'Small (400px)', description: 'Perfect for simple confirmations and alerts' },
    { size: 'medium', label: 'Medium (500px)', description: 'Default size for most use cases' },
    { size: 'large', label: 'Large (700px)', description: 'Ideal for forms and detailed content' },
    { size: 'xlarge', label: 'X-Large (900px)', description: 'For complex layouts and data tables' },
    { size: 'fullscreen', label: 'Fullscreen', description: 'Takes up most of the viewport' },
  ];
  
  return (
    <div style={{ padding: '2rem' }}>
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Modal Sizes</h3>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        {sizes.map(({ size, label }) => (
          <Button key={size} onClick={() => setActiveSize(size)} variant="outline">
            {label}
          </Button>
        ))}
      </div>
      
      {sizes.map(({ size, label, description }) => (
        <Modal
          key={size}
          isOpen={activeSize === size}
          onClose={() => setActiveSize(null)}
          size={size}
          title={`${label} Modal`}
          showFooter={true}
          actions={[
            { label: 'Close', variant: 'ghost', onClick: () => setActiveSize(null) }
          ]}
        >
          <div>
            <p><strong>Size:</strong> {size}</p>
            <p><strong>Description:</strong> {description}</p>
            <p>This modal demonstrates the <em>{size}</em> size variant. Each size is optimized for different content types and use cases.</p>
          </div>
        </Modal>
      ))}
    </div>
  );
};

// Modal Variants
export const Variants = () => {
  const [activeVariant, setActiveVariant] = useState(null);
  
  const variants = [
    { 
      variant: 'default', 
      label: 'Default', 
      icon: '💼',
      description: 'Standard modal with subtle border and shadow'
    },
    { 
      variant: 'elevated', 
      label: 'Elevated', 
      icon: '⬆️',
      description: 'Enhanced shadow for more prominence'
    },
    { 
      variant: 'bordered', 
      label: 'Bordered', 
      icon: '🔲',
      description: 'Prominent border using primary color'
    },
    { 
      variant: 'subtle', 
      label: 'Subtle', 
      icon: '🎭',
      description: 'Minimal styling with light background'
    },
    { 
      variant: 'alert', 
      label: 'Alert', 
      icon: '⚠️',
      description: 'Red accent for error states and warnings'
    },
    { 
      variant: 'success', 
      label: 'Success', 
      icon: '✅',
      description: 'Green accent for successful operations'
    },
    { 
      variant: 'warning', 
      label: 'Warning', 
      icon: '🔶',
      description: 'Orange accent for cautionary messages'
    },
    { 
      variant: 'info', 
      label: 'Info', 
      icon: 'ℹ️',
      description: 'Blue accent for informational content'
    },
  ];
  
  return (
    <div style={{ padding: '2rem' }}>
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Modal Variants</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {variants.map(({ variant, label }) => (
          <Button key={variant} onClick={() => setActiveVariant(variant)} variant="outline">
            {label}
          </Button>
        ))}
      </div>
      
      {variants.map(({ variant, label, icon, description }) => (
        <Modal
          key={variant}
          isOpen={activeVariant === variant}
          onClose={() => setActiveVariant(null)}
          variant={variant}
          title={`${label} Modal`}
          icon={icon}
          showFooter={true}
          actions={[
            { label: 'Got it', variant: 'primary', onClick: () => setActiveVariant(null) }
          ]}
        >
          <div>
            <p><strong>Variant:</strong> {variant}</p>
            <p>{description}</p>
          </div>
        </Modal>
      ))}
    </div>
  );
};

// Modal Types
export const Types = () => {
  const [activeType, setActiveType] = useState(null);
  
  const types = [
    { type: 'modal', label: 'Standard Modal', description: 'Centered modal with backdrop' },
    { type: 'dialog', label: 'Dialog Modal', description: 'Modal with colored header bar' },
    { type: 'sheet', label: 'Bottom Sheet', description: 'Slides up from bottom' },
    { type: 'drawer', label: 'Side Drawer', description: 'Slides in from the right side' },
  ];
  
  return (
    <div style={{ padding: '2rem' }}>
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Modal Types</h3>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        {types.map(({ type, label }) => (
          <Button key={type} onClick={() => setActiveType(type)} variant="outline">
            {label}
          </Button>
        ))}
      </div>
      
      <Modal
        isOpen={activeType === 'modal'}
        onClose={() => setActiveType(null)}
        type="modal"
        title="Standard Modal"
        showFooter={true}
        actions={[
          { label: 'Close', variant: 'primary', onClick: () => setActiveType(null) }
        ]}
      >
        <p>This is a standard centered modal that appears with a backdrop overlay.</p>
        <p>Perfect for most modal use cases including forms, confirmations, and content display.</p>
      </Modal>
      
      <DialogModal
        isOpen={activeType === 'dialog'}
        onClose={() => setActiveType(null)}
        title="Dialog Modal"
        showFooter={true}
        actions={[
          { label: 'Close', variant: 'ghost', onClick: () => setActiveType(null) }
        ]}
      >
        <p>This is a dialog-style modal with a distinctive colored header.</p>
        <p>Great for important announcements and system dialogs.</p>
      </DialogModal>
      
      <SheetModal
        isOpen={activeType === 'sheet'}
        onClose={() => setActiveType(null)}
        title="Bottom Sheet"
        showFooter={true}
        actions={[
          { label: 'Close', variant: 'primary', onClick: () => setActiveType(null) }
        ]}
      >
        <p>This is a bottom sheet that slides up from the bottom of the screen.</p>
        <p>Perfect for mobile interfaces, action menus, and quick selections.</p>
        <div style={{ height: '200px', background: 'var(--gray-50)', borderRadius: 'var(--border-radius)', padding: '1rem', margin: '1rem 0' }}>
          <p>Additional content area...</p>
        </div>
      </SheetModal>
      
      <DrawerModal
        isOpen={activeType === 'drawer'}
        onClose={() => setActiveType(null)}
        title="Side Drawer"
        showFooter={true}
        actions={[
          { label: 'Close', variant: 'primary', onClick: () => setActiveType(null) }
        ]}
      >
        <p>This is a side drawer that slides in from the right edge.</p>
        <p>Ideal for settings panels, filters, navigation menus, and detailed forms.</p>
        <div style={{ marginTop: '2rem' }}>
          <h4 style={{ marginBottom: '1rem' }}>Navigation Menu</h4>
          {['Dashboard', 'Projects', 'Team', 'Settings', 'Help'].map(item => (
            <div key={item} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--border-light)' }}>
              {item}
            </div>
          ))}
        </div>
      </DrawerModal>
    </div>
  );
};

// Alert Modals
export const AlertModals = () => {
  const [alertType, setAlertType] = useState(null);
  
  const alerts = [
    { type: 'success', label: 'Success', icon: '✅', title: 'Operation Successful', message: 'Your changes have been saved successfully!' },
    { type: 'error', label: 'Error', icon: '❌', title: 'Operation Failed', message: 'Unable to complete the operation. Please try again.' },
    { type: 'warning', label: 'Warning', icon: '⚠️', title: 'Warning', message: 'This action may have unintended consequences.' },
    { type: 'info', label: 'Info', icon: 'ℹ️', title: 'Information', message: 'Here\'s some important information you should know.' },
  ];
  
  return (
    <div style={{ padding: '2rem' }}>
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Alert Modals</h3>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        {alerts.map(({ type, label }) => (
          <Button key={type} onClick={() => setAlertType(type)} variant="outline">
            {label} Alert
          </Button>
        ))}
      </div>
      
      {alerts.map(({ type, label, icon, title, message }) => (
        <AlertModal
          key={type}
          isOpen={alertType === type}
          onClose={() => setAlertType(null)}
          type={type}
          title={title}
          icon={icon}
          confirmText="Got it"
        >
          <p>{message}</p>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>
            This is a <strong>{type}</strong> alert modal with automatic styling and behavior.
          </p>
        </AlertModal>
      ))}
    </div>
  );
};

// Confirmation Modals
export const ConfirmationModals = () => {
  const [confirmAction, setConfirmAction] = useState(null);
  
  const actions = [
    { 
      action: 'delete', 
      label: 'Delete Item', 
      title: 'Confirm Deletion', 
      message: 'Are you sure you want to delete this item? This action cannot be undone.',
      confirmText: 'Delete',
      confirmVariant: 'danger'
    },
    { 
      action: 'publish', 
      label: 'Publish Post', 
      title: 'Publish Post', 
      message: 'Ready to publish this post? It will be visible to all users immediately.',
      confirmText: 'Publish',
      confirmVariant: 'primary'
    },
    { 
      action: 'logout', 
      label: 'Log Out', 
      title: 'Confirm Logout', 
      message: 'You will be logged out of your account. Any unsaved changes will be lost.',
      confirmText: 'Log Out',
      confirmVariant: 'primary'
    },
  ];
  
  const handleConfirm = (action) => {
    alert(`Action confirmed: ${action}`);
    setConfirmAction(null);
  };
  
  return (
    <div style={{ padding: '2rem' }}>
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Confirmation Modals</h3>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        {actions.map(({ action, label }) => (
          <Button key={action} variant="outline" onClick={() => setConfirmAction(action)}>
            {label}
          </Button>
        ))}
      </div>
      
      {actions.map(({ action, title, message, confirmText, confirmVariant }) => (
        <ConfirmModal
          key={action}
          isOpen={confirmAction === action}
          onClose={() => setConfirmAction(null)}
          onConfirm={() => handleConfirm(action)}
          title={title}
          confirmText={confirmText}
          confirmVariant={confirmVariant}
          cancelText="Cancel"
        >
          <p>{message}</p>
        </ConfirmModal>
      ))}
    </div>
  );
};

// Complex Content Modal
export const ComplexContent = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'general',
    priority: 'medium'
  });
  
  const handleSave = () => {
    console.log('Saving:', formData);
    alert('Form saved successfully!');
    setIsOpen(false);
  };
  
  return (
    <div style={{ padding: '2rem' }}>
      <Button onClick={() => setIsOpen(true)}>Open Complex Modal</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Create New Project"
        size="large"
        showFooter={true}
        actions={[
          { label: 'Cancel', variant: 'ghost', onClick: () => setIsOpen(false) },
          { label: 'Save Draft', variant: 'outline', onClick: () => console.log('Draft saved') },
          { label: 'Create Project', variant: 'primary', onClick: handleSave },
        ]}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: 'var(--text-primary)' }}>
              Project Title *
            </label>
            <input 
              type="text" 
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              style={{ 
                width: '100%', 
                padding: '0.75rem', 
                border: '1px solid var(--border-color)', 
                borderRadius: 'var(--border-radius)',
                fontSize: '1rem',
                transition: 'border-color var(--transition-fast)'
              }} 
              placeholder="Enter project title..." 
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: 'var(--text-primary)' }}>
              Description
            </label>
            <textarea 
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              style={{ 
                width: '100%', 
                padding: '0.75rem', 
                border: '1px solid var(--border-color)', 
                borderRadius: 'var(--border-radius)',
                minHeight: '120px',
                fontSize: '1rem',
                resize: 'vertical',
                transition: 'border-color var(--transition-fast)'
              }} 
              placeholder="Describe your project..." 
            />
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: 'var(--text-primary)' }}>
                Category
              </label>
              <select 
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                style={{ 
                  width: '100%', 
                  padding: '0.75rem', 
                  border: '1px solid var(--border-color)', 
                  borderRadius: 'var(--border-radius)',
                  fontSize: '1rem',
                  backgroundColor: 'var(--bg-primary)'
                }}
              >
                <option value="general">General</option>
                <option value="development">Development</option>
                <option value="design">Design</option>
                <option value="marketing">Marketing</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: 'var(--text-primary)' }}>
                Priority
              </label>
              <select 
                value={formData.priority}
                onChange={(e) => setFormData({...formData, priority: e.target.value})}
                style={{ 
                  width: '100%', 
                  padding: '0.75rem', 
                  border: '1px solid var(--border-color)', 
                  borderRadius: 'var(--border-radius)',
                  fontSize: '1rem',
                  backgroundColor: 'var(--bg-primary)'
                }}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>
          
          <div className="modal__scrollable">
            <h4 style={{ marginBottom: '1rem' }}>Recent Projects</h4>
            {Array.from({ length: 8 }, (_, i) => (
              <div key={i} style={{ 
                padding: '0.75rem', 
                borderBottom: '1px solid var(--border-light)', 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <div style={{ fontWeight: '500' }}>Project {i + 1}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    Created 2 days ago
                  </div>
                </div>
                <div style={{ 
                  padding: '0.25rem 0.5rem', 
                  borderRadius: 'var(--border-radius-sm)', 
                  fontSize: '0.75rem',
                  backgroundColor: 'var(--primary-lightest)',
                  color: 'var(--primary-color)'
                }}>
                  Active
                </div>
              </div>
            ))}
          </div>
        </div>
      </Modal>
    </div>
  );
};

// Minimal Modal
export const MinimalModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div style={{ padding: '2rem' }}>
      <Button onClick={() => setIsOpen(true)}>Open Minimal Modal</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        showHeader={false}
        showFooter={false}
        closeOnBackdropClick={true}
        variant="elevated"
      >
        <div style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <div style={{ 
            fontSize: '4rem', 
            marginBottom: '1rem',
            background: 'var(--success-light)',
            width: '80px',
            height: '80px',
            borderRadius: 'var(--border-radius-full)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.5rem'
          }}>
            🎉
          </div>
          <h3 style={{ 
            marginBottom: '1rem', 
            color: 'var(--text-primary)',
            fontSize: '1.5rem',
            fontWeight: '600'
          }}>
            Success!
          </h3>
          <p style={{ 
            color: 'var(--text-secondary)', 
            marginBottom: '2rem',
            fontSize: '1rem'
          }}>
            Your action was completed successfully.
          </p>
          <Button onClick={() => setIsOpen(false)} variant="primary">
            Got it!
          </Button>
        </div>
      </Modal>
    </div>
  );
};

// Nested Modals
export const NestedModals = () => {
  const [firstOpen, setFirstOpen] = useState(false);
  const [secondOpen, setSecondOpen] = useState(false);
  
  return (
    <div style={{ padding: '2rem' }}>
      <Button onClick={() => setFirstOpen(true)}>Open First Modal</Button>
      
      <Modal
        isOpen={firstOpen}
        onClose={() => setFirstOpen(false)}
        title="First Modal"
        showFooter={true}
        actions={[
          { label: 'Cancel', variant: 'ghost', onClick: () => setFirstOpen(false) },
          { label: 'Open Second Modal', variant: 'primary', onClick: () => setSecondOpen(true) },
        ]}
      >
        <p>This is the first modal in a nested modal demonstration.</p>
        <p>Click "Open Second Modal" to see how modals can be layered properly with correct z-indexing and backdrop handling.</p>
      </Modal>
      
      <Modal
        isOpen={secondOpen}
        onClose={() => setSecondOpen(false)}
        title="Second Modal"
        variant="elevated"
        showFooter={true}
        actions={[
          { label: 'Close This', variant: 'ghost', onClick: () => setSecondOpen(false) },
          { label: 'Close Both', variant: 'primary', onClick: () => { setSecondOpen(false); setFirstOpen(false); } },
        ]}
      >
        <p>This is the second modal, nested inside the first one.</p>
        <p>Notice how the backdrop becomes darker for each nested level, and focus management is properly handled.</p>
        <div style={{ 
          padding: '1rem', 
          background: 'var(--info-light)', 
          borderRadius: 'var(--border-radius)',
          border: '1px solid var(--info-color)',
          marginTop: '1rem'
        }}>
          <strong>Pro tip:</strong> Nested modals maintain proper accessibility and keyboard navigation.
        </div>
      </Modal>
    </div>
  );
};

// Interactive Playground
export const Playground = Template.bind({});
Playground.args = {
  title: 'Playground Modal',
  children: (
    <div>
      <p>Use the controls in the Storybook panel to experiment with different modal configurations.</p>
      <p>This playground allows you to test various combinations of props and see how they affect the modal's appearance and behavior.</p>
      <div style={{ 
        marginTop: '2rem', 
        padding: '1rem', 
        background: 'var(--gray-50)', 
        borderRadius: 'var(--border-radius)' 
      }}>
        <h4>Available Controls:</h4>
        <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
          <li>Variant (styling)</li>
          <li>Size (dimensions)</li>
          <li>Type (behavior)</li>
          <li>Header & Footer options</li>
          <li>Accessibility settings</li>
        </ul>
      </div>
    </div>
  ),
  variant: 'default',
  size: 'medium',
  type: 'modal',
  showHeader: true,
  showFooter: true,
  showCloseButton: true,
  closeOnBackdropClick: true,
  closeOnEscape: true,
  footerAlign: 'right'
};