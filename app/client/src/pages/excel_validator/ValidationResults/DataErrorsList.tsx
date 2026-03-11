import React from "react";

type Props = {
  dataErrors: Record<string, string[]>;
};

const DataErrorsList: React.FC<Props> = ({ dataErrors }) => {
  if (Object.keys(dataErrors).length === 0) return null;

  return (
    <div className='mb-4'>
      <h4 className='heading-lnds-color text-lg md:text-xl lg:text-2xl'>
        Data errors (missing required values or invalid formats):
      </h4>
      {Object.entries(dataErrors).map(([sheet, errors]) => (
        <div key={sheet} className='mb-4 p-4 rounded-md'>
          <strong className='text-lg text-lnds-red'>{sheet}:</strong>
          <ul className='list-disc ml-6'>
            {errors.map((error, i) => (
              <li key={`${sheet}-error-${i}-${error.slice(0, 20)}`} className='text-lnds-red'>
                {error}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default DataErrorsList;
