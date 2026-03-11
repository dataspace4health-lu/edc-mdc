import { test } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { DatasetFormPage } from "../pages/datasetform-page";
import { DistributionsPage } from "../pages/distributions-page";
import { AddRelationsPage } from "../pages/add-relations-page";
import { DummyDataset, DummyDataset2, DummyDistribution } from "../fixtures.ts/dataset-fixture";
import { loginAsContributor } from "../test-utils/login-as";

test("005.create dataset relation", async ({ page }) => {
  await loginAsContributor(page);
  const dataset1 = DummyDataset;
  const dataset2 = DummyDataset2;

  const datasetFormPage = new DatasetFormPage(page);
  await datasetFormPage.openEditPage(1);
  await datasetFormPage.assertEditPageLoaded(1);
  await datasetFormPage.update();

  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.navigateToDatasetForm();
  await datasetFormPage.assertPageLoaded();

  await datasetFormPage.setContact(dataset2.contact);
  await datasetFormPage.setTitle(dataset2.title);
  await datasetFormPage.setDescription(dataset2.description);
  await datasetFormPage.setGroupManagers(dataset2.groupManagers);
  await datasetFormPage.setDatasetType(dataset2.types);
  await datasetFormPage.setKeywords(dataset2.keywords);
  await datasetFormPage.setThemes(dataset2.themes);
  await datasetFormPage.setSpatialCoverages(dataset2.spatial_coverages);
  await datasetFormPage.setmonitoringLocation(dataset2.monitoringLocation);
  await datasetFormPage.setApplicableLegislations(dataset2.applicableLegislations);
  await datasetFormPage.setConventions(dataset2.conventions);
  await datasetFormPage.setAreasOfWork(dataset2.areasOfWork);
  await datasetFormPage.setRightsStatment(dataset2.rights);
  await datasetFormPage.setPeriodicity(dataset2.periodicity);
  await datasetFormPage.setNotes(dataset2.notes);
  await datasetFormPage.setDuration(dataset2.duration_of_administrative_utility);
  await datasetFormPage.setFinalDisposition(dataset2.final_disposition);
  await datasetFormPage.setVersion(dataset2.version);
  await datasetFormPage.setVersionNotes(dataset2.version_notes);
  await datasetFormPage.setProvenance(dataset2.provenance);
  await datasetFormPage.setCreatorName(dataset2.creatorNames);
  await datasetFormPage.setPublisherName(dataset2.publisherName);
  await datasetFormPage.setTimePeriodStart(dataset2.start);
  await datasetFormPage.setTimePeriodEnd(dataset2.end);

  await datasetFormPage.setSpatialResolutions(dataset2.spatial_resolutions);
  await datasetFormPage.saveAsDraft();

  // Add a minimal distribution for dataset 2 so this scenario is self-contained.
  await page.getByRole("link", { name: "Distributions" }).click();
  await page.waitForTimeout(1000);

  const distributionsPage = new DistributionsPage(page);
  await distributionsPage.expandForm();
  await page.waitForTimeout(500);
  await distributionsPage.setDistributionTitle("Dummy Dist 2");
  await distributionsPage.setDistributionAccessURLs(DummyDistribution.access_urls);
  await distributionsPage.setDistributionRightsStatment(dataset2.rights);
  await distributionsPage.submitDistribution();
  await distributionsPage.assertDistributionCreated();

  await datasetFormPage.goToHomePage();
  await page.waitForTimeout(1000); // wait for redirect

  await landingPage.assertDatasetCreated(dataset2);

  const relationsPage = new AddRelationsPage(page);

  await relationsPage.openPage();
  await relationsPage.assertPageLoaded();
  await relationsPage.addDatasetRelation();
  await relationsPage.assertAddedDatasetRelation();

  await landingPage.openPage();
  await landingPage.openDatasetModal("2");
  await landingPage.openRelationsTab();
  await landingPage.assertRelationsEntry("has Part", dataset1.title);
  await landingPage.closeModal();

  await landingPage.openDatasetModal("1");
  await landingPage.openRelationsTab();
  await landingPage.assertRelationsEntry("is Part Of", dataset2.title);
  await landingPage.closeModal();
});

test("005.a Create external relation", async ({ page }) => {
  await loginAsContributor(page);

  const relationsPage = new AddRelationsPage(page);
  await relationsPage.openPage();
  await relationsPage.assertPageLoaded();
  await relationsPage.addExternalRelation();
  await relationsPage.assertAddedExternalRelation();
});

test("005.b Remove relations", async ({ page }) => {
  await loginAsContributor(page);

  const relationsPage = new AddRelationsPage(page);
  await relationsPage.openPage();
  await relationsPage.assertPageLoaded();
  await relationsPage.removeRelation();
});
