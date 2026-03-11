import React from "react";
import { ValidationResult as ValidationResultType } from "./Types";
import ValidationSummary from "./ValidationResults/ValidationSummary";
import MissingSheetsList from "./ValidationResults/MissingSheetsList";
import MissingHeadersList from "./ValidationResults/MissingHeadersList";
import DataErrorsList from "./ValidationResults/DataErrorsList";

type Props = {
  validationResult: ValidationResultType;
};

const ValidationResult: React.FC<Props> = ({ validationResult }) => {
  return (
    <div className='mt-6'>
      <ValidationSummary valid={validationResult.valid} />
      <MissingSheetsList missingSheets={validationResult.missingSheets} />
      <MissingHeadersList missingHeaders={validationResult.missingHeaders} />
      <DataErrorsList dataErrors={validationResult.dataErrors} />
    </div>
  );
};

export default ValidationResult;
