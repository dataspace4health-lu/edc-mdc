import { createContext, useContext, useState, ReactNode } from "react";

interface UnsavedContextType {
  isUnSaved: boolean;
  setIsUnSaved: (d: boolean) => void;
}

const UnsavedContext = createContext<UnsavedContextType | null>(null);

interface UnsavedProviderProps {
  children: ReactNode;
}

export const UnsavedProvider = ({ children }: UnsavedProviderProps) => {
  const [isUnSaved, setIsUnSaved] = useState(false);
  return (
    <UnsavedContext.Provider value={{ isUnSaved, setIsUnSaved }}>
      {children}
    </UnsavedContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useUnsaved = (): UnsavedContextType => {
  const context = useContext(UnsavedContext);
  if (!context) {
    throw new Error("useUnsaved must be used within an UnsavedProvider");
  }
  return context;
};
