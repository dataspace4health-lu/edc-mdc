import React, { useState } from "react";
import { ChevronDownIcon, ChevronUpIcon, LinkIcon } from "@heroicons/react/24/solid";

export type ApplicableLegislationTagProps = {
  eng_label: string;
  description?: string | null | undefined;
  link?: string | null | undefined;
  isExpanded: boolean;
  onExpand: () => void;
};

const ApplicableLegislationTag: React.FC<ApplicableLegislationTagProps> = ({
  eng_label,
  description,
  link,
  isExpanded,
  onExpand,
}) => {
  return (
    <div className='relative inline-flex flex-col bg-lnds-purple rounded-lg px-2 py-1 mr-2 mb-2 text-xs'>
      <div className='flex items-center'>
        <span className='text-white mr-2'>{eng_label}</span>
        <button onClick={onExpand} className='text-white'>
          {isExpanded ? (
            <ChevronUpIcon className='h-4 w-4' />
          ) : (
            <ChevronDownIcon className='h-4 w-4' />
          )}
        </button>
      </div>

      {isExpanded && (
        <div className='mt-2'>
          {description && <p className='text-white mb-2'>{description}</p>}
          {link && (
            <a
              href={link}
              target='_blank'
              rel='noopener noreferrer'
              className='flex items-center text-white hover:underline'
            >
              <LinkIcon className='h-4 w-4 mr-1' />
              View legal document
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export type ApplicableLegislationTagsProps = {
  legislations: Array<{
    eng_label: string;
    description?: string | null | undefined;
    link?: string | null | undefined;
  }>;
};

const ApplicableLegislationTags: React.FC<ApplicableLegislationTagsProps> = ({ legislations }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className='flex flex-wrap'>
      {legislations.map((legislation, index) => (
        <ApplicableLegislationTag
          key={`${legislation.eng_label}-${index}`}
          {...legislation}
          isExpanded={expandedIndex === index}
          onExpand={() => handleExpand(index)}
        />
      ))}
    </div>
  );
};

export default ApplicableLegislationTags;
