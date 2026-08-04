// ViewSection.stories.jsx
import React from 'react';
import ViewSection from './ViewSection';

export default {
  title: 'Components/ViewSection',
  component: ViewSection,
};

export const Default = () => (
  <ViewSection title="Pricing">
    <p>Price: 320</p>
    <p>Cost Price: 128</p>
  </ViewSection>
);
