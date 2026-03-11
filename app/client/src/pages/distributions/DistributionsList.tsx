import { useState } from "react";
import { useAlert } from "@lnds-lu/design-system";
import { ShareIcon } from "@heroicons/react/24/solid";
import { ResourceDistributionType, ResourceDatasetType } from "../../types";
import { DistributionSection } from "../../components/Modals/DistributionSection";
import { deleteDistributionById } from "./distributionsApi";
import { useLoaderData } from "react-router-dom";
import { FormType } from "../../types";
import EmptyScreen from "../../components/EmptyScreen";
import { appAlerts } from "../../utils/appAlerts";

type DistributionsListProps = {
  dataset: ResourceDatasetType;
  distributions: ResourceDistributionType[];
  isEditable: boolean;
  onDelete: (distributionId: number) => void;
  onEdit: (distribution: ResourceDistributionType) => void;
  triggerActivityLogRefresh: () => void;
};

const DistributionsList = ({
  dataset,
  distributions,
  isEditable,
  onDelete,
  onEdit,
  triggerActivityLogRefresh,
}: DistributionsListProps) => {
  const { setAlert } = useAlert();
  const [confirmingDelete, setConfirmingDelete] = useState<number | null>(null);
  const loaderData = useLoaderData() as { datasetId: number; formFields: FormType };
  const formFields = loaderData.formFields;

  const handleDelete = async (distributionId: number) => {
    try {
      await deleteDistributionById(dataset.id, distributionId);
      onDelete(distributionId);
      triggerActivityLogRefresh();
      setAlert(appAlerts.distributionDeleted());
    } catch (error) {
      console.error("Delete error:", error);
      setAlert(appAlerts.distributionDeleteFailed());
    } finally {
      setConfirmingDelete(null);
    }
  };

  if (distributions.length === 0) {
    return (
      <EmptyScreen message='No distributions found. Add one to get started!' Icon={ShareIcon} />
    );
  }

  return (
    <div className='flex flex-col gap-6'>
      {distributions.map((distribution) => (
        <DistributionSection
          key={distribution.id}
          distribution={distribution}
          formFields={formFields}
          isEditable={isEditable}
          onEdit={() => onEdit(distribution)}
          onDelete={() => handleDelete(distribution.id!)}
          confirmingDelete={confirmingDelete === distribution.id}
          onConfirmDelete={() => setConfirmingDelete(distribution.id!)}
          onCancelDelete={() => setConfirmingDelete(null)}
        />
      ))}
    </div>
  );
};

export default DistributionsList;
