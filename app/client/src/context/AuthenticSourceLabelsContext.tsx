import { createContext, useContext, useState, ReactNode } from "react";
import {
  ResourceAuthenticSourceLabel,
  DatasetStatusEnum,
  ResourceUserType,
  ResourceDatasetType,
} from "../types";
import client from "../zodiosClient/client";

type UpdatableDataDictionaryEntry = {
  entryId: number;
  isAuthenticSource: boolean;
};

interface AuthenticSourceLabelsContextType {
  labels: ResourceAuthenticSourceLabel[];
  activeLabels: ResourceAuthenticSourceLabel[];
  fetchLabels: () => Promise<void>;
  createLabel: (newLabel: ResourceAuthenticSourceLabel) => void;
  removeLabel: (labelId: number) => void;
  updateLabel: (updatedLabel: ResourceAuthenticSourceLabel) => void;
  assignAuthenticSouceLabel: (entryId: number, labelId: number, datasetId: number) => Promise<void>;
  showSaveEntriesBtn: boolean;
  showSaveLabelAssignmentsBtn: boolean;
  saveLabels: (datasetId: number) => Promise<void>;
  saveEntries: (datasetId: number) => Promise<void>;
  completeReview: (datasetId: number) => Promise<void>;
  toggleAuthenticSourceEntry: (entryId: number, flag: boolean) => void;
  canAssignLabels: (datasetStatus: string, user: ResourceUserType | null) => boolean;
  canMarkAsAuthenticSource: (
    dataset: ResourceDatasetType,
    user: ResourceUserType | null,
  ) => boolean;
  canReviewNoAuthenticSource: (
    dataset: ResourceDatasetType,
    user: ResourceUserType | null,
  ) => boolean;
  reset: () => void;
}

const AuthenticSourceLabelsContext = createContext<AuthenticSourceLabelsContextType | null>(null);

interface AuthenticSourceLabelsProviderProps {
  children: ReactNode;
}

