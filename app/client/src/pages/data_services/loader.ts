import client from "../../zodiosClient/client";

const DataServiceLoader = async () => {
  return (
    (await client.get_data_services_api_v1_data_services_get({
      withCredentials: true,
    })) || []
  );
};

export default DataServiceLoader;
