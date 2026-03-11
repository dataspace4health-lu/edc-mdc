import { DatasetFormInputs } from "./datasetDTO";
import datasetSchema from "../../schemas/datasetSchema";

export const defaultDatasetFormInputs: DatasetFormInputs = {} as unknown as DatasetFormInputs;

datasetSchema.forEach((schema) => {
  // @ts-expect-error Element implicitly has an 'any' type
  defaultDatasetFormInputs[schema.name] = schema.testData;
});
