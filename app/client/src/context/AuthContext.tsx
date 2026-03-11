import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { ResourceUserType } from "../types";
import client from "../zodiosClient/client";

interface AuthContextType {
  user: ResourceUserType | null;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

const BASE_URL = import.meta.env.VITE_BASE_URL || "";

const PUBLIC_ROUTES = [
  "/excel-validator",
  "/unauthorised",
  "/first-time-login",
  "/ctie-only-access",
];

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<ResourceUserType | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkUserLoggedIn = async () => {
    const rawPath = window.location.pathname;
    const currentPath =
      BASE_URL && rawPath.startsWith(BASE_URL)
        ? rawPath.slice(BASE_URL.length) || "/"
        : rawPath;

    if (PUBLIC_ROUTES.includes(currentPath)) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const user: ResourceUserType = await client.get_user_api_v1_user_get({
        withCredentials: true,
      });

      // Check if user has CTIE-only access and redirect
      if (user.has_ctie_only_access) {
        window.location.href = `${BASE_URL}/ctie-only-access`;
        return;
      }

      setUser(user);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkUserLoggedIn();
  }, []);

  return <AuthContext.Provider value={{ user, isLoading }}>{children}</AuthContext.Provider>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
