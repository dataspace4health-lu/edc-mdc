import React from "react";

type Props = {
  missingHeaders: Record<string, string[]>;
};

const MissingHeadersList: React.FC<Props> = ({ missingHeaders }) => {
  if (Object.keys(missingHeaders).length === 0) return null;

  return (
    <div className='mb-4'>
      <h4 className='text-xl font-semibold text-lnds-dark-blue'>
        Missing required headers per sheet:
      </h4>
      {Object.entries(missingHeaders).map(([sheet, headers]) => (
        <div key={sheet} className='mb-2'>
          <strong className='text-lg text-lnds-blue'>{sheet}:</strong>
          <ul className='list-disc ml-6'>
            {headers.map((header) => (
              <li key={header} className='text-lnds-gray'>
                {header}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default MissingHeadersList;
