import { ArrowPathIcon } from "@heroicons/react/24/solid";

export function Spinner({ message }: Readonly<{ message?: string }>) {
  return (
    <div className='flex flex-col items-center justify-center space-y-2'>
      <ArrowPathIcon className='w-8 h-8 animate-spin text-lnds-blue' />
      {message && <p className='text-sm text-lnds-gray'>{message}</p>}
    </div>
  );
}
