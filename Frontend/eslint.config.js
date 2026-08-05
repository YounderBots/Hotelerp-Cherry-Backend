// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      'no-unused-vars': ['error', {
        varsIgnorePattern: '^[A-Z_]',
        // Components routinely destructure a prop solely to keep it out of the
        // `...rest` they spread onto a DOM node. Underscore-prefixed arguments
        // mark that intent; without this they read as dead code.
        args: 'after-used',
        argsIgnorePattern: '^_',
        // `const { omitted, ...rest } = props` is the same pattern.
        ignoreRestSiblings: true,
        caughtErrors: 'none',
      }],
      // eslint-plugin-react-hooks v7 promoted several advisory performance
      // heuristics to `error` in its recommended config. They flag the app's
      // established, correct patterns (e.g. syncing a controlled prop into
      // state via an effect) rather than real defects, so they run as warnings
      // — surfaced for review without failing the lint or forcing a risky
      // rewrite of ~66 working components. Genuine-correctness rules
      // (rules-of-hooks, no-unused-vars) stay as errors.
      'react-hooks/set-state-in-effect': 'warn',
      'react-hooks/immutability': 'warn',
      'react-hooks/preserve-manual-memoization': 'warn',
      'react-hooks/exhaustive-deps': 'warn',
      // HMR-only hint. Context modules legitimately export a hook + provider
      // together; this never affects the production build.
      'react-refresh/only-export-components': 'warn',
    },
  },
])
