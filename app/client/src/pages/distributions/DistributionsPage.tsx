import { useState, useEffect } from "react";
import { useLoaderData, useOutletContext } from "react-router-dom";
import { fetchDistributions } from "./distributionsApi";
import { ResourceDistributionType, ResourceDatasetType, FormType } from "../../types";
import InsertDistribution from "./InsertDistribution";
import DistributionsList from "./DistributionsList";
import { useAuth } from "../../context/AuthContext";
import { usePageTitle } from "../../hooks/usePageTitle";

const DistributionsPage = () => {
  const loaderData = useLoaderData() as { datasetId: number; formFields: FormType };
  const { datasetId, formFields } = loaderData;
  const { user } = useAuth();

  const { dataset: contextDataset, triggerActivityLogRefresh } = useOutletContext() as {
    dataset: ResourceDatasetType;
    triggerActivityLogRefresh: () => void;
  };

  const [distributions, setDistributions] = useState<ResourceDistributionType[]>([]);
  const [editingDistribution, setEditingDistribution] = useState<ResourceDistributionType | null>(
    null,
  );

  usePageTitle(contextDataset ? `${contextDataset.title} - Distributions` : "Distributions");

  useEffect(() => {
    const loadData = async () => {
      const data = await fetchDistributions(datasetId);
      setDistributions(data);
    };
    loadData();
  }, [datasetId]);

  const handleDistributionAdded = (newDistribution: ResourceDistributionType) => {
    setDistributions((prevDistributions) => [newDistribution, ...prevDistributions]);
  };

  const handleDistributionDeleted = (distributionId: number) => {
    setDistributions((prevData) => prevData.filter((dist) => dist.id !== distributionId));
    triggerActivityLogRefresh();
  };

  const handleDistributionUpdated = (updatedDistribution: ResourceDistributionType) => {
    setDistributions((prevData) =>
      prevData.map((dist) => (dist.id === updatedDistribution.id ? updatedDistribution : dist)),
    );
    triggerActivityLogRefresh();
  };

  const handleEditClick = (distribution: ResourceDistributionType) => {
    setEditingDistribution(distribution);
  };

  const handleCancelEdit = () => {
    setEditingDistribution(null);
  };

  const isHealthDataset =
    contextDataset?.health_categories && contextDataset.health_categories.length > 0;

  return (
    <div className='flex flex-col w-full space-y-8'>
      <InsertDistribution
        datasetId={datasetId}
        onDistributionAdded={handleDistributionAdded}
        onDistributionUpdated={handleDistributionUpdated}
        triggerActivityLogRefresh={triggerActivityLogRefresh}
        editingDistribution={editingDistribution}
        onCancelEdit={handleCancelEdit}
        formLoaderData={formFields}
        user={user}
        isHealthDataset={isHealthDataset}
        datasetRightsStatement={contextDataset?.rights_statement}
      />
      {contextDataset && (
        <DistributionsList
          dataset={contextDataset}
          distributions={distributions}
          isEditable={true}
          onDelete={handleDistributionDeleted}
          onEdit={handleEditClick}
          triggerActivityLogRefresh={triggerActivityLogRefresh}
        />
      )}
    </div>
  );
};

export default DistributionsPage;
