import { Card, RadioButton } from "@lnds-lu/design-system";
import { useUIConfig } from "../context/UIConfigContext";
import { HEALTH_RELATED_DATA_EXPLANATION } from "../constants/health";

interface HealthDatasetSelectorProps {
  isHealthDataset: boolean;
  healthDataAccessLevel: string | null;
  onHealthDatasetChange: (isHealth: boolean) => void;
  onAccessLevelChange: (level: string) => void;
}

export default function HealthDatasetSelector({
  isHealthDataset,
  healthDataAccessLevel,
  onHealthDatasetChange,
  onAccessLevelChange,
}: HealthDatasetSelectorProps) {
  const { config } = useUIConfig();

  if (!config?.enable_health_dataset_selector) {
    return null;
  }

  return (
    <>
      {/* Question 1: Is this a health dataset? */}
      <Card className='p-6 bg-gray-50'>
        <RadioButton
          name='_isHealthDataset'
          label='Does this dataset contain health-related data?'
          options={[
            {
              value: "yes",
              label: "Yes",
            },
            {
              value: "no",
              label: "No",
            },
          ]}
          defaultValue={isHealthDataset ? "yes" : "no"}
          onClick={(value) => onHealthDatasetChange(value === "yes")}
          info='Select yes if this dataset is related to health.'
          popoverInfo={HEALTH_RELATED_DATA_EXPLANATION}
        />
      </Card>

      {/* Question 2: Access level (only shown for health datasets) */}
      {isHealthDataset && (
        <Card className='p-6 bg-blue-50'>
          <RadioButton
            name='_healthDataAccessLevel'
            label='Who can access this health data?'
            options={[
              {
                value: "NON_PUBLIC",
                label: "Non-public",
              },
              {
                value: "RESTRICTED",
                label: "Restricted",
              },
              {
                value: "PUBLIC",
                label: "Public",
              },
            ]}
            defaultValue={healthDataAccessLevel ?? undefined}
            onClick={(value) => onAccessLevelChange(value)}
            info='Choose the access level.'
            popoverInfo={
              <ul className='list-disc pl-5 space-y-2'>
                <li>
                  <strong>Non-public:</strong> Personal health data that is not openly accessible
                  and requires Health Data Access Body approval.
                </li>
                <li>
                  <strong>Restricted:</strong> Non-personal health data with access conditions such
                  as registration or license.
                </li>
                <li>
                  <strong>Public:</strong> Non-personal health data that is openly accessible
                  without restrictions.
                </li>
              </ul>
            }
          />
        </Card>
      )}
    </>
  );
}
