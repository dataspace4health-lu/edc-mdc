import { ActionFunctionArgs } from "react-router";
import client from "../../zodiosClient/client";
import { RelationSchema } from "./dto";
import { parseWithZod } from "@conform-to/zod/v4";

export const relationsFormAction = async ({ request }: ActionFunctionArgs) => {
  const formData = await request.formData();
  const submission = parseWithZod(formData, { schema: RelationSchema });

  if (submission.status === "success" && submission.value.sourceId) {
    const { relationKind, sourceId } = submission.value;

    try {
      if (
        relationKind === "dataset" &&
        submission.value.targetId &&
        submission.value.relationType
      ) {
        await client.add_relation_api_v1_datasets__dataset_id__relations_post(
          {
            relation_kind: "dataset",
            target_dataset: Number(submission.value.targetId),
            relation_type: submission.value.relationType,
          },
          {
            params: {
              dataset_id: Number(sourceId),
            },
            withCredentials: true,
          },
        );
      } else if (relationKind === "external" && submission.value.externalUrl) {
        await client.add_relation_api_v1_datasets__dataset_id__relations_post(
          {
            relation_kind: "external",
            external_url: submission.value.externalUrl,
            external_role: submission.value.externalRole || undefined,
            external_description: submission.value.externalDescription || undefined,
          },
          {
            params: {
              dataset_id: Number(sourceId),
            },
            withCredentials: true,
          },
        );
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      if (error.response?.data?.detail) {
        return submission.reply({
          formErrors: [error.response.data.detail],
        });
      }
      throw error;
    }
  }

  return submission.reply();
};
