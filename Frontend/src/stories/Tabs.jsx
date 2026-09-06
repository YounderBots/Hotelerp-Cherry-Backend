import React, { useState, useRef, useEffect } from 'react';
import './Tabs.css';

// Tab Component
//
// `label`, `icon`, `badge` and `disabled` are read by the parent <Tabs> off
// `child.props` to build the tab header — this component only renders the
// panel body. They are destructured here purely so `...props` does not spread
// them onto the <div>, which React would warn about as unknown DOM attributes.
// The leading underscore marks them as deliberately unused.
const Tab = ({
  label: _label,
  icon: _icon,
  badge: _badge,
  disabled: _disabled = false,
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
  const [atStart, setAtStart] = useState(true);
  const [atEnd, setAtEnd] = useState(false);

  // Sync with controlled value
  useEffect(() => {
    if (value !== undefined) {
      setActiveTab(value);
    }
  }, [value]);

  // Re-sync when the parent re-renders with new tab content (e.g. a tab's
  // children reflecting freshly-fetched data). Without this, `tabs` stays
  // frozen at whatever `children` looked like on first mount.
  useEffect(() => {
    setTabs(React.Children.toArray(children));
  }, [children]);

  // Whether the tab strip overflows, and which way it can still be scrolled.
  //
  // The overflow test was always here and always correct. What was missing is
  // that the BUTTONS only rendered if the page had opted in with
  // `scrollable`, so a page with more tabs than fit -- Add Reservation, with
  // one tab per room type -- clipped the last label mid-word and offered
  // nothing to click. The header scrolls by wheel and touch, but
  // `scrollbar-width: none` hides even the scrollbar that would hint at it.
  //
  // Overflow is a fact about the rendered strip, not a decision for the
  // caller, so the buttons now follow the measurement.
  useEffect(() => {
    const header = tabsHeaderRef.current;
    const checkScroll = () => {
      if (!header || !tabsListRef.current) return;
      const overflowing = tabsListRef.current.scrollWidth > header.offsetWidth + 1;
      setShowScrollButtons(overflowing);
      setAtStart(header.scrollLeft <= 1);
      setAtEnd(header.scrollLeft + header.offsetWidth >= header.scrollWidth - 1);
    };

    checkScroll();
    window.addEventListener('resize', checkScroll);
    header?.addEventListener('scroll', checkScroll, { passive: true });
    return () => {
      window.removeEventListener('resize', checkScroll);
      header?.removeEventListener('scroll', checkScroll);
    };
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
    ${scrollable || showScrollButtons ? 'tabs-scrollable' : ''}
    ${showScrollButtons ? 'scrollable' : ''}
    ${className}
  `.trim();

  return (
    <div className={tabsClass} {...props}>
      <div className="tabs-header" ref={tabsHeaderRef}>
        {showScrollButtons && !atStart && (
          <button
            type="button"
            className="tabs-scroll-btn prev"
            onClick={() => scrollTabs('prev')}
            aria-label="Scroll tabs left"
            data-glyph="‹"
          />
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

        {showScrollButtons && !atEnd && (
          <button
            type="button"
            className="tabs-scroll-btn next"
            onClick={() => scrollTabs('next')}
            aria-label="Scroll tabs right"
            data-glyph="›"
          />
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