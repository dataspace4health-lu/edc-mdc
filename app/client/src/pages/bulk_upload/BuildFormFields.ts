import * as XLSX from "xlsx";
import { extractHeaders, extractRows, splitValues, cleanHeader } from "../excel_validator/Utils";
import { getOrganisationMap } from "../excel_validator/ValidationModals/validateContacts";
import {
  fetchFormFields,
  processAndAddMissingApplicableLegislation,
  processAndAddMissingKeywords,
} from "./Loader";
import { addToMapSet } from "./Utils";
import { ResourceUserType } from "../../types";

export const processMissingFormFields = async (
  workbook: XLSX.WorkBook,
  user: ResourceUserType,
  logCallback?: (message: string) => void,
): Promise<void> => {
  const assignPublisherIdToMissingFields = user.feature_options.enable_multi_tenants;

  try {
    const rawData = await fetchFormFields();

    const datasetSheet = workbook.Sheets["DatasetTemplate"];
    if (!datasetSheet) return;

    const headers = extractHeaders(datasetSheet).map(cleanHeader);
    const rows = extractRows(datasetSheet);
    const getCell = (row: string[], key: string) =>
      headers.includes(key) ? (row[headers.indexOf(key)]?.trim() ?? "") : "";

    const organisationMap = getOrganisationMap(rawData);
    const missingKeywordsMap: Record<string, Set<string>> = {};
    const missingApplicableLegislationsMap: Record<string, Set<string>> = {};

    const distributionSheet = workbook.Sheets["DistributionTemplate"];
    if (distributionSheet) {
      const distHeaders = extractHeaders(distributionSheet).map(cleanHeader);
      const distRows = extractRows(distributionSheet);
      const getDistCell = (row: string[], key: string) =>
        distHeaders.includes(key) ? (row[distHeaders.indexOf(key)]?.trim() ?? "") : "";

      for (const row of distRows) {
        const datasetTitle = getDistCell(row, "dataset title");
        const publisherName = rows.find((r) => getCell(r, "title") === datasetTitle)?.[
          headers.indexOf("publisher")
        ];
        const publisherId = organisationMap[publisherName || ""]?.id;
        if (!publisherId) continue;

        const rawApplicableLegislations = splitValues(getDistCell(row, "applicable legislations"));
        for (const l of rawApplicableLegislations) {
          // Check if legislation exists in rawData, if not add to missing map
          const searchTerm = l.trim();
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const found = rawData.dataset.applicable_legislations?.find((item: any) => {
            return (
              item.eng_label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              item.value?.toLowerCase() === searchTerm.toLowerCase() ||
              item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              item.link?.toLowerCase() === searchTerm.toLowerCase()
            );
          });
          if (!found) {
            addToMapSet(missingApplicableLegislationsMap, String(publisherId), searchTerm);
          }
        }
      }
    }

    for (const row of rows) {
      const publisherName = getCell(row, "publisher");
      const publisherId = organisationMap[publisherName]?.id;
      if (!publisherId) continue;

      const rawKeywords = splitValues(getCell(row, "keywords"));
      const keywordsArray = rawData.dataset.keywords as {
        eng_label: string;
        organisation_ids?: number[];
      }[];
      const missingKeywords = rawKeywords.filter((k) => {
        const keyword = keywordsArray.find((kw) => kw.eng_label === k);

        if (!keyword) return true;

        if (!keyword.organisation_ids || keyword.organisation_ids.length === 0) {
          return false;
        }

        return !keyword.organisation_ids.includes(publisherId);
      });

      if (missingKeywords.length > 0) {
        missingKeywords.forEach((k) => addToMapSet(missingKeywordsMap, String(publisherId), k));
      }

      const rawApplicableLegislations = splitValues(getCell(row, "applicable legislations"));
      for (const l of rawApplicableLegislations) {
        // Check if legislation exists in rawData, if not add to missing map
        const searchTerm = l.trim();
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const found = rawData.dataset.applicable_legislations?.find((item: any) => {
          return (
            item.eng_label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.value?.toLowerCase() === searchTerm.toLowerCase() ||
            item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.link?.toLowerCase() === searchTerm.toLowerCase()
          );
        });
        if (!found) {
          addToMapSet(missingApplicableLegislationsMap, String(publisherId), searchTerm);
        }
      }
    }

    for (const publisherId in missingKeywordsMap) {
      const keywords = Array.from(missingKeywordsMap[publisherId]);
      if (keywords.length > 0 && logCallback) {
        logCallback(`Found ${keywords.length} missing keyword(s) to add`);
      }
      try {
        await processAndAddMissingKeywords(
          assignPublisherIdToMissingFields ? publisherId : null,
          keywords,
          logCallback,
        );
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        const errorMsg = `Error while adding keywords for publisher "${publisherId}": ${err.message || err}`;
        console.error(errorMsg);
        if (logCallback) logCallback(`✗ ${errorMsg}`);
      }
    }

    for (const publisherId in missingApplicableLegislationsMap) {
      const legislations = Array.from(missingApplicableLegislationsMap[publisherId]);

      if (legislations.length > 0) {
        if (logCallback) {
          logCallback(`Found ${legislations.length} missing applicable legislations to add`);
        }
        try {
          await processAndAddMissingApplicableLegislation(
            assignPublisherIdToMissingFields ? publisherId : null,
            legislations,
            logCallback,
          );
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
          const errorMsg = `Error while adding legislation for publisher "${publisherId}": ${err.message || err}`;
          console.error(errorMsg);
          if (logCallback) logCallback(`✗ ${errorMsg}`);
        }
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (err: any) {
    console.error("Error while processing missing keywords and legislation:", err.message || err);
  }
};
