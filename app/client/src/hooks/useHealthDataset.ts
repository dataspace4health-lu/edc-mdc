import { useState } from "react";
import { ResourceDatasetType } from "../types";

export const useHealthDataset = (datasetLoaderData?: ResourceDatasetType) => {
  const [isHealthDataset, setIsHealthDataset] = useState<boolean>(() => {
    // Initialize from existing dataset data
    if (datasetLoaderData) {
      return (
        (datasetLoaderData.health_categories && datasetLoaderData.health_categories.length > 0) ||
        (datasetLoaderData.health_themes && datasetLoaderData.health_themes.length > 0)
      );
    }
    return false;
  });
  const [healthDataAccessLevel, setHealthDataAccessLevel] = useState<string | null>(null);

  const handleAccessLevelChange = (level: string) => {
    setHealthDataAccessLevel(level);
  };

  const shouldShowHealthFields = (fieldName: string): boolean => {
    if (
      fieldName === "healthCategories" ||
      fieldName === "healthThemes" ||
      fieldName === "maxTypicalAge" ||
      fieldName === "minTypicalAge" ||
      fieldName === "numberOfRecords" ||
      fieldName === "numberOfUniqueIndividuals" ||
      fieldName === "populationCoverage" ||
      fieldName === "codeValues" ||
      fieldName === "purpose" ||
      fieldName === "codingSystems" ||
      fieldName === "healthLegalBasis" ||
      fieldName === "retentionPeriodStart" ||
      fieldName === "retentionPeriodEnd" ||
      fieldName === "personalData"
    ) {
      return isHealthDataset;
    }
    return true;
  };

  return {
    isHealthDataset,
    healthDataAccessLevel,
    setIsHealthDataset,
    setHealthDataAccessLevel,
    handleAccessLevelChange,
    shouldShowHealthFields,
  };
};
