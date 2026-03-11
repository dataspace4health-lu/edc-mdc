import client from "../../zodiosClient/client";

export const usersLoader = async () => {
  return (await client.get_organisations_api_v1_organisations_get({ withCredentials: true })) || [];
};
