export const DiffBlock = ({
  label,
  oldValue,
  newValue,
}: {
  label: string;
  oldValue?: string | null;
  newValue?: string | null;
}) => {
  const isRemoved = newValue === undefined || newValue === null;
  const isAdded = oldValue === undefined || oldValue === null;

  const showChange = oldValue !== newValue;

  if (!showChange) return null;

  return (
    <div className='text-sm space-y-1'>
      {isRemoved && (
        <div className='bg-lnds-red/10 text-lnds-red px-3 py-2 rounded-md border-l-4 border-l-lnds-red'>
          <span className='font-medium'>- {label}:</span>{" "}
          <span className='text-lnds-gray dark:text-lnds-lightest-gray'>{oldValue}</span>
        </div>
      )}
      {isAdded && (
        <div className='bg-lnds-green/10 text-lnds-green px-3 py-2 rounded-md border-l-4 border-l-lnds-green'>
          <span className='font-medium'>+ {label}:</span>{" "}
          <span className='text-lnds-gray dark:text-lnds-lightest-gray'>{newValue}</span>
        </div>
      )}
      {!isAdded && !isRemoved && (
        <>
          <div className='bg-lnds-red/10 text-lnds-red px-3 py-2 rounded-md border-l-4 border-l-lnds-red'>
            <span className='font-medium'>- {label}:</span>{" "}
            <span className='text-lnds-gray dark:text-lnds-lightest-gray'>{oldValue}</span>
          </div>
          <div className='bg-lnds-green/10 text-lnds-green px-3 py-2 rounded-md border-l-4 border-l-lnds-green'>
            <span className='font-medium'>+ {label}:</span>{" "}
            <span className='text-lnds-gray dark:text-lnds-lightest-gray'>{newValue}</span>
          </div>
        </>
      )}
    </div>
  );
};
