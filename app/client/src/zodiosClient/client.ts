import { createApiClient } from "./openapi.json.client";
import { loginUrl } from "../utils/authUrls";
import axios, { AxiosResponse, AxiosError } from "axios";

const axiosInstance = axios.create();

axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response && error.response.status === 401) {
      window.location.href = loginUrl();
    }
    return Promise.reject(error); // Return any other error unchanged
  },
);

const client = createApiClient(import.meta.env.VITE_BASE_URL, { axiosInstance });

const clientWithoutValidation = createApiClient(import.meta.env.VITE_BASE_URL, {
  axiosInstance,
  validate: false,
});

export { clientWithoutValidation };

export default client;
