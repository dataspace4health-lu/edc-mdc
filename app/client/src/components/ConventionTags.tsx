import React from "react";

export type ConventionTagsProps = {
  tags: string[];
};

const ConventionTags: React.FC<ConventionTagsProps> = ({ tags }) => {
  return (
    <div className='flex flex-wrap'>
      {tags.map((tag) => (
        <div
          key={tag}
          className='relative inline-flex flex-col bg-lnds-purple rounded-lg px-2 py-1 mr-2 mb-2 text-xs'
        >
          <div className='flex items-center'>
            <span className='text-white mr-2'>{tag}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ConventionTags;
