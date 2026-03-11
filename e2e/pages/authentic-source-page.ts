import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";
import { readFileSync } from "fs";

type Format = "ttl" | "rdf" | "jsonld";

export class AuthenticSourceLabelsPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/authentic_sources`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/authentic_sources`);
    await this.page.waitForLoadState("networkidle");

    await expect(this.page.locator("h2").filter({ hasText: "Authentic Sources" })).toBeVisible();
    await expect(this.page.getByText("Download RDF")).toBeVisible();
  }

  private async expandCreateFormIfCollapsed() {
    const expandButton = this.page.getByRole("button", { name: /Expand Form/i });
    const chevronButton = this.page.locator("button").filter({ hasText: "Expand Form" });

    if (await expandButton.isVisible()) {
      await expandButton.click();
    } else if (await chevronButton.isVisible()) {
      await chevronButton.click();
    }
    await expect(this.page.locator('input[name="name"]')).toBeVisible();
  }

  private async findLabelContainerByName(name: string) {
    const containers = await this.page.locator("div.section-lnds-color").all();

    for (const container of containers) {
      const labelText = await container.textContent();
      if (labelText && labelText.includes(name)) {
        return container;
      }
    }
    return null;
  }

  async createLabel(name: string, description: string) {
    await this.expandCreateFormIfCollapsed();

    await this.page.locator('input[name="name"]').fill(name);
    await this.page.locator('textarea[name="description"]').fill(description);

    await this.page.getByRole("button", { name: "Create Label" }).click();

    await this.page.waitForSelector('[role="alert"]', { state: "visible" });
    await expect(this.page.locator('[role="alert"]')).toContainText("successfully");

    await expect(this.page.getByText(name).first()).toBeVisible({ timeout: 10000 });
  }

  async createLabels(labels: Array<{ name: string; description: string }>) {
    for (const label of labels) {
      await this.createLabel(label.name, label.description);
    }
  }

  async editLabel(oldName: string, newName: string, newDescription: string) {
    const container = await this.findLabelContainerByName(oldName);
    if (!container) throw new Error(`Label "${oldName}" not found for edit.`);

    await container.locator("button").filter({ hasText: "" }).first().click();

    await this.page.locator('input[name="name"]').fill(newName);
    await this.page.locator('textarea[name="description"]').fill(newDescription);

    await this.page.getByRole("button", { name: "Update Label" }).click();

    await this.page.waitForSelector('[role="alert"]', { state: "visible" });
    await expect(this.page.getByText(newName).first()).toBeVisible();
  }

  async assertLabelVisible(name: string) {
    await expect(this.page.getByText(name).first()).toBeVisible();
  }

  async getCountBadge(): Promise<number> {
    const badge = this.page.locator("span.bg-lnds-purple").first();
    const text = (await badge.textContent())?.trim() || "0";
    return Number(text);
  }

  async openDownloadMenu() {
    await this.page.getByRole("button", { name: /Download RDF/i }).click();
    await expect(this.page.getByText("RDF/XML")).toBeVisible();
  }

  async downloadCatalogue(format: Format = "rdf") {
    const promise = this.page.waitForEvent("download");
    try {
      await this.page.goto(`${BASE_URL}/api/v1/authentic-source-labels/catalogue.${format}`);
      // eslint-disable-next-line no-empty, @typescript-eslint/no-unused-vars
    } catch (error) {}

    await this.page.waitForLoadState("networkidle");
    const download = await promise;

    await download.path();
    await download.saveAs(`./${download.suggestedFilename()}`);

    expect(download.suggestedFilename()).toBe(`catalogue.${format}`);
  }

  async assertAuthenticSourceLabels() {
    const content = readFileSync("./catalogue.rdf", { encoding: "utf8" });

    // Check for AuthenticSourceLabel type
    expect(
      /<cdsp:AuthenticSourceLabel\b[^>]*>|<rdf:type[^>]+mindig_lu\.gitlab\.io\/DCAT-AP-LU\/vocab\/cdsp(\/|#)AuthenticSourceLabel/.test(
        content,
      ),
    ).toBe(true);

    // Check for basic label properties
    expect(content).toContain("<dct:title");
    expect(content).toContain("<dct:description");
    expect(content).toContain("<cdsp:assignedAt");
    expect(content).toContain("<cdsp:status");
    expect(content).toContain("<cdsp:datasetTitle");
    expect(content).toContain("<cdsp:datasetIdentifier");
  }

  getCatalogueContent() {
    return readFileSync("./catalogue.rdf", { encoding: "utf8" });
  }

  async assignLabel(rowName: string, label: string, datasetId: string | number) {
    const table = this.page.locator("table tbody");
    if (!(await table.isVisible())) {
      const card = this.page.locator(`[class*="dataset-card-${datasetId}"]`);
      await expect(card).toBeVisible({ timeout: 10_000 });

      const view = card
        .getByRole("button", { name: /^view$/i })
        .or(card.getByRole("link", { name: /^view$/i }))
        .or(card.locator("button,a").filter({ hasText: /^view$/i }));
      await expect(view).toBeVisible({ timeout: 5_000 });
      await view.click();

      await this.page.waitForURL((u) => u.search.includes("datasetId="), { timeout: 10_000 });

      const dialog = this.page.getByRole("dialog");
      const container = (await dialog.count()) ? dialog : this.page;

      const dataDictTab = container
        .getByRole("tab", { name: /data dictionary/i })
        .or(container.getByRole("button", { name: /data dictionary/i }))
        .or(container.locator("button,a").filter({ hasText: /data dictionary/i }));

      await expect(dataDictTab).toBeVisible({ timeout: 10_000 });
      await dataDictTab.click();

      await expect(table).toBeVisible({ timeout: 10_000 });
    }

    const row = table.locator("tr").filter({ hasText: rowName });
    await expect(row).toBeVisible({ timeout: 10_000 });
    await row.scrollIntoViewIfNeeded();

    const toggleWrapper = row.locator(`[name*="authentic-source"]`).locator("xpath=..");
    await expect(toggleWrapper).toBeVisible({ timeout: 5_000 });
    await toggleWrapper.click();
    await this.page.waitForTimeout(300);

    const dropdownButton = row.locator("button").filter({ hasText: /Select Label|Change Label/i });
    await expect(dropdownButton).toBeVisible({ timeout: 5_000 });
    await dropdownButton.click();

    const dropdown = this.page.locator('div[class*="absolute"][class*="z-50"]');
    await expect(dropdown).toBeVisible({ timeout: 5_000 });

    const labelBtn = dropdown.locator("button").filter({ hasText: label });
    await expect(labelBtn).toBeVisible({ timeout: 5_000 });
    await labelBtn.click();

    const updated = row.locator("button").filter({ hasText: label });
    await expect(updated).toBeVisible({ timeout: 5_000 });
  }

  async clickConfirmAuthenticSources() {
    const modal = this.page.getByRole("dialog");
    const scoped = modal
      .locator(
        'button:has-text("Apply Label Assignments"), button:has-text("Confirm Authentic Sources")',
      )
      .first();

    const global = this.page
      .locator(
        'button:has-text("Apply Label Assignments"), button:has-text("Confirm Authentic Sources")',
      )
      .first();

    const target = (await scoped.isVisible().catch(() => false)) ? scoped : global;

    await target.waitFor({ state: "visible", timeout: 10_000 });
    await target.scrollIntoViewIfNeeded();
    await target.click();
    await this.page.getByRole("alert").waitFor({ state: "visible", timeout: 10_000 });
  }
}
