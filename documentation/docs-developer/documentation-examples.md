---
sidebar_label: "Documentation examples"
sidebar_position: 99
description: "Examples and reference guide for writing documentation in this project."
---
import useBaseUrl from '@docusaurus/useBaseUrl';

# Documentation examples

This page provides examples and best practices for common documentation patterns used in this project.

## Images

### Basic image syntax

Use the `<img>` tag with `useBaseUrl` to add images to documentation:

```markdown
<img src={useBaseUrl('/path/to/image.png')} alt="Descriptive alt text" width="750" />
```

**Components:**
- **src:** Use `{useBaseUrl('/path/to/image.png')}` for proper path resolution
- **alt:** Descriptive text for accessibility (required)
- **width:** Typically `750` for screenshots, adjust as needed

### Image examples

#### Screenshot with descriptive alt text

```markdown
<img src={useBaseUrl('/manage-datasets/add-dataset.png')} alt="Screenshot of the add dataset button" width="750" />
```

#### Smaller image for UI elements

```markdown
<img src={useBaseUrl('/icons/edit-icon.png')} alt="Edit icon" width="24" />
```

#### Diagram or illustration

```markdown
<img src={useBaseUrl('/diagrams/dataset-lifecycle.png')} alt="Diagram showing the dataset lifecycle from draft to published" width="600" />
```

### Best practices for images

- **Alt text:** Always provide meaningful descriptions for screen readers
- **Width:** Use consistent widths (750 for full screenshots, smaller for icons/buttons)
- **File location:** Store images in `/static/` folder with organized subfolders
- **File naming:** Use descriptive kebab-case names (e.g., `create-dataset-form.png`)
- **Screenshot quality:** Remove PII and decorative elements, keep focus on relevant content

---

## External links

### Link with external indicator

Use superscript arrow for external links:

```markdown
[DCAT-AP-LU Vocabulary<sup>↗</sup>](https://mindig_lu.gitlab.io/DCAT-AP-LU/)
```

**Result:** [DCAT-AP-LU Vocabulary<sup>↗</sup>](https://mindig_lu.gitlab.io/DCAT-AP-LU/)

---

## Admonitions

### Tip admonition

```markdown
:::tip Title (optional)

Your tip content goes here.

:::
```

**Example:**

:::tip Continue later

Your dataset is now saved. To continue editing later, select **Cancel** to close the dataset editor.

:::

### Other admonition types

```markdown
:::note
This is a note
:::

:::warning
This is a warning
:::

:::danger
This is a danger alert
:::

:::info
This is an info box
:::
```

---

## Lists

### Numbered procedure list

```markdown
1. Select **Add dataset** on the main menu.

2. Fill out the dataset form.

3. Select **Preview & Save**.
```

**Best practices:**
- Leave blank lines between steps
- Use consistent action verbs (Select, Enter, Go to)
- Bold UI element names

### Bulleted list

```markdown
- **Item label:** Description of the item
- **Another item:** Description here
- Third item without label
```

---

## Inline formatting

### Text formatting examples

```markdown
- **Bold** for UI elements: Select **Save as Draft**
- *Italic* for emphasis (use sparingly)
- `Code` for code snippets or technical terms
- [Internal link](/user-guide/add-a-dataset)
- [External link<sup>↗</sup>](https://example.com)
```

---

## Code blocks

### With syntax highlighting

```markdown
\```python
def hello_world():
    print("Hello, world!")
\```
```

### With filename

```markdown
\```json title="config.json"
{
  "setting": "value"
}
\```
```

---

## Tables

### Basic table

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

### Table with alignment

```markdown
| Left aligned | Center aligned | Right aligned |
|:-------------|:--------------:|--------------:|
| Data 1       | Data 2         | Data 3        |
```

---

## In this guide section

Use a consistent format at the top of user guide pages:

```markdown
In this guide  
> [Overview](#overview)  
> [Section name](#section-name)  
> [Another section](#another-section)
```

---

## Page frontmatter

### Standard user guide page

```markdown
---
slug: /page-slug
sidebar_label: "Sidebar Title"
sidebar_position: 1
description: "Brief description for SEO and previews."
---
```

### Required imports

```markdown
import useBaseUrl from '@docusaurus/useBaseUrl';
import FeatureFlag from '@site/src/components/FeatureFlag';
```

---

## What's next section

Use at the end of guides to link to related content:

```markdown
:::tip What's next?

Now that you've created your dataset, [**submit it for review**](/user-guide/submit-datasets-for-review) or continue [**adding enhancements**](/user-guide/category/enhance-datasets).

:::
```

---

## Style guidelines

Follow these guidelines when writing documentation:

- Use UK English spelling and grammar
- Use active voice where possible
- Use "Select" instead of "Click"
- Use sentence case for headings
- Include serial (Oxford) commas
- Bold UI element names: **Add dataset**
- Use descriptive link text (not "click here")
- Keep sentences concise and clear
- Structure content with clear headings

For complete style guidance, see the [LNDS Style Guide](https://github.com/your-org/dca-metadata-capture/blob/main/lnds-style-guide.md) in the project root.
