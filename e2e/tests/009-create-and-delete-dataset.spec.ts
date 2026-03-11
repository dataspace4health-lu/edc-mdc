import { test } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { DatasetFormPage } from "../pages/datasetform-page";
import { DummyDataset } from "../fixtures.ts/dataset-fixture";
import { loginAsDataManager, loginAsGroupManagerAndLogout } from "../test-utils/login-as";

test("009.create and delete dataset", async ({ page }) => {
  await loginAsGroupManagerAndLogout(page);

  await loginAsDataManager(page);
  const dataset = DummyDataset;
  dataset.title = "title";

  const landingPage = new LandingPage(page);
  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.navigateToDatasetForm();

  const datasetFormPage = new DatasetFormPage(page);
  await datasetFormPage.assertPageLoaded();

  await datasetFormPage.setTitle(dataset.title);
  await datasetFormPage.setDescription(dataset.description);
  if (dataset.dataset_series) {
    await datasetFormPage.setDatasetSeries(dataset.dataset_search);
  }
  await datasetFormPage.setVersion(dataset.version);
  await datasetFormPage.setVersionNotes(dataset.version_notes);
  await datasetFormPage.setProvenance(dataset.provenance);
  await datasetFormPage.setPublisherName(dataset.publisherName);
  await datasetFormPage.setGroupManagers(dataset.groupManagers);
  await datasetFormPage.setDatasetType(dataset.types);
  await datasetFormPage.setTimePeriodStart(dataset.start);
  await datasetFormPage.setPeriodicity(dataset.periodicity);
  await datasetFormPage.setRightsStatment(dataset.rights);

  await datasetFormPage.setKeywords(dataset.keywords);
  await datasetFormPage.setThemes(dataset.themes);
  await datasetFormPage.setContact(dataset.contact);

  await page.waitForTimeout(500);

  await datasetFormPage.saveAsDraft();
  await datasetFormPage.goToHomePage();
  await page.waitForTimeout(1000);

  await landingPage.assertDatasetCreated(dataset);
  await page.waitForTimeout(1000);

  await landingPage.switchToDraftTab();
  await landingPage.openDatasetOptions();
  await landingPage.selectDeleteOption();
  await landingPage.confirmDatasetDeletion();
  await page.waitForTimeout(1000);
});
