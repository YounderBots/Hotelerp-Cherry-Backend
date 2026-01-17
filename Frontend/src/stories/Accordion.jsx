import React, { useState } from "react";
import "./Accordion.css";
import { LuAArrowDown } from "react-icons/lu";
import { ChevronDown } from "lucide-react";

const AccordionItem = ({
  item,
  index,
  isOpen,
  onToggle,
  variant
}) => {
  const renderIcon = () => {
    return (
      <span className={`accordion-icon ${isOpen ? "open" : ""}`}>
        {/* Rotate handled by CSS */}
        <ChevronDown />
      </span>
    );
  };

  return (
    <div className={`accordion-item ${isOpen ? "open" : ""}`}>
      <div className={`accordion-header ${isOpen ? "open" : ""}`} onClick={onToggle}>
        <h3 className={`accordion-title ${isOpen ? "open" : ""}`}>{item.title}</h3>
        {renderIcon()}
      </div>

      <div className={`accordion-content ${isOpen ? "open" : ""}`}>
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
          index={index}
          isOpen={openItems.includes(index)}
          onToggle={() => toggleItem(index)}
          variant={variant}
        />
      ))}
    </div>
  );
};

export default Accordion;
