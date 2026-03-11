const backendBaseurl = (path: string) => {
  const baseUrl = import.meta.env.VITE_BASE_URL;
  const normalizedBaseUrl = baseUrl && baseUrl !== "/" ? `${baseUrl}/` : "";
  return `${normalizedBaseUrl}${path}`;
};

export const logoutUrl = () => backendBaseurl("logout");
export const loginUrl = () => backendBaseurl("login");
