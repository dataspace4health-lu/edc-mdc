import React from "react";
import { DatasetAccuracyCheck } from "./DatasetAccuracyCheck";
import { DatasetPublicationCheck } from "./DatasetPublicationCheck";

interface DatasetApprovalWorkflowProps {
  setMetadataAccuracyReviewed: (value: boolean) => void;
  setPublicationDecisionMade: (value: boolean) => void;
}

const DatasetApprovalWorkflow: React.FC<DatasetApprovalWorkflowProps> = ({
  setMetadataAccuracyReviewed,
  setPublicationDecisionMade,
}) => {
  const handleMetadataAccuracyChange = (accurate: boolean) => {
    setMetadataAccuracyReviewed(accurate);
  };

  const handlePublicationDecisionChange = (shouldPublish: boolean) => {
    setPublicationDecisionMade(shouldPublish);
  };

  return (
    <div className='space-y-6'>
      <DatasetAccuracyCheck onAccuracyChange={handleMetadataAccuracyChange} />
      <DatasetPublicationCheck onPublicationDecisionChange={handlePublicationDecisionChange} />
    </div>
  );
};

export default DatasetApprovalWorkflow;