export const AuthenticSourceLabelsProvider = ({ children }: AuthenticSourceLabelsProviderProps) => {
  const [initialLabels, setInitialLabels] = useState<ResourceAuthenticSourceLabel[]>([]);
  const [labels, setLabels] = useState<ResourceAuthenticSourceLabel[]>([]);
  const [activeLabels, setActiveLabels] = useState<ResourceAuthenticSourceLabel[]>([]); // ✅ new
  const [updatableEntries, setUpdatableEntries] = useState<UpdatableDataDictionaryEntry[]>([]);
  const [reviewedAlready, setReviewedAlready] = useState<boolean>(false);

  const fetchLabels = async () => {
    const response = await client.get_authentic_source_labels_api_v1_authentic_source_labels_get({
      queries: { include_deprecated: true },
      withCredentials: true,
    });
    const allLabels = response as ResourceAuthenticSourceLabel[];

    setLabels(allLabels);
    setActiveLabels(allLabels.filter((label) => !label.is_deprecated));
    setInitialLabels(allLabels);
  };

  const createLabel = (newLabel: ResourceAuthenticSourceLabel) => {
    setLabels((prevLabels) => {
      const updated = [...prevLabels, newLabel];
      setActiveLabels(updated.filter((label) => !label.is_deprecated));
      return updated;
    });
  };

  const removeLabel = (labelId: number) => {
    setLabels((prevLabels) => {
      const updated = prevLabels.filter((label) => label.id !== labelId);
      setActiveLabels(updated.filter((label) => !label.is_deprecated));
      return updated;
    });
  };

  const updateLabel = (updatedLabel: ResourceAuthenticSourceLabel) => {
    setLabels((prevLabels) => {
      const updated = prevLabels.map((label) =>
        label.id === updatedLabel.id ? { ...label, ...updatedLabel } : label,
      );
      setActiveLabels(updated.filter((label) => !label.is_deprecated));
      return updated;
    });
  };

  const canAssignLabels = (datasetStatus: string, user: ResourceUserType | null): boolean => {
    return (
      datasetStatus === DatasetStatusEnum.PUBLISHED &&
      !!user?.feature_options.enable_authentic_source &&
      !!user?.permissions?.includes("authentic-source:assign")
    );
  };

  const canMarkAsAuthenticSource = (
    dataset: ResourceDatasetType,
    user: ResourceUserType | null,
  ): boolean => {
    return (
      dataset.status === DatasetStatusEnum.PUBLISHED &&
      !dataset.authentic_source_reviewed_at &&
      !!user?.feature_options.enable_authentic_source &&
      dataset.user_id === user.id
    );
  };

  const canReviewNoAuthenticSource = (
    dataset: ResourceDatasetType,
    user: ResourceUserType | null,
  ): boolean => {
    return (
      !reviewedAlready &&
      dataset.status === DatasetStatusEnum.PUBLISHED &&
      !dataset.authentic_source_reviewed_at &&
      !!user?.feature_options.enable_authentic_source &&
      !!user?.permissions?.includes("authentic-source:assign")
    );
  };

  const assignAuthenticSouceLabel = async (entryId: number, labelId: number, datasetId: number) => {
    const existingLabel = labels.find((l) => l.data_dictionary_entry_id === entryId);
    if (existingLabel) {
      setLabels((prevLabels) => {
        const updated = prevLabels.map((l) =>
          l.data_dictionary_entry_id === entryId
            ? { ...l, data_dictionary_entry_id: null, dataset_id: null, dataset_title: null }
            : l,
        );
        setActiveLabels(updated.filter((label) => !label.is_deprecated));
        return updated;
      });
    }

    setLabels((prevLabels) => {
      const updated = prevLabels.map((l) =>
        l.id === labelId ? { ...l, data_dictionary_entry_id: entryId, dataset_id: datasetId } : l,
      );
      setActiveLabels(updated.filter((label) => !label.is_deprecated));
      return updated;
    });
  };

  const toggleAuthenticSourceEntry = (entryId: number, flag: boolean) => {
    const updatableEntry = updatableEntries.find((e) => e.entryId === entryId);
    if (flag) {
      if (updatableEntry) {
        setUpdatableEntries((prevEntries) =>
          prevEntries.map((entry) =>
            entry.entryId === entryId ? { ...entry, isAuthenticSource: true } : entry,
          ),
        );
      } else {
        setUpdatableEntries((prevEntries) => [
          ...prevEntries,
          { entryId, isAuthenticSource: true },
        ]);
      }
    } else {
      if (updatableEntry) {
        setUpdatableEntries((prevEntries) =>
          prevEntries.map((entry) =>
            entry.entryId === entryId ? { ...entry, isAuthenticSource: false } : entry,
          ),
        );
      } else {
        setUpdatableEntries((prevEntries) => [
          ...prevEntries,
          { entryId, isAuthenticSource: false },
        ]);
      }

      setLabels((prevLabels) => {
        const updated = prevLabels.map((l) =>
          l.data_dictionary_entry_id === entryId
            ? { ...l, data_dictionary_entry_id: null, dataset_id: null }
            : l,
        );
        setActiveLabels(updated.filter((label) => !label.is_deprecated));
        return updated;
      });
    }
  };

  const completeReview = async (datasetId: number) => {
    await client.complete_authentic_source_review_api_v1_datasets__dataset_id__authentic_source_complete_review_post(
      undefined,
      { params: { dataset_id: datasetId }, withCredentials: true },
    );
    setReviewedAlready(true);
  };

  const saveLabels = async (datasetId: number) => {
    const response =
      await client.assign_authentic_source_label_api_v1_authentic_source_assignments_post(
        {
          label_assignments: labels.map((label) => ({
            label_id: label.id,
            assigned_entry_id: label.data_dictionary_entry_id ?? null,
          })),
        },
        {
          withCredentials: true,
        },
      );

    await completeReview(datasetId);
    setLabels(response);
    setActiveLabels(response.filter((label) => !label.is_deprecated));
    setInitialLabels(response);
  };

  const showSaveEntriesBtn = updatableEntries.length > 0;

  const hasLabelsChanged =
    initialLabels.length !== labels.length ||
    initialLabels.some((label, index) => {
      const currentLabel = labels[index];
      return (
        label.id !== currentLabel.id ||
        label.data_dictionary_entry_id !== currentLabel.data_dictionary_entry_id ||
        label.dataset_id !== currentLabel.dataset_id
      );
    });

  const showSaveLabelAssignmentsBtn = hasLabelsChanged;

  const saveEntries = async (datasetId: number) => {
    if (updatableEntries.length === 0) {
      return;
    }

    await client.bulk_update_authentic_source_api_v1_datasets__dataset_id__data_dictionaries_bulk_update_authentic_source_post(
      {
        entries: updatableEntries.map((entry) => ({
          entry_id: entry.entryId,
          is_authentic_source: entry.isAuthenticSource,
        })),
      },
      { params: { dataset_id: datasetId }, withCredentials: true },
    );
    setUpdatableEntries([]);
  };

  const reset = () => {
    setLabels(initialLabels);
    setActiveLabels(initialLabels.filter((label) => !label.is_deprecated));
    setUpdatableEntries([]);
  };

  return (
    <AuthenticSourceLabelsContext.Provider
      value={{
        labels,
        activeLabels,
        fetchLabels,
        createLabel,
        removeLabel,
        updateLabel,
        assignAuthenticSouceLabel,
        saveLabels,
        showSaveEntriesBtn,
        showSaveLabelAssignmentsBtn,
        saveEntries,
        completeReview,
        toggleAuthenticSourceEntry,
        canAssignLabels,
        canMarkAsAuthenticSource,
        canReviewNoAuthenticSource,
        reset,
      }}
    >
      {children}
    </AuthenticSourceLabelsContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuthenticSourceLabels = () => {
  const context = useContext(AuthenticSourceLabelsContext);
  if (!context) {
    throw new Error(
      "useAuthenticSourceLabels must be used within an AuthenticSourceLabelsProvider",
    );
  }
  return context;
};
