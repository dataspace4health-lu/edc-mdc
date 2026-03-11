import { createContext, useContext, useState, ReactNode } from "react";

interface LeftSidebarContextType {
  isSidebarOpen: boolean;
  setSidebarOpen: (isOpen: boolean) => void;
}

const LeftSidebarContext = createContext<LeftSidebarContextType | null>(null);

interface LeftSidebarProviderProps {
  children: ReactNode;
}

export const LeftSidebarProvider = ({ children }: LeftSidebarProviderProps) => {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  return (
    <LeftSidebarContext.Provider value={{ isSidebarOpen: sidebarOpen, setSidebarOpen }}>
      {children}
    </LeftSidebarContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useLeftSidebar = () => {
  const context = useContext(LeftSidebarContext);
  if (!context) {
    throw new Error("useLeftSidebar must be used within an LeftSidebarProvider");
  }
  return context;
};
