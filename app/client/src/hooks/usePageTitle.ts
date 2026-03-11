import { useEffect } from "react";

const APP_NAME = "Dataset Metadata Capture";
const APP_NAME_DEV = "Dataset Metadata Capture (DEV)";

/**
 * Custom hook to set the browser page title dynamically.
 * @param title - The page-specific title (e.g., "Organisations", dataset name)
 * @param suffix - Optional suffix to append (defaults to app name)
 */
export function usePageTitle(title?: string, suffix?: string) {
  useEffect(() => {
    const baseAppName = import.meta.env.DEV ? APP_NAME_DEV : APP_NAME;
    const finalSuffix = suffix !== undefined ? suffix : ` - ${baseAppName}`;

    document.title = title ? `${title}${finalSuffix}` : baseAppName;

    return () => {
      document.title = baseAppName;
    };
  }, [title, suffix]);
}
