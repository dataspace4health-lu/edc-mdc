# Contributing to documentation

## In this guide

- [About this documentation](#about-this-documentation)
- [Documentation structure](#documentation-structure)
- [Set up your development environment](#set-up-your-development-environment)
- [Make contributions](#make-contributions)
- [Writing guidelines](#writing-guidelines)
- [Submit your changes](#submit-your-changes)
- [Review process](#review-process)

## About this documentation

This documentation is built using [Docusaurus](https://docusaurus.io/) with content written in Markdown. 

This documentation covers key concepts and guides for different audiences:

- **Key concepts**: Understand datasets, metadata, roles, and workflows
- **User guides**: Learn how to manage datasets, organisations, and vocabularies
- **Developer guides**: Set up development environments and contribute code
- **System admin guides**: Configure and maintain your Metadata Capture instance

## Documentation structure

The documentation is organized into several key sections:

```
docs/
├── intro.md                    # Welcome page and overview
├── key-concepts/              # Fundamental concepts users need to understand
│   ├── what-is-mdc.md
│   ├── datasets-and-metadata.md
│   ├── roles-and-permissions.md
│   └── the-dataset-record-lifecycle.md
├── user-guide/                # End-user documentation
│   ├── get-started/
│   ├── manage-datasets/
│   ├── manage-organisations/
│   ├── manage-roles/
│   └── manage-vocabularies/
├── developer-guide/           # Technical documentation for developers
│   ├── set-up-a-developer-env.md
│   ├── run-app-on-windows.md
│   ├── run-tests.md
│   └── ...
├── system-admin-guide/        # System administration documentation
└── CHANGELOG.md              # Release notes and version history
```

Each section contains a `_category_.json` file that defines the section's title, position, and other metadata.

## Set up your development environment

### Prerequisites

- **Node.js** (version 18 or higher)
- **npm** or **yarn**
- **Git**

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd dca-metadata-capture
   ```

2. **Navigate to the documentation directory**:
   ```bash
   cd documentation
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Start the development server**:
   ```bash
   npm start
   ```

This opens the documentation site at `http://localhost:3000` with live reload enabled.

### Available scripts

- `npm start` - Start development server with live reload
- `npm run build` - Build the static site for production
- `npm run serve` - Serve the built site locally
- `npm run clear` - Clear Docusaurus cache
- `npm run typecheck` - Run TypeScript type checking

## 

### Add new pages

1. **Create a new Markdown file** in the appropriate directory
2. **Add frontmatter** at the top of the file:
   ```markdown
   ---
   slug: your-page-slug
   title: "Your page title"
   sidebar_position: 3
   description: "Brief description for SEO"
   ---
   ```

3. **Update navigation** if needed by modifying `sidebars.ts` or the relevant `_category_.json`

#### Editing existing pages

1. **Navigate to the file** you want to edit
2. **Make your changes** following our [writing guidelines](#writing-guidelines)
3. **Test locally** using `npm start` to verify your changes look correct

#### Link to other pages

For each page, use the slug: `/title-of-the-page`

To link to this page, use any of the following formats depending on the section:
 
```markdown
[Link text](/user-guide/title-of-the-page)
[Link text](/developer/title-of-the-page)
[Link text](/system-admin/title-of-the-page)
```

### Work with images and assets

- Place images in `static/img/` directory
- Reference them in markdown as `/img/your-image.png`
- Optimize images for web (compress, appropriate format)
- Always include alt text for accessibility

### Add code examples

Use syntax highlighting for better readability:

```python
# Python example
def hello_world():
    print("Hello, World!")
```

```javascript
// JavaScript example
function helloWorld() {
    console.log("Hello, World!");
}
```

## Writing guidelines

### Grammar and formatting

- **Oxford commas**: Use Oxford commas (serial commas) in lists of three or more items
- **Sentence case for headings**: Use sentence case for all headings and titles
  - Do: "Set up your development environment"
  - Don't: "Set Up Your Development Environment"
- **Use verb phrases over gerunds**: When writing how-to guides, prefer titles with active verb phrases over gerunds in headings and instructions
  - Do: "Set up", "Log in", "Sign out"
  - Don't: "Setting up", "Logging in", "Signing out"
- **Table of contents**: Include an "In this guide" table of contents when a page has 3 or more main headings (H2 level)

### Style and tone

- **Clear and concise**: Write in simple, direct language
- **User-focused**: Write from the user's perspective
- **Consistent terminology**: Use the same terms throughout the documentation
- **Active voice**: Prefer active over passive voice, and present tense for instructions

### Structure

- **Use descriptive headings**: Make it easy to scan and navigate
- **Use action-oriented language**: Start instructions with verbs
- **Break up long content**: Use subheadings, bullet points, and short paragraphs
- **Provide context**: Start sections with brief introductions

### Admonitions or infoboxes

Docusaurus supports admonitions to highlight important information:

```markdown
:::tip
This is a helpful tip for users.
:::

:::warning
This is important information users should be aware of.
:::

:::danger
This is critical information that could cause problems if ignored.
:::
```

To see more of Docusaurus formatting and features, refer to the [Docusaurus documentation](https://docusaurus.io/doc).


### Content types

#### Tutorials
- **Step-by-step instructions**. Example: How to add a dataset
- **Expected outcomes** for each step
- **Screenshots or diagrams** where helpful
- **Troubleshooting section** for common issues

#### Reference documentation
- **Comprehensive coverage** of facts. Example: glossary, feature descriptions
- **Consistent formatting**
- **Examples for each feature**
- **Links to related concepts**

#### Conceptual content
- **Clear explanations** of complex topics. Example: What is Metadata Capture?
- **Real-world examples**
- **Diagrams or visuals** to illustrate concepts
- **Links to practical applications**

## Submit your changes

### Before submitting

1. **Test your changes**:
   ```bash
   npm start  # Verify content displays correctly
   npm run build  # Ensure no build errors
   npm run typecheck  # Check for TypeScript errors
   ```

2. **Check links**: Ensure all internal and external links work

3. **Review formatting**: Check that tables, lists, and code blocks display correctly

4. **Spell check**: Use a spell checker or grammar tool

### Creating a pull request

1. **Create a feature branch**:
   ```bash
   git checkout -b docs/your-feature-name
   ```

2. **Commit your changes**:
   ```bash
   git add .
   git commit -m "docs: Add guide for feature X"
   ```

3. **Push to your fork**:
   ```bash
   git push origin docs/your-feature-name
   ```

4. **Create a pull request** with:
   - **Clear title** describing the change
   - **Detailed description** of what you've added/changed
   - **Screenshots** if you've made visual changes
   - **Links to related issues**


## Review process

### What to expect

1. **Automated checks**: Your PR will run automated builds and checks
2. **Review by maintainers**: Core team members will review your contribution
3. **Feedback and iteration**: You may receive suggestions for improvements
4. **Merge**: Once approved, your changes will be merged

### Review criteria

Reviewers will check for:
- **Accuracy**: Is the information correct and up-to-date?
- **Clarity**: Is the content easy to understand?
- **Consistency**: Does it match existing style and terminology?
- **Completeness**: Are there any gaps or missing information?
- **Accessibility**: Is the content accessible to all users?

Thank you for helping make our documentation better!

---

For questions about contributing to the main codebase, see the main [CONTRIBUTING.md](../CONTRIBUTING.md) file in the repository root.