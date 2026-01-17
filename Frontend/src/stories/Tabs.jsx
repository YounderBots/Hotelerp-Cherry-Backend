import React, { useState, useRef, useEffect } from 'react';
import './Tabs.css';

// Tab Component
const Tab = ({ 
  label, 
  icon, 
  badge, 
  disabled = false, 
  children, 
  className = '',
  loading = false,
  ...props 
}) => {
  return (
    <div 
      className={`tab-panel ${className}`} 
      {...props}
    >
      {loading ? (
        <div className="tab-panel loading">
          <div className="tab-loading-spinner"></div>
        </div>
      ) : (
        children
      )}
    </div>
  );
};

// Main Tabs Component
const Tabs = ({
  children,
  defaultValue,
  value,
  onValueChange,
  variant = 'default',
  size = 'default',
  orientation = 'horizontal',
  scrollable = false,
  addable = false,
  removable = false,
  onTabAdd,
  onTabRemove,
  className = '',
  ...props
}) => {
  const [activeTab, setActiveTab] = useState(value || defaultValue || 0);
  const [tabs, setTabs] = useState(React.Children.toArray(children));
  const tabsHeaderRef = useRef(null);
  const tabsListRef = useRef(null);
  const [showScrollButtons, setShowScrollButtons] = useState(false);

  // Sync with controlled value
  useEffect(() => {
    if (value !== undefined) {
      setActiveTab(value);
    }
  }, [value]);

  // Check if scroll buttons are needed
  useEffect(() => {
    const checkScroll = () => {
      if (tabsHeaderRef.current && tabsListRef.current) {
        const headerWidth = tabsHeaderRef.current.offsetWidth;
        const listWidth = tabsListRef.current.scrollWidth;
        setShowScrollButtons(listWidth > headerWidth);
      }
    };

    checkScroll();
    window.addEventListener('resize', checkScroll);
    return () => window.removeEventListener('resize', checkScroll);
  }, [tabs]);

  const handleTabChange = (index) => {
    if (tabs[index]?.props.disabled) return;
    
    if (onValueChange) {
      onValueChange(index);
    }
    if (value === undefined) {
      setActiveTab(index);
    }
  };

  const handleAddTab = () => {
    const newTab = {
      props: {
        label: `Tab ${tabs.length + 1}`,
        children: `Content for Tab ${tabs.length + 1}`
      }
    };
    
    const newTabs = [...tabs, newTab];
    setTabs(newTabs);
    onTabAdd?.(newTabs.length - 1, newTab);
    handleTabChange(newTabs.length - 1);
  };

  const handleRemoveTab = (index, e) => {
    e.stopPropagation();
    
    if (tabs.length <= 1) return;
    
    const newTabs = tabs.filter((_, i) => i !== index);
    setTabs(newTabs);
    onTabRemove?.(index);
    
    if (activeTab === index) {
      const newActiveTab = index === 0 ? 0 : index - 1;
      handleTabChange(newActiveTab);
    } else if (activeTab > index) {
      setActiveTab(activeTab - 1);
    }
  };

  const scrollTabs = (direction) => {
    if (tabsHeaderRef.current) {
      const scrollAmount = 200;
      tabsHeaderRef.current.scrollBy({
        left: direction === 'next' ? scrollAmount : -scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  const tabsClass = `
    tabs-container
    ${variant !== 'default' ? `tabs-${variant}` : ''}
    ${size !== 'default' ? `tabs-${size}` : ''}
    ${orientation === 'vertical' ? 'tabs-vertical' : ''}
    ${scrollable ? 'tabs-scrollable' : ''}
    ${scrollable && showScrollButtons ? 'scrollable' : ''}
    ${className}
  `.trim();

  return (
    <div className={tabsClass} {...props}>
      <div className="tabs-header" ref={tabsHeaderRef}>
        {scrollable && showScrollButtons && (
          <button 
            className="tabs-scroll-btn prev"
            onClick={() => scrollTabs('prev')}
          >
            ‹
          </button>
        )}
        
        <div className={`tabs-list ${orientation}`} ref={tabsListRef}>
          {tabs.map((tab, index) => (
            <button
              key={index}
              className={`
                tab-trigger 
                ${orientation}
                ${activeTab === index ? 'active' : ''}
                ${tab.props.disabled ? 'disabled' : ''}
              `.trim()}
              onClick={() => handleTabChange(index)}
              disabled={tab.props.disabled}
            >
              {tab.props.icon && (
                <span className="tab-icon">{tab.props.icon}</span>
              )}
              {tab.props.label}
              {tab.props.badge && (
                <span className="tab-badge">{tab.props.badge}</span>
              )}
              {removable && tabs.length > 1 && (
                <button 
                  className="tab-remove-btn"
                  onClick={(e) => handleRemoveTab(index, e)}
                  title="Remove tab"
                >
                  ×
                </button>
              )}
            </button>
          ))}
        </div>

        {scrollable && showScrollButtons && (
          <button 
            className="tabs-scroll-btn next"
            onClick={() => scrollTabs('next')}
          >
            ›
          </button>
        )}

        {addable && (
          <button className="tabs-add-btn" onClick={handleAddTab} title="Add tab">
            +
          </button>
        )}
      </div>

      <div className="tabs-content">
        {tabs.map((tab, index) => (
          <div
            key={index}
            className={`
              tab-panel 
              ${activeTab === index ? 'active' : ''}
              ${tab.props.animation || ''}
            `.trim()}
          >
            {tab.props.children}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tabs;
export { Tab };