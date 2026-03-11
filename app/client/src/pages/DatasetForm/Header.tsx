import { PlusCircleIcon, PencilSquareIcon, XCircleIcon } from "@heroicons/react/24/solid";
import DatasetFormCacheManager from "../../utils/DatasetFormCacheManager";
import { Button, CardHeading } from "@lnds-lu/design-system";

interface HeaderProps {
  isEditForm: boolean;
}

export default function Header(props: Readonly<HeaderProps>) {
  const { isEditForm } = props;
  return (
    <div className='rounded-t flex flex-row justify-between items-center section-lnds-color mb-8'>
      <div>
        {isEditForm && (
          <CardHeading
            label={"Edit Dataset Metadata"}
            Icon={PencilSquareIcon}
            className='flex w-full mb-4'
          />
        )}
        {!isEditForm && (
          <CardHeading
            label={"Add Dataset Metadata"}
            Icon={PlusCircleIcon}
            className='flex w-full mb-4'
          />
        )}
      </div>
      {!isEditForm && (
        <Button
          onClick={() => {
            DatasetFormCacheManager.clear();
            window.location.reload();
          }}
          Icon={XCircleIcon}
          label='Reset Form'
          btnType='danger'
        />
      )}
    </div>
  );
}
