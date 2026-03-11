import React from "react";

type Props = {
  missingSheets: string[];
};

const MissingSheetsList: React.FC<Props> = ({ missingSheets }) => {
  if (missingSheets.length === 0) return null;

  return (
    <div className='mb-4'>
      <h4 className='text-xl font-semibold text-lnds-dark-blue'>Missing required sheets:</h4>
      <ul className='list-disc ml-6'>
        {missingSheets.map((sheet) => (
          <li key={sheet} className='text-lnds-gray'>
            {sheet}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MissingSheetsList;
