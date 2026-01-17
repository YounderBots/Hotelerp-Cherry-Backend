// Form.stories.jsx
import React, { useState } from 'react';
import Input from './Input';
import Textarea from './Textarea';
import Select from './Select';
import  Checkbox,{CheckboxGroup}  from './Checkbox';
import  Radio, {RadioGroup } from './Radio';
import Switch from './Switch';
import Form from './Form';
import Button from '../Button';

export default {
  title: 'Components/Forms',
};

// Input Stories
export const TextInput = () => {
  const [value, setValue] = useState('');
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Input
        label="Username"
        placeholder="Enter your username"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        helperText="Choose a unique username"
      />
    </div>
  );
};

export const InputStates = () => {
  const [value, setValue] = useState('');
  return (
    <div style={{ maxWidth: '400px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Input
        label="Normal Input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <Input
        label="Disabled Input"
        value="Disabled text"
        disabled
      />
      <Input
        label="Error Input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        error
        helperText="This field is required"
      />
      <Input
        label="Success Input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        success
        helperText="Valid input"
      />
      <Input
        label="With Icon"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        icon="🔍"
        placeholder="Search..."
      />
    </div>
  );
};

export const PasswordInput = () => {
  const [password, setPassword] = useState('');
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Input
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        helperText="At least 8 characters"
      />
    </div>
  );
};

export const InputSizes = () => {
  const [value, setValue] = useState('');
  return (
    <div style={{ maxWidth: '400px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Input
        label="Small Input"
        size="small"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Small size"
      />
      <Input
        label="Medium Input (Default)"
        size="medium"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Medium size"
      />
      <Input
        label="Large Input"
        size="large"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Large size"
      />
    </div>
  );
};

// Textarea Stories
export const TextareaBasic = () => {
  const [value, setValue] = useState('');
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Textarea
        label="Description"
        placeholder="Enter your description"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        helperText="Describe in detail"
        rows={4}
      />
    </div>
  );
};

export const TextareaWithCounter = () => {
  const [value, setValue] = useState('');
  const maxLength = 200;
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Textarea
        label="Bio"
        placeholder="Tell us about yourself"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        maxLength={maxLength}
        helperText={`Maximum ${maxLength} characters`}
        rows={3}
      />
    </div>
  );
};

// Select Stories
export const SelectBasic = () => {
  const [selected, setSelected] = useState('');
  
  const options = [
    { value: '', label: 'Select a country', disabled: true },
    { value: 'us', label: 'United States' },
    { value: 'ca', label: 'Canada' },
    { value: 'uk', label: 'United Kingdom' },
    { value: 'au', label: 'Australia' },
  ];
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Select
        label="Country"
        options={options}
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
        helperText="Select your country"
      />
    </div>
  );
};

export const MultiSelect = () => {
  const [selected, setSelected] = useState([]);

  const options = [
    { value: 'react', label: 'React' },
    { value: 'vue', label: 'Vue' },
    { value: 'angular', label: 'Angular' },
    { value: 'svelte', label: 'Svelte' },
  ];

  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Select
        label="Select frameworks"
        options={options}
        value={selected}
        multiple
        onChange={(e) => {
          setSelected(e.target.value); // ✅ ARRAY
        }}
        helperText="Select one or more frameworks"
      />
    </div>
  );
};


// Checkbox Stories
export const CheckboxBasic = () => {
  const [checked, setChecked] = useState(false);
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Checkbox
        label="I agree to the terms and conditions"
        checked={checked}
        onChange={(e) => setChecked(e.target.checked)}
        helperText="You must agree to continue"
      />
    </div>
  );
};

export const CheckboxGroupExample = () => {
  const [selected, setSelected] = useState([]);
  
  const options = [
    { value: 'email', label: 'Email notifications' },
    { value: 'sms', label: 'SMS notifications' },
    { value: 'push', label: 'Push notifications' },
    { value: 'newsletter', label: 'Newsletter' },
  ];
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <CheckboxGroup
        label="Notification Preferences"
        options={options}
        value={selected}
        onChange={setSelected}
        helperText="Choose how you want to receive notifications"
      />
    </div>
  );
};

