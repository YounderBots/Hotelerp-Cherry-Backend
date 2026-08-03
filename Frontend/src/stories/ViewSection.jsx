// ViewSection.jsx
import React from 'react';
import './ViewSection.css';

const ViewSection = ({ title, children, className = '' }) => (
  <div className={['view-section', className].filter(Boolean).join(' ')}>
    {title && <h4 className="view-section__title">{title}</h4>}
    {children}
  </div>
);

export default ViewSection;
