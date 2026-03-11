import { test } from "@playwright/test";
import { DocsPage } from "../pages/docs-page";

test("012.should load /docs and display documentation content", async ({ page }) => {
  const docs = new DocsPage(page);

  await docs.openDocsPage();
  await docs.assertDocsLoaded();
  await docs.assertSidebarLinks();
});