// Radio Stories
export const RadioBasic = () => {
  const [selected, setSelected] = useState('');
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Radio
        label="Option 1"
        checked={selected === 'option1'}
        onChange={() => setSelected('option1')}
        name="radio-group"
        value="option1"
      />
      <Radio
        label="Option 2"
        checked={selected === 'option2'}
        onChange={() => setSelected('option2')}
        name="radio-group"
        value="option2"
      />
    </div>
  );
};

export const RadioGroupExample = () => {
  const [selected, setSelected] = useState('option1');
  
  const options = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' },
    { value: 'option4', label: 'Option 4' },
  ];
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <RadioGroup
        label="Vertical Radio Group"
        options={options}
        value={selected}
        onChange={setSelected}
        layout="vertical"
        helperText="Select one option"
      />
      
      <RadioGroup
        label="Horizontal Radio Group"
        options={options.slice(0, 3)}
        value={selected}
        onChange={setSelected}
        layout="horizontal"
      />
    </div>
  );
};

// Switch Stories
export const SwitchBasic = () => {
  const [enabled, setEnabled] = useState(false);
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem' }}>
      <Switch
        label="Enable notifications"
        checked={enabled}
        onChange={(e) => setEnabled(e.target.checked)}
        helperText="Receive notifications about updates"
      />
    </div>
  );
};

export const SwitchSizes = () => {
  const [small, setSmall] = useState(false);
  const [medium, setMedium] = useState(true);
  const [large, setLarge] = useState(false);
  
  return (
    <div style={{ maxWidth: '400px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Switch
        label="Small Switch"
        checked={small}
        onChange={(e) => setSmall(e.target.checked)}
        size="small"
      />
      <Switch
        label="Medium Switch (Default)"
        checked={medium}
        onChange={(e) => setMedium(e.target.checked)}
        size="medium"
      />
      <Switch
        label="Large Switch"
        checked={large}
        onChange={(e) => setLarge(e.target.checked)}
        size="large"
      />
    </div>
  );
};

// Complete Form Example
export const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    country: '',
    bio: '',
    notifications: [],
    subscription: 'free',
    terms: false,
    newsletter: true,
  });

  const countries = [
    { value: '', label: 'Select a country', disabled: true },
    { value: 'us', label: 'United States' },
    { value: 'ca', label: 'Canada' },
    { value: 'uk', label: 'United Kingdom' },
    { value: 'au', label: 'Australia' },
  ];

  const notificationOptions = [
    { value: 'email', label: 'Email' },
    { value: 'sms', label: 'SMS' },
    { value: 'push', label: 'Push' },
  ];

  const subscriptionOptions = [
    { value: 'free', label: 'Free' },
    { value: 'pro', label: 'Pro ($9.99/month)' },
    { value: 'enterprise', label: 'Enterprise ($49.99/month)' },
  ];

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    alert('Form submitted successfully!');
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
      <Form
        title="Create Account"
        subtitle="Join our community today"
        onSubmit={handleSubmit}
        submitLabel="Sign Up"
      >
        <div className="form-row">
          <Input
            label="First Name"
            required
            value={formData.firstName}
            onChange={(e) => handleChange('firstName', e.target.value)}
            placeholder="John"
          />
          <Input
            label="Last Name"
            required
            value={formData.lastName}
            onChange={(e) => handleChange('lastName', e.target.value)}
            placeholder="Doe"
          />
        </div>

        <Input
          label="Email Address"
          type="email"
          required
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          placeholder="john@example.com"
          helperText="We'll never share your email"
        />

        <Input
          label="Password"
          type="password"
          required
          value={formData.password}
          onChange={(e) => handleChange('password', e.target.value)}
          helperText="At least 8 characters with letters and numbers"
        />

        <Select
          label="Country"
          required
          options={countries}
          value={formData.country}
          onChange={(e) => handleChange('country', e.target.value)}
        />

        <Textarea
          label="About You"
          value={formData.bio}
          onChange={(e) => handleChange('bio', e.target.value)}
          placeholder="Tell us about yourself..."
          maxLength={500}
          rows={3}
        />

        <CheckboxGroup
          label="Notification Preferences"
          options={notificationOptions}
          value={formData.notifications}
          onChange={(value) => handleChange('notifications', value)}
          helperText="Choose how you want to be notified"
        />

        <RadioGroup
          label="Subscription Plan"
          required
          options={subscriptionOptions}
          value={formData.subscription}
          onChange={(value) => handleChange('subscription', value)}
          layout="vertical"
        />

        <div className="form-row">
          <Checkbox
            label="I agree to the Terms of Service"
            required
            checked={formData.terms}
            onChange={(e) => handleChange('terms', e.target.checked)}
          />
          
          <Switch
            label="Subscribe to newsletter"
            checked={formData.newsletter}
            onChange={(e) => handleChange('newsletter', e.target.checked)}
          />
        </div>
      </Form>
    </div>
  );
};

