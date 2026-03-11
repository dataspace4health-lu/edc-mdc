import { test } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { DatasetFormPage } from "../pages/datasetform-page";
import { loginAsDataManager } from "../test-utils/login-as";

test("010.a Create new version from published dataset", async ({ page }) => {
  await loginAsDataManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.switchToPublishedTab();
  await landingPage.openDatasetModal("1");

  await landingPage.createNewVersion();

  const datasetFormPage = new DatasetFormPage(page);
  await datasetFormPage.setTitle("Dummy Dataset 1 version 1");
  await datasetFormPage.saveAsDraft();
  await datasetFormPage.goToHomePage();
});

test("010.b View new version in draft tab", async ({ page }) => {
  await loginAsDataManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.switchToDraftTab();
  await landingPage.openDatasetModal("4");

  await landingPage.assertDatasetStatus("Draft");
  await landingPage.closeModal();
});

test("010.c View new version changes", async ({ page }) => {
  await loginAsDataManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.switchToDraftTab();
  await landingPage.openDatasetModal("4");
  await landingPage.viewChanges();
  await landingPage.showChanges();

  await landingPage.assertVersionChangesContain({
    headers: ["Changes from last version", "Current Version", "Last Version"],
    fieldName: "Title",
    oldValue: "Dummy Dataset 1",
    newValue: "Dummy Dataset 1 version 1",
  });

  await landingPage.closeModal();
});

test("010.d Publish new version", async ({ page }) => {
  await loginAsDataManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.switchToDraftTab();
  await landingPage.openDatasetModal("4");

  await landingPage.clickSubmitDataset();
  await landingPage.validateDataset();
  await landingPage.approveDataset();
  await landingPage.publishDataset();

  await landingPage.closeModal();
});

test("010.e Verify original dataset is deprecated when new version is published", async ({
  page,
}) => {
  await loginAsDataManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.switchToDeprecatedTab();
  await landingPage.openDatasetModal("1");

  await landingPage.assertDatasetDeprecated("Deprecated");
  await landingPage.closeModal();
});
