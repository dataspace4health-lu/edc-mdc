import { useState } from "react";
import { Button } from "@lnds-lu/design-system";
import { GlobeAltIcon, XMarkIcon } from "@heroicons/react/24/solid";
import { useAlert } from "@lnds-lu/design-system";
import client from "../../zodiosClient/client";
import { ResourceFormField, ApplicableLegislationFormField } from "../../types";
import { appAlerts } from "../../utils/appAlerts";

interface PromoteToGlobalProps {
  field: ResourceFormField | ApplicableLegislationFormField;
  fieldType: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formatting: Record<string, { singular: string; plural: string; Icon: any }>;
  onPromoteSuccess: (promotedField: ResourceFormField | ApplicableLegislationFormField) => void;
  className?: string;
  isCurrentField?: boolean;
}

const PromoteToGlobal: React.FC<PromoteToGlobalProps> = ({
  field,
  fieldType,
  formatting,
  onPromoteSuccess,
  className = "",
  isCurrentField = false,
}) => {
  const [showPromoteModal, setShowPromoteModal] = useState(false);
  const { setAlert } = useAlert();

  const handlePromoteToGlobal = () => {
    setShowPromoteModal(true);
  };

  const confirmPromoteToGlobal = async () => {
    if (!field) return;

    try {
      const promotedField =
        await client.promote_form_field_to_global_api_v1_form_fields__field_type___key__promote_global_put(
          undefined,
          {
            params: {
              field_type: fieldType,
              key: field.key,
            },
            withCredentials: true,
          },
        );

      setAlert(appAlerts.singularPromotedToGlobal(formatting[fieldType].singular));

      onPromoteSuccess(promotedField);
      setShowPromoteModal(false);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      setAlert(
        appAlerts.genericValidationError(
          error?.response?.data?.detail || appAlerts.failedToPromoteToGlobal().message,
        ),
      );
    } finally {
      setShowPromoteModal(false);
    }
  };

  const cancelPromotion = () => {
    setShowPromoteModal(false);
  };

  return (
    <>
      <Button
        btnType='transparent'
        Icon={GlobeAltIcon}
        className={`${isCurrentField ? "text-white" : ""} ${className}`}
        onClick={handlePromoteToGlobal}
      />

      {showPromoteModal && (
        <div className='fixed inset-0 bg-lnds-gray bg-opacity-50 flex items-center justify-center z-50'>
          <div className='bg-white dark:bg-gray-800 p-6 rounded-lg max-w-md w-full mx-4'>
            <h3 className='text-lg font-semibold mb-4 heading-lnds-color'>
              <GlobeAltIcon className='h-5 w-5 inline-block mr-2' />
              Promote to Global
            </h3>
            <p className='mb-4 text-lnds-color'>
              Are you sure you want to promote "<strong>{field.eng_label}</strong>" to global? This
              will remove all organization assignments and make it available to all organizations.
            </p>
            <div className='flex justify-center gap-3'>
              <Button
                btnType='secondary'
                label='Cancel'
                Icon={XMarkIcon}
                onClick={cancelPromotion}
              />
              <Button
                label='Promote to Global'
                Icon={GlobeAltIcon}
                onClick={confirmPromoteToGlobal}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PromoteToGlobal;
