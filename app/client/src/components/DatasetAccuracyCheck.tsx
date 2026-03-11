import React from "react";
import { ToggleButton } from "@lnds-lu/design-system";

interface DatasetAccuracyCheckProps {
  onAccuracyChange: (accurate: boolean) => void;
}

export const DatasetAccuracyCheck: React.FC<DatasetAccuracyCheckProps> = ({ onAccuracyChange }) => {
  return (
    <ToggleButton
      info='Please review all metadata fields and confirm their accuracy and completeness.'
      yesLabel='Yes'
      noLabel='No'
      key='isAccurate'
      name='isAccurate'
      label='Step 1: Is the metadata record complete and accurate?'
      onChange={(ev) => onAccuracyChange(ev.target.checked)}
      defaultValue={false}
    />
  );
};
