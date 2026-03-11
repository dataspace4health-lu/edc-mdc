import React from "react";
import { ToggleButton } from "@lnds-lu/design-system";

interface DatasetPublicationCheckProps {
  onPublicationDecisionChange: (shouldPublish: boolean) => void;
}

export const DatasetPublicationCheck: React.FC<DatasetPublicationCheckProps> = ({
  onPublicationDecisionChange,
}) => {
  return (
    <ToggleButton
      info='Decide whether the metadata record for this dataset should be publicly visible online in the "catalogue des données du secteur public": By doing so, you will conform with article 8, paragraph 2 of the Data Governance Act [Regulation (EU) 2022/868] which states that "The single information point shall make available by electronic means a searchable asset list containing an overview of all available data resources including, where relevant, those data resources that are available at sectoral, regional or local information points, with relevant information describing the available data, including at least the data format and size and the conditions for their re-use." If you choose not to publish this metadata record, please choose "No" below and mark the record as "Internal only" in the next step.'
      yesLabel='Yes'
      noLabel='No'
      key='shouldPublish'
      name='shouldPublish'
      label='⚠️ Step 2: Should the metadata record be published?'
      onChange={(ev) => onPublicationDecisionChange(ev.target.checked)}
      defaultValue={false}
    />
  );
};
