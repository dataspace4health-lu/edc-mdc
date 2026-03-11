import { useState } from "react";
import { TrashIcon, ArchiveBoxIcon, XMarkIcon, ArrowPathIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import Tooltip from "./Tooltip";

interface ConfirmableActionButtonProps {
  onConfirm: () => void;
  onCancel?: () => void;
  size?: "small" | "regular";
  iconClassName?: string;
  action: "delete" | "deprecate" | "restore" | "remove-iam-roles";
}

const ConfirmableActionButton: React.FC<ConfirmableActionButtonProps> = ({
  onConfirm,
  onCancel,
  size = "small",
  iconClassName,
  action,
}) => {
  const [confirming, setConfirming] = useState(false);

  const config = {
    delete: {
      icon: TrashIcon,
      btnType: "danger" as const,
      buttonLabel: "Confirm",
      iconClassName:
        iconClassName ?? "h-6 w-6 text-lnds-red hover:text-lnds-dark-blue cursor-pointer",
      title: "Delete",
      tooltipText: "Delete",
    },
    deprecate: {
      icon: ArchiveBoxIcon,
      btnType: "danger" as const,
      buttonLabel: "Confirm",
      iconClassName: iconClassName ?? "h-6 w-6 icon-lnds-color cursor-pointer",
      title: "Deprecate",
      tooltipText: "Deprecate",
    },
    restore: {
      icon: ArrowPathIcon,
      btnType: "danger" as const,
      buttonLabel: "Confirm",
      iconClassName: iconClassName ?? "h-6 w-6 icon-lnds-color cursor-pointer",
      title: "Restore",
      tooltipText: "Restore",
    },
    "remove-iam-roles": {
      icon: TrashIcon,
      btnType: "danger" as const,
      buttonLabel: "Confirm",
      iconClassName:
        iconClassName ?? "h-6 w-6 text-lnds-red hover:text-lnds-dark-blue cursor-pointer",
      title: "Remove IAM Role",
      tooltipText: "Remove IAM Role",
    },
  };

  const { icon: IconComponent, btnType, buttonLabel, tooltipText } = config[action];

  return confirming ? (
    <div className='flex gap-1'>
      <Button
        label={buttonLabel}
        btnType={btnType}
        size={size}
        Icon={IconComponent}
        onClick={() => {
          onConfirm();
          setConfirming(false);
        }}
      />
      <Button
        label='Cancel'
        btnType='secondary'
        size={size}
        Icon={XMarkIcon}
        onClick={() => {
          setConfirming(false);
          onCancel?.();
        }}
      />
    </div>
  ) : (
    <Tooltip text={tooltipText}>
      <Button
        btnType='transparent'
        Icon={IconComponent}
        onClick={() => setConfirming(true)}
        className='p-2 w-10 h-10 rounded-md flex items-center justify-center'
      />
    </Tooltip>
  );
};

export default ConfirmableActionButton;
