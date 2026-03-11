const designSystemConfig = require("@lnds-lu/design-system/tailwind.config.js");

/** @type {import('tailwindcss').Config} */
module.exports = {
  ...designSystemConfig,
  theme: {
    ...designSystemConfig.theme,
    extend: {
      ...designSystemConfig.theme?.extend,
      spacing: {
        ...designSystemConfig.theme?.extend?.spacing,
        128: "32rem",
        144: "36rem",
      },
    },
  },
  content: [
    "./node_modules/@lnds-lu/design-system/dist/**/*.{js,jsx,ts,tsx}",
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
};
