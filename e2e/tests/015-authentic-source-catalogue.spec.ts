import { test, expect } from "@playwright/test";
import { loginAsCatalogueManager } from "../test-utils/login-as";
import { LandingPage } from "../pages/landing-page";
import { AddDictionaryPage } from "../pages/add-dictionary-page";
import { AuthenticSourceLabelsPage } from "../pages/authentic-source-page";
import { DatasetFormPage } from "../pages/datasetform-page";
import {
  DummyAuthenticSourceLabel,
  DummyAuthenticSourceLabel2,
  DummyAuthenticSourceLabel3,
} from "../fixtures.ts/authentic-source-label-fixture";

test.skip("0015.a.Authentic source labels: create and assign", async ({ page }) => {
  await loginAsCatalogueManager(page);

  const aslPage = new AuthenticSourceLabelsPage(page);
  await aslPage.openPage();
  await aslPage.assertPageLoaded();

  // Create authentic source labels
  await aslPage.createLabel(DummyAuthenticSourceLabel.name, DummyAuthenticSourceLabel.description);
  await aslPage.assertLabelVisible(DummyAuthenticSourceLabel.name);

  await aslPage.createLabel(
    DummyAuthenticSourceLabel2.name,
    DummyAuthenticSourceLabel2.description,
  );
  await aslPage.assertLabelVisible(DummyAuthenticSourceLabel2.name);

  await aslPage.createLabel(
    DummyAuthenticSourceLabel3.name,
    DummyAuthenticSourceLabel3.description,
  );
  await aslPage.assertLabelVisible(DummyAuthenticSourceLabel3.name);

  const labelCount = await aslPage.getCountBadge();
  expect(labelCount).toBeGreaterThanOrEqual(3);

  // Navigate to datasets and prepare a dataset for assignment
  const landingPage = new LandingPage(page);
  await landingPage.openPage();

  await page.getByRole("link", { name: /Draft/ }).click();
  await page.waitForLoadState("networkidle");

  const draftDatasetCard = page.locator('[class*="dataset-card-"]').first();
  await expect(draftDatasetCard).toBeVisible({ timeout: 10000 });

  const datasetId =
    (await draftDatasetCard.evaluate((card) => {
      const classNames = card.className;
      const match = classNames.match(/dataset-card-(\d+)/);
      return match ? match[1] : null;
    })) || "1";

  // Add data dictionary entries
  const ddPage = new AddDictionaryPage(page, datasetId);
  await ddPage.openPage();
  await ddPage.assertPageLoaded();
  await ddPage.addDictionaryEntry();
  await ddPage.bulkUploadDictionary();

  // Set up dataset for publishing
  const form = new DatasetFormPage(page);
  await form.openEditPage(Number(datasetId));
  await form.assertEditPageLoaded(Number(datasetId));

  await form.setGroupManagers(["Yunis Adam"]);

  await form.update();

  // Publish the dataset
  await landingPage.openPage();
  await page.getByRole("link", { name: /Draft/i }).click();
  await page.waitForLoadState("networkidle");
  await landingPage.openDatasetModal(datasetId);
  await landingPage.clickSubmitDataset();
  await landingPage.validateDataset();
  await landingPage.approveDataset();
  await landingPage.publishDataset();
  await landingPage.closeModal();

  await landingPage.openPage();
  await page.getByRole("link", { name: /Published/i }).click();

  // Assign labels to data dictionary entries
  await aslPage.assignLabel("Data_1", DummyAuthenticSourceLabel.name, datasetId);

  await aslPage.assignLabel("Data_2", DummyAuthenticSourceLabel2.name, datasetId);
  await aslPage.clickConfirmAuthenticSources();

  await page.waitForTimeout(1000);

  // Verify labels were assigned by going back to the authentic source page
  await aslPage.openPage();
  await aslPage.assertLabelVisible(DummyAuthenticSourceLabel.name);
  await aslPage.assertLabelVisible(DummyAuthenticSourceLabel2.name);
  await aslPage.downloadCatalogue("rdf");
  await aslPage.assertAuthenticSourceLabels();
});
