import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { RightsLabelValueMapping } from "../fixtures.ts/dataset-fixture";
import { fillAutoComplete } from "../test-utils/fill-auto-complete";
import { BASE_URL } from "../config";

const dropdowns = [
  "publisherName",
  "creatorName",
  "contact",
  "groupManagers",
  "keywords",
  "themes",
  "datasetType",
  "periodicity",
  "dataProtectionTypes",
  "applicableLegislations",
  "conformsTo",
  "datasetLanguages",
  "spatialCoverages",
  "landingPages",
  "documentation",
  "conventions",
  "areasOfWork",
  "areasOfCompetence",
  "finalDisposition",
  "spatialResolutions",
  "wasGeneratedBy",
  "otherIdentifiers",
];

export class DatasetFormPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async openEditPage(datasetId: number): Promise<void> {
    await this.page.goto(`${BASE_URL}/datasets/${datasetId}/edit`);
  }

  async assertEditPageLoaded(datasetId: number): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/datasets/${datasetId}/edit`);
    expect(this.page.url()).toContain(`/datasets/${datasetId}/edit`);
    expect(await this.page.locator("h1").first().innerText()).toBe("Edit Dataset Metadata");
  }

  async assertPageLoaded(): Promise<void> {
    await this.page.waitForURL(`${BASE_URL}/datasetform`);
    expect(this.page.url()).toContain("datasetform");
    expect(await this.page.locator("h1").first().innerText()).toBe("Add Dataset Metadata");
  }

  async setDatasetSeries(dataset_search: string): Promise<void> {
    const hiddenCheckbox = await this.page.locator(`[name='isDatasetSeries']`);
    // @ts-expect-error Property 'click' does not exist on type
    await hiddenCheckbox.evaluate((checkbox) => checkbox.click());
    await this.page.locator(`[name='datasetSearch']`).fill(dataset_search);
    await this.page
      .locator("form")
      .getByRole("button", { name: "Add", exact: true })
      .first()
      .click();
  }

  async setGroupManagers(groupManagers: string[]): Promise<void> {
    const dropdownIndex = dropdowns.indexOf("groupManagers");
    await fillAutoComplete(this.page, dropdownIndex, groupManagers);
  }

  async setPublisherName(publisher: string): Promise<void> {
    const publisherIndex = dropdowns.indexOf("publisherName");
    await fillAutoComplete(this.page, publisherIndex, publisher);
  }

  async setCreatorName(creators: string | string[]): Promise<void> {
    const creatorIndex = dropdowns.indexOf("creatorName");
    await fillAutoComplete(this.page, creatorIndex, creators);
  }

  async setContact(contact: string): Promise<void> {
    const contactIndex = dropdowns.indexOf("contact");
    await fillAutoComplete(this.page, contactIndex, contact);
  }

  async setKeywords(keywords: string[]): Promise<void> {
    const keywordsIndex = dropdowns.indexOf("keywords");
    await fillAutoComplete(this.page, keywordsIndex, keywords);
  }

  async setThemes(themes: string[]): Promise<void> {
    const themesIndex = dropdowns.indexOf("themes");
    await fillAutoComplete(this.page, themesIndex, themes);
  }

  async setDatasetType(types: string[]): Promise<void> {
    const datasetTypeIndex = dropdowns.indexOf("datasetType");
    await fillAutoComplete(this.page, datasetTypeIndex, types);
  }

  async setFrequency(frequency: string): Promise<void> {
    const FrequencyIndex = dropdowns.indexOf("frequency");
    await fillAutoComplete(this.page, FrequencyIndex, frequency);
  }

  async setSpatialCoverages(spatial_coverages: string[]): Promise<void> {
    const spatialCoveragesIndex = dropdowns.indexOf("spatialCoverages");
    await fillAutoComplete(this.page, spatialCoveragesIndex, spatial_coverages);
  }

  async setConventions(conventions: string[]): Promise<void> {
    const conventionsIndex = dropdowns.indexOf("conventions");
    await fillAutoComplete(this.page, conventionsIndex, conventions);
  }

  async setAreasOfWork(areas_of_work: string[]): Promise<void> {
    const areasOfWorkIndex = dropdowns.indexOf("areasOfWork");
    await fillAutoComplete(this.page, areasOfWorkIndex, areas_of_work);
  }

  async setAreasOfCompetence(areas_of_competence: string[]): Promise<void> {
    const areasOfCompetenceIndex = dropdowns.indexOf("areasOfCompetence");
    await fillAutoComplete(this.page, areasOfCompetenceIndex, areas_of_competence);
  }

  async setModificationDate(modification_date: string): Promise<void> {
    await this.page.locator(`[name='modified_at']`).fill(modification_date);
  }

  async setReleaseDate(release_date: string): Promise<void> {
    await this.page.locator(`[name='releaseDate']`).fill(release_date);
  }

  async setGeneratedBy(generated_by: string[]): Promise<void> {
    const GeneratedByIndex = dropdowns.indexOf("wasGeneratedBy");
    await fillAutoComplete(this.page, GeneratedByIndex, generated_by);
  }

  async setApplicableLegislations(applicableLegislations: string[]): Promise<void> {
    const applicableLegislationsIndex = dropdowns.indexOf("applicableLegislations");
    await fillAutoComplete(this.page, applicableLegislationsIndex, applicableLegislations);
  }

  async setPeriodicity(period: string): Promise<void> {
    const periodicityIndex = dropdowns.indexOf("periodicity");
    await fillAutoComplete(this.page, periodicityIndex, period);
  }

  async setDataProtectionTypes(data_protection_types: string[]): Promise<void> {
    const dataProtectionTypesIndex = dropdowns.indexOf("dataProtectionTypes");
    await fillAutoComplete(this.page, dataProtectionTypesIndex, data_protection_types);
  }

  async setDataConformsTo(conforms_to: string[]): Promise<void> {
    const conformsToIndex = dropdowns.indexOf("conformsTo");
    await fillAutoComplete(this.page, conformsToIndex, conforms_to);
  }

  async setDatasetLanguages(languages: string[]): Promise<void> {
    const datasetLanguagesIndex = dropdowns.indexOf("datasetLanguages");
    await fillAutoComplete(this.page, datasetLanguagesIndex, languages);
  }

  async setLandingPages(landing_pages: string[]): Promise<void> {
    const landingPagesIndex = dropdowns.indexOf("landingPages");
    await fillAutoComplete(this.page, landingPagesIndex, landing_pages);
  }

  async setDatasetDocumentation(documentation: string[]): Promise<void> {
    const documentationIndex = dropdowns.indexOf("documentation");
    await fillAutoComplete(this.page, documentationIndex, documentation);
  }

  async setFinalDisposition(disposition: string): Promise<void> {
    const dispositionIndex = dropdowns.indexOf("finalDisposition");
    await fillAutoComplete(this.page, dispositionIndex, disposition);
  }

  async setSpatialResolutions(spatial_resolutions: number[]): Promise<void> {
    const spatialResolutionsIndex = dropdowns.indexOf("spatialResolutions");
    const spatialResolutionsAsStrings = spatial_resolutions.map(String);
    await fillAutoComplete(this.page, spatialResolutionsIndex, spatialResolutionsAsStrings);
  }

  async setTemporalResolution(temporal_resolution: string): Promise<void> {
    await this.page.locator(`[name='temporalResolution']`).fill(temporal_resolution);
  }

  async setOtherID(other_identifiers: string[]): Promise<void> {
    const OtherIDIndex = dropdowns.indexOf("otherIdentifiers");
    await fillAutoComplete(this.page, OtherIDIndex, other_identifiers);
  }

  async setTitle(title: string): Promise<void> {
    await this.page.locator(`[name='title']`).fill(title);
  }

  async setDescription(description: string): Promise<void> {
    await this.page.locator(`[name='description']`).fill(description);
  }

  async setmonitoringLocation(monitoring_location: string): Promise<void> {
    await this.page.locator(`[name='monitoringLocation']`).fill(monitoring_location);
  }

  async setRightsStatment(rights: string): Promise<void> {
    await this.page
      .locator(`input[value='${RightsLabelValueMapping[rights]}'][name='rightsStatement']`)
      .click();
  }

  async setTimePeriodStart(start: string): Promise<void> {
    await this.page.locator(`[name='timePeriodStart']`).fill(start);
  }

  async setTimePeriodEnd(end: string): Promise<void> {
    await this.page.locator(`[name='timePeriodEnd']`).fill(end);
  }

  async setNotes(notes: string): Promise<void> {
    await this.page.locator(`[name='notes']`).fill(notes);
  }

  async setVersion(version: string): Promise<void> {
    await this.page.locator(`[name='version']`).fill(version);
  }

  async setVersionNotes(version_notes: string[]): Promise<void> {
    await this.page
      .getByPlaceholder("Add description between versions")
      .first()
      .fill(version_notes[0]);
  }

  async setDuration(duration_of_administrative_utility: number): Promise<void> {
    await this.page
      .locator(`[name='duration_of_administrative_utility']`)
      .fill(duration_of_administrative_utility.toString());
  }

  async setProvenance(provenance: string[]): Promise<void> {
    await this.page.getByPlaceholder("Enter provenance information").first().fill(provenance[0]);
  }

  async saveAsDraft(): Promise<void> {
    await this.page.locator("form").getByRole("button", { name: "Preview & Save" }).click();
    await this.page.locator("#modal").getByRole("button", { name: "Save as Draft" }).click();
  }

  async goToHomePage(): Promise<void> {
    await this.page.goto(BASE_URL);
    await this.page.waitForURL(BASE_URL);
  }

  async update(): Promise<void> {
    await this.page.locator("form").getByRole("button", { name: "Preview & Save" }).click();
    await this.page.locator("#modal").getByRole("button", { name: "Save as Draft" }).click();
  }
}
