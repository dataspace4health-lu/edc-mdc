import React, { useEffect, useState, useRef } from "react";
import * as XLSX from "xlsx";
import ValidationResult from "../excel_validator/Result";
import { validateWorkbook } from "../excel_validator/ValidationModals/validateWorkbook";
import { ValidationResult as ValidationResultType } from "../excel_validator/Types";
import { Button, Card, CardHeading } from "@lnds-lu/design-system";
import {
  TrashIcon,
  PlusCircleIcon,
  DocumentArrowUpIcon,
  ArrowUpTrayIcon,
  HomeIcon,
  ClipboardDocumentIcon,
} from "@heroicons/react/24/solid";
import { submitDatasets } from "./Utils";
import { extractDatasetsFromWorkbook } from "./BuildDatasets";
import { useAlert } from "@lnds-lu/design-system";
import { useAuth } from "../../context/AuthContext";
import { extractDataDictionariesFromWorkbook } from "./BuildDataDictionary";
import { processMissingFormFields } from "./BuildFormFields";
import { processMissingContacts } from "./BuildContact";
import client from "../../zodiosClient/client";
import { useNavigate } from "react-router-dom";
import { usePageTitle } from "../../hooks/usePageTitle";
import { appAlerts } from "../../utils/appAlerts";

const BulkUpload = () => {
  usePageTitle("Bulk Upload");
  const navigate = useNavigate();
  const { user } = useAuth();
  const { setAlert } = useAlert();

  const [file, setFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResultType | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitErrors, setSubmitErrors] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [currentStage, setCurrentStage] = useState<string>("");
  const [failedStage, setFailedStage] = useState<string>("");
  const [progressLogs, setProgressLogs] = useState<string[]>([]);
  const [importComplete, setImportComplete] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setProgressLogs((prev) => [...prev, `[${timestamp}] ${message}`]);
  };

  const copyLogsToClipboard = () => {
    const logsText = progressLogs.join("\n");
    navigator.clipboard
      .writeText(logsText)
      .then(() => {
        setAlert(appAlerts.logsCopied());
      })
      .catch((err) => {
        console.error("Failed to copy logs:", err);
        setAlert(appAlerts.logsCopyFailed());
      });
  };

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [progressLogs]);

  const resetAll = () => {
    setFile(null);
    setValidationResult(null);
    setErrorMessage(null);
    setLoading(false);
    setSubmitErrors([]);
    setCurrentStage("");
    setFailedStage("");
    setProgressLogs([]);
    setImportComplete(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleFile = (selectedFile: File) => {
    setFile(selectedFile);
  };

  useEffect(() => {
    if (file) {
      handleFileRead(file);
    }
  }, [file]);

  const handleFileRead = async (file: File) => {
    setLoading(true);
    setErrorMessage(null);
    setValidationResult(null);
    setSubmitErrors([]);
    setCurrentStage("Scanning file for viruses...");

    // First, scan the file for viruses
    try {
      const scanResult = await client.scan_file_api_v1_antivirus_scan_post(
        { file: file },
        { withCredentials: true },
      );

      if (!scanResult.is_clean) {
        setErrorMessage(`File scan failed: ${scanResult.message}`);
        setLoading(false);
        setCurrentStage("");
        return;
      }
    } catch (error) {
      console.error("Virus scan error:", error);
      setErrorMessage(
        "Failed to scan file: " + (error instanceof Error ? error.message : String(error)),
      );
      setLoading(false);
      setCurrentStage("");
      return;
    }

    setCurrentStage("Validating file structure...");

    const reader = new FileReader();
    reader.onload = async (event) => {
      const binaryStr = event.target?.result;
      if (!binaryStr) {
        setErrorMessage("Failed to read the file.");
        setLoading(false);
        setCurrentStage("");
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
          "Validation error: " + (error instanceof Error ? error.message : String(error)),
        );
        console.error(error);
      } finally {
        setLoading(false);
        setCurrentStage("");
      }
    };

    reader.readAsBinaryString(file);
  };

  const handleDatasetCreation = async () => {
    if (!file) return;

    setLoading(true);
    setSubmitErrors([]);
    setCurrentStage("");
    setFailedStage("");
    setProgressLogs([]);
    setImportComplete(false);

    let activeStage = "";

    try {
      activeStage = "Reading file";
      setCurrentStage(activeStage + "...");
      addLog(`Started: ${activeStage}`);
      const workbook = XLSX.read(await file.arrayBuffer(), { type: "array" });
      addLog(`✓ File read successfully`);

      activeStage = "Adding missing keywords and applicable legislations";
      setCurrentStage(activeStage + "...");
      addLog(`Started: ${activeStage}`);
      await processMissingFormFields(workbook, user!, addLog);
      addLog(`✓ Keywords and applicable legislations processed`);

      activeStage = "Adding missing contacts";
      setCurrentStage(activeStage + "...");
      addLog(`Started: ${activeStage}`);
      const contactErrors = await processMissingContacts(workbook, addLog);
      if (contactErrors.length > 0) {
        addLog(`✗ Failed to add contacts`);
        contactErrors.forEach((err) => addLog(`  - ${err}`));
        setFailedStage(activeStage);
        setSubmitErrors(contactErrors);
        setCurrentStage("");
        return;
      }
      addLog(`✓ Contacts processed`);

      activeStage = "Preparing datasets";
      setCurrentStage(activeStage + "...");
      addLog(`Started: ${activeStage}`);
      const datasets = await extractDatasetsFromWorkbook(workbook);
      const data_dictionary = extractDataDictionariesFromWorkbook(workbook);
      addLog(`✓ Prepared ${datasets.length} dataset(s) for import`);

      activeStage = "Creating datasets";
      setCurrentStage(activeStage + "...");
      addLog(`Started: ${activeStage}`);
      const { errors, successCount } = await submitDatasets(datasets, data_dictionary, addLog);

      if (successCount > 0) {
        addLog(`✓ Successfully created ${successCount} dataset(s)`);
        setAlert(appAlerts.bulkDatasetsCreated(successCount));
      }

      if (errors.length > 0) {
        addLog(`✗ Some datasets failed to import`);
        errors.forEach((err) => addLog(`  - ${err}`));
        setFailedStage(activeStage);
        setSubmitErrors(errors);
        setCurrentStage("");
      } else {
        addLog(`✓ Import completed successfully!`);
        setCurrentStage("Import completed successfully!");
        setImportComplete(true);
      }
    } catch (e) {
      console.error(e);
      const errorMessage = e instanceof Error ? e.message : String(e);
      addLog(`✗ Error during ${activeStage}: ${errorMessage}`);
      setFailedStage(activeStage || "unknown stage");
      setSubmitErrors([errorMessage]);
      setCurrentStage("");
    } finally {
      setLoading(false);
    }
  };

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      handleFile(droppedFile);
    }
  };

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
  };

  return (
    <Card className='md:w-3/4 mx-4 md:mx-auto my-8 p-6'>
      <div className='flex flex-row justify-between items-center mb-8'>
        <CardHeading
          label='Bulk Import Datasets'
          Icon={DocumentArrowUpIcon}
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
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-md p-8 w-full text-center transition-colors ${
          isDragging ? "border-lnds-blue bg-lnds-light-blue" : "border-lnds-lightest-gray"
        }`}
        onClick={() => fileInputRef.current?.click()}
      >
        {!file && !loading && !errorMessage && (
          <div className='flex flex-col items-center space-y-4 mt-4'>
            <p className='text-lg font-medium text-lnds-gray text-center dark:text-lnds-lightest-gray'>
              {isDragging ? "Drop the file here..." : "Drag & drop your Excel file here"}
            </p>
            <p className='text-sm text-lnds-light-gray text-center dark:text-lnds-lightest-gray'>
              or click to upload
            </p>

            <input
              type='file'
              accept='.xlsx,.xlsm'
              ref={fileInputRef}
              onChange={onFileInputChange}
              style={{ display: "none" }}
            />

            <Button
              label='Upload Excel file'
              Icon={ArrowUpTrayIcon}
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              btnType='primary'
            />
          </div>
        )}

        {loading && (
          <div className='text-center'>
            <p className='font-semibold text-lnds-gray dark:text-lnds-lightest-gray'>
              Processing the file...
            </p>
            {currentStage && (
              <p className='text-sm text-lnds-light-gray dark:text-lnds-gray mt-2'>
                {currentStage}
              </p>
            )}
          </div>
        )}

        {errorMessage && (
          <div className='text-center font-semibold text-lnds-red'>{errorMessage}</div>
        )}

        {file && !loading && !errorMessage && (
          <div className='flex flex-col items-center space-y-4 mt-4'>
            <p className='text-lnds-light-gray dark:text-lnds-lightest-gray'>
              Selected file:{" "}
              <span className='font-semibold text-lnds-gray dark:text-lnds-lightest-gray'>
                {file.name}
              </span>
            </p>

            <Button
              Icon={TrashIcon}
              label='Remove File'
              btnType='danger'
              onClick={(e) => {
                e.stopPropagation();
                resetAll();
              }}
            />
          </div>
        )}
      </div>

      {validationResult && !loading && <ValidationResult validationResult={validationResult} />}

      {progressLogs.length > 0 && (
        <div className='border border-lnds-color px-6 py-4 rounded mb-8 mt-8 bg-white dark:bg-gray-800'>
          <div className='flex justify-between items-center mb-3'>
            <p className='font-semibold text-lg text-lnds-gray dark:text-white'>
              Import Progress Log:
            </p>
            <Button
              Icon={ClipboardDocumentIcon}
              label='Copy Logs'
              onClick={copyLogsToClipboard}
              btnType='secondary'
            />
          </div>
          <div className='bg-white dark:bg-gray-900 border border-lnds-light-gray dark:border-gray-700 rounded-md p-4 max-h-96 overflow-y-auto font-mono text-sm'>
            {progressLogs.map((log, i) => (
              <div
                key={`log-${i}`}
                className={`py-1 ${
                  log.includes("✓")
                    ? "text-lnds-blue"
                    : log.includes("✗")
                      ? "text-lnds-red"
                      : "text-lnds-gray dark:text-lnds-lightest-gray"
                }`}
              >
                {log}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
          {importComplete && (
            <div className='mt-4 flex justify-center'>
              <Button
                Icon={HomeIcon}
                label='Go to Home'
                onClick={() => navigate("/")}
                btnType='primary'
              />
            </div>
          )}
        </div>
      )}

      {submitErrors.length > 0 && (
        <div className='border border-lnds-red text-lnds-red px-6 py-4 rounded mb-8 mt-8'>
          <p className='font-semibold mb-3 text-lg'>Submission Errors:</p>
          {failedStage && (
            <div className='bg-lnds-red text-white px-4 py-3 rounded-md mb-4 font-semibold'>
              ⚠️ Failed during: {failedStage}
            </div>
          )}
          <ul className='list-disc list-inside space-y-1'>
            {submitErrors.map((err, i) => (
              <li key={`error-${err}-${i}`} className='pl-1'>
                {err}
              </li>
            ))}
          </ul>
        </div>
      )}

      {validationResult?.valid && !loading && !importComplete && (
        <div className='flex justify-center mt-6'>
          <Button
            Icon={PlusCircleIcon}
            label='Import Datasets'
            onClick={handleDatasetCreation}
            btnType='primary'
          />
        </div>
      )}
    </Card>
  );
};

export default BulkUpload;
