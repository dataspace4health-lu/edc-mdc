import { test } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { loginAsContributor } from "../test-utils/login-as";

test("007.activity log test", async ({ page }) => {
  await loginAsContributor(page);
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.openDatasetModal("1");
  await landingPage.openActivityLogsTab();
  await landingPage.assertActivityLogs();
});
