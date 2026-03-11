import React from "react";

type Props = {
  valid: boolean;
};

const ValidationSummary: React.FC<Props> = ({ valid }) => (
  <p className='flex text-2xl mb-4'>
    <h3 className='heading-lnds-color text-lg md:text-xl lg:text-2xl mr-3'>Validation Result: </h3>
    {valid ? (
      <span className='text-lnds-green'>Import ready to proceed</span>
    ) : (
      <span className='text-lnds-red'>Import has errors, please review the details below</span>
    )}
  </p>
);

export default ValidationSummary;
