import * as XLSX from "xlsx";
import { extractHeaders, extractRows, splitValues, cleanHeader } from "../excel_validator/Utils";
import { getOrganisationMap } from "../excel_validator/ValidationModals/validateContacts";
import { DatasetFormInputs } from "../DatasetForm/datasetDTO";
import { fetchFormFields } from "./Loader";
import { parseDate, notNull } from "./Utils";
import { getDatasetFormInputsSchema } from "../DatasetForm/datasetDTO";
import { DistributionFormInputs, getDistributionFormInputSchema } from "../distributions/dto";
import { rightStatementsValues } from "./Utils";
import { availabilityOptions } from "../../schemas/distributionSchema";
import { dataProtectionTypeOptions } from "../../utils/dataProtectionLabels";
import { splitPrinciplesAndLegislation } from "./Utils";
import { getApplicableLegislationValueFromLabel } from "./Utils";
import { personalDataOptions } from "../../utils/personalDataLabels";

export type DatasetWithDistributions = DatasetFormInputs & {
  distributions?: DistributionFormInputs[];
};

export const extractDatasetsFromWorkbook = async (
  workbook: XLSX.WorkBook,
): Promise<DatasetWithDistributions[]> => {
  const datasetSheet = workbook.Sheets["DatasetTemplate"];
  const distributionSheet = workbook.Sheets["DistributionTemplate"];
  if (!datasetSheet) return [];

  const datasetHeaders = extractHeaders(datasetSheet).map(cleanHeader);
  const distributionHeaders = distributionSheet
    ? extractHeaders(distributionSheet).map(cleanHeader)
    : [];

  const rowAtIndexDataset = (row: string[], key: string): string =>
    datasetHeaders.includes(key) && row[datasetHeaders.indexOf(key)]
      ? row[datasetHeaders.indexOf(key)].trim()
      : "";

  const rowAtIndexDistribution = (row: string[], key: string): string =>
    distributionHeaders.includes(key) && row[distributionHeaders.indexOf(key)]
      ? row[distributionHeaders.indexOf(key)].trim()
      : "";

  const rawData = await fetchFormFields();
  const organisationMap = getOrganisationMap(rawData);

  const getValueFromLabel = (field: string, label: string): string | null => {
    const found = rawData.dataset[field]?.find((item) => item.eng_label === label);
    return found ? found.value : null;
  };

  const getValueFromLabelDistribution = (field: string, label: string): string | null => {
    const found = rawData.distribution[field]?.find((item) => item.eng_label === label);
    return found ? found.value : null;
  };

  const distributionRows = distributionSheet ? extractRows(distributionSheet) : [];
  const distributionsMap: Record<string, DistributionFormInputs[]> = {};

  for (const row of distributionRows) {
    const datasetTitle = rowAtIndexDistribution(row, "dataset title");
    const distributionTitle = rowAtIndexDistribution(row, "distribution title");

    const rightsLabel = rowAtIndexDistribution(row, "rights");
    const rightsValue = rightStatementsValues[rightsLabel];

    const applicableLegislationDistributions = splitValues(
      rowAtIndexDistribution(row, "applicable legislations"),
    );
    const { legislations: legislationDistributions } = splitPrinciplesAndLegislation(
      applicableLegislationDistributions,
    );

    const availabilityLabel = rowAtIndexDistribution(row, "availability");
    const availabilityValue =
      availabilityOptions.find(
        (opt) => opt.label.toLowerCase().trim() === availabilityLabel.toLowerCase().trim(),
      )?.value || "";

    const spatialRestrictions = splitValues(rowAtIndexDistribution(row, "spatial restrictions"))
      .map((label) => getValueFromLabelDistribution("spatial_restrictions", label))
      .filter(notNull);

    const formatLabel = rowAtIndexDistribution(row, "format");
    const fileFormatValue = getValueFromLabelDistribution("file_types", formatLabel);

    const rawDistributionLanguages = splitValues(rowAtIndexDistribution(row, "language"));
    const distributionLanguageValues = rawDistributionLanguages
      .map((l) => getValueFromLabelDistribution("languages", l))
      .filter(notNull);

    const distribution: DistributionFormInputs = {
      title: distributionTitle,
      description: rowAtIndexDistribution(row, "description"),
      accessURLs: splitValues(rowAtIndexDistribution(row, "access url")),
      fileFormat: fileFormatValue || "",
      license: rowAtIndexDistribution(row, "license") || "no_license",
      languages: distributionLanguageValues,
      distributionRightsStatement: rightsValue,
      mediaType:
        rowAtIndexDistribution(row, "media type/compression format/packaging format") || "",
      compressionFormat:
        rowAtIndexDistribution(row, "media type/compression format/packaging format") || "",
      packagingFormat:
        rowAtIndexDistribution(row, "media type/compression format/packaging format") || "",
      applicableLegislations:
        legislationDistributions.length > 0
          ? legislationDistributions
              .map((label) => getApplicableLegislationValueFromLabel(label, rawData) || label)
              .filter((value, index, self) => self.indexOf(value) === index)
          : [],
      availability: availabilityValue,
      spatialRestrictions: spatialRestrictions,
    };

    const parsedDistribution = getDistributionFormInputSchema({ requireByteSize: false }).safeParse(
      distribution,
    );

    if (!parsedDistribution.success) {
      const errorMessages = parsedDistribution.error.issues
        .map((e) => `${e.path.join(".")} : ${e.message}`)
        .join("; ");
      throw new Error(
        `Invalid distribution for dataset "${datasetTitle}" - "${distributionTitle}": ${errorMessages}`,
      );
    }

    if (!distributionsMap[datasetTitle]) {
      distributionsMap[datasetTitle] = [];
    }

    distributionsMap[datasetTitle].push(parsedDistribution.data);
  }

  const rows = extractRows(datasetSheet);
  const datasets: DatasetWithDistributions[] = [];

  for (const row of rows) {
    const title = rowAtIndexDataset(row, "title");
    const publisherName = rowAtIndexDataset(row, "publisher");
    const contactName = rowAtIndexDataset(row, "contact point name");
    const contactEmail = rowAtIndexDataset(row, "contact point email");

    const org = organisationMap[publisherName];
    if (!org?.id) throw new Error(`Invalid publisher for "${title}"`);
    const publisherId = org.id.toString();

    const contactLabel = `${contactName} (${contactEmail})`;
    const contact = rawData.contact.contacts.find(
      (c) => c.eng_label.trim().toLowerCase() === contactLabel.trim().toLowerCase(),
    );

    const contactId = contact ? Number(contact.value) : undefined;

    const timePeriodStart = parseDate(rowAtIndexDataset(row, "start date"));
    const timePeriodEnd = parseDate(rowAtIndexDataset(row, "end date"));
    const rawThemes = splitValues(rowAtIndexDataset(row, "themes"));

    const themeValues = rawThemes
      .map((t) => {
        const item = rawData.dataset.themes?.find((theme) =>
          theme.value.toLowerCase().includes(`/${t.toLowerCase()}`),
        );
        return item?.value ?? null;
      })
      .filter(notNull);

    const rawDatasetTypes = splitValues(rowAtIndexDataset(row, "dataset types"));
    const datasetTypeValues = rawDatasetTypes
      .map((t) => getValueFromLabel("dataset_types", t))
      .filter(notNull);

    const rawKeywords = splitValues(rowAtIndexDataset(row, "keywords"));
    const keywordValues = rawKeywords.map((k) => getValueFromLabel("keywords", k)).filter(notNull);

    const periodicityLabel = rowAtIndexDataset(row, "frequency");
    const periodicity = getValueFromLabel("periodicities", periodicityLabel);

    const rightsLabel = rowAtIndexDataset(row, "access rights").toLowerCase();
    const rightsValue = rightStatementsValues[rightsLabel];

    const applicableLegislation = splitValues(rowAtIndexDataset(row, "applicable legislations"));
    const { legislations } = splitPrinciplesAndLegislation(applicableLegislation);

    const rawLanguages = splitValues(rowAtIndexDataset(row, "language"));
    const languageValues = rawLanguages
      .map((l) => getValueFromLabel("languages", l))
      .filter(notNull);

    const rawDataProtectionTypes = splitValues(rowAtIndexDataset(row, "data protection types"));
    const dataProtectionValues = rawDataProtectionTypes
      .map((label) => {
        const found = dataProtectionTypeOptions.find(
          (opt) => opt.label.toLowerCase().trim() === label.toLowerCase().trim(),
        );
        return found ? found.value : null;
      })
      .filter(notNull);

    const rawSpatialCoverages = splitValues(rowAtIndexDataset(row, "geographical coverage"));
    const spatialCoverageValues = rawSpatialCoverages
      .map((sc) => getValueFromLabel("spatial_coverages", sc))
      .filter(notNull);

    const rawHealthCategories = splitValues(rowAtIndexDataset(row, "health categories"));
    const healthCategoryValues = rawHealthCategories
      .map((hc) => getValueFromLabel("health_categories", hc))
      .filter(notNull);

    const rawHealthThemes = splitValues(rowAtIndexDataset(row, "health themes"));
    const healthThemeValues = rawHealthThemes
      .map((ht) => getValueFromLabel("health_themes", ht))
      .filter(notNull);

    const creatorName = rowAtIndexDataset(row, "creator");
    const creatorOrg = organisationMap[creatorName];
    const creatorId = creatorOrg?.id ? [creatorOrg.id.toString()] : [];

    const rawLandingPages = splitValues(rowAtIndexDataset(row, "landing page"));
    const landingPages = rawLandingPages.filter(notNull);
    const rawDocumentation = splitValues(rowAtIndexDataset(row, "documentation"));
    const documentation = rawDocumentation.filter(notNull);
    const rawPurpose = splitValues(rowAtIndexDataset(row, "purpose"));
    const purpose = rawPurpose.filter(notNull);

    const uniqueValues = new Set<string>();

    const applicableLegislations =
      legislations.length > 0
        ? legislations
            .map((label) => getApplicableLegislationValueFromLabel(label, rawData) || label)
            .filter((value) => {
              if (uniqueValues.has(value)) return false;
              uniqueValues.add(value);
              return true;
            })
        : [];

    const personalDataRaw = splitValues(rowAtIndexDataset(row, "personal data"));
    const personalDataValues = personalDataRaw
      .map((label) => {
        const found = personalDataOptions.find(
          (opt) => opt.label.toLowerCase().trim() === label.toLowerCase().trim(),
        );
        return found ? found.value : null;
      })
      .filter(notNull);

    const dataset: DatasetWithDistributions = {
      title,
      description: rowAtIndexDataset(row, "description"),
      contactIds: contactId ? [contactId] : undefined,
      publisherId,
      themes: themeValues as [string, ...string[]],
      datasetTypes: datasetTypeValues as [string, ...string[]],
      keywords: keywordValues.length > 0 ? keywordValues : undefined,
      healthCategories:
        healthCategoryValues.length > 0
          ? (healthCategoryValues as [string, ...string[]])
          : undefined,
      healthThemes:
        healthThemeValues.length > 0 ? (healthThemeValues as [string, ...string[]]) : undefined,
      periodicity: periodicity ?? undefined,
      rightsStatement: rightsValue,
      timePeriodStart: timePeriodStart ?? undefined,
      timePeriodEnd: timePeriodEnd,
      retentionPeriodStart: undefined,
      retentionPeriodEnd: undefined,

      distributions: distributionsMap[title] || [],

      applicableLegislations: applicableLegislations,
      languages: languageValues as [string, ...string[]],
      dataProtectionTypes: dataProtectionValues as [string, ...string[]],
      spatial_coverages: spatialCoverageValues as [string, ...string[]],
      creatorId,
      spatialResolutions: [],
      provenance: [],
      healthLegalBasis: [],
      versionNotes: [],
      personalData: personalDataValues,
      ...(landingPages.length > 0 && { landingPages }),
      ...(documentation.length > 0 && { documentation }),
      ...(purpose.length > 0 && { purpose }),
    };

    const parsed = getDatasetFormInputsSchema({
      enableHealthDcat: false,
    }).safeParse(dataset);

    if (!parsed.success) {
      const errorMessages = parsed.error.issues
        .map((e) => `${e.path.join(".")} : ${e.message}`)
        .join("; ");
      throw new Error(`Validation failed for dataset "${title}": ${errorMessages}`);
    }

    datasets.push({
      ...parsed.data,
      distributions: distributionsMap[title] || [],
    });
  }

  return datasets;
};
