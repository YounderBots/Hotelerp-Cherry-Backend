// ErrorAlert.stories.jsx
import React from 'react';
import ErrorAlert from './ErrorAlert';

export default {
  title: 'Components/ErrorAlert',
  component: ErrorAlert,
};

export const Default = () => <ErrorAlert message="Discount name already exists for this company." />;
