import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";
import { DummyDataset } from "../fixtures.ts/dataset-fixture";

export class AddRelationsPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/datasets/2/relations`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/datasets/2/relations`);
    expect(this.page.url()).toContain("datasets/2/relations");
    expect(await this.page.locator("h1").first().innerText()).toContain("Add Relation");
  }

  async addDatasetRelation(): Promise<void> {
    await fillAutoComplete(this.page, 0, ["Link to Other Dataset"]);
    await fillAutoComplete(this.page, 1, ["has Part"]);
    await fillAutoComplete(this.page, 2, ["DRAFT"]);

    const searchInput = this.page.getByPlaceholder("Search for datasets to add...");
    await searchInput.fill(DummyDataset.title);
    await expect(this.page.getByText("Search Results")).toBeVisible({ timeout: 10000 });
    const titleEl = this.page.getByText(DummyDataset.title, { exact: true });
    await expect(titleEl).toBeVisible();
    const row = titleEl.locator("xpath=..");
    await row.getByRole("button", { name: "Select" }).click();

    await this.page.getByRole("button", { name: "Add Relation" }).click();
    await this.page.waitForLoadState("networkidle");
  }

  async addExternalRelation(): Promise<void> {
    await fillAutoComplete(this.page, 0, ["Link to Other External Resource"]);
    await this.page.getByLabel("External URL").fill("https://resourcecee.com");
    await fillAutoComplete(this.page, 1, ["Described By"]);
    await this.page.getByLabel("Description").fill("Test external resource description");

    await this.page.getByRole("button", { name: "Add Relation" }).click();
    await this.page.waitForLoadState("networkidle");
  }

  async assertAddedDatasetRelation(): Promise<void> {
    await this.page.waitForSelector("text=Dataset Relations", {
      state: "visible",
      timeout: 5000,
    });

    const relationSection = this.page
      .locator("text=Dataset Relations")
      .locator("xpath=following-sibling::div[1]");
    await expect(relationSection).toContainText("has Part");
    await expect(relationSection).toContainText(DummyDataset.title);
  }

  async assertAddedExternalRelation(): Promise<void> {
    await this.page.waitForSelector("text=Links to external resources", {
      state: "visible",
      timeout: 5000,
    });

    const externalSection = this.page
      .locator("text=Links to external resources")
      .locator("xpath=following-sibling::div[1]");
    await expect(externalSection).toContainText("https://resourcecee.com");
  }

  async removeRelation(identifier: string = DummyDataset.title): Promise<void> {
    const card = this.page.locator(".space-y-4 > div").filter({ hasText: identifier }).first();

    await expect(card).toBeVisible({ timeout: 10000 });

    await card.locator("button:has(svg)").click();

    await this.page.waitForLoadState("networkidle");
  }
}
