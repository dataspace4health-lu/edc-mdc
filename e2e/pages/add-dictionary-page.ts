import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { DummyDataDictionary } from "../fixtures.ts/data-dictionary-fixture";
import { BASE_URL } from "../config";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";
import * as fs from "fs";

export class AddDictionaryPage {
  readonly page: Page;
  private datasetId: string;

  constructor(page: Page, datasetId: string | number = 1) {
    this.page = page;
    this.datasetId = String(datasetId);
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/datasets/${this.datasetId}/dictionaries`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    await this.page.waitForURL(`${BASE_URL}/datasets/${this.datasetId}/dictionaries`);
    expect(this.page.url()).toContain(`datasets/${this.datasetId}/dictionaries`);
    expect(await this.page.locator("h1").first().innerText()).toBe("Add Dataset Dictionary");
    await this.page.waitForLoadState("networkidle");
  }

  async addDictionaryEntry(): Promise<void> {
    await this.page.locator("button:has-text('Expand form')").click();
    await this.page.getByPlaceholder("Name").click();
    await this.page.getByPlaceholder("Name").fill(DummyDataDictionary.name);

    await fillAutoComplete(this.page, 0, DummyDataDictionary.fieldType);

    await this.page.locator('[name="description"]').click();
    await this.page.locator('[name="description"]').fill(DummyDataDictionary.description);

    await this.page.getByPlaceholder("Max Allowed Value").click();
    await this.page
      .getByPlaceholder("Max Allowed Value")
      .fill(DummyDataDictionary.maxAllowedValue.toString());

    await this.page.getByPlaceholder("Min Allowed Value").click();
    await this.page
      .getByPlaceholder("Min Allowed Value")
      .fill(DummyDataDictionary.minAllowedValue.toString());

    await this.page.getByPlaceholder("Variable Unit").click();
    await this.page.getByPlaceholder("Variable Unit").fill(DummyDataDictionary.variableUnit);

    await this.page.getByPlaceholder("Allowed Values", { exact: true }).click();
    await this.page
      .getByPlaceholder("Allowed Values", { exact: true })
      .fill(DummyDataDictionary.allowedValues);

    await this.page.getByPlaceholder("Allowed Values Description", { exact: true }).click();
    await this.page
      .getByPlaceholder("Allowed Values Description", { exact: true })
      .fill(DummyDataDictionary.allowedValuesDescription);

    await this.page.waitForTimeout(300);
    await fillAutoComplete(this.page, 1, "Yes");
    await fillAutoComplete(this.page, 2, "Yes");

    await this.page.getByRole("button", { name: "Insert" }).click();
    await this.page.waitForLoadState("networkidle");
  }

  async bulkUploadDictionary(): Promise<void> {
    const filePath = "./fixtures.ts/data_dictionary_bulk_upload.csv";
    if (!fs.existsSync(filePath)) {
      throw new Error(`CSV file not found at path: ${filePath}`);
    }
    await this.page.getByRole("button", { name: "Bulk Upload" }).click();

    const input = await this.page.locator('input[type="file"][accept=".csv"]');
    await input.setInputFiles(filePath);

    await this.page.waitForFunction(
      () => {
        const rows = document.querySelectorAll("table tbody tr");
        return rows.length > 0;
      },
      { timeout: 30000 },
    );
  }

  async filterColumns(): Promise<void> {
    await this.page.getByRole("button", { name: "Filter Columns" }).click();

    const dropdown = this.page.locator("div.absolute.z-20");
    await dropdown.waitFor({ state: "visible", timeout: 10000 });

    const checkboxes = dropdown.locator("input[type='checkbox']");
    const checkboxCount = await checkboxes.count();

    for (let i = 0; i < checkboxCount; i++) {
      const checkbox = checkboxes.nth(i);
      const isChecked = await checkbox.isChecked();
      if (!isChecked) {
        await checkbox.check();
      }
    }
    await this.page.getByRole("button", { name: "Filter Columns" }).click();
  }

  async assertDictionaryEntries(): Promise<void> {
    const rows = this.page.locator("table tbody tr");
    await this.filterColumns();
    const rowCount = await rows.count();

    expect(rowCount).toBeGreaterThan(0);

    const tableText = await this.page.locator("table tbody").textContent();

    expect(tableText).toContain(DummyDataDictionary.name);
    expect(tableText).toContain(DummyDataDictionary.description);
    expect(tableText).toContain(DummyDataDictionary.fieldType);

    expect(tableText).toContain("Data_1");
    expect(tableText).toContain("This is a test description for field 1");
    expect(tableText).toContain("String");
    expect(tableText).toContain("No");
    expect(tableText).toContain("Yes");
    expect(tableText).toContain("[1,2,3]");
    expect(tableText).toContain("[1=Low, 2=Medium, 3=High]");

    expect(tableText).toContain("Data_2");
    expect(tableText).toContain("This is a test description for field 2");
    expect(tableText).toContain("Integer");
    expect(tableText).toContain("Yes");
    expect(tableText).toContain("No");
    expect(tableText).toContain("100");
    expect(tableText).toContain("10");
    expect(tableText).toContain("kg");
    expect(tableText).toContain("[10,20,30]");
    expect(tableText).toContain("[10=Low, 20=Medium, 30=High]");
  }

  async removeDictionaryEntry(): Promise<void> {
    const rows = this.page.locator("table tbody tr");
    const initialRowCount = await rows.count();

    if (initialRowCount === 0) {
      console.log("No rows to delete");
      return;
    }

    const deleteButton = rows.first().locator("td .icon-lnds-color").last();
    await deleteButton.waitFor({ state: "attached", timeout: 5000 });
    await deleteButton.click();

    await this.page.waitForFunction((initialRowCount) => {
      const currentRowCount = document.querySelectorAll("table tbody tr").length;
      return currentRowCount < initialRowCount;
    }, initialRowCount);
  }

  async assertRemovedDictionaryEntry(): Promise<void> {
    const noEntriesText = await this.page
      .locator('text="No entries available"')
      .first()
      .textContent();

    expect(noEntriesText).toContain("No entries available");
  }

  async cleanupExistingEntries(): Promise<void> {
    let rows = this.page.locator("table tbody tr");
    let rowCount = await rows.count();

    while (rowCount > 0) {
      await this.removeDictionaryEntry();

      rows = this.page.locator("table tbody tr");
      rowCount = await rows.count();
    }
  }

  async reorderEntries(): Promise<void> {
    // Wait for table to load
    await this.page.waitForSelector("table tbody tr");

    // Click the Reorder button
    await this.page.getByRole("button", { name: "Reorder" }).click();

    // Wait for reorder mode to be active (Save Order button appears)
    await this.page.waitForSelector('button:has-text("Save Order")', { timeout: 10000 });

    // Click the down arrow on the first entry to move it down
    await this.page
      .locator("table tbody tr")
      .first()
      .locator("button[aria-label='Move down']")
      .click();

    // Wait a moment for the UI to update
    await this.page.waitForTimeout(500);

    // Click Save Order button
    await this.page.getByRole("button", { name: "Save Order" }).click();

    // Wait for success message
    await this.page.waitForSelector('text="Order saved successfully"', { timeout: 10000 });

    // Wait for table to reload
    await this.page.waitForLoadState("networkidle");
  }

  async assertReorderedEntries(): Promise<void> {
    // Wait for table to be visible
    await this.page.waitForSelector("table tbody tr");

    // Get the first two entries
    const rows = this.page.locator("table tbody tr");
    const rowCount = await rows.count();

    // Should have at least 2 entries
    expect(rowCount).toBeGreaterThanOrEqual(2);

    // The first entry should now be "Data_2" (moved from second position)
    const firstEntryName = await rows.first().locator("td").first().textContent();
    expect(firstEntryName).toBe("Data_2");

    // The second entry should now be "Data_1" (moved down from first position)
    const secondEntryName = await rows.nth(1).locator("td").first().textContent();
    expect(secondEntryName).toBe("Data_1");
  }
}
