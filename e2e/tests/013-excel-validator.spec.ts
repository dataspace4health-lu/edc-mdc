import { test, expect } from "@playwright/test";
import { updateFeatureFlag, resetConfig } from "../test-utils/config-api";
import { loginAsCatalogueManager } from "../test-utils/login-as";
import { BulkUploadPage } from "../pages/bulk-upload-page";
import { LandingPage } from "../pages/landing-page";
import { OrganisationFormPage } from "../pages/organisationform-page";
import {
  BulkUploadedDataset1,
  BulkUploadedDataset2,
  Distribution,
  NonExistentContact,
} from "../fixtures.ts/bulk-upload-fixture";
import { KeywordsPage } from "../pages/keywords-page";
import { ApplicableLegislationPage } from "../pages/applicable-legislation-page";

test.beforeEach(async () => {
  await resetConfig();
  await updateFeatureFlag("enable_multi_tenants", true);
});

test("013.Validate and Upload datasets", async ({ page }) => {
  await loginAsCatalogueManager(page);

  const bulkUploadPage = new BulkUploadPage(page);
  const landingPage = new LandingPage(page);
  const organisationFormPage = new OrganisationFormPage(page);
  const contact = NonExistentContact;
  const keywordsPage = new KeywordsPage(page);
  const applicableLegislationPage = new ApplicableLegislationPage(page);

  await bulkUploadPage.openPage();
  await bulkUploadPage.assertPageLoaded();
  await bulkUploadPage.uploadFile();
  await expect(page.getByText("Selected file: DCAT-AP-LU_official-e2e.xlsm")).toBeVisible({
    timeout: 5000,
  });
  await bulkUploadPage.clickCreateDataset();
  await bulkUploadPage.assertSuccessMessage();

  await landingPage.openPage();
  await landingPage.assertPageLoaded();

  await bulkUploadPage.openDatasetModal("5");
  await bulkUploadPage.assertDatasetModal(BulkUploadedDataset1);
  await bulkUploadPage.openDistributionsTab();
  await bulkUploadPage.assertDistributions(Distribution);

  await bulkUploadPage.openDictionaryTab();
  await bulkUploadPage.assertDictionaryEntry();

  await landingPage.openPage();
  await landingPage.assertPageLoaded();

  await bulkUploadPage.openDatasetModal("6");
  await bulkUploadPage.assertDatasetModal(BulkUploadedDataset2);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();

  await organisationFormPage.openPage();
  await organisationFormPage.assertPageLoaded();
  await organisationFormPage.openOrganisationContactsPage();

  await expect(page.locator(`text=${contact.name}`).nth(0)).toBeVisible();
  await expect(page.locator(`text=${contact.email}`)).toBeVisible();
  await expect(page.locator(`text=${contact.role}`)).toBeVisible();

  await keywordsPage.openPage();
  await keywordsPage.assertPageLoaded();
  await keywordsPage.assertKeywordCreated("society");
  await keywordsPage.assertKeywordCreated("policy");
  await keywordsPage.assertKeywordCreated("people");

  await applicableLegislationPage.openPage();
  await applicableLegislationPage.assertPageLoaded();
  await applicableLegislationPage.assertCreated("Law #123, art 5");
  await applicableLegislationPage.assertCreated("Applicable Legislation");
});
