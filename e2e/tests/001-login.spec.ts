import { test } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { KeycloakPage } from "../pages/keycloak-page";
import { resetConfig } from "../test-utils/config-api";

const authContextFile = ".auth/user.json";

// This will run before each test across ALL test files
test.beforeEach(async () => {
  await resetConfig();
});

// This will run after each test across ALL test files
test.afterEach(async () => {
  await resetConfig();
});

test("001.login and logout flows valid", async ({ page }) => {
  const keycloakPage = new KeycloakPage(page);

  await keycloakPage.openPage("login");
  await keycloakPage.assertPageLoaded("Sign in to your account");
  await keycloakPage.login("ami@lnds.lu", "test");

  await page.waitForLoadState("networkidle");

  const landingPage = new LandingPage(page);

  await landingPage.assertPageLoaded();
  await landingPage.assertAppTitle();
  await page.context().storageState({ path: authContextFile });

  await landingPage.logout();

  await page.waitForLoadState("networkidle");

  await keycloakPage.assertPageLoaded("Logging out");
  await keycloakPage.confirmLogout();
  await keycloakPage.assertLoggedOut();
});
