import React, { useId, useState } from "react";
import "./Accordion.css";
import { ChevronDown } from "lucide-react";

const AccordionItem = ({
  item,
  isOpen,
  onToggle,
}) => {
  // The header was a <div onClick>: not reachable by keyboard, not announced
  // as expandable, and invisible to screen readers as a control. A real
  // <button> restores Enter/Space and focus, and aria-expanded/aria-controls
  // tie it to the panel it opens.
  const panelId = useId();
  const headerId = useId();

  return (
    <div className={`accordion-item ${isOpen ? "open" : ""}`}>
      <h3 className="accordion-heading">
        <button
          type="button"
          id={headerId}
          className={`accordion-header ${isOpen ? "open" : ""}`}
          onClick={onToggle}
          aria-expanded={isOpen}
          aria-controls={panelId}
        >
          <span className={`accordion-title ${isOpen ? "open" : ""}`}>{item.title}</span>
          <span className={`accordion-icon ${isOpen ? "open" : ""}`} aria-hidden="true">
            {/* Rotation handled by CSS */}
            <ChevronDown />
          </span>
        </button>
      </h3>

      {/* `inert` rather than `hidden`: the collapse is animated with max-height,
          which `hidden` (display:none) would cut short. `inert` still removes
          the collapsed panel from the tab order and the accessibility tree. */}
      <div
        id={panelId}
        role="region"
        aria-labelledby={headerId}
        inert={!isOpen}
        className={`accordion-content ${isOpen ? "open" : ""}`}
      >
        <div className="accordion-content-inner">
          {item.content}
        </div>
      </div>
    </div>
  );
};

const Accordion = ({
  items = [],
  variant = "classic",
  allowMultiple = false,
  defaultOpen = [],
  bordered = true,
  size = "md"
}) => {
  const [openItems, setOpenItems] = useState(defaultOpen);

  const toggleItem = (index) => {
    if (allowMultiple) {
      setOpenItems((prev) =>
        prev.includes(index)
          ? prev.filter((i) => i !== index)
          : [...prev, index]
      );
    } else {
      setOpenItems((prev) =>
        prev.includes(index) ? [] : [index]
      );
    }
  };

  const wrapperClasses = [
    "accordion",
    `variant-${variant}`,
    `size-${size}`,
    !bordered ? "no-border" : ""
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={wrapperClasses}>
      {items.map((item, index) => (
        <AccordionItem
          key={index}
          item={item}
          isOpen={openItems.includes(index)}
          onToggle={() => toggleItem(index)}
        />
      ))}
    </div>
  );
};

export default Accordion;
