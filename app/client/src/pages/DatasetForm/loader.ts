import client from "../../zodiosClient/client";
import { FormType } from "../../types";

export const datasetFormLoader = async (): Promise<FormType> => {
  const formFields = await client.retrieve_form_fields_api_v1_form_fields_get({
    withCredentials: true,
  });

  return {
    dataset: formFields.dataset,
    distribution: formFields.distribution,
    organisation: formFields.organisation,
    contact: formFields.contact,
    data_service: formFields.data_service,
  };
};
