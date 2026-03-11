import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";

export class KeywordsPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/keywords`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/keywords`);
    await this.page.waitForTimeout(2000);
    expect(this.page.url()).toContain("keywords");
    const pageText = await this.page.textContent("body");
    expect(pageText).toContain("Create Keyword");
  }

  async expandForm(): Promise<void> {
    await this.page.locator("button:has-text('Expand form')").click();
  }

  async setKeywordLabel(label: string): Promise<void> {
    await this.page.locator(`[name='engLabel']`).fill(label);
  }

  async setKeywordOrganisation(organisation: string): Promise<void> {
    await fillAutoComplete(this.page, 0, organisation);
  }

  async createKeyword(): Promise<void> {
    await this.page.locator("button:has-text('Create Keyword')").click();
  }

  async assertKeywordCreated(keywordLabel: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    const expected = keywordLabel.toLowerCase();
    await expect
      .poll(
        async () => {
          const pageText = ((await this.page.textContent("body")) || "").toLowerCase();
          return pageText.includes(expected);
        },
        { timeout: 20000 },
      )
      .toBe(true);
  }

  async editKeyword(keywordLabel: string): Promise<void> {
    const allKeywordContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allKeywordContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(keywordLabel)) {
        await container.locator("button").first().click();
        return;
      }
    }

    throw new Error(`Keyword with label "${keywordLabel}" not found.`);
  }

  async updateKeyword(): Promise<void> {
    await this.page.locator("button:has-text('Update Keyword')").click();
  }

  async promoteKeywordToGlobal(keywordLabel: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    await this.page.waitForTimeout(2000);
    const allKeywordContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allKeywordContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(keywordLabel)) {
        await container.locator("button").nth(1).click();
        return;
      }
    }

    throw new Error(`Keyword with label "${keywordLabel}" not found.`);
  }

  async confirmPromotion(): Promise<void> {
    await this.page.locator("button:has-text('Promote to Global')").click();
    await this.page.waitForLoadState("networkidle");
  }

  async cancelPromotion(): Promise<void> {
    await this.page.locator("button:has-text('Cancel')").click();
  }

  async assertKeywordIsGlobal(keywordLabel: string): Promise<void> {
    await this.page.waitForTimeout(2000);
    const allKeywordContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allKeywordContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(keywordLabel)) {
        await expect(container.locator("text=Global")).toBeVisible();
        return;
      }
    }

    throw new Error(`Keyword with label "${keywordLabel}" not found.`);
  }

  async assertPromoteButtonVisible(keywordLabel: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    const allKeywordContainers = await this.page.locator("div.border-b div.p-4").all();

    for (const container of allKeywordContainers) {
      const heading = await container.locator("span.font-medium.mb-1").textContent();

      if (heading?.includes(keywordLabel)) {
        const buttonCount = await container.locator("button").count();
        expect(buttonCount).toBe(2); // edit + promote buttons
        return;
      }
    }

    throw new Error(`Keyword with label "${keywordLabel}" not found.`);
  }
}
