import { PlusCircleIcon } from "@heroicons/react/24/solid";

interface AddButtonProps {
  onAdd: () => void;
  label: string;
  currentCount: number;
}

export default function AddButton(props: Readonly<AddButtonProps>) {
  const { onAdd, label, currentCount } = props;
  return (
    <button
      className='border-lnds-color cursor-pointer rounded-lg border px-4 py-2 hover:bg-lnds-dark-blue hover:text-white text-lnds-dark-blue dark:text-white flex flex-col items-center justify-center w-full mb-4'
      onClick={(ev) => {
        ev.preventDefault();
        onAdd();
      }}
    >
      <div className='flex items-center justify-center'>
        <PlusCircleIcon className='h-5 w-5 md:h-6 md:w-6 inline-block mr-2' />
        <p className='text-md md:text-lg'>{label}</p>
      </div>
      {currentCount > 0 && <p className='text-sm'>(currently: {currentCount})</p>}
    </button>
  );
}
