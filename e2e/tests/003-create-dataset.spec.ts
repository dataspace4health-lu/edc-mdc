import { test } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { DatasetFormPage } from "../pages/datasetform-page";
import { DistributionsPage } from "../pages/distributions-page";
import { DummyDataset, DummyDistribution } from "../fixtures.ts/dataset-fixture";
import { loginAsContributor, loginAsGroupManagerAndLogout } from "../test-utils/login-as";

test("003.navigate to dataset form and create dataset", async ({ page }) => {
  // Login once as group manager so that user is created in db with role GroupManager. We need this user to create dataset
  await loginAsGroupManagerAndLogout(page);
  await loginAsContributor(page);

  const dataset = DummyDataset;
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.navigateToDatasetForm();

  const datasetFormPage = new DatasetFormPage(page);
  await datasetFormPage.assertPageLoaded();

  await datasetFormPage.setTitle(dataset.title);
  await datasetFormPage.setDescription(dataset.description);
  await datasetFormPage.setVersion(dataset.version);
  await datasetFormPage.setVersionNotes(dataset.version_notes);

  await datasetFormPage.setPublisherName(dataset.publisherName);
  await datasetFormPage.setCreatorName(dataset.creatorNames);
  await datasetFormPage.setContact(dataset.contact);
  await datasetFormPage.setGroupManagers(dataset.groupManagers);

  await datasetFormPage.setKeywords(dataset.keywords);
  await datasetFormPage.setThemes(dataset.themes);
  await datasetFormPage.setDatasetType(dataset.types);

  await datasetFormPage.setTimePeriodStart(dataset.start);
  await datasetFormPage.setTimePeriodEnd(dataset.end);
  await datasetFormPage.setPeriodicity(dataset.periodicity);
  await datasetFormPage.setReleaseDate(dataset.release_date);
  await datasetFormPage.setModificationDate(dataset.modification_date);

  await datasetFormPage.setRightsStatment(dataset.rights);
  await datasetFormPage.setDataProtectionTypes(dataset.data_protection_types);
  await datasetFormPage.setApplicableLegislations(dataset.applicableLegislations);
  await datasetFormPage.setDataConformsTo(dataset.conforms_to);

  await datasetFormPage.setDatasetLanguages(dataset.languages);
  await datasetFormPage.setSpatialCoverages(dataset.spatial_coverages);
  await datasetFormPage.setmonitoringLocation(dataset.monitoringLocation);
  await datasetFormPage.setLandingPages(dataset.landingPages);

  await datasetFormPage.setDatasetDocumentation(dataset.documentation);
  await datasetFormPage.setProvenance(dataset.provenance);

  await datasetFormPage.setConventions(dataset.conventions);
  await datasetFormPage.setAreasOfWork(dataset.areasOfWork);
  await datasetFormPage.setAreasOfCompetence(dataset.areasOfCompetence);
  await datasetFormPage.setDuration(dataset.duration_of_administrative_utility);
  await datasetFormPage.setFinalDisposition(dataset.final_disposition);
  await datasetFormPage.setNotes(dataset.notes);
  await datasetFormPage.setSpatialResolutions(dataset.spatial_resolutions);
  await datasetFormPage.setTemporalResolution(dataset.temporal_resolution);
  await datasetFormPage.setGeneratedBy(dataset.generated_by);
  await datasetFormPage.setOtherID(dataset.other_identifiers);

  await datasetFormPage.saveAsDraft();
  await page.waitForTimeout(5000);

  // Navigate to distributions page from sidebar
  await page.getByRole("link", { name: "Distributions" }).click();
  await page.waitForTimeout(1000);

  const distributionsPage = new DistributionsPage(page);
  await distributionsPage.expandForm();
  await page.waitForTimeout(500); // Wait for form to expand

  await distributionsPage.setDistributionTitle(DummyDistribution.title);
  await distributionsPage.setDistributionDescription(DummyDistribution.description);

  if (DummyDistribution.internalOnly) {
    await distributionsPage.setDistributionInternalOnly();
  }

  await distributionsPage.setDistributionPath(DummyDistribution.distribution_path);

  await distributionsPage.setDistributionFormat(DummyDistribution.format);
  await distributionsPage.setDistributionMediaType(DummyDistribution.media_type);
  await distributionsPage.setDistributionCompressionFormat(DummyDistribution.compression_format);
  await distributionsPage.setDistributionPackagingFormat(DummyDistribution.packaging_format);
  await distributionsPage.setDistributionSizeBytes(DummyDistribution.size_bytes);
  await distributionsPage.setDistributionCheckSum(DummyDistribution.checksum);
  await distributionsPage.setDistributionAccessURLs(DummyDistribution.access_urls);
  await distributionsPage.setDistributionDownloadURL(DummyDistribution.download_urls);

  await distributionsPage.setDistributionRightsStatment(dataset.rights);
  await distributionsPage.setDistributionLicense(DummyDistribution.license);

  if (DummyDistribution.policy_actions && DummyDistribution.policy_actions.length > 0) {
    await distributionsPage.setDistributionDataPolicy();
    await page.waitForTimeout(2000);

    const firstAction = DummyDistribution.policy_actions[0];

    if (firstAction.policyActionType !== "permission") {
      await distributionsPage.setDistributionAction(firstAction.policyActionType);
      await page.waitForTimeout(500);
    }

    await distributionsPage.setDistributionConstraint(firstAction.policyConstraintType);
    await page.waitForTimeout(1500);

    if (firstAction.policyConstraintType === "temporal") {
      await distributionsPage.setDistributionTemporalRestrictionStart(
        firstAction.temporalRestrictionStart,
      );
      await distributionsPage.setDistributionTemporalRestrictionEnd(
        firstAction.temporalRestrictionEnd,
      );
    }
  }

  await distributionsPage.setDistributionApplicableLegislations(
    DummyDistribution.applicableLegislations,
  );
  await distributionsPage.setDistributionLinkedSchemas(DummyDistribution.linked_schemas);
  await distributionsPage.setDistributionLanguages(DummyDistribution.language);

  await distributionsPage.setDistributionAvailability(DummyDistribution.availability);
  await distributionsPage.setDistributionDCATStatus(DummyDistribution.distributionDCATStatus);
  await distributionsPage.setDistributionReleaseDate(DummyDistribution.distribution_release_date);

  await distributionsPage.setDistributionModificationDate(DummyDistribution.modification_date);
  await distributionsPage.setDistributionDocumentation(DummyDistribution.documentation);
  await distributionsPage.setDistributionNotes(DummyDistribution.notes);
  await distributionsPage.setDistributionSpatialResolution(
    DummyDistribution.distribution_spatial_resolution,
  );
  await distributionsPage.setDistributionTemporalResolution(
    DummyDistribution.distribution_temporal_resolution,
  );

  await distributionsPage.submitDistribution();
  await distributionsPage.assertDistributionCreated();

  // Go back to landing page to verify dataset
  await datasetFormPage.goToHomePage();
  await page.waitForTimeout(5000);
  await landingPage.assertDatasetCreated(dataset);
});
