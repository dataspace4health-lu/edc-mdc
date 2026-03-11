import { expect } from "@playwright/test";
import type { Page, Locator } from "playwright";
import { BASE_URL } from "../config";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";

export class UsersPage {
  readonly page: Page;
  readonly visibleAlert: Locator;

  constructor(page: Page) {
    this.page = page;
    this.visibleAlert = this.page.locator("div[role=alert]:visible");
  }

  async openPage() {
    await this.page.goto(`${BASE_URL}/users`);
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/users`);
    expect(this.page.url()).toContain("users");
    expect(await this.page.locator("h1").first().innerText()).toBe("Filters");
    expect(await this.page.locator("h1:has-text('Assign Role')").innerText()).toContain(
      "Assign Role",
    );
  }

  async SelectExpandForm(): Promise<void> {
    await this.page.locator("button:has-text('Expand form')").click();
  }

  async setUserEmail(email: string): Promise<void> {
    await this.page.locator(`[name='email']`).fill(email);
  }

  async setUserOrganisation(organisation: string): Promise<void> {
    await fillAutoComplete(this.page, 1, organisation);
  }

  async setUserRole(role: string): Promise<void> {
    await fillAutoComplete(this.page, 2, role);
  }

  async createAssignment(): Promise<void> {
    await this.page.locator("button:has-text('Assign Role')").click();
    await this.page.waitForLoadState("networkidle");
  }
  async assertAssignCreated(): Promise<void> {
    await expect(this.visibleAlert).toContainText("Role assigned successfully");
  }

  async deleteOrganisation(): Promise<void> {
    await this.page.locator("button:has-text('Remove')").click();
    await this.page.waitForLoadState("networkidle");
  }

  async assertOrganisationDeleted(): Promise<void> {
    await expect(this.visibleAlert).toContainText("Organisation removed successfully");
  }

  async deleteRole(role: string): Promise<void> {
    const roleChip = this.page
      .locator("span", { hasText: role })
      .filter({ has: this.page.locator('button[aria-label="remove"]') })
      .first();
    await expect(roleChip).toBeVisible();
    await roleChip.locator('button[aria-label="remove"]').click();
    await this.page.waitForLoadState("networkidle");
  }

  async assertRoleDeleted(): Promise<void> {
    await expect(this.visibleAlert).toContainText("Role removed successfully");
  }

  async assertAssignDeleted(role: string): Promise<void> {
    await expect(this.page.locator(`span:has-text("${role}")`)).toHaveCount(0);
  }

  async deleteUnassignedUser(user: string): Promise<void> {
    const card = this.findUserCardByName(user);
    await card.locator(`button[title="Delete user"]`).click();
    await this.page.waitForLoadState("networkidle");
  }

  async assertUserDeleted(user: string): Promise<void> {
    await expect(this.findUserCardByName(user)).toHaveCount(0);
  }

  findUserCardByName(user: string): Locator {
    return this.page.locator(`xpath=//div[contains(., "${user}")]`);
  }

  async assertUserCreated(email: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");

    const userCard = this.page.locator(
      `xpath=//div[contains(@class, "section-lnds-color") and contains(., "${email}")]`,
    );

    await expect(userCard.first()).toBeVisible();
  }

  async DeprecateUser(email: string): Promise<void> {
    const userCard = this.page
      .locator(`xpath=//div[contains(@class, "section-lnds-color") and contains(., "${email}")]`)
      .first();

    const deprecateTitle = userCard.locator(
      "button.cursor-pointer.bg-transparent.border-lnds-color.border.p-2.w-10.h-10.rounded-md.flex.items-center.justify-center",
    );
    const deprecateIcon = deprecateTitle.nth(1);

    await expect(deprecateIcon).toBeVisible();
    await deprecateIcon.click();

    const confirmButton = this.page.getByRole("button", { name: "Confirm" });
    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
  }

  async assertUserDeprecated(email: string): Promise<void> {
    await this.page.waitForLoadState("networkidle");
    await this.page.waitForTimeout(2000);

    const userCard = this.page.locator(`xpath=//div[contains(., "${email}")]`);

    const text = await userCard.first().textContent();

    expect(text).toContain(email);
    expect(text).toContain("Deprecated");
  }
}
