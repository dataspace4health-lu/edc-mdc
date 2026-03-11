import { LandingPage } from "../pages/landing-page";
import { KeycloakPage } from "../pages/keycloak-page";

export const loginAsDataManager = async (page) => {
  const keycloakPage = new KeycloakPage(page);

  await keycloakPage.openPage("login");
  await keycloakPage.assertPageLoaded("Sign in to your account");
  await keycloakPage.login("ami@lnds.lu", "test");

  await page.waitForLoadState("networkidle");

  const landingPage = new LandingPage(page);
  await landingPage.assertPageLoaded();
  await landingPage.assertAppTitle();
};

export const loginAsContributor = async (page) => {
  const keycloakPage = new KeycloakPage(page);

  await keycloakPage.openPage("login");
  await keycloakPage.assertPageLoaded("Sign in to your account");
  await keycloakPage.login("jia@lnds.lu", "test");

  await page.waitForLoadState("networkidle");

  const landingPage = new LandingPage(page);
  await landingPage.assertPageLoaded();
  await landingPage.assertAppTitle();
};

export const loginAsCatalogueManager = async (page) => {
  const keycloakPage = new KeycloakPage(page);

  await keycloakPage.openPage("login");
  await keycloakPage.assertPageLoaded("Sign in to your account");
  await keycloakPage.login("safe@lnds.lu", "test");

  await page.waitForLoadState("networkidle");

  const landingPage = new LandingPage(page);
  await landingPage.assertPageLoaded();
  await landingPage.assertAppTitle();
};

export const loginAsGroupManagerAndLogout = async (page) => {
  const keycloakPage = new KeycloakPage(page);

  await keycloakPage.openPage("login");
  await keycloakPage.assertPageLoaded("Sign in to your account");
  await keycloakPage.login("yunis@lnds.lu", "test");

  await page.waitForLoadState("networkidle");

  const landingPage = new LandingPage(page);
  await landingPage.assertPageLoaded();
  await landingPage.assertAppTitle();

  await landingPage.logout();

  await page.waitForLoadState("networkidle");

  await keycloakPage.assertPageLoaded("Logging out");
  await keycloakPage.confirmLogout();
  await keycloakPage.assertLoggedOut();
};
