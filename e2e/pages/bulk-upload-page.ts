import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";

export class BulkUploadPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  private getVisibleModal() {
    return this.page.locator("#modal:visible").last();
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/datasets/bulk-upload`);
  }

  async switchToDraftTab(): Promise<void> {
    const draftTabLink = this.page.locator('a[href*="/?status=DRAFT"]');
    await draftTabLink.click();
    await this.waitForLoaderToDisappear();
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/datasets/bulk-upload`);
    const heading = await this.page.locator("h1").first().innerText();
    expect(heading).toBe("Bulk Import Datasets");
  }

  async uploadFile() {
    const filePath = "./fixtures.ts/DCAT-AP-LU_official-e2e.xlsm";
    const [chooser] = await Promise.all([
      this.page.waitForEvent("filechooser"),
      this.page.getByRole("button", { name: "Upload Excel file" }).click(),
    ]);
    await chooser.setFiles(filePath);
    await this.page
      .getByText("Processing the file...")
      .waitFor({ state: "detached", timeout: 15000 });
  }

  async clickCreateDataset() {
    const createBtn = this.page.getByRole("button", { name: "Import Datasets" });
    await expect(createBtn).toBeVisible({ timeout: 10000 });
    await createBtn.click();
  }

  async assertSuccessMessage() {
    await expect
      .poll(
        async () => {
          const bodyText = (await this.page.textContent("body")) || "";
          return (
            /(?:\d+)\s+dataset(?:s)?\s+successfully\s+created!/i.test(bodyText) ||
            /import completed successfully!/i.test(bodyText)
          );
        },
        { timeout: 30000 },
      )
      .toBe(true);

    await this.page.waitForLoadState("networkidle", {
      timeout: 10000,
    });
  }

  async assertDatasetExists(dataset): Promise<void> {
    await this.waitForLoaderToDisappear();
    const contactName = dataset.contact.split(" ")[0];
    const titleVisible = await this.page.getByText(dataset.title).first().isVisible();

    const rightsVisible = await this.page.getByText(dataset.rights).first().isVisible();

    const descriptionVisible = await this.page.getByText(dataset.description).first().isVisible();

    const contactNameVisible = await this.page.getByText(contactName).first().isVisible();

    const keyword1 = await this.page
      .getByText(dataset.keywords[0].toUpperCase())
      .first()
      .isVisible();

    const keyword2 = await this.page
      .getByText(dataset.keywords[1].toUpperCase())
      .first()
      .isVisible();

    const applicable_legislation = await this.page
      .getByText(dataset.applicableLegislations[0].toUpperCase())
      .first()
      .isVisible();

    const datasetTypeVisible1 = await this.page.getByText(dataset.types[0]).first().isVisible();

    const distributionsVisible = await this.page.getByText("Distributions").first().isVisible();

    expect(titleVisible).toBe(true);
    expect(rightsVisible).toBe(true);
    expect(descriptionVisible).toBe(true);
    expect(contactNameVisible).toBe(true);
    expect(keyword1).toBe(true);
    expect(keyword2).toBe(true);
    expect(applicable_legislation).toBe(true);
    expect(datasetTypeVisible1).toBe(true);
    expect(distributionsVisible).toBe(true);
  }

  async openDatasetModal(datasetId: string): Promise<void> {
    const card = this.page.locator(`#root div.dataset-card-${datasetId}`);
    await card.waitFor({ state: "visible" });
    const viewDatasetButton = card.getByRole("button", { name: /^View$/ });
    await viewDatasetButton.click();
    await this.page.waitForLoadState("networkidle");
  }

  async assertDatasetModal(dataset): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    const modal = this.getVisibleModal();
    await modal.waitFor({ state: "visible" });
    await expect(modal).not.toContainText("Please Wait");

    const datasetModalText = await modal.textContent();

    expect(datasetModalText).toEqual(expect.stringContaining(dataset.title));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.description));

    expect(datasetModalText).toEqual(expect.stringContaining(dataset.contact.split(" ")[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.publisherName));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.creatorNames[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.keywords[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.applicableLegislations[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.themes[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.rights));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.types[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.data_protection_types[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.languages[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.periodicity));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.spatial_coverages[0]));

    const match = (datasetModalText || "").match(
      /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/,
    );
    expect(match?.[0]).toMatch(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/);
  }

  async openDistributionsTab(): Promise<void> {
    await this.page.getByRole("button", { name: "Distributions" }).click();
    await this.waitForLoaderToDisappear();
  }

  async assertDistributions(distribution): Promise<void> {
    await this.waitForLoaderToDisappear();

    // Expand the distribution accordion by clicking on it
    await this.page.getByRole("heading", { name: distribution.title }).click();
    await this.page.waitForTimeout(500);

    const distributionModalText = await this.getVisibleModal().textContent();

    expect(distributionModalText).toEqual(expect.stringContaining(distribution.title));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.description));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.access_urls[0]));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.format));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.license));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.rights));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.languages[0]));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.media_type));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.compression_format));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.packaging_format));
    expect(distributionModalText).toEqual(
      expect.stringContaining(distribution.applicableLegislations[0]),
    );
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.availability));
  }

  async waitForLoaderToDisappear(): Promise<void> {
    const loader = this.page.locator(".animate-spin").first();
    if (await loader.isVisible({ timeout: 3000 })) {
      await loader.waitFor({ state: "hidden", timeout: 10000 });
    }
  }

  async openDictionaryTab(): Promise<void> {
    await this.page.getByRole("button", { name: "Data Dictionary" }).click();
    await this.waitForLoaderToDisappear();
  }

  async assertDictionaryEntry(): Promise<void> {
    await this.page.waitForTimeout(2000);
    const tableText = await this.page
      .locator("#modal:visible")
      .getByRole("table")
      .textContent({ timeout: 10000 });

    expect(tableText).toEqual(expect.stringContaining("variable_1"));
    expect(tableText).toEqual(expect.stringContaining("This is a test description for field 1"));
    expect(tableText).toEqual(expect.stringContaining("Boolean"));

    expect(tableText).toContain("variable_1");
    expect(tableText).toContain("This is a test description for field 1");
    expect(tableText).toContain("Boolean");

    expect(tableText).toContain("variable_2");
    expect(tableText).toContain("This is a test description for field 2");
    expect(tableText).toContain("Boolean");
  }

  async openOrganisationContactsPage(): Promise<void> {
    await this.page.locator("a:has-text('Contacts')").click();
  }
}
