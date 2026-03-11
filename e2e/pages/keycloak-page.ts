import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";

export class KeycloakPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage(path: string) {
    await this.page.goto(`${BASE_URL}/${path}`);
  }

  async login(username: string, password: string): Promise<void> {
    await this.page.fill("#username", username);
    await this.page.fill("#password", password);
    await this.page.click("#kc-login");
  }

  async confirmLogout(): Promise<void> {
    const logoutButton = this.page.locator("#kc-logout");
    await logoutButton.click();
  }

  async assertPageLoaded(message: string): Promise<void> {
    await expect(this.page.locator("h1")).toHaveText(message);
  }

  async assertLoggedOut() {
    await expect(this.page.locator("#kc-page-title")).toHaveText("You are logged out");
  }
}
