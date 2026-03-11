import { BuildingOfficeIcon, PencilSquareIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import { Link } from "react-router-dom";
import { ResourceDatasetType, DatasetStatusEnum } from "../types";
import EmptyScreen from "./EmptyScreen";
import QualifiedAttributionCard from "../pages/QualifiedAttribution/QualifiedAttributionCard";

interface QualifiedAttributionsTabProps {
  dataset: ResourceDatasetType;
}

export const QualifiedAttributionsTab = ({ dataset }: QualifiedAttributionsTabProps) => {
  return (
    <div className='px-1 sm:px-2'>
      {DatasetStatusEnum.DRAFT === dataset.status && (
        <div className='flex justify-end mb-4'>
          <Button
            btnType='secondary'
            Link={Link}
            to={`/datasets/${dataset.id}/qualified-attributions`}
            Icon={PencilSquareIcon}
            label='Manage Qualified Attributions'
          />
        </div>
      )}

      {!dataset.qualified_attributions || dataset.qualified_attributions.length === 0 ? (
        <EmptyScreen message='No qualified attributions available' Icon={BuildingOfficeIcon} />
      ) : (
        <div className='dark:bg-gray-800 p-4 rounded-lg'>
          <h3 className='label-lnds-color text-xl font-semibold mb-4 pb-2 border-b-2 border-lnds-color'>
            Qualified Attributions
          </h3>
          <div className='space-y-2'>
            {dataset.qualified_attributions.map((attribution) => (
              <QualifiedAttributionCard
                key={attribution.id}
                datasetId={dataset.id}
                attribution={attribution}
                readOnly={true}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
