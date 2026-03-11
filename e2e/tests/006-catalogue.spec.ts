import { test } from "@playwright/test";
import { CataloguePage } from "../pages/catalogue-page";
import { LandingPage } from "../pages/landing-page";
import { loginAsDataManager } from "../test-utils/login-as";

test("006.Download Catalogue", async ({ page }) => {
  await loginAsDataManager(page);

  const landingPage = new LandingPage(page);
  await landingPage.openDatasetModal("1");
  await landingPage.clickSubmitDataset();
  await landingPage.validateDataset();
  await landingPage.approveDataset();
  await landingPage.publishDataset();
  await landingPage.closeModal();

  await landingPage.openDatasetModal("2");
  await landingPage.clickSubmitDataset();
  await landingPage.validateDataset();
  await landingPage.approveDataset();
  await landingPage.publishDataset();
  await landingPage.closeModal();

  const cataloguePage = new CataloguePage(page);

  await cataloguePage.downloadCatalogue();
  await cataloguePage.assertDataset();
});
