import { ReactNode, useState } from "react";
import { ExclamationTriangleIcon, XMarkIcon } from "@heroicons/react/24/solid";

const DismissibleAlert = ({
  message,
  type,
  className,
  overrideClose,
}: {
  message: ReactNode;
  type: "info" | "warning" | "error";
  className?: string;
  overrideClose?: () => void;
}) => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  let bgColor = "bg-yellow-50 dark:bg-yellow-900/30";
  let textColor = "text-yellow-700 dark:text-yellow-200";
  let iconColor = "text-yellow-400 dark:text-yellow-500";

  if (type === "error") {
    bgColor = "bg-red-50 dark:bg-red-900/30";
    textColor = "text-red-700 dark:text-red-200";
    iconColor = "text-red-400 dark:text-red-500";
  } else if (type === "info") {
    bgColor = "bg-blue-50 dark:bg-blue-900/30";
    textColor = "text-blue-700 dark:text-blue-200";
    iconColor = "text-blue-400 dark:text-blue-500";
  }

  const onClose = overrideClose ? overrideClose : () => setIsVisible(false);

  return (
    <div className={`w-full mt-4 border border-lnds-color ${className}`}>
      <div className={`flex rounded p-4 justify-between items-baseline ${bgColor} ${textColor}`}>
        <div className='flex items-start'>
          <ExclamationTriangleIcon className={`h-5 w-5 mt-1 mr-2 flex-shrink-0 ${iconColor}`} />
          <div className={`${textColor} whitespace-pre-line`}>
            {typeof message === "string" ? message : message}
          </div>
        </div>
        <button
          onClick={onClose}
          className={`hover:text-lnds-dark-blue focus:outline-none ${textColor}`}
        >
          <XMarkIcon className='h-5 w-5' />
        </button>
      </div>
    </div>
  );
};

export default DismissibleAlert;
