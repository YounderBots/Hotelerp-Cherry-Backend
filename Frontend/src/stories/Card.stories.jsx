import React from 'react';
import { FaUser, FaChartLine, FaShoppingCart, FaExclamationTriangle, FaInfoCircle } from 'react-icons/fa';
import Card from './Card';

export default {
  title: 'Components/Card',
  component: Card,
  argTypes: {
    bgColor: {
      control: { type: 'text' },
      description: 'Background color (CSS variable, hex, rgb, or named color)'
    },
    textColor: {
      control: { type: 'text' },
      description: 'Text color override'
    },
    iconBg: {
      control: { type: 'text' },
      description: 'Icon background color'
    },
    fluid: {
      control: { type: 'boolean' },
      description: 'Full width card'
    },
    width: {
      control: { type: 'text' },
      description: 'Custom width'
    },
    value: {
      control: { type: 'text' },
      description: 'Main value (number animates, string displays as-is)'
    },
    label: {
      control: { type: 'text' },
      description: 'Label text'
    },
    className: {
      control: { type: 'text' },
      description: 'Additional CSS classes'
    }
  },
};

// Default Template
const Template = (args) => <Card {...args} />;

// Default Card
export const Default = Template.bind({});
Default.args = {
  value: 1247,
  label: 'Total Users',
  icon: <FaUser />
};

// Color Variants
export const Primary = Template.bind({});
Primary.args = {
  value: 324,
  label: 'New Orders',
  bgColor: 'var(--primary-color)',
  textColor: 'var(--white)',
  icon: <FaShoppingCart />
};

export const Success = Template.bind({});
Success.args = {
  value: 89,
  label: 'Success Rate',
  bgColor: 'var(--success-color)',
  textColor: 'var(--white)',
  icon: <FaChartLine />
};

export const Warning = Template.bind({});
Warning.args = {
  value: 12,
  label: 'Pending Issues',
  bgColor: 'var(--warning-color)',
  icon: <FaExclamationTriangle />
};

export const Error = Template.bind({});
Error.args = {
  value: 5,
  label: 'Critical Errors',
  bgColor: 'var(--error-color)',
  textColor: 'var(--white)',
  icon: <FaExclamationTriangle />
};

export const Info = Template.bind({});
Info.args = {
  value: 42,
  label: 'Notifications',
  bgColor: 'var(--info-color)',
  textColor: 'var(--white)',
  icon: <FaInfoCircle />
};

// Custom Background Colors
export const CustomColors = Template.bind({});
CustomColors.args = {
  value: 1567,
  label: 'Custom Styled',
  bgColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  textColor: '#ffffff',
  iconBg: 'rgba(255,255,255,0.2)',
  icon: <FaChartLine />
};

export const HexColor = Template.bind({});
HexColor.args = {
  value: 899,
  label: 'Hex Color Example',
  bgColor: '#4f46e5',
  textColor: '#ffffff',
  icon: <FaUser />
};

// Icon Variants
export const WithCustomIconBackground = Template.bind({});
WithCustomIconBackground.args = {
  value: 256,
  label: 'Custom Icon BG',
  iconBg: 'var(--primary-light)',
  textColor: 'var(--primary-dark)',
  icon: <FaChartLine />
};

export const WithoutIcon = Template.bind({});
WithoutIcon.args = {
  value: 2048,
  label: 'No Icon Card'
};

// Size and Layout Variants
export const FluidWidth = Template.bind({});
FluidWidth.args = {
  value: 100,
  label: 'Fluid Width Card',
  fluid: true,
  icon: <FaUser />
};

export const CustomWidth = Template.bind({});
CustomWidth.args = {
  value: 512,
  label: 'Custom Width (300px)',
  width: '300px',
  icon: <FaShoppingCart />
};

// String Values (No Animation)
export const StringValue = Template.bind({});
StringValue.args = {
  value: '$1,247.89',
  label: 'Revenue',
  icon: <FaChartLine />
};

export const PercentageValue = Template.bind({});
PercentageValue.args = {
  value: '98.5%',
  label: 'Uptime',
  bgColor: 'var(--success-color)',
  textColor: 'var(--white)',
  icon: <FaChartLine />
};

// Interactive Demo
export const InteractiveDemo = (args) => {
  const [value, setValue] = React.useState(1000);
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button onClick={() => setValue(500)}>Set to 500</button>
        <button onClick={() => setValue(1500)}>Set to 1500</button>
        <button onClick={() => setValue(2500)}>Set to 2500</button>
      </div>
      
      <Card {...args} value={value} />
    </div>
  );
};
InteractiveDemo.args = {
  label: 'Interactive Value',
  icon: <FaChartLine />
};

// Grid Layout Showcase
export const GridShowcase = () => (
  <div style={{ 
    display: 'grid', 
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
    gap: '20px',
    padding: '20px'
  }}>
    <Card value={1247} label="Total Users" icon={<FaUser />} />
    <Card value={324} label="New Orders" bgColor="var(--primary-color)" textColor="var(--white)" icon={<FaShoppingCart />} />
    <Card value={89} label="Success Rate" bgColor="var(--success-color)" textColor="var(--white)" icon={<FaChartLine />} />
    <Card value={12} label="Pending Issues" bgColor="var(--warning-color)" icon={<FaExclamationTriangle />} />
    <Card value={5} label="Critical Errors" bgColor="var(--error-color)" textColor="var(--white)" icon={<FaExclamationTriangle />} />
    <Card value="98.5%" label="Uptime" bgColor="var(--info-color)" textColor="var(--white)" icon={<FaInfoCircle />} />
  </div>
);

// Responsive Test
export const ResponsiveTest = () => (
  <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
      <Card value={1247} label="Fluid Card Example" fluid={true} icon={<FaUser />} />
      <Card value={324} label="Another Fluid Card" fluid={true} bgColor="var(--primary-color)" textColor="var(--white)" icon={<FaShoppingCart />} />
    </div>
  </div>
);

// Hover Effects Showcase
export const HoverEffects = () => (
  <div style={{ display: 'flex', gap: '20px', padding: '40px', flexWrap: 'wrap' }}>
    <Card value={1247} label="Hover Me" icon={<FaUser />} />
    <Card value={324} label="Hover Me Too" bgColor="var(--primary-color)" textColor="var(--white)" icon={<FaShoppingCart />} />
    <Card value={89} label="And Me" bgColor="var(--success-color)" textColor="var(--white)" icon={<FaChartLine />} />
  </div>
);