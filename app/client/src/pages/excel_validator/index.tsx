import React, { useState } from "react";
import * as XLSX from "xlsx";
import { Button, Card, CardHeading } from "@lnds-lu/design-system";
import { TrashIcon, CheckCircleIcon } from "@heroicons/react/24/solid";
import ValidationResultComponent from "./Result";
import { validateWorkbook } from "./ValidationModals/validateWorkbook";
import { ValidationResult } from "./Types";
import { usePageTitle } from "../../hooks/usePageTitle";

const ExcelValidator = () => {
  usePageTitle("Excel Validator");
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const resetState = () => {
    setValidationResult(null);
    setErrorMessage(null);
    setFileName(null);
    const input = document.getElementById("fileInput") as HTMLInputElement;
    if (input) input.value = "";
  };

  const handleFileRead = async (file: File) => {
    resetState();
    setFileName(file.name);
    setLoading(true);

    const reader = new FileReader();
    reader.onload = async (event) => {
      const binaryStr = event.target?.result;
      if (!binaryStr) {
        setErrorMessage("Failed to read file.");
        setLoading(false);
        return;
      }

      try {
        const workbook = XLSX.read(binaryStr, { type: "binary" });
        const { missingSheets, missingHeaders, dataErrors } = await validateWorkbook(workbook);

        const isValid =
          missingSheets.length === 0 &&
          Object.keys(missingHeaders).length === 0 &&
          Object.keys(dataErrors).length === 0;

        setValidationResult({ valid: isValid, missingSheets, missingHeaders, dataErrors });
      } catch (error) {
        setErrorMessage(
          "Error processing Excel file: " +
            (error instanceof Error ? error.message : String(error)),
        );
        console.error("Validation error:", error);
      } finally {
        setLoading(false);
      }
    };

    reader.readAsBinaryString(file);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileRead(file);
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileRead(file);
  };

  return (
    <div className='flex flex-col h-screen'>
      <Card className='md:w-3/4 mx-4 md:mx-auto mt-8 p-6'>
        <div className='flex flex-row justify-between items-center mb-8'>
          <CardHeading
            label='Validate Excel Template'
            Icon={CheckCircleIcon}
            className='flex w-full mb-4'
          />
          <a
            href='https://gitlab.com/mindig_lu/DCAT-AP-LU/-/raw/master/DCAT-AP-LU_official.xlsm'
            download
            className='text-sm text-lnds-blue underline hover:text-lnds-dark-blue'
          >
            Download Sample Excel Template
          </a>
        </div>

        <div className='flex items-center justify-center'>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleFileDrop}
            className={`border-2 border-dashed rounded-md p-8 text-center w-full transition-colors ${
              isDragging ? "border-lnds-blue" : "border-lnds-lightest-gray"
            }`}
          >
            {fileName && !loading && !errorMessage && (
              <div className='mt-4'>
                <p className='text-lnds-light-gray'>
                  Selected file: <span className='font-semibold text-lnds-gray'>{fileName}</span>
                </p>
              </div>
            )}
            <div className='flex justify-center items-center w-full mt-4'>
              {fileName && !loading && !errorMessage && (
                <Button
                  Icon={TrashIcon}
                  label='Remove file'
                  onClick={resetState}
                  btnType='danger'
                />
              )}
            </div>
            {!fileName && (
              <div>
                <p className='mb-2 text-lg font-medium text-lnds-gray'>
                  {isDragging ? "Drop the file here..." : "Drag & drop your Excel file here"}
                </p>
                <p className='text-sm text-lnds-light-gray mb-4'>or click to upload</p>

                <input
                  id='fileInput'
                  type='file'
                  accept='.xlsx,.xlsm'
                  onClick={(e) => {
                    (e.target as HTMLInputElement).value = "";
                  }}
                  onChange={handleFileInputChange}
                  className='file:py-2 file:px-4 file:border-0 file:rounded-md file:bg-lnds-blue file:text-white hover:file:bg-lnds-dark-blue cursor-pointer'
                />
              </div>
            )}
            {loading && (
              <p className='text-center font-semibold text-lnds-gray'>Validating the file...</p>
            )}

            {errorMessage && (
              <p className='text-center font-semibold text-lnds-red'>{errorMessage}</p>
            )}
          </div>
        </div>

        {validationResult && !errorMessage && (
          <ValidationResultComponent validationResult={validationResult} />
        )}
      </Card>
    </div>
  );
};

export default ExcelValidator;
