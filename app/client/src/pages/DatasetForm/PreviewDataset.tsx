import { useState, useEffect } from "react";
import { DatasetFormInputs } from "./datasetDTO";
import { PreviewModal } from "../../components/Modals/PreviewModal";
import { DatasetDetails } from "../../components/Modals/DatasetDetails";
import { FormType, ResourceDatasetType } from "../../types";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { datasetIdsToSeriesMembership } from "../../utils/memberDatasetsutils";

export default function PreviewDataset({
  isSubmitting,
  datasetFormValues,
  formLoaderData,
  onSubmission,
  onModalOpen,
  datasetCreated = false,
  currentTab,
  setCurrentTab,
}: Readonly<{
  isSubmitting: boolean;
  datasetFormValues?: DatasetFormInputs | null;
  formLoaderData: FormType;
  onSubmission: (dataset: DatasetFormInputs) => Promise<void>;
  onModalOpen: () => void;
  datasetCreated?: boolean;
  currentTab: string;
  setCurrentTab: React.Dispatch<React.SetStateAction<string>>;
}>) {
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [refreshComments] = useState(false);

  const closePreviewModal = () => {
    setPreviewModalOpen(false);
  };

  const onSaveDraft = async () => {
    if (datasetFormValues) {
      setPreviewModalOpen(false);
      await onSubmission(datasetFormValues);
    }
  };

  const datasetForPreview = (dataset: DatasetFormInputs): ResourceDatasetType => {
    const allDatasetLanguages = formLoaderData.dataset.languages || [];

    // Convert contactIds to strings for comparison since form values can be strings, numbers, or single value
    const rawContactIds = dataset.contactIds;
    const contactIdArray = Array.isArray(rawContactIds)
      ? rawContactIds
      : rawContactIds
        ? [rawContactIds]
        : [];
    const contactIdStrings = contactIdArray.map((id) => String(id));
    const contacts =
      contactIdStrings.length > 0
        ? formLoaderData.contact.contacts.filter((contact) =>
            contactIdStrings.includes(contact.value),
          )
        : [];

    const contactNames = contacts.map((c) => c.eng_label.split(" (")[0]);
    const contactEmails = contacts.map((c) => c.eng_label.split(" (")[1]?.replace(")", "") || "");
    const contactIds = contacts.map((c) => parseInt(c.value));

    const groupManagerNames =
      (formLoaderData.dataset.group_managers || [])
        .filter((manager) => dataset.groupManagers?.includes(Number(manager.value)))
        .map((manager) => manager.eng_label) || [];
    return {
      id: -1,
      user_id: -1,
      author_name: "",
      comments_count: 0,
      title: dataset.title,
      status: "DRAFT",
      status_triggers: [],
      total_dictionaries: 0,
      total_relations: 0,
      has_versions: false,
      description: dataset.description,
      release_date: dataset.releaseDate ? DateUtils.toYMD(new Date(dataset.releaseDate)) : null,
      modified_at: dataset.modified_at ? DateUtils.toYMD(new Date(dataset.modified_at)) : null,
      released_at: dataset.released_at ? DateUtils.toYMD(new Date(dataset.released_at)) : null,
      deprecated_at: dataset.deprecated_at
        ? DateUtils.toYMD(new Date(dataset.deprecated_at))
        : null,
      contact_ids: contactIds,
      contact_names: contactNames,
      contact_emails: contactEmails,
      publisher_id: dataset.publisherId as unknown as number,
      publisher_name:
        (
          (formLoaderData.organisation.organisations as { value: string; eng_label: string }[]) ||
          []
        ).find((c) => c.value === dataset.publisherId)?.eng_label || "",
      creator_names: Array.isArray(dataset.creatorId)
        ? dataset.creatorId
            .map(
              (id) =>
                (
                  (formLoaderData.organisation.organisations as {
                    value: string;
                    eng_label: string;
                  }[]) || []
                ).find((c) => c.value === id)?.eng_label || "",
            )
            .filter(Boolean)
        : [],
      submitted_at: DateUtils.nowISO(),
      time_period_end:
        (dataset.timePeriodEnd && DateUtils.toYMD(new Date(dataset.timePeriodEnd))) || null,
      time_period_start:
        (dataset.timePeriodStart && DateUtils.toYMD(new Date(dataset.timePeriodStart))) || null,
      retention_period_start:
        (dataset.retentionPeriodStart && DateUtils.toYMD(new Date(dataset.retentionPeriodStart))) ||
        null,
      retention_period_end:
        (dataset.retentionPeriodEnd && DateUtils.toYMD(new Date(dataset.retentionPeriodEnd))) ||
        null,
      dataset_types: (formLoaderData.dataset.dataset_types || []).filter((it) =>
        dataset.datasetTypes.includes(it.value),
      ),
      rights_statement: dataset.rightsStatement,
      periodicity:
        (formLoaderData.dataset.periodicities || []).find(
          (it) => it.value === dataset.periodicity,
        ) ?? null,
      creator_ids: Array.isArray(dataset.creatorId)
        ? dataset.creatorId.map((id) => Number(id))
        : [],
      identifier: dataset.identifier ?? "",
      notes: dataset.notes ?? null,
      version: dataset.version ?? null,
      version_change_type: null,
      duration_of_administrative_utility: dataset.duration_of_administrative_utility ?? null,
      max_typical_age: dataset.maxTypicalAge ?? null,
      min_typical_age: dataset.minTypicalAge ?? null,
      number_of_records: dataset.numberOfRecords ?? null,
      number_of_unique_individuals: dataset.numberOfUniqueIndividuals ?? null,
      population_coverage: dataset.populationCoverage ?? null,
      code_values: dataset.codeValues
        ? typeof dataset.codeValues === "string"
          ? [dataset.codeValues]
          : dataset.codeValues
        : [],
      purpose: dataset.purpose
        ? typeof dataset.purpose === "string"
          ? [dataset.purpose]
          : dataset.purpose
        : [],
      coding_systems: dataset.codingSystems
        ? typeof dataset.codingSystems === "string"
          ? [dataset.codingSystems]
          : dataset.codingSystems
        : [],
      final_disposition: dataset.final_disposition ?? null,
      themes: (formLoaderData.dataset.themes || []).filter((it) =>
        dataset.themes.includes(it.value),
      ),
      qualified_attributions: [],
      keywords: (formLoaderData.dataset.keywords || []).filter((it) =>
        dataset.keywords?.includes(it.value),
      ),
      health_categories: (formLoaderData.dataset.health_categories || []).filter((it) =>
        dataset.healthCategories?.includes(it.value),
      ),
      health_themes: (formLoaderData.dataset.health_themes || []).filter((it) =>
        dataset.healthThemes?.includes(it.value),
      ),
      applicable_legislations: dataset.applicableLegislations
        ? typeof dataset.applicableLegislations === "string"
          ? [dataset.applicableLegislations]
          : dataset.applicableLegislations
        : [],
      conventions: dataset.conventions
        ? typeof dataset.conventions === "string"
          ? [dataset.conventions]
          : dataset.conventions
        : [],
      areas_of_work: dataset.areasOfWork
        ? typeof dataset.areasOfWork === "string"
          ? [dataset.areasOfWork]
          : dataset.areasOfWork
        : [],
      areas_of_competence: dataset.areasOfCompetence
        ? typeof dataset.areasOfCompetence === "string"
          ? [dataset.areasOfCompetence]
          : dataset.areasOfCompetence
        : [],
      spatial_coverages:
        (formLoaderData.dataset.spatial_coverages || []).filter((it) =>
          dataset.spatial_coverages?.includes(it.value),
        ) ?? [],
      group_manager_ids: Array.isArray(dataset.groupManagers)
        ? dataset.groupManagers.map(Number)
        : [],
      group_manager_names: groupManagerNames,
      data_protection_types: dataset.dataProtectionTypes
        ? typeof dataset.dataProtectionTypes === "string"
          ? [dataset.dataProtectionTypes]
          : dataset.dataProtectionTypes
        : [],
      monitoring_location: dataset.monitoringLocation ?? null,
      health_legal_basis: dataset.healthLegalBasis
        ? (typeof dataset.healthLegalBasis === "string"
            ? [dataset.healthLegalBasis]
            : dataset.healthLegalBasis
          ).filter((v) => v !== undefined && v !== null && v !== "" && v.trim() !== "")
        : [],
      provenance: dataset.provenance
        ? (typeof dataset.provenance === "string"
            ? [dataset.provenance]
            : dataset.provenance
          ).filter((v) => v !== undefined && v !== null && v !== "" && v.trim() !== "")
        : [],
      languages: allDatasetLanguages.filter((l) => dataset.languages?.includes(l.value)),
      landing_pages: dataset.landingPages
        ? typeof dataset.landingPages === "string"
          ? [dataset.landingPages]
          : dataset.landingPages
        : [],
      documentation: dataset.documentation
        ? typeof dataset.documentation === "string"
          ? [dataset.documentation]
          : dataset.documentation
        : [],
      conforms_to: dataset.conformsTo
        ? typeof dataset.conformsTo === "string"
          ? [dataset.conformsTo]
          : dataset.conformsTo
        : [],
      is_any_dictionary_authentic_source: false,
      is_dataset_series: dataset.isDatasetSeries ?? false,
      member_datasets: dataset.memberDatasets
        ? datasetIdsToSeriesMembership(dataset.memberDatasets.split(","))
        : [],
      other_identifiers: dataset.otherIdentifiers
        ? typeof dataset.otherIdentifiers === "string"
          ? [dataset.otherIdentifiers]
          : dataset.otherIdentifiers
        : [],
      was_generated_by: dataset.wasGeneratedBy
        ? typeof dataset.wasGeneratedBy === "string"
          ? [dataset.wasGeneratedBy]
          : dataset.wasGeneratedBy
        : [],
      version_notes: dataset.versionNotes
        ? (typeof dataset.versionNotes === "string"
            ? [dataset.versionNotes]
            : dataset.versionNotes
          ).filter((v) => v !== undefined && v !== null && v !== "" && v.trim() !== "")
        : [],
      spatial_resolutions: dataset.spatialResolutions
        ? Array.isArray(dataset.spatialResolutions)
          ? dataset.spatialResolutions
          : [dataset.spatialResolutions]
        : [],
      temporal_resolution: dataset.temporalResolution,
      personal_data: dataset.personalData
        ? typeof dataset.personalData === "string"
          ? [dataset.personalData]
          : dataset.personalData
        : [],
      distributions: [],
    };
  };

  useEffect(() => {
    if (datasetFormValues && isSubmitting) {
      setPreviewModalOpen(true);
      onModalOpen();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSubmitting]);

  return (
    <PreviewModal
      isOpen={previewModalOpen}
      onClose={closePreviewModal}
      onContinueEditing={closePreviewModal}
      onSaveDraft={onSaveDraft}
      title={datasetFormValues?.title || ""}
      showAchievement={datasetCreated}
    >
      {datasetFormValues && (
        <DatasetDetails
          dataset={datasetForPreview(datasetFormValues)}
          formFields={formLoaderData}
          refreshComments={refreshComments}
          currentTab={currentTab}
          setCurrentTab={setCurrentTab}
        />
      )}
    </PreviewModal>
  );
}
