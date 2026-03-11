import React from "react";
import Tooltip from "./Tooltip";
import { ComputerDesktopIcon, ArrowDownTrayIcon } from "@heroicons/react/24/solid";

export type InitialsAvatarProps = {
  name?: string | null;
  isSystem?: boolean;
  isImported?: boolean;
  showTooltip?: boolean;
};

const InitialsAvatar: React.FC<InitialsAvatarProps> = ({
  name: propName,
  showTooltip,
  isSystem,
  isImported,
}) => {
  const name = propName || (isSystem ? "System" : isImported ? "Imported Dataset" : "Unknown User");
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  let avatar = (
    <div className='w-8 h-8 rounded-full bg-lnds-lightest-gray flex items-center justify-center'>
      <span className='text-sm font-medium text-lnds-gray'>{initials}</span>
    </div>
  );

  if (isImported) {
    avatar = (
      <div className='w-8 h-8 rounded-full bg-lnds-green flex items-center justify-center'>
        <ArrowDownTrayIcon className='w-5 h-5 text-white' />
      </div>
    );
  } else if (isSystem) {
    avatar = (
      <div className='w-8 h-8 rounded-full bg-lnds-lightest-gray flex items-center justify-center'>
        <ComputerDesktopIcon className='w-5 h-5 text-lnds-gray' />
      </div>
    );
  }

  if (showTooltip) {
    return <Tooltip text={name}>{avatar}</Tooltip>;
  }

  return avatar;
};

export default InitialsAvatar;
