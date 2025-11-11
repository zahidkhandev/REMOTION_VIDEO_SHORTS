import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    // Note: Per the eslint/config docs, `defineConfig` isn't a function,
    // but this structure is common with `eslint-define-config`.
    // Assuming you have the correct packages, this structure is fine.
    // If you run into issues, you might just want `export default [ ... ]`
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommended, // Spread the array
      reactHooks.configs["recommended-latest"],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020, // You can update this to 'latest' or 2022/2023 if you prefer
      sourceType: "module", // Good practice for modern JS
      globals: {
        ...globals.browser,
        ...globals.node, // Added node globals since this config will be read by node
      },
      parser: tseslint.parser, // Explicitly set the parser
      parserOptions: {
        project: "./tsconfig.app.json", // Point to your app's tsconfig
      },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "@typescript-eslint": tseslint,
    },
    rules: {
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  },
]);
