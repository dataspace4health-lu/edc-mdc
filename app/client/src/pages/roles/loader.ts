import client from "../../zodiosClient/client";

export const rolesLoader = async () => {
  return (
    (await client.get_config_roles_api_v1_config_roles_get({
      withCredentials: true,
    })) || []
  );
};
