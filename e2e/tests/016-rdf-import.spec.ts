import { test } from "@playwright/test";
import { RdfImportPage } from "../pages/rdf-import-page";
import { loginAsCatalogueManager } from "../test-utils/login-as";

test("016.a import dataset and edit title and description", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const rdfImportPage = new RdfImportPage(page);
  await rdfImportPage.openPage();
  await rdfImportPage.assertPageLoaded();

  const rdfContent = await rdfImportPage.createTestRdf("test-dataset-001");
  await rdfImportPage.importRdfContent(rdfContent);
  await rdfImportPage.assertSuccessAlert();
  await rdfImportPage.assertViewDatasetButtonExists();

  await rdfImportPage.clickViewDatasetButton();
  await rdfImportPage.navigateToEditPage();

  await rdfImportPage.editDatasetFields(
    "Edited Test Dataset Title",
    "This is an edited description for the test dataset.",
  );
  await rdfImportPage.saveDatasetAsDraft();
  await rdfImportPage.assertDatasetUpdatedSuccessfully();
});

test("016.b prevent duplicate dataset import", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const rdfImportPage = new RdfImportPage(page);
  await rdfImportPage.openPage();
  await rdfImportPage.assertPageLoaded();

  const rdfContent = await rdfImportPage.createTestRdf(
    "test-dataset-002",
    "Edited Test Dataset Title",
    "This is an edited description for the test dataset.",
  );
  await rdfImportPage.importRdfContent(rdfContent);
  await rdfImportPage.assertErrorAlert(
    "A dataset with the same title, description, and publisher already exists.",
  );
});
