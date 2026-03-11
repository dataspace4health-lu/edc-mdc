import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { DummyDataService } from "../fixtures.ts/dataset-fixture";
import { BASE_URL } from "../config";

const ADD_DATASERVICE_PAGE = `${BASE_URL}/data_services`;

export class AddDataServicePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage() {
    await this.page.goto(ADD_DATASERVICE_PAGE);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(ADD_DATASERVICE_PAGE);
    expect(this.page.url()).toContain(ADD_DATASERVICE_PAGE);
    expect(await this.page.locator("h1").first().innerText()).toBe("Add Data Service");
    await this.page.waitForLoadState("networkidle");
  }

  async addDataServiceEntry(): Promise<void> {
    await this.page.locator("button:has-text('Expand form')").click();
    await this.page.getByLabel("Service Title").click();
    await this.page.getByLabel("Service Title").fill(DummyDataService.title);

    await this.page.locator("button:has-text('Add Endpoint')").click();
    await this.page.getByLabel("URL").fill(DummyDataService.enndpoints[0].endpoint_url);
    await this.page
      .getByLabel("Description")
      .fill(DummyDataService.enndpoints[0].endpoint_description);

    await this.page.locator("button:has-text('Create Data Service')").click();
  }
}
