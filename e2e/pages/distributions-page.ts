import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";
import { BASE_URL } from "../config";
import { RightsLabelValueMapping } from "../fixtures.ts/dataset-fixture";

const dropdowns = [
  "distributionPath",
  "distributionFormat", // This is "fileFormat" in schema
  "mediaType",
  "compressionFormat",
  "packagingFormat",
  "accessURLs",
  "downloadURLs",
  "accessService", // This is "accessServices" in schema
  "distributionLicense", // This is "license" in schema
  "action", // policyActionType (inside policy)
  "constraint", // policyConstraintType (inside policy)
  "distributionApplicableLegislations", // This is "legalBases" in schema
  "linkedSchemas",
  "distributionLanguages", // This is "languages" in schema
  "distributionAvailability", // This is "availability" in schema
  "distributionDCATStatus",
  "documentation", // Multi-value documentation field
];

export class DistributionsPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openPage(datasetId: number): Promise<void> {
    await this.page.goto(`${BASE_URL}/datasets/${datasetId}/distributions`);
  }

  async assertPageLoaded(datasetId: number): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/datasets/${datasetId}/distributions`);
    expect(this.page.url()).toContain(`/datasets/${datasetId}/distributions`);
  }

  async expandForm(): Promise<void> {
    await this.page.locator("button:has-text('Expand form')").click();
  }

  async setDistributionTitle(title: string): Promise<void> {
    await this.page.locator(`[name='title']`).first().fill(title);
  }

  async setDistributionDescription(description: string): Promise<void> {
    await this.page.locator(`[name='description']`).first().fill(description);
  }

  async setDistributionInternalOnly(): Promise<void> {
    const hiddenCheckbox = await this.page.locator(`[name='internalOnly']`);
    // @ts-expect-error Property 'click' does not exist on type
    await hiddenCheckbox.evaluate((checkbox) => checkbox.click());
  }

  async setDistributionPath(path: string): Promise<void> {
    const distributionPathIndex = dropdowns.indexOf("distributionPath");
    await fillAutoComplete(this.page, distributionPathIndex, path);
  }

  async setDistributionFormat(format: string): Promise<void> {
    const distributionFormatIndex = dropdowns.indexOf("distributionFormat");
    await fillAutoComplete(this.page, distributionFormatIndex, format);
  }

  async setDistributionMediaType(mediaType: string): Promise<void> {
    const mediaTypeIndex = dropdowns.indexOf("mediaType");
    await fillAutoComplete(this.page, mediaTypeIndex, mediaType);
  }

  async setDistributionCompressionFormat(compressionFormat: string): Promise<void> {
    const compressionFormatIndex = dropdowns.indexOf("compressionFormat");
    await fillAutoComplete(this.page, compressionFormatIndex, compressionFormat);
  }

  async setDistributionPackagingFormat(packagingFormat: string): Promise<void> {
    const packagingFormatIndex = dropdowns.indexOf("packagingFormat");
    await fillAutoComplete(this.page, packagingFormatIndex, packagingFormat);
  }

  async setDistributionSizeBytes(sizeBytes: number): Promise<void> {
    await this.page.locator(`[name='byteSize']`).first().fill(sizeBytes.toString());
  }

  async setDistributionCheckSum(checksum: string): Promise<void> {
    await this.page.locator(`[name='checksum']`).first().fill(checksum);
  }

  async setDistributionAccessURLs(accessURLs: string | string[]): Promise<void> {
    const accessURLsIndex = dropdowns.indexOf("accessURLs");
    await fillAutoComplete(this.page, accessURLsIndex, accessURLs);
  }

  async setDistributionDownloadURL(downloadURLs: string | string[]): Promise<void> {
    const downloadURLsIndex = dropdowns.indexOf("downloadURLs");
    await fillAutoComplete(this.page, downloadURLsIndex, downloadURLs);
  }

  async setDistributionRightsStatment(rightsStatement: string): Promise<void> {
    const rightsValue = RightsLabelValueMapping[rightsStatement];
    await this.page
      .locator(`input[name='distributionRightsStatement'][value='${rightsValue}']`)
      .click();
  }

  async setDistributionLicense(license: string): Promise<void> {
    const distributionLicenseIndex = dropdowns.indexOf("distributionLicense");
    await fillAutoComplete(this.page, distributionLicenseIndex, license);
  }

  async setDistributionDataPolicy(): Promise<void> {
    const hiddenCheckbox = this.page.locator(`[name='hasPolicy']`).first();
    // @ts-expect-error Property 'click' does not exist on type
    await hiddenCheckbox.evaluate((checkbox) => checkbox.click());
  }

  async setDistributionAction(action: string): Promise<void> {
    const actionIndex = dropdowns.indexOf("action");
    await fillAutoComplete(this.page, actionIndex, action);
  }

  async setDistributionConstraint(constraint: string): Promise<void> {
    const constraintIndex = dropdowns.indexOf("constraint");
    await fillAutoComplete(this.page, constraintIndex, constraint);
  }

  async setDistributionTemporalRestrictionStart(date: string): Promise<void> {
    await this.page
      .locator(`[name='policyActions[0].temporalRestrictionStart']`)
      .first()
      .fill(date);
  }

  async setDistributionTemporalRestrictionEnd(date: string): Promise<void> {
    await this.page.locator(`[name='policyActions[0].temporalRestrictionEnd']`).first().fill(date);
  }

  async setDistributionApplicableLegislations(
    applicableLegislations: string | string[],
  ): Promise<void> {
    const distributionApplicableLegislationsIndex = dropdowns.indexOf(
      "distributionApplicableLegislations",
    );
    await fillAutoComplete(
      this.page,
      distributionApplicableLegislationsIndex,
      applicableLegislations,
    );
  }

  async setDistributionLinkedSchemas(linkedSchemas: string | string[]): Promise<void> {
    const linkedSchemasIndex = dropdowns.indexOf("linkedSchemas");
    await fillAutoComplete(this.page, linkedSchemasIndex, linkedSchemas);
  }

  async setDistributionLanguages(languages: string | string[]): Promise<void> {
    const distributionLanguagesIndex = dropdowns.indexOf("distributionLanguages");
    await fillAutoComplete(this.page, distributionLanguagesIndex, languages);
  }

  async setDistributionAvailability(availability: string): Promise<void> {
    const distributionAvailabilityIndex = dropdowns.indexOf("distributionAvailability");
    await fillAutoComplete(this.page, distributionAvailabilityIndex, availability);
  }

  async setDistributionDCATStatus(status: string): Promise<void> {
    const distributionDCATStatusIndex = dropdowns.indexOf("distributionDCATStatus");
    await fillAutoComplete(this.page, distributionDCATStatusIndex, status);
  }

  async setDistributionReleaseDate(date: string): Promise<void> {
    await this.page.locator(`[name='releaseDate']`).fill(date);
  }

  async setDistributionModificationDate(date: string): Promise<void> {
    await this.page.locator(`[name='modificationDate']`).fill(date);
  }

  async setDistributionDocumentation(documentation: string | string[]): Promise<void> {
    const documentationIndex = dropdowns.indexOf("documentation");
    await fillAutoComplete(this.page, documentationIndex, documentation);
  }

  async setDistributionNotes(notes: string): Promise<void> {
    await this.page.locator(`[name='notes']`).first().fill(notes);
  }

  async setDistributionSpatialResolution(spatialResolution: number): Promise<void> {
    await this.page.locator(`[name='spatialResolution']`).fill(spatialResolution.toString());
  }

  async setDistributionTemporalResolution(temporalResolution: string): Promise<void> {
    await this.page.locator(`[name='temporalResolution']`).fill(temporalResolution);
  }

  async submitDistribution(): Promise<void> {
    await this.page.getByRole("button", { name: /Insert/i }).click();
  }

  async assertDistributionCreated(): Promise<void> {
    await expect(this.page.getByText(/Distribution added successfully/i)).toBeVisible({
      timeout: 5000,
    });
  }
}
