import Accordion from "./Accordion";
import "./Accordion.css";

const sampleItems = [
  { title: "What is your return policy?", content: "We offer a 30-day return policy..." },
  { title: "How long does shipping take?", content: "Standard shipping takes 5-7 business days..." },
  { title: "Do you ship internationally?", content: "Yes, to 50+ countries..." },
  { title: "How can I track my order?", content: "A tracking number will be emailed..." }
];

export default {
  title: "Components/Accordion",
  component: Accordion,
  tags: ["docsPage"],
  parameters: {
    docs: {
      description: {
        component: `
A flexible Accordion component with multiple design variants and smooth animations.
Fully themed using CSS variables from **index.css** with automatic light/dark mode support.
        `
      }
    }
  },
  argTypes: {
    variant: {
      control: "select",
      options: ["classic", "minimal", "filled", "bordered", "elegant", "card"],
      description: "Visual styles for accordion",
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
      description: "Size of the accordion",
    },
    allowMultiple: {
      control: "boolean",
      description: "Allow multiple items to be expanded",
    },
    bordered: {
      control: "boolean",
      description: "Enable/disable border styling",
    },
    defaultOpen: {
      control: "object",
      description: "Indexes of items opened by default",
    },
    items: {
      control: false,
      description: "Array of accordion panels including title and content",
    }
  }
};

const Template = (args) => <Accordion {...args} />;

/* === PRIMARY STORY === */
export const Playground = Template.bind({});
Playground.args = {
  items: sampleItems,
  variant: "classic",
  size: "md",
  allowMultiple: false,
  bordered: true,
  defaultOpen: [0]
};

Playground.parameters = {
  docs: {
    description: {
      story: "Play around using the controls to explore component variants."
    }
  }
};

/* === INDIVIDUAL VARIANT PRESETS === */
export const Classic = Template.bind({});
Classic.args = { ...Playground.args, variant: "classic" };

export const Minimal = Template.bind({});
Minimal.args = { ...Playground.args, variant: "minimal" };

export const Filled = Template.bind({});
Filled.args = { ...Playground.args, variant: "filled" };

export const Bordered = Template.bind({});
Bordered.args = { ...Playground.args, variant: "bordered" };

export const Elegant = Template.bind({});
Elegant.args = { ...Playground.args, variant: "elegant" };

export const Card = Template.bind({});
Card.args = { ...Playground.args, variant: "card" };

export const AllowMultiple = Template.bind({});
AllowMultiple.args = {
  ...Playground.args,
  allowMultiple: true,
  defaultOpen: [0, 2]
};

export const Sizes = Template.bind({});
Sizes.args = {
  ...Playground.args,
  size: "lg"
};
Sizes.parameters = {
  docs: {
    description: {
      story: "Change sizes using the control. Small, Medium & Large styling support."
    }
  }
};
