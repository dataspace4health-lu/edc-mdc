import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { readFileSync } from "fs";
import { join } from "path";
import { BASE_URL } from "../config";

export class RdfImportPage {
  readonly page: Page;
  private readonly TIMEOUTS = { SHORT: 5000, MEDIUM: 10000, LOADING: 30000 };
  private readonly RDF_FILE_PATH = "../fixtures/test-dataset-template.rdf";
  private readonly RDF_MIME_TYPE = "application/rdf+xml";

  constructor(page: Page) {
    this.page = page;
  }

  async openPage(): Promise<void> {
    await this.page.goto(`${BASE_URL}/datasets/import-rdf`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/datasets/import-rdf`);

    if (
      await this.page
        .locator("text=You are not authorised")
        .isVisible({ timeout: 2000 })
        .catch(() => false)
    ) {
      throw new Error(
        "User does not have permission to access RDF import. Required permission: 'datasets:edit:draft'",
      );
    }

    await expect(this.page.locator("form")).toBeVisible({ timeout: this.TIMEOUTS.MEDIUM });
    await expect(
      this.page.locator("h1, h2, h3").filter({ hasText: /Import Dataset from RDF/i }),
    ).toBeVisible({ timeout: this.TIMEOUTS.SHORT });
    await expect(this.page.locator('input[type="file"]')).toBeVisible({
      timeout: this.TIMEOUTS.SHORT,
    });
  }

  private async selectFileFromContent(rdfContent: string): Promise<void> {
    const fileInput = this.page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: "test-dataset.rdf",
      mimeType: this.RDF_MIME_TYPE,
      buffer: Buffer.from(rdfContent, "utf-8"),
    });
  }

  private async selectRdfFormat(): Promise<void> {
    const combobox = this.page.getByRole("combobox").first();
    await expect(combobox).toBeVisible({ timeout: this.TIMEOUTS.SHORT });
    await combobox.click();
    await this.page.getByRole("option", { name: /RDF\/XML/ }).click();
  }

  private async clickImportButton(): Promise<void> {
    const btn = this.page.locator('button:has-text("Import Dataset")').first();
    await expect(btn).toBeEnabled({ timeout: this.TIMEOUTS.SHORT });
    await btn.scrollIntoViewIfNeeded();
    await btn.click();
  }

  private async waitForImportLoading(): Promise<void> {
    await this.page
      .waitForLoadState("networkidle", { timeout: this.TIMEOUTS.LOADING })
      .catch(() => {});
  }

  async assertSuccessAlert(): Promise<void> {
    await expect(this.page.getByText(/imported successfully/i)).toBeVisible({
      timeout: this.TIMEOUTS.MEDIUM,
    });
  }

  async assertErrorAlert(errorMessage: string): Promise<void> {
    const escapedMessage = errorMessage.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    await expect(
      this.page.getByRole("alert").getByText(new RegExp(escapedMessage, "i")),
    ).toBeVisible({
      timeout: this.TIMEOUTS.MEDIUM,
    });
  }

  async assertViewDatasetButtonExists(): Promise<void> {
    await expect(this.page.getByRole("button", { name: /View Dataset/i })).toBeVisible();
  }

  async clickViewDatasetButton(): Promise<void> {
    await this.page.getByRole("button", { name: /View Dataset/i }).click();
  }

  async importRdfContent(rdfContent: string): Promise<void> {
    await this.selectFileFromContent(rdfContent);
    await this.selectRdfFormat();
    await this.clickImportButton();
    await this.waitForImportLoading();
  }

  async loadTestDatasetRdf(): Promise<string> {
    const rdfPath = join(__dirname, this.RDF_FILE_PATH);
    return readFileSync(rdfPath, "utf-8");
  }

  async createTestRdf(identifier: string, title?: string, description?: string): Promise<string> {
    let rdf = await this.loadTestDatasetRdf();
    rdf = rdf.replace("template-test", identifier);
    if (title) rdf = rdf.replace("Test Dataset Template", title);
    if (description) rdf = rdf.replace("Template dataset for testing RDF import.", description);
    return rdf;
  }

  async editDatasetFields(title: string, description: string): Promise<void> {
    const titleInput = this.page.locator('input[name="title"]').first();
    const descriptionTextarea = this.page.locator('textarea[name="description"]').first();

    await Promise.all([
      titleInput.waitFor({ state: "visible" }),
      descriptionTextarea.waitFor({ state: "visible" }),
    ]);

    await titleInput.clear();
    await titleInput.fill(title);

    await descriptionTextarea.clear();
    await descriptionTextarea.fill(description);
  }

  async saveDatasetAsDraft(): Promise<void> {
    await this.page.getByRole("button", { name: /Preview & Save/i }).click();
    await this.page.waitForLoadState("networkidle");
    await this.page.getByRole("button", { name: /Save as Draft/i }).click();
    await this.page.waitForLoadState("networkidle");
  }

  async navigateToEditPage(): Promise<void> {
    await this.page.waitForURL(/\/datasets\/\d+/);
    await this.page.getByRole("link", { name: /Edit/i }).click();
    await this.page.waitForURL(/\/datasets\/\d+\/edit/);
    await this.page.waitForLoadState("networkidle");
  }

  async assertDatasetUpdatedSuccessfully(): Promise<void> {
    await expect(this.page.getByText(/Dataset updated successfully/i)).toBeVisible({
      timeout: this.TIMEOUTS.MEDIUM,
    });
  }
}
