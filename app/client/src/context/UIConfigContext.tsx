import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import client from "../zodiosClient/client";

interface UIConfigType {
  unauthorised_message: string;
  technical_support_message: string;
  source_instance_url: string;
  source_dataset_url_pattern: string;
  is_ctie_instance: boolean;
  default_access_url: string;
  enable_health_dataset_selector: boolean;
}

interface UIConfigContextType {
  config: UIConfigType | null;
  isLoading: boolean;
}

const UIConfigContext = createContext<UIConfigContextType | null>(null);

interface UIConfigProviderProps {
  children: ReactNode;
}

export const UIConfigProvider = ({ children }: UIConfigProviderProps) => {
  const [config, setConfig] = useState<UIConfigType | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setIsLoading(true);
        const response = await client.get_ui_config_api_v1_ui_config_get({
          withCredentials: true,
        });
        // @ts-expect-error 'response' is of type 'unknown'.
        setConfig(response);
      } catch (error) {
        console.error("Error fetching UI config:", error);
        // Set defaults if fetch fails
        setConfig({
          unauthorised_message: "",
          technical_support_message: "",
          source_instance_url: "",
          source_dataset_url_pattern: "/?id={id}",
          is_ctie_instance: false,
          default_access_url: "",
          enable_health_dataset_selector: false,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchConfig();
  }, []);

  return (
    <UIConfigContext.Provider value={{ config, isLoading }}>{children}</UIConfigContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useUIConfig = () => {
  const context = useContext(UIConfigContext);
  if (!context) {
    throw new Error("useUIConfig must be used within a UIConfigProvider");
  }
  return context;
};
