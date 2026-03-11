import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAlert, Button, Card, CardHeading, DropdownSelect } from "@lnds-lu/design-system";
import { CloudArrowUpIcon, ArrowTopRightOnSquareIcon } from "@heroicons/react/24/solid";
import { SingleValue } from "react-select";
import client from "../../zodiosClient/client";
import DismissibleAlert from "../../components/DismissibleAlert";
import { ResourceDatasetType } from "../../types";
import { usePageTitle } from "../../hooks/usePageTitle";
import { appAlerts } from "../../utils/appAlerts";

type FormatOption = { value: string; label: string };

const SUPPORTED_FORMATS: FormatOption[] = [
  { value: "xml", label: "RDF/XML (.rdf, .xml)" },
  { value: "turtle", label: "Turtle (.ttl)" },
  { value: "json-ld", label: "JSON-LD (.jsonld)" },
];

const RdfImportPage = () => {
  usePageTitle("RDF Import");
  const { setAlert, clearAlert } = useAlert();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [format, setFormat] = useState<string>("xml");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdDataset, setCreatedDataset] = useState<ResourceDatasetType | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCreatedDataset(null);
    setErrorMessage(null);
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    clearAlert();
    setErrorMessage(null);

    if (!file) {
      setAlert(appAlerts.rdfFileRequired());
      return;
    }

    const extension = file.name.split(".").pop()?.toLowerCase();
    if (!extension) {
      setAlert(appAlerts.fileExtensionRequired());
      return;
    }

    setIsSubmitting(true);
    try {
      const body: { rdf_file: File; rdf_format?: string } = { rdf_file: file };
      if (format) {
        body.rdf_format = format;
      }

      const response = await client.import_dataset_from_rdf_api_v1_datasets_import_rdf_post(body, {
        withCredentials: true,
      });
      setCreatedDataset(response);
      setAlert(appAlerts.datasetImported(response.title));
    } catch (error) {
      console.error("Failed to import dataset from RDF", error);
      const fallbackMessage =
        (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Import failed. Please verify the RDF file and try again.";
      setErrorMessage(fallbackMessage);
      setAlert(appAlerts.fallbackErrorMessage(fallbackMessage));
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedFormatOption =
    SUPPORTED_FORMATS.find((option) => option.value === format) ?? SUPPORTED_FORMATS[0];

  return (
    <Card className='md:w-3/4 mx-4 md:mx-auto my-8 p-6'>
      {errorMessage && (
        <div className='mb-4'>
          <DismissibleAlert message={errorMessage} type='error' />
        </div>
      )}
      <CardHeading label='Import Dataset from RDF' Icon={CloudArrowUpIcon} className='flex' />
      <form className='mt-4 flex flex-col gap-6' onSubmit={handleSubmit}>
        <div>
          <input type='file' accept='.ttl,.rdf,.xml,.jsonld,.json' onChange={handleFileChange} />
          <p className='mt-2 text-xs text-gray-500'>Supported formats: Turtle, RDF/XML, JSON-LD.</p>
        </div>

        <DropdownSelect
          name='rdf_format'
          label='RDF Format'
          options={SUPPORTED_FORMATS}
          isMulti={false}
          defaultValue={selectedFormatOption.value}
          onChange={(option) =>
            setFormat((option as SingleValue<FormatOption> | undefined)?.value ?? "turtle")
          }
        />

        <div className='flex items-center gap-3'>
          <Button
            Icon={CloudArrowUpIcon}
            label='Import Dataset'
            isFormSubmit={true}
            isLoading={isSubmitting}
          />
          {createdDataset && (
            <Button
              btnType='secondary'
              Icon={ArrowTopRightOnSquareIcon}
              label='View Dataset'
              isFormSubmit={false}
              onClick={(event) => {
                event.preventDefault();
                navigate(`/datasets/${createdDataset.id}`);
              }}
            />
          )}
        </div>
      </form>
    </Card>
  );
};

export default RdfImportPage;
