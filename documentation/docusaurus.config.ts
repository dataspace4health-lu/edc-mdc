import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: "Metadata Capture Documentation",
  tagline: "Documentation for the Metadata Capture Application",
  favicon: "img/favicon.svg",

  // Set the production url of your site here
  url: process.env.DOCS_URL || "https://your-docusaurus-site.example.com",
  // Set the /<baseUrl>/ pathname under which your site is served
  // Use environment variable to support both app hosting (/docs/) and GitLab Pages (/)
  baseUrl: process.env.DOCS_BASE_URL || "/docs/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "lnds-lu/", // Usually your GitHub org/user name.
  projectName: "dca-metadata-capture", // Usually your repo name.

  onBrokenLinks: "warn",

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: "warn",
    },
  },
  themes: ["@docusaurus/theme-mermaid"],
  presets: [
    [
      "classic",
      {
        docs: {
          id: "user-guide",
          path: "docs-user-guide",
          routeBasePath: "/user-guide",
          sidebarPath: "./sidebars-user-guide.ts",
          async sidebarItemsGenerator({defaultSidebarItemsGenerator, ...args}) {
            const sidebarItems = await defaultSidebarItemsGenerator(args);
            // Filter out documentation-tracker.md from sidebar
            return sidebarItems.filter((item) => item.type !== 'doc' || item.id !== 'documentation-tracker');
          },
        },
        blog: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          // Redirect old workflow path to new record lifecycle path
          {
            from: '/user-guide/key-concepts/the-dataset-workflow',
            to: '/user-guide/key-concepts/the-dataset-record-lifecycle',
          },
        ],
      },
    ],

    [
      require.resolve("docusaurus-lunr-search"),
      {
        languages: ["en"],
        indexBaseUrl: true,
        enableHighlight: true,
        // Configure scoped search for different documentation sections
        searchResultLimits: 8,
        searchResultContextMaxLength: 50,
        // Enable filtering by route path
        filterByDocId: true,
      },
    ],
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "system-admin",
        path: "docs-system-admin",
        routeBasePath: "/system-admin",
        sidebarPath: "./sidebars-system-admin.ts",
      },
    ],
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "developer",
        path: "docs-developer",
        routeBasePath: "/developer",
        sidebarPath: "./sidebars-developer.ts",
      },
    ],
  ],

  clientModules: [
    require.resolve('./src/client/searchInit.js'),
  ],

  themeConfig: {
    // Top navigation bar - alight right
    navbar: {
      title: " Metadata Capture Documentation", // Upper left side title next to logo
      logo: {
        alt: "Logo",
        src: "img/logo.svg",
      },
      items: [
        {
          type: "docSidebar",
          sidebarId: "userGuideSidebar",
          docsPluginId: "user-guide",
          position: "right",
          label: "Users",
        },
        {
          type: "docSidebar",
          sidebarId: "systemAdminSidebar",
          docsPluginId: "system-admin",
          position: "right",
          label: "System admins",
        },
        {
          type: "docSidebar",
          sidebarId: "developerSidebar",
          docsPluginId: "developer",
          position: "right",
          label: "Developers",
        },
        {
          type: "search",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          html: `
            <div style="color: #b3b3b3;">
              <a href="https://metadata.demo.lnds.tech/" target="_blank" rel="noopener noreferrer" style="color: #b3b3b3;">Demo↗</a>
              <span>&nbsp; &nbsp; &nbsp;|&nbsp; &nbsp; &nbsp;</span>
              <a href="https://gitlab.com/lnds-lu/service-library/dca-metadata-capture" target="_blank" rel="noopener noreferrer" style="color: #b3b3b3;">Source code↗</a>
              <span> &nbsp; &nbsp; &nbsp;|&nbsp; &nbsp; &nbsp; </span>
              <a href="${process.env.DOCS_BASE_URL || "/docs/"}developer/CHANGELOG" style="color: #b3b3b3;">Changelog</a>
              <span> &nbsp; &nbsp; &nbsp;|&nbsp; &nbsp; &nbsp;</span>
              <a href="https://www.lnds.lu/" target="_blank" rel="noopener noreferrer" style="color: #b3b3b3;">About LNDS↗</a>
              <span>&nbsp; &nbsp; &nbsp;|&nbsp; &nbsp; &nbsp;    </span>
              <a href="https://service.desk.lnds.lu/" target="_blank" rel="noopener noreferrer" style="color: #b3b3b3;">Contact support↗</a>
            </div>
          `,
        },
      ],
      copyright: `${new Date().getFullYear()} Luxembourg National Data Service (LNDS). It is a brand of PNED G.I.E., an economic interest group established by the Luxembourg government and public institutes 2023 <br/> All rights reserved <br/>`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
