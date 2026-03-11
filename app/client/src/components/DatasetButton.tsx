interface DatasetButtonProps {
  label: string;
  type: "submit" | "reset" | "button";
  onClick: React.MouseEventHandler<HTMLButtonElement> | undefined;
}

export default function DatasetButton(props: Readonly<DatasetButtonProps>) {
  const { label, type, onClick } = props;
  return (
    <button
      type={type}
      onClick={onClick}
      className='whitespace-no-wrap inline-flex items-center justify-center rounded-md bg-lnds-blue px-4 py-2 text-base font-medium leading-6 text-white shadow-sm hover:bg-lnds-yellow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
    >
      {label}
    </button>
  );
}
