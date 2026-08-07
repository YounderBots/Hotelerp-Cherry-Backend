/// <reference types="vitest/config" />
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';
import { playwright } from '@vitest/browser-playwright';
// This config is ESM ("type": "module"), so __dirname does not exist here —
// referencing it at all was an undefined identifier guarded by a typeof check.
const dirname = path.dirname(fileURLToPath(import.meta.url));

// More info at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon
export default defineConfig(({ mode }) => {
  // The dev server's host/port come from Frontend/.env (VITE_ vars only, so no
  // backend secret is ever read here). start-network.ps1 generates that file
  // from the root .env; running `npm run dev` alone falls back to the defaults.
  const env = loadEnv(mode, dirname, 'VITE_');
  return {
  plugins: [react()],
  server: {
    host: env.VITE_DEV_HOST || '0.0.0.0',
    port: Number(env.VITE_DEV_PORT) || 5173,
    strictPort: true,
  },
  test: {
    projects: [{
      extends: true,
      plugins: [
      // The plugin will run tests for the stories defined in your Storybook config
      // See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
      storybookTest({
        configDir: path.join(dirname, '.storybook')
      })],
      test: {
        name: 'storybook',
        browser: {
          enabled: true,
          headless: true,
          provider: playwright({}),
          instances: [{
            browser: 'chromium'
          }]
        },
        setupFiles: ['.storybook/vitest.setup.js']
      }
    }]
  }
  };
});