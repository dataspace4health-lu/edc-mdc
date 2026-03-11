import { ActionFunctionArgs } from "react-router";
import { getDatasetFormInputsSchema } from "./datasetDTO";

import { parseWithZod } from "@conform-to/zod/v4";

export const datasetFormAction = async ({ request }: ActionFunctionArgs) => {
  const formData = await request.formData();

  const enableHealthDcat = formData.get("_enableHealthDcat") === "true";
  const schema = getDatasetFormInputsSchema({ enableHealthDcat });

  const submission = parseWithZod(formData, { schema });

  return submission.reply();
};
