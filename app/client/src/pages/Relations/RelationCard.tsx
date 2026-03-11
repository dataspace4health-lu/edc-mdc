import { DatasetRelation } from "../../types";
import client from "../../zodiosClient/client";
import { useAlert, Card } from "@lnds-lu/design-system";
import RelationLink from "../../components/RelationLink";
import { TrashIcon, RectangleGroupIcon, TagIcon } from "@heroicons/react/24/solid";
import { twMerge } from "tailwind-merge";
import { appAlerts } from "../../utils/appAlerts";

interface RelationCardProps {
  sourceId: number;
  relation: DatasetRelation;
  getNewerVersionRelation: (relation: DatasetRelation) => DatasetRelation | null;
  onDelete: (relationId: number) => void;
  className?: string;
}

export default function RelationCard(props: Readonly<RelationCardProps>) {
  const { sourceId, relation, onDelete, className } = props;
  const { setAlert } = useAlert();

  const handleDelete = async () => {
    try {
      await client.delete_relation_api_v1_datasets__dataset_id__relations__relation_id__delete(
        undefined,
        {
          params: {
            dataset_id: sourceId,
            relation_id: relation.id,
          },
          withCredentials: true,
        },
      );
      onDelete(relation.id);
      setAlert(appAlerts.relationDeleted());
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setAlert(
        appAlerts.genericValidationError(err?.message || appAlerts.serverErrorTryLater().message),
      );
    }
  };

  const newerVersionRelation =
    relation.relationKind === "dataset" ? props.getNewerVersionRelation(relation) : null;

  return (
    <Card className={twMerge("w-full", "p-4", className)}>
      <div className='flex justify-between items-start gap-4'>
        {relation.relationKind === "dataset" ? (
          <RelationLink
            relationType={relation.relationType!}
            datasetId={relation.datasetId!}
            datasetTitle={relation.title!}
            hasNewerVersion={!!newerVersionRelation}
            newerVersionId={newerVersionRelation?.datasetId ?? undefined}
            status={relation.status!}
          />
        ) : (
          <div className='flex flex-col break-all'>
            <a
              href={relation.externalUrl!}
              target='_blank'
              rel='noopener noreferrer'
              className='text-lnds-color underline break-all hover:text-lnds-dark-blue dark:hover:text-white flex items-center mb-1'
            >
              <RectangleGroupIcon className='h-5 w-5 mr-1' />
              {relation.externalUrl}
            </a>
            {relation.externalRole && (
              <span className='text-lnds-gray dark:text-gray-400 text-sm flex items-center mb-1'>
                <TagIcon className='h-4 w-4 mr-1' />
                {relation.externalRole}
              </span>
            )}
            {relation.externalDescription && (
              <span className='text-sm text-lnds-gray dark:text-gray-400 break-words'>
                {relation.externalDescription}
              </span>
            )}
          </div>
        )}
        <button onClick={handleDelete} className='hover:text-lnds-red'>
          <TrashIcon className='h-6 w-6 icon-lnds-color' />
        </button>
      </div>
    </Card>
  );
}
