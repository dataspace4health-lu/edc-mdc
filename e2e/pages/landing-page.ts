import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { DummyDataDictionary } from "../fixtures.ts/data-dictionary-fixture";
import { BASE_URL } from "../config";

export class LandingPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  private getVisibleModal() {
    return this.page.locator("#modal:visible").last();
  }

  async openPage(): Promise<void> {
    await this.page.goto(BASE_URL);
    await this.waitForLoaderToDisappear();
  }

  async navigateToDatasetForm(): Promise<void> {
    const addDatasetLink = this.page.locator("a").getByText("Add dataset");
    await addDatasetLink.click();
    await this.waitForLoaderToDisappear();
  }

  async logout(): Promise<void> {
    await this.page.click("#user-menu");
    const logoutLink = this.page.locator("a span").getByText("Logout");
    await logoutLink.click();
  }

  async assertPageLoaded(): Promise<void> {
    expect(this.page.locator("#user-menu")).toBeVisible();
  }

  async assertAppTitle(): Promise<void> {
    const title = await this.page.title();
    expect(title).toContain("Dataset Metadata Capture");
    await expect(this.page.locator("header nav a.text-base").first()).toContainText(
      "Metadata Capture",
    );
  }

  async assertDatasetCreated(dataset): Promise<void> {
    await this.assertDatasetExists(dataset);
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

    const datasetTypeVisible1 = await this.page.getByText(dataset.types[0]).first().isVisible();

    const datasetTypeVisible2 = await this.page.getByText(dataset.types[1]).first().isVisible();

    const distributionsVisible = await this.page.getByText("Distributions").first().isVisible();

    expect(titleVisible).toBe(true);
    expect(rightsVisible).toBe(true);
    expect(descriptionVisible).toBe(true);
    expect(contactNameVisible).toBe(true);
    expect(keyword1).toBe(true);
    expect(keyword2).toBe(true);
    expect(datasetTypeVisible1).toBe(true);
    expect(datasetTypeVisible2).toBe(true);
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
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.version));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.version_notes[0]));

    expect(datasetModalText).toEqual(expect.stringContaining(dataset.contact.split(" ")[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.publisherName));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.keywords[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.keywords[1]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.themes[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.themes[1]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.spatial_coverages[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.conventions[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.areasOfWork[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.areasOfCompetence[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.applicableLegislations[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.rights));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.types[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.types[1]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.periodicity));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.provenance[0]));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.conforms_to[0]));
    // Check that at least one spatial resolution value is displayed
    expect(datasetModalText).toEqual(
      expect.stringContaining(dataset.spatial_resolutions[0].toString()),
    );
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.temporal_resolution));
    expect(datasetModalText).toEqual(expect.stringContaining(dataset.other_identifiers[0]));

    const identifier = await this.getDatasetIdentifier();
    expect(identifier).toMatch(/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/);
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
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.download_urls[0]));

    expect(distributionModalText).toEqual(expect.stringContaining(distribution.format));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.language[0]));
    expect(distributionModalText).toEqual(
      expect.stringContaining(distribution.applicableLegislations[0]),
    );
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.media_type));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.compression_format));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.packaging_format));
    expect(distributionModalText).toEqual(
      expect.stringContaining(distribution.size_bytes.toString()),
    );
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.checksum));
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.availability));
    distribution.documentation.forEach((doc) => {
      expect(distributionModalText).toEqual(expect.stringContaining(doc));
    });
    expect(distributionModalText).toEqual(expect.stringContaining(distribution.linked_schemas[0]));
    expect(distributionModalText).toEqual(
      expect.stringContaining(distribution.distributionDCATStatus),
    );
    expect(distributionModalText).toEqual(
      expect.stringContaining(distribution.distribution_spatial_resolution.toString()),
    );
    expect(distributionModalText).toEqual(
      expect.stringContaining(distribution.distribution_temporal_resolution),
    );
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

    expect(tableText).toEqual(expect.stringContaining(DummyDataDictionary.name));
    expect(tableText).toEqual(expect.stringContaining(DummyDataDictionary.description));
    expect(tableText).toEqual(expect.stringContaining(DummyDataDictionary.fieldType));

    expect(tableText).toContain("Data_1");
    expect(tableText).toContain("This is a test description for field 1");
    expect(tableText).toContain("String");

    expect(tableText).toContain("Data_2");
    expect(tableText).toContain("This is a test description for field 2");
    expect(tableText).toContain("Integer");
  }

  async openRelationsTab(): Promise<void> {
    await this.page.getByRole("button", { name: "Relations", exact: true }).click();
    await this.waitForLoaderToDisappear();
  }

  async openActivityLogsTab(): Promise<void> {
    const modal = this.getVisibleModal();
    await modal.waitFor({ state: "visible", timeout: 10000 });

    await this.page.waitForTimeout(1000);

    const moreButton = modal.getByRole("button", { name: "More", exact: true });
    await moreButton.waitFor({ state: "visible", timeout: 10000 });
    await moreButton.click();

    await this.page.waitForTimeout(500);
    const activityLogsButton = this.getVisibleModal().getByRole("button", {
      name: "Activity Logs",
    });

    await activityLogsButton.waitFor({ state: "visible", timeout: 10000 });
    await activityLogsButton.click();

    await this.page.waitForLoadState("networkidle");
  }

  async clickSubmitDataset(): Promise<void> {
    await this.page.getByRole("button", { name: "Submit Dataset" }).click();
    await this.page.getByRole("button", { name: "Submit Dataset" }).click();
  }

  async validateDataset(): Promise<void> {
    await this.page.getByRole("button", { name: "Validate Dataset" }).click();
    await this.page.getByRole("button", { name: "Validate Dataset" }).click();
    await this.waitForLoaderToDisappear();
  }

  async approveDataset(): Promise<void> {
    const modal = this.getVisibleModal();
    const beginApprovalButton = modal.getByRole("button", { name: "Begin Approval Process" });

    if (await beginApprovalButton.isVisible()) {
      await beginApprovalButton.click();
      await modal.locator("input[name='isAccurate']").check();
      await modal.locator("input[name='shouldPublish']").check();
      await modal.getByRole("button", { name: "Approve for Publishing" }).click();
    } else {
      await this.page.getByRole("button", { name: "Approve Dataset" }).click();
      await this.page.getByRole("button", { name: "Approve Dataset" }).click();
    }

    await this.waitForLoaderToDisappear();
  }

  async publishDataset(): Promise<void> {
    await this.page.getByRole("button", { name: "Publish Dataset" }).click();
    await this.page.getByRole("button", { name: "Publish Dataset" }).click();
    await this.waitForLoaderToDisappear();
  }

  async backToDraft(): Promise<void> {
    await this.page.getByRole("button", { name: "Revert to Draft" }).click();
    await this.page.getByRole("button", { name: "Revert to Draft" }).click();
    await this.waitForLoaderToDisappear();
  }

  async assertRelationsEntry(relationName: string, datasetTitle: string): Promise<void> {
    await this.page.waitForTimeout(2000);
    const datasetLink = this.getVisibleModal().getByRole("link", { name: datasetTitle });
    await expect(datasetLink).toBeVisible({ timeout: 10000 });

    const relationContainer = datasetLink.locator(
      "xpath=ancestor::span[contains(@class, 'flex flex-col')]",
    );

    await expect(relationContainer.locator("span.label-lnds-color")).toContainText(relationName);

    await expect(datasetLink).toContainText(datasetTitle);
  }

  async assertActivityLogs(): Promise<void> {
    await this.page.waitForTimeout(2000);
    const activityLogs = await this.page
      .locator("#modal:visible")
      .getByRole("list")
      .first()
      .textContent({ timeout: 10000 });

    expect(activityLogs).toBeTruthy();
  }

  async closeModal(): Promise<void> {
    await this.getVisibleModal().getByLabel("Close").click();
  }

  async switchToPublishedTab(): Promise<void> {
    const publishedTabLink = this.page.locator('a[href*="/?status=PUBLISHED"]').first();
    await publishedTabLink.click();
    await this.page.waitForLoadState("networkidle");
  }

  async switchToDraftTab(): Promise<void> {
    const draftTabLink = this.page.locator('a[href*="/?status=DRAFT"]').first();
    await draftTabLink.click();
    await this.waitForLoaderToDisappear();
  }

  async createNewVersion(): Promise<void> {
    const moreButton = this.getVisibleModal().locator("button.p-2.rounded.hover\\:bg-gray-100");
    await moreButton.waitFor({ state: "visible" });
    await moreButton.click();

    await this.page.waitForTimeout(500);

    const createVersionButton = this.getVisibleModal().getByRole("button", {
      name: /create a version/i,
    });

    try {
      await createVersionButton.waitFor({ state: "visible" });
      await createVersionButton.click();
    } catch {
      throw new Error(
        "Create a Version button not found. Ensure dataset is PUBLISHED with has_versions=false.",
      );
    }

    const versionTypeModal = this.getVisibleModal();
    await versionTypeModal.getByRole("radio", { name: /metadata only/i }).check();
    await versionTypeModal.getByRole("button", { name: /create draft version/i }).click();

    await this.page.waitForLoadState("networkidle");
    await this.waitForLoaderToDisappear();

    const identifier = await this.getDatasetIdentifier();
    expect(identifier).toMatch(/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/);
  }

  async getDatasetIdentifier(): Promise<string> {
    const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/;
    const modalText = (await this.getVisibleModal().textContent()) || "";
    const modalMatch = modalText.match(uuidRegex);
    if (modalMatch) return modalMatch[0];

    const bodyText = (await this.page.textContent("body")) || "";
    const bodyMatch = bodyText.match(uuidRegex);
    if (bodyMatch) return bodyMatch[0];

    const urlMatch = this.page.url().match(uuidRegex);
    if (urlMatch) return urlMatch[0];

    throw new Error("Dataset identifier (UUID) not found in modal content, page content, or URL.");
  }

  async assertDatasetStatus(expectedStatus: string): Promise<void> {
    const modal = this.getVisibleModal();
    await expect(modal).not.toContainText("Please Wait");
    const statusText = await modal.textContent();
    expect(statusText).toEqual(expect.stringContaining(expectedStatus));
  }

  async viewChanges(): Promise<void> {
    const viewChangesButton = this.getVisibleModal().getByRole("button", {
      name: /view changes/i,
    });
    await viewChangesButton.waitFor({ state: "visible" });
    await viewChangesButton.click();
    await this.page.waitForTimeout(500);
  }

  async showChanges(): Promise<void> {
    const showChangesButton = this.getVisibleModal().getByRole("button", {
      name: /show changes/i,
    });
    await showChangesButton.waitFor({ state: "visible" });
    await showChangesButton.click();
    // Wait for expansion animation to complete
    await this.page.waitForTimeout(1000);
  }

  async getVersionChanges(): Promise<string> {
    await this.page.waitForFunction(() => {
      const text = document.body.innerText;
      return text.includes("Changes from last version") || text.includes("Current Version");
    });
    return (await this.getVisibleModal().textContent()) || "";
  }

  async assertVersionChangesContain(changes: {
    headers: string[];
    fieldName: string;
    oldValue: string;
    newValue: string;
  }): Promise<void> {
    await this.page.waitForFunction(
      ({ oldValue, newValue }) => {
        const modal = document.querySelector("#modal");
        const text = modal?.textContent || "";
        return text.includes(oldValue) && text.includes(newValue);
      },
      { oldValue: changes.oldValue, newValue: changes.newValue },
      { timeout: 10000 },
    );
    const changesText = await this.getVersionChanges();

    changes.headers.forEach((header) => {
      expect(changesText).toContain(header);
    });

    // Verify changed field and values are visible in diff
    expect(changesText).toContain(changes.fieldName);
    expect(changesText).toContain(changes.oldValue);
    expect(changesText).toContain(changes.newValue);
  }

  async switchToDeprecatedTab(): Promise<void> {
    const deprecatedTabLink = this.page.locator('a[href*="/?status=DEPRECATED"]').first();
    await deprecatedTabLink.click();
    await this.waitForLoaderToDisappear();
  }

  async assertDatasetDeprecated(expectedStatus: string = "Deprecated"): Promise<void> {
    const modal = this.getVisibleModal();
    await expect(modal).not.toContainText("Please Wait");
    const statusText = await modal.textContent();
    expect(statusText?.toUpperCase()).toEqual(
      expect.stringContaining(expectedStatus.toUpperCase()),
    );
  }

  async openDatasetOptions(): Promise<void> {
    const datasetButton = this.page.locator("button.p-2.rounded.hover\\:bg-gray-100").first();
    await datasetButton.waitFor({ state: "visible", timeout: 1000 });
    const isVisible = await datasetButton.isVisible();
    if (isVisible) {
      await datasetButton.click();
    }
  }

  async selectDeleteOption(): Promise<void> {
    const deleteOption = this.page.locator("button", { hasText: "Delete" });
    await deleteOption.waitFor({ state: "visible", timeout: 1000 });
    await deleteOption.click();
  }

  async confirmDatasetDeletion(): Promise<void> {
    const confirmationText = this.page.getByText("Are you sure you want to delete this dataset?");
    await expect(confirmationText).toBeVisible();
    const confirmDeleteButton = this.page.locator("button.bg-lnds-red", { hasText: "Delete" });
    await confirmDeleteButton.click();
    expect(this.page.locator("div[role=alert]")).toHaveText("Dataset deleted successfully");
  }

  async selectFilterOption(filterLabel: string, optionValue: string): Promise<void> {
    const filterSection = this.page.locator(`h1:has-text("${filterLabel}")`).locator("..");
    const combobox = filterSection.getByRole("combobox");
    await combobox.click();
    await combobox.fill(optionValue);
    await this.page.waitForTimeout(300);
    await this.page.keyboard.press("Enter");
    await this.page.waitForTimeout(500);
  }

  async removeFilterTag(tagText: string): Promise<void> {
    const removeButton = this.page.locator(`[aria-label="Remove ${tagText}"]`);
    await removeButton.click();
    await this.page.waitForTimeout(500);
  }
}
