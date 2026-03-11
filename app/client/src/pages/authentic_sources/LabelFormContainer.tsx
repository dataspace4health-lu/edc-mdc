import { useState } from "react";
import { Card, CardHeading, Button } from "@lnds-lu/design-system";
import { PlusCircleIcon, ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/solid";
import { ResourceAuthenticSourceLabel } from "../../types";
import AuthenticSourceLabelForm from "./AuthenticSourceLabelForm";

interface LabelFormContainerProps {
  onLabelCreate: (label: ResourceAuthenticSourceLabel) => void;
  onLabelUpdate: (label: ResourceAuthenticSourceLabel) => void;
  editingLabel?: ResourceAuthenticSourceLabel | null;
  onEditingChange: (label: ResourceAuthenticSourceLabel | null) => void;
}

const LabelFormContainer = ({
  onLabelCreate,
  onLabelUpdate,
  editingLabel,
  onEditingChange,
}: LabelFormContainerProps) => {
  const [isFormExpanded, setIsFormExpanded] = useState(false);

  const handleCreate = (label: ResourceAuthenticSourceLabel) => {
    onLabelCreate(label);
    setIsFormExpanded(false);
  };

  const handleUpdate = (label: ResourceAuthenticSourceLabel) => {
    onLabelUpdate(label);
    onEditingChange(null);
    setIsFormExpanded(false);
  };

  const handleCancel = () => {
    onEditingChange(null);
    setIsFormExpanded(false);
  };

  const handleNewLabel = () => {
    onEditingChange(null);
    setIsFormExpanded(true);
  };

  return (
    <Card className='p-8 mb-6'>
      <div
        className={`rounded-t flex flex-row justify-between items-center section-lnds-color ${
          isFormExpanded ? "mb-4" : ""
        }`}
      >
        <CardHeading
          label={`${editingLabel ? "Edit" : "Create"} Authentic Source Label`}
          Icon={PlusCircleIcon}
          className='flex'
        />
        {editingLabel && (
          <Button
            btnType='transparent'
            label='New Label'
            onClick={handleNewLabel}
            Icon={PlusCircleIcon}
          />
        )}
        {!editingLabel && (
          <Button
            btnType='transparent'
            label={isFormExpanded ? "Collapse Form" : "Expand Form"}
            onClick={() => setIsFormExpanded(!isFormExpanded)}
            Icon={isFormExpanded ? ChevronUpIcon : ChevronDownIcon}
          />
        )}
      </div>

      <div
        className={`transition-all duration-300 ${
          isFormExpanded || editingLabel
            ? "max-h-[1000px] opacity-100"
            : "max-h-0 opacity-0 overflow-hidden"
        }`}
      >
        <AuthenticSourceLabelForm
          label={editingLabel}
          onCreate={handleCreate}
          onUpdate={handleUpdate}
          onCancel={handleCancel}
        />
      </div>
    </Card>
  );
};

export default LabelFormContainer;
