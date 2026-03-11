import { ResourceDatasetType, ResourceDataDictionaryEntry, DatasetStatusEnum } from "../../types";
import { useAuth } from "../../context/AuthContext";

interface AuthenticSourceStatusMessageProps {
  dataset: ResourceDatasetType;
  entries: ResourceDataDictionaryEntry[];
}

const AuthenticSourceStatusMessage = ({ dataset, entries }: AuthenticSourceStatusMessageProps) => {
  const { user } = useAuth();

  // Only show for published datasets when authentic source feature is enabled
  if (
    dataset.status !== DatasetStatusEnum.PUBLISHED ||
    !user?.feature_options.enable_authentic_source
  ) {
    return null;
  }

  const hasAuthenticEntries = entries.some((entry) => entry.is_authentic_source);
  const isReviewed = dataset.authentic_source_reviewed_at !== null;

  const getStatusConfig = () => {
    if (isReviewed && !hasAuthenticEntries) {
      return {
        message:
          "This dataset has been reviewed for authentic source and has no authentic entries.",
        borderColor: "border-lnds-color",
        dotColor: "bg-lnds-gray",
      };
    }

    if (!isReviewed && !hasAuthenticEntries) {
      return {
        message: "This dataset can be marked for authentic source.",
        borderColor: "border-lnds-blue",
        dotColor: "bg-lnds-blue",
      };
    }

    if (!isReviewed && hasAuthenticEntries) {
      return {
        message: "This dataset contains authentic source entries pending review.",
        borderColor: "border-lnds-yellow",
        dotColor: "bg-lnds-yellow",
      };
    }

    return null;
  };

  const statusConfig = getStatusConfig();

  if (!statusConfig) {
    return null;
  }

  return (
    <div className={`mb-4 p-3 rounded-lg border ${statusConfig.borderColor}`}>
      <div className='flex items-center space-x-2'>
        <div className={`w-2 h-2 rounded-full ${statusConfig.dotColor}`}></div>
        <span className='text-sm'>{statusConfig.message}</span>
      </div>
    </div>
  );
};

export default AuthenticSourceStatusMessage;
