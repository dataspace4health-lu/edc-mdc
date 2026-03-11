import React, { useMemo, useState, useEffect, useCallback } from "react";
import { ChatBubbleOvalLeftIcon } from "@heroicons/react/24/solid";
import InitialsAvatar from "../InitialsAvatar";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { ResourceDatasetComment } from "../../types";
import client from "../../zodiosClient/client";
import EmptyScreen from "../EmptyScreen";
import { useAlert } from "@lnds-lu/design-system";
import { ResourceDatasetType } from "../../types";
import { useAuth } from "../../context/AuthContext";
import ConfirmableActionButton from "../ConfirmableActionButton";
import { appAlerts } from "../../utils/appAlerts";

const forbiddenStatuses = ["PUBLISHED", "INTERNAL_ONLY", "DEPRECATED"];

const commentsLoader = async (datasetId: number): Promise<ResourceDatasetComment[]> => {
  return await client.get_dataset_comments_api_v1_datasets__dataset_id__comments_get({
    params: { dataset_id: datasetId },
    withCredentials: true,
  });
};

interface CommentListProps {
  dataset: ResourceDatasetType;
  refreshComments: boolean;
}

const groupCommentsByDate = (
  comments: ResourceDatasetComment[],
): Record<string, ResourceDatasetComment[]> => {
  return comments.reduce(
    (acc: Record<string, ResourceDatasetComment[]>, comment: ResourceDatasetComment) => {
      const date = DateUtils.getStartOfDay(comment.timestamp).toISOString();
      acc[date] = acc[date] || [];
      acc[date].push(comment);
      return acc;
    },
    {},
  );
};

const formatDateSection = (dateString: string) => {
  const today = DateUtils.getStartOfToday();
  const commentDate = DateUtils.getStartOfDay(dateString);

  if (DateUtils.areDatesEqual(today, commentDate)) {
    return "Today";
  } else {
    return DateUtils.formatDate(dateString);
  }
};

const shouldAllowDelete = (status: string, canDelete: boolean): boolean => {
  return canDelete && !forbiddenStatuses.includes(status);
};

export const CommentList: React.FC<CommentListProps> = ({ dataset, refreshComments }) => {
  const [comments, setComments] = useState<ResourceDatasetComment[]>([]);
  const { setAlert } = useAlert();
  const { user } = useAuth();
  const canDeleteComments = user?.permissions?.includes("comments:delete") ?? false;

  const fetchComments = useCallback(async () => {
    try {
      const response = await commentsLoader(dataset.id);
      setComments(response);
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  }, [dataset.id]);

  const handleDeleteComment = async (commentId: number) => {
    if (!canDeleteComments) {
      setAlert(appAlerts.commentDeletePermissionDenied());
      return;
    }

    if (forbiddenStatuses.includes(dataset.status)) {
      setAlert(appAlerts.datasetStatusDeletionBlocked(dataset.status));
      return;
    }
    try {
      await client.delete_comment_api_v1_dataset_comments__comment_id__delete(undefined, {
        params: { comment_id: commentId },
        withCredentials: true,
      });

      setAlert(appAlerts.commentDeleted());
      await fetchComments();
    } catch (error) {
      console.error("Error deleting comment:", error);
      setAlert(appAlerts.commentDeleteFailed());
    }
  };

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  useEffect(() => {
    if (refreshComments) {
      fetchComments();
    }
  }, [refreshComments, fetchComments]);

  const sortedGroupedComments = useMemo(() => {
    const groupedComments = groupCommentsByDate(comments);
    return Object.entries(groupedComments).sort(([dateA], [dateB]) => {
      return DateUtils.diff(dateB, dateA);
    });
  }, [comments]);

  if (comments.length === 0) {
    return <EmptyScreen message='No comments yet' Icon={ChatBubbleOvalLeftIcon} />;
  }

  return (
    <div className='px-4'>
      {sortedGroupedComments.map(([date, dateComments]) => (
        <div key={date} className='mb-8'>
          <h3 className='text-lnds-blue mb-4'>{formatDateSection(date)}</h3>
          <div className='space-y-4'>
            {dateComments.map((comment) => (
              <div key={comment.id} className='flex flex-col'>
                <div className='flex items-start space-x-3'>
                  <div className='flex-shrink-0'>
                    <InitialsAvatar name={comment.author} showTooltip={true} />
                  </div>
                  <div className='flex-1'>
                    <div className='flex items-baseline justify-between mb-1 label-lnds-color'>
                      <div className='flex space-x-2'>
                        <span className='font-medium'>{comment.author}</span>
                        <span className='text-xs'>{DateUtils.formatTime(comment.timestamp)}</span>
                      </div>
                    </div>
                    <div className='relative rounded-lg p-3 border border-lnds-color'>
                      {shouldAllowDelete(dataset.status, canDeleteComments) && (
                        <div className='absolute top-3 right-3'>
                          <ConfirmableActionButton
                            onConfirm={() => handleDeleteComment(comment.id)}
                            action='delete'
                          />
                        </div>
                      )}
                      <p className='text-lnds-color whitespace-pre-wrap'>{comment.content}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default CommentList;
