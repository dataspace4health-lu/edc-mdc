import React from "react";

export type EmptyScreenProps = {
  message: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Icon: any;
};

const EmptyScreen: React.FC<EmptyScreenProps> = ({ message, Icon }) => {
  return (
    <div className='w-full'>
      <div className='border-2 border-dashed border-lnds-color rounded-lg p-12 flex flex-col items-center justify-center text-gray-500'>
        <Icon className='h-16 w-16 icon-lnds-color' />
        <p className='mt-2 text-lg font-semibold'>{message}</p>
      </div>
    </div>
  );
};

export default EmptyScreen;
