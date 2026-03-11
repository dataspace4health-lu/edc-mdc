import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";

export class OrganisationFormPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/organisations`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/organisations`);
    expect(this.page.url()).toContain("organisations");
    expect(await this.page.locator("h1").first().innerText()).toBe("Add Organisation");
  }

  async assert403Error(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/organisations`);
    expect(this.page.url()).toContain("organisations");
    expect(await this.page.locator("#root > div.flex > div > div > h1").first().innerText()).toBe(
      "You don't have permission to access this page",
    );
  }

  async setOrganisationName(name: string): Promise<void> {
    await this.page.locator("button:has-text('Expand form')").click();
    await this.page.locator(`[name='name']`).fill(name);
  }

  async setOrganisationType(type: string): Promise<void> {
    await fillAutoComplete(this.page, 0, type);
  }

  async setOrganisationEmail(email: string): Promise<void> {
    await this.page.locator(`[name='email']`).fill(email);
  }

  async submitOrganisation(): Promise<void> {
    await this.page.locator("button:has-text('Create Organisation')").click();
    await this.page.waitForLoadState("networkidle");
  }

  async assertOrganisationCreated(organisationName: string): Promise<void> {
    await expect(this.page.locator(`text=${organisationName}`).first()).toBeVisible();
  }

  async DeprecateOrganisaton(): Promise<void> {
    const deprecateTitle = this.page.locator(
      "button.cursor-pointer.bg-transparent.border-lnds-color.border.p-2.w-10.h-10.rounded-md.flex.items-center.justify-center",
    );
    const deprecateIcon = deprecateTitle.nth(1);

    await expect(deprecateIcon).toBeVisible();
    await deprecateIcon.click();

    const confirmButton = this.page.getByRole("button", { name: "Confirm" });
    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
  }

  async assertOrganisationDeprecated(orgName: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    await this.page.waitForTimeout(2000);
    const orgList = this.page.locator(
      ".section-lnds-color.border-lnds-color.border.p-4.flex.w-full.flex-col",
    );
    const org1 = await orgList.nth(0).textContent();

    await expect(org1).toContain(orgName);
    await expect(org1).toContain("Deprecated");
  }

  async openOrganisationContactsPage(): Promise<void> {
    await this.page.locator("a:has-text('Contacts')").last().click();
    await this.page.waitForURL(`${BASE_URL}/organisations/1`);
    expect(this.page.url()).toContain("organisations/1");
  }

  async setContactName(name: string): Promise<void> {
    await this.page.locator(`[name='name']`).fill(name);
  }

  async setContactEmail(email: string): Promise<void> {
    await this.page.locator(`[name='email']`).fill(email);
  }

  async setContactRole(role: string): Promise<void> {
    await this.page.locator(`[name='role']`).fill(role);
  }

  async submitContact(): Promise<void> {
    await this.page.getByRole("button", { name: "Add" }).click();
  }

  async DeprecateContact(): Promise<void> {
    const deprecateButton = this.page
      .locator('td:last-child button[class*="cursor-pointer"]')
      .last();

    await expect(deprecateButton).toBeVisible();
    await deprecateButton.click();

    const confirmButton = this.page.getByRole("button", { name: "Confirm" });
    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
  }

  async restoreContact(): Promise<void> {
    const restoreButton = this.page.locator('td:last-child button[class*="cursor-pointer"]').last();

    await expect(restoreButton).toBeVisible();
    await restoreButton.click();

    const confirmButton = this.page.getByRole("button", { name: "Confirm" });
    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
  }

  async DeleteContact(): Promise<void> {
    const buttons = this.page.locator(
      "button.cursor-pointer.bg-transparent.border-lnds-color.border.p-2.w-10.h-10.rounded-md.flex.items-center.justify-center",
    );
    const deleteButton = buttons.nth(1);

    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
    const confirmButton = this.page.getByRole("button", { name: "Confirm" });
    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
  }

  async assertContactCreated(): Promise<void> {
    const alert = this.page.locator('div[role="alert"]');
    await expect(alert).toHaveText("Contact added successfully");
    await this.page.waitForTimeout(2000);
  }

  async assertContactDeleted(): Promise<void> {
    const alert = this.page.locator('div[role="alert"]');
    await expect(alert).toHaveText("Contact deleted successfully");
    await this.page.waitForTimeout(2000);
  }

  async assertContactDeprecated(): Promise<void> {
    const alert = this.page.locator('div[role="alert"]');
    await expect(alert).toHaveText("Contact successfully deprecated");
    await this.page.waitForTimeout(2000);
  }

  async assertContactRestored(): Promise<void> {
    const alert = this.page.locator('div[role="alert"]');
    await expect(alert).toHaveText("Contact successfully restored");
    await this.page.waitForTimeout(2000);
  }
}
