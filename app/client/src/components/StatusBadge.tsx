type StatusBadgeProps = {
  isDeprecated?: boolean;
  isActive?: boolean;
};

export default function StatusBadge({ isDeprecated, isActive }: StatusBadgeProps) {
  if (isDeprecated) {
    return (
      <span className='inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-500 text-white'>
        Deprecated
      </span>
    );
  }

  if (isActive) {
    return (
      <span className='inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-lnds-green text-white'>
        Active Assignment
      </span>
    );
  }

  return (
    <span className='inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-lnds-gray text-white'>
      Unassigned
    </span>
  );
}