// Form Layout Examples
export const TwoColumnForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    zip: '',
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Form
      title="Contact Information"
      onSubmit={() => alert('Submitted!')}
      submitLabel="Save Changes"
    >
      <div className="form-row">
        <Input
          label="Full Name"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="John Doe"
        />
        <Input
          label="Email"
          type="email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          placeholder="john@example.com"
        />
      </div>

      <div className="form-row">
        <Input
          label="Phone Number"
          type="tel"
          value={formData.phone}
          onChange={(e) => handleChange('phone', e.target.value)}
          placeholder="(123) 456-7890"
        />
        <Input
          label="Address"
          value={formData.address}
          onChange={(e) => handleChange('address', e.target.value)}
          placeholder="123 Main St"
        />
      </div>

      <div className="form-row">
        <Input
          label="City"
          value={formData.city}
          onChange={(e) => handleChange('city', e.target.value)}
          placeholder="New York"
        />
        <Input
          label="ZIP Code"
          value={formData.zip}
          onChange={(e) => handleChange('zip', e.target.value)}
          placeholder="10001"
        />
      </div>
    </Form>
  );
};

// Input Variations
export const InputVariations = () => {
  const [value, setValue] = useState('');
  
  return (
    <div style={{ maxWidth: '500px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <Input
        label="With Left Icon"
        icon="$"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="0.00"
        helperText="Amount in USD"
      />
      
      <Input
        label="With Prepended Text"
        prepend="https://"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="example.com"
        helperText="Enter your website URL"
      />
      
      <Input
        label="With Appended Text"
        append="kg"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="0"
        helperText="Weight in kilograms"
      />
      
      <Input
        label="With Icon and Error"
        icon="✉️"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="invalid email"
        error
        helperText="Please enter a valid email address"
      />
    </div>
  );
};

// All Form Elements
export const AllFormElements = () => {
  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
      <h2 style={{ marginBottom: '1.5rem', color: 'var(--text-primary)' }}>All Form Elements</h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <Input
          label="Text Input"
          placeholder="Enter text"
        />
        
        <Input
          label="Password Input"
          type="password"
          placeholder="Enter password"
        />
        
        <Select
          label="Select Dropdown"
          options={[
            { value: 'option1', label: 'Option 1' },
            { value: 'option2', label: 'Option 2' },
            { value: 'option3', label: 'Option 3' },
          ]}
        />
        
        <Textarea
          label="Textarea"
          placeholder="Enter multi-line text"
          rows={3}
        />
        
        <CheckboxGroup
          label="Checkbox Group"
          options={[
            { value: 'check1', label: 'Checkbox 1' },
            { value: 'check2', label: 'Checkbox 2' },
            { value: 'check3', label: 'Checkbox 3' },
          ]}
        />
        
        <RadioGroup
          label="Radio Group"
          options={[
            { value: 'radio1', label: 'Radio 1' },
            { value: 'radio2', label: 'Radio 2' },
            { value: 'radio3', label: 'Radio 3' },
          ]}
        />
        
        <Switch
          label="Toggle Switch"
        />
        
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
          <Button variant="ghost">Cancel</Button>
          <Button variant="primary">Submit</Button>
        </div>
      </div>
    </div>
  );
};