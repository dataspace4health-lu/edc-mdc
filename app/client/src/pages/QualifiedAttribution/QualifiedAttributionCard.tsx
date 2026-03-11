import { ResourceQualifiedAttribution } from "../../types";
import { Button } from "@lnds-lu/design-system";
import { PencilIcon, BuildingOfficeIcon } from "@heroicons/react/24/solid";
import { QualifiedAttributionRoleOptions } from "./dto";

interface QualifiedAttributionCardProps {
  datasetId: number;
  attribution: ResourceQualifiedAttribution;
  current?: ResourceQualifiedAttribution | null;
  onEdit?: (attribution: ResourceQualifiedAttribution) => void;
  readOnly?: boolean;
}

export default function QualifiedAttributionCard(props: Readonly<QualifiedAttributionCardProps>) {
  const { attribution, current, onEdit, readOnly = false } = props;

  const roleLabel =
    QualifiedAttributionRoleOptions.find((opt) => opt.value === attribution.role)?.label ||
    attribution.role;

  const isSelected = current?.id === attribution.id;

  return (
    <div
      className={`border-b border-lnds-color w-full ${
        isSelected ? "bg-lnds-purple text-white" : ""
      }`}
    >
      <div className='p-4 flex justify-between items-start w-full'>
        <div className='flex flex-col w-full flex-1 min-w-0'>
          <span className={`font-medium mb-1 ${isSelected ? "text-white" : "heading-lnds-color"}`}>
            <BuildingOfficeIcon className='h-4 w-4 inline-block mr-1' />
            {attribution.organisation_name}
          </span>
          <span
            className={`text-justify text-sm break-words ${isSelected ? "text-white" : "text-lnds-color"}`}
          >
            {roleLabel}
          </span>
        </div>
        {!readOnly && onEdit && (
          <div className='flex gap-1'>
            <Button
              btnType='transparent'
              Icon={PencilIcon}
              className={`${isSelected ? "text-white" : ""}`}
              onClick={() => onEdit(attribution)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
