import client from "../../zodiosClient/client";

export const datasetListLoader = async () => {
  const formFields = await client.retrieve_form_fields_api_v1_form_fields_get({
    withCredentials: true,
  });

  return { formFields };
};
