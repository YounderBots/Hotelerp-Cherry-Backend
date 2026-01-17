/** @type { import('@storybook/react-vite').Preview } */
import { withThemeByClassName } from '@storybook/addon-themes';
import './preview.css'; // loads variables into Storybook iframe
const preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
   docs: {
    source: { type: 'code' }, // enables code preview
  },

  decorators: [
    withThemeByClassName({
      themes: {
        light: 'light', // applies class="light"
        // dark: 'dark',   // applies class="dark"
      },
      defaultTheme: 'light',
      parentSelector: 'body',
    }),
  ],
   tags: ['autodocs'],
};

export default preview;