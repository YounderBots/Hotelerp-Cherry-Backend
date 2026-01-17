  // Modal.stories.jsx - Updated with new theme examples
  import React, { useState } from 'react';
  import Modal, { 
    AlertModal, 
    ConfirmModal, 
    DialogModal, 
    SheetModal, 
    DrawerModal,
    FormModal,
    ViewModal 
  } from './Modal';

  // Mock Button component matching the theme
  const Button = ({ 
    children, 
    onClick, 
    variant = 'primary', 
    size = 'medium',
    className = '',
    ...props 
  }) => (
    <button
      className={`btn ${className}`}
      onClick={onClick}
      {...props}
      style={{
        padding: '10px 18px',
        borderRadius: '10px',
        border: 'none',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: '600',
        transition: 'all 0.2s ease',
        backgroundColor: variant === 'primary' ? 'var(--primary-color)' : 
                        variant === 'secondary' ? 'var(--gray-100)' :
                        variant === 'error' ? 'var(--error-color)' : 'var(--gray-200)',
        color: variant === 'primary' ? 'var(--text-white)' :
              variant === 'secondary' ? 'var(--text-secondary)' :
              variant === 'error' ? 'var(--text-white)' : 'var(--text-primary)',
        ...(variant === 'primary' && {
          background: 'linear-gradient(135deg, var(--primary-color), var(--primary-mild))'
        }),
        ...props.style
      }}
      onMouseEnter={(e) => {
        if (variant === 'primary') {
          e.target.style.boxShadow = '0 6px 18px rgba(133, 1, 38, 0.35)';
        } else if (variant === 'secondary') {
          e.target.style.backgroundColor = 'var(--gray-200)';
        }
      }}
      onMouseLeave={(e) => {
        if (variant === 'primary') {
          e.target.style.boxShadow = 'none';
        } else if (variant === 'secondary') {
          e.target.style.backgroundColor = 'var(--gray-100)';
        }
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
      bodyLayout: {
        control: { type: 'select' },
        options: ['single', 'grid', 'custom'],
      },
    },
    parameters: {
      layout: 'fullscreen',
      docs: {
        description: {
          component: 'A versatile modal component updated to match the new Premium Maroon theme. Features grid layouts for forms, view modes, and MasterData.css compatibility.'
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

  // Basic Modal Story - Matches MasterData.css
  export const Basic = Template.bind({});
  Basic.args = {
    title: 'Basic Modal',
    children: (
      <div>
        <p>This modal uses the new Premium Maroon theme styling.</p>
        <p>It includes proper focus management, keyboard navigation, and accessibility features.</p>
      </div>
    ),
    showFooter: true,
    size: 'medium',
  };

  // MasterData Form Modal
  export const MasterDataForm = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    const formFields = [
      { name: 'countryName', label: 'Country Name', type: 'text', placeholder: 'Enter country name' },
      { name: 'currencySymbol', label: 'Currency Symbol', type: 'text', placeholder: 'Enter currency symbol' },
      { name: 'currencyName', label: 'Currency Name', type: 'text', placeholder: 'Enter currency name' },
      { name: 'currencyCode', label: 'Currency Code', type: 'text', placeholder: 'Enter ISO code' },
    ];
    
    const handleSubmit = (data) => {
      console.log('Form submitted:', data);
      alert('Form data: ' + JSON.stringify(data, null, 2));
      setIsOpen(false);
    };
    
    return (
      <div style={{ padding: '2rem' }}>
        <Button onClick={() => setIsOpen(true)}>Open Form Modal</Button>
        
        <Modal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          title="Add New Currency"
          size="large"
          bodyLayout="grid"
          showFooter={true}
          actions={[
            { label: 'Cancel', variant: 'secondary', onClick: () => setIsOpen(false) },
            { label: 'Save', variant: 'primary', onClick: () => handleSubmit({}) },
          ]}
        >
          {formFields.map((field) => (
            <div key={field.name} className="form-group">
              <label htmlFor={field.name}>{field.label}</label>
              <input
                id={field.name}
                type={field.type}
                placeholder={field.placeholder}
                style={{
                  padding: '11px 14px',
                  borderRadius: '10px',
                  border: '1px solid var(--border-dark)',
                  fontSize: '14px',
                  background: 'var(--bg-primary)',
                  transition: 'all 0.2s ease',
                  width: '100%'
                }}
              />
            </div>
          ))}
        </Modal>
      </div>
    );
  };

  // View Modal Example (like in MasterData)
  export const ViewModalExample = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    const viewData = {
      countryName: 'United States',
      currencySymbol: '$',
      currencyName: 'US Dollar',
      currencyCode: 'USD'
    };
    
    return (
      <div style={{ padding: '2rem' }}>
        <Button onClick={() => setIsOpen(true)} variant="secondary">View Currency Details</Button>
        
        <Modal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          title="View Currency"
          size="small"
          bodyLayout="single"
          viewMode={true}
          showFooter={true}
          actions={[
            { label: 'Close', variant: 'secondary', onClick: () => setIsOpen(false) },
          ]}
        >
          <div className="form-group">
            <label>Country Name</label>
            <input value={viewData.countryName} disabled />
          </div>

          <div className="form-group">
            <label>Currency Symbol</label>
            <input value={viewData.currencySymbol} disabled />
          </div>

          <div className="form-group">
            <label>Currency Name</label>
            <input value={viewData.currencyName} disabled />
          </div>

          <div className="form-group">
            <label>Currency Code</label>
            <input value={viewData.currencyCode} disabled />
          </div>
        </Modal>
      </div>
    );
  };

  // Modal Sizes with MasterData styling
  export const Sizes = () => {
    const [activeSize, setActiveSize] = useState(null);
    
    const sizes = [
      { size: 'small', label: 'Small (360px)', description: 'Perfect for simple confirmations and alerts' },
      { size: 'medium', label: 'Medium (420px)', description: 'Default size for most use cases' },
      { size: 'large', label: 'Large (720px)', description: 'Ideal for forms and detailed content' },
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
              { label: 'Close', variant: 'secondary', onClick: () => setActiveSize(null) }
            ]}
          >
            <div>
              <p><strong>Size:</strong> {size}</p>
              <p><strong>Description:</strong> {description}</p>
              <p>This modal demonstrates the <em>{size}</em> size variant.</p>
            </div>
          </Modal>
        ))}
      </div>
    );
  };

  // Alert Modals with theme styling
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

  // Confirmation Modal with destructive action
  export const DeleteConfirmation = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    const handleDelete = () => {
      alert('Item deleted!');
      setIsOpen(false);
    };
    
    return (
      <div style={{ padding: '2rem' }}>
        <Button onClick={() => setIsOpen(true)} variant="error">Delete Item</Button>
        
        <ConfirmModal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          onConfirm={handleDelete}
          title="Confirm Deletion"
          confirmText="Delete"
          cancelText="Cancel"
          destructive={true}
        >
          <p>Are you sure you want to delete this item?</p>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            This action cannot be undone. All associated data will be permanently removed.
          </p>
        </ConfirmModal>
      </div>
    );
  };

  // Grid Layout Modal (like MasterData forms)
  export const GridLayoutModal = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    const formFields = [
      { label: 'First Name', placeholder: 'Enter first name' },
      { label: 'Last Name', placeholder: 'Enter last name' },
      { label: 'Email', placeholder: 'Enter email address', type: 'email' },
      { label: 'Phone', placeholder: 'Enter phone number', type: 'tel' },
      { label: 'Department', placeholder: 'Select department' },
      { label: 'Role', placeholder: 'Select role' },
    ];
    
    return (
      <div style={{ padding: '2rem' }}>
        <Button onClick={() => setIsOpen(true)}>Open Grid Form</Button>
        
        <Modal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          title="Employee Details"
          size="large"
          bodyLayout="grid"
          showFooter={true}
          actions={[
            { label: 'Cancel', variant: 'secondary', onClick: () => setIsOpen(false) },
            { label: 'Save Employee', variant: 'primary', onClick: () => setIsOpen(false) },
          ]}
        >
          {formFields.map((field, index) => (
            <div key={index} className="form-group">
              <label>{field.label}</label>
              <input
                type={field.type || 'text'}
                placeholder={field.placeholder}
                style={{
                  padding: '11px 14px',
                  borderRadius: '10px',
                  border: '1px solid var(--border-dark)',
                  fontSize: '14px',
                  background: 'var(--bg-primary)',
                  transition: 'all 0.2s ease',
                  width: '100%'
                }}
              />
            </div>
          ))}
        </Modal>
      </div>
    );
  };

  // Using FormModal component
  export const FormModalExample = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    const formFields = [
      { name: 'roomType', label: 'Room Type', type: 'text', placeholder: 'Enter room type' },
      { name: 'description', label: 'Description', type: 'text', placeholder: 'Enter description' },
      { name: 'basePrice', label: 'Base Price', type: 'number', placeholder: 'Enter base price' },
      { name: 'maxOccupancy', label: 'Max Occupancy', type: 'number', placeholder: 'Enter max occupancy' },
      { name: 'bedType', label: 'Bed Type', type: 'select', options: [
        { value: 'single', label: 'Single' },
        { value: 'double', label: 'Double' },
        { value: 'queen', label: 'Queen' },
        { value: 'king', label: 'King' },
      ]},
      { name: 'status', label: 'Status', type: 'select', options: [
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' },
        { value: 'maintenance', label: 'Under Maintenance' },
      ]},
    ];
    
    const handleSubmit = (data) => {
      console.log('Form submitted:', data);
      alert('Room Type saved: ' + JSON.stringify(data, null, 2));
      setIsOpen(false);
    };
    
    return (
      <div style={{ padding: '2rem' }}>
        <Button onClick={() => setIsOpen(true)}>Add Room Type</Button>
        
        <FormModal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          onSubmit={handleSubmit}
          onCancel={() => setIsOpen(false)}
          title="Add New Room Type"
          fields={formFields}
          size="large"
        />
      </div>
    );
  };

  // Using ViewModal component
  export const ViewModalExampleComponent = () => {
    const [isOpen, setIsOpen] = useState(false);
    
    const viewData = {
      roomType: 'Deluxe Suite',
      description: 'Spacious suite with ocean view',
      basePrice: '$299',
      maxOccupancy: '4',
      bedType: 'King',
      status: 'Active'
    };
    
    const viewFields = [
      { name: 'roomType', label: 'Room Type' },
      { name: 'description', label: 'Description' },
      { name: 'basePrice', label: 'Base Price' },
      { name: 'maxOccupancy', label: 'Max Occupancy' },
      { name: 'bedType', label: 'Bed Type' },
      { name: 'status', label: 'Status' },
    ];
    
    return (
      <div style={{ padding: '2rem' }}>
        <Button onClick={() => setIsOpen(true)} variant="secondary">View Room Details</Button>
        
        <ViewModal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          title="Room Type Details"
          data={viewData}
          fields={viewFields}
          size="medium"
        />
      </div>
    );
  };

  // Interactive Playground
  export const Playground = Template.bind({});
  Playground.args = {
    title: 'Modal Playground',
    children: (
      <div>
        <p>Use the controls in the Storybook panel to experiment with different modal configurations.</p>
        <p>This playground allows you to test various combinations of props.</p>
        <div className="form-group" style={{ marginTop: '1.5rem' }}>
          <label>Example Input Field</label>
          <input type="text" placeholder="Type something..." />
        </div>
      </div>
    ),
    variant: 'default',
    size: 'medium',
    type: 'modal',
    bodyLayout: 'single',
    showHeader: true,
    showFooter: true,
    showCloseButton: true,
    closeOnBackdropClick: true,
    closeOnEscape: true,
    footerAlign: 'right'
  };