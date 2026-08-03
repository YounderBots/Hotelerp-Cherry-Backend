// Toast.stories.jsx
import React from 'react';
import Toast from './Toast';

export default {
  title: 'Components/Toast',
  component: Toast,
  argTypes: {
    type: {
      control: { type: 'select' },
      options: ['success', 'update', 'delete', 'error'],
    },
  },
};

const Template = (args) => <Toast {...args} />;

export const Success = Template.bind({});
Success.args = { show: true, type: 'success', message: 'Discount Type added successfully' };

export const Update = Template.bind({});
Update.args = { show: true, type: 'update', message: 'Discount Type updated successfully' };

export const Delete = Template.bind({});
Delete.args = { show: true, type: 'delete', message: 'Discount Type deleted successfully' };

export const Error = Template.bind({});
Error.args = { show: true, type: 'error', message: 'Something went wrong' };
