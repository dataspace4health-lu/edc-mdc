import { test } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { DummyDataset, DummyDistribution } from "../fixtures.ts/dataset-fixture";
import { loginAsContributor } from "../test-utils/login-as";

test("008.dataset modal test", async ({ page }) => {
  await loginAsContributor(page);
  const dataset = DummyDataset;
  const distribution = DummyDistribution;
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.openDatasetModal("1");
  await landingPage.assertDatasetModal(dataset);
  await landingPage.openDistributionsTab();
  await landingPage.assertDistributions(distribution);
});
