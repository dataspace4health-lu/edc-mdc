import { useEffect } from "react";
import DatasetFormCacheManager from "../utils/DatasetFormCacheManager";

export function useAutoSave({ formRef }: { formRef: React.RefObject<HTMLFormElement> }) {
  useEffect(() => {
    const formEl = formRef.current;

    if (!formEl) return;

    const handleInputChange = () => {
      const formData = new FormData(formEl);
      const formValues = Object.fromEntries(formData.entries());
      DatasetFormCacheManager.save(formValues);
    };

    formEl.addEventListener("input", handleInputChange);

    return () => formEl.removeEventListener("input", handleInputChange);
  }, [formRef]);
}
