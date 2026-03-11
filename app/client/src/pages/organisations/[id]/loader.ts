import client from "../../../zodiosClient/client";
import { ResourceOrganisation } from "../../../types";

export const organisationLoader = async (id: number): Promise<ResourceOrganisation | undefined> => {
  const org = await client.get_organisation_by_id_api_v1_organisations__organisation_id__get({
    params: { organisation_id: id },
    withCredentials: true,
  });

  return org;
};
