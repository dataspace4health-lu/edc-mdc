import { useState } from "react";
import { QuestionMarkCircleIcon } from "@heroicons/react/24/outline";
import { Popover } from "@lnds-lu/design-system";

type FieldInfoHeaderProps = {
  label: string;
  popoverInfo?: string;
  required?: boolean;
  as?: "h3" | "span" | "label";
  htmlFor?: string;
  containerClassName?: string;
  labelClassName?: string;
};

const FieldInfoHeader = ({
  label,
  popoverInfo,
  required,
  as = "span",
  htmlFor,
  containerClassName = "flex items-center gap-1 mb-1",
  labelClassName = "label-lnds-color",
}: Readonly<FieldInfoHeaderProps>) => {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const LabelTag = as;
  const labelNode = (
    <>
      {label}
      {required && <span className='ml-1 text-lnds-red'>*</span>}
    </>
  );

  if (!popoverInfo) {
    if (as === "label") {
      return (
        <LabelTag className={`${labelClassName} block mb-1`} htmlFor={htmlFor}>
          {labelNode}
        </LabelTag>
      );
    }

    return <LabelTag className={`${labelClassName} block mb-1`}>{labelNode}</LabelTag>;
  }

  return (
    <div className={containerClassName}>
      {as === "label" ? (
        <LabelTag className={labelClassName} htmlFor={htmlFor}>
          {labelNode}
        </LabelTag>
      ) : (
        <LabelTag className={labelClassName}>{labelNode}</LabelTag>
      )}
      {popoverInfo && (
        <Popover
          isOpen={isInfoOpen}
          onClose={() => setIsInfoOpen(false)}
          className='max-w-sm'
          trigger={
            <button
              type='button'
              onClick={() => setIsInfoOpen(!isInfoOpen)}
              className='icon-lnds-color inline-flex items-center justify-center rounded-sm opacity-75 hover:opacity-100 focus:outline-none transition-opacity'
              aria-label='Field information'
              aria-expanded={isInfoOpen}
              title='Show field information'
            >
              <QuestionMarkCircleIcon className='h-4 w-4' />
            </button>
          }
        >
          <div className='text-lnds-color'>{popoverInfo}</div>
        </Popover>
      )}
    </div>
  );
};

export default FieldInfoHeader;
