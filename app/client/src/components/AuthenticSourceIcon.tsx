import { CheckBadgeIcon } from "@heroicons/react/24/solid";
import Tooltip from "./Tooltip";
import { ResourceDatasetType } from "../types";

interface AuthenticSourceIconProps {
  dataset: ResourceDatasetType;
}

export default function AuthenticSourceIcon(props: Readonly<AuthenticSourceIconProps>) {
  const { dataset } = props;
  if (!dataset.is_any_dictionary_authentic_source) {
    return null;
  }

  return (
    <Tooltip text='Contains Authentic Source data dictionary entries'>
      <div className='flex items-center gap-1 rounded-md bg-green-100 py-1 px-2 border border-green-300'>
        <CheckBadgeIcon className='h-4 w-4 text-green-600' />
      </div>
    </Tooltip>
  );
}
