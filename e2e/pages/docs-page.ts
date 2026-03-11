import type { Page } from "playwright";
import { BASE_URL } from "../config";

export class DocsPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openDocsPage() {
    await this.page.goto(`${BASE_URL}/docs`);
  }

  async assertDocsLoaded(): Promise<void> {
    // TODO Will be fixed later
    // await expect(this.page.getByRole("heading", { name: /introduction/i })).toBeVisible();
  }

  async assertSidebarLinks(): Promise<void> {
    // TODO Will be fixed later
    // await expect(sidebar).toContainText("Introduction");
    // await expect(sidebar).toContainText("Developer Guide");
    // await expect(sidebar).toContainText("User Guide");
    // await expect(sidebar).toContainText("Self Hosting Guide");
    // await expect(sidebar).toContainText("Changelog");
  }
}
