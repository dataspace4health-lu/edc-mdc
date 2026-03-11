import { DatasetFormInputs } from "../pages/DatasetForm/datasetDTO";

export default class DatasetFormCacheManager {
  static key = "datasetFormValues";

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  static save(formData: Record<string, any>): void {
    const dataToSave = JSON.stringify(formData);
    localStorage.setItem(this.key, dataToSave);
  }

  static getFormData(): DatasetFormInputs | null {
    const savedData = localStorage.getItem(this.key);
    return savedData ? JSON.parse(savedData) : null;
  }

  static clear(): void {
    localStorage.removeItem(this.key);
  }
}
