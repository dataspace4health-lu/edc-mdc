import { test } from "@playwright/test";
import { AddDictionaryPage } from "../pages/add-dictionary-page";
import { LandingPage } from "../pages/landing-page";
import { loginAsContributor } from "../test-utils/login-as";

test("004.add and remove data dictionary", async ({ page }) => {
  await loginAsContributor(page);
  const dictionaryPage = new AddDictionaryPage(page, "1");

  await dictionaryPage.openPage();
  await dictionaryPage.assertPageLoaded();
  await dictionaryPage.cleanupExistingEntries();
  await dictionaryPage.bulkUploadDictionary();
  await dictionaryPage.addDictionaryEntry();
  await dictionaryPage.assertDictionaryEntries();

  await dictionaryPage.reorderEntries();
  await dictionaryPage.assertReorderedEntries();

  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.openDatasetModal("1");
  await landingPage.openDictionaryTab();
  await landingPage.assertDictionaryEntry();

  await dictionaryPage.openPage();
  await dictionaryPage.assertPageLoaded();
  await dictionaryPage.cleanupExistingEntries();
  await dictionaryPage.assertRemovedDictionaryEntry();
});
