import { ExclamationTriangleIcon, InformationCircleIcon } from "@heroicons/react/24/solid";

interface VersionChangeTypeLabelProps {
  versionChangeType?: string | null;
}

const getVersionTypeTextClass = (versionChangeType?: string | null) => {
  if (versionChangeType === "METADATA_ONLY") {
    return "border border-lnds-color text-lnds-color bg-transparent";
  }
  if (versionChangeType === "UNDERLYING_DATA") {
    return "border border-lnds-color text-lnds-color bg-transparent";
  }
  return "border border-gray-300 bg-gray-100 text-gray-700";
};

const getVersionTypeShortLabel = (versionChangeType?: string | null) => {
  if (versionChangeType === "METADATA_ONLY") {
    return "Metadata only changed";
  }
  if (versionChangeType === "UNDERLYING_DATA") {
    return "Data + metadata changed";
  }
  return "Unspecified change";
};

export default function VersionChangeTypeLabel({
  versionChangeType,
}: Readonly<VersionChangeTypeLabelProps>) {
  const Icon =
    versionChangeType === "UNDERLYING_DATA" ? ExclamationTriangleIcon : InformationCircleIcon;

  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-sm font-semibold ${getVersionTypeTextClass(
        versionChangeType,
      )}`}
    >
      <Icon className='h-4 w-4' />
      {getVersionTypeShortLabel(versionChangeType)}
    </span>
  );
}
