import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";

export class ApplicableLegislationPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/applicable_legislations`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/applicable_legislations`);
    await this.page.waitForTimeout(2000);
    expect(this.page.url()).toContain("applicable_legislations");
    const pageText = await this.page.textContent("body");
    expect(pageText).toContain("Create Applicable Legislation");
  }

  async expandForm(): Promise<void> {
    await this.page.locator("button:has-text('Expand form')").click();
  }

  async setLabel(label: string): Promise<void> {
    await this.page.locator(`[name='engLabel']`).fill(label);
  }

  async setOrganisation(organisation: string): Promise<void> {
    await fillAutoComplete(this.page, 0, organisation);
  }

  async create(): Promise<void> {
    await this.page.locator("button:has-text('Create Applicable Legislation')").click();
  }

  async assertCreated(label: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    await expect(this.page.locator(`text=${label}`).first()).toBeVisible();
  }

  async editApplicableLegislation(label: string): Promise<void> {
    const allContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(label)) {
        await container.locator("button").first().click();
        return;
      }
    }

    throw new Error(`Applicable legislation with label "${label}" not found.`);
  }

  async updateApplicableLegislation(): Promise<void> {
    await this.page.locator("button:has-text('Update Applicable Legislation')").click();
  }

  async promoteApplicableLegislationToGlobal(label: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    await this.page.waitForTimeout(1000);

    const allContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(label)) {
        await container.locator("button").nth(1).click();
        return;
      }
    }

    throw new Error(`Applicable legislation with label "${label}" not found.`);
  }

  async confirmPromotion(): Promise<void> {
    await this.page.locator("button:has-text('Promote to Global')").click();
    await this.page.waitForTimeout(1000);
  }

  async cancelPromotion(): Promise<void> {
    await this.page.locator("button:has-text('Cancel')").click();
  }

  async assertIsGlobal(label: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    const allContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(label)) {
        await expect(container.locator("text=Global")).toBeVisible();
        return;
      }
    }

    throw new Error(`Applicable legislation with label "${label}" not found.`);
  }

  async assertPromoteButtonVisible(label: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    const allContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(label)) {
        const buttonCount = await container.locator("button").count();
        expect(buttonCount).toBe(2);
        return;
      }
    }

    throw new Error(`Applicable legislation with label "${label}" not found.`);
  }
}
