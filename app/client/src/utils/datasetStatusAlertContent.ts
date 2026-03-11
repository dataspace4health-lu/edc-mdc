import { createElement, type ReactNode } from "react";
import PublishedDatasetToastBody from "../components/alerts/PublishedDatasetToastBody";

export interface DatasetStatusAlertContent {
  title: string;
  body: ReactNode;
  message: string;
}

const formatStatus = (status: string): string =>
  status
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

const transitionBodies: Record<string, ReactNode> = {
  "DRAFT->COMPLETED":
    "A user with permission to validate has been notified and can now review this dataset.",
  "COMPLETED->VALIDATED":
    "A user with permission to approve has been notified and can now review this dataset.",
  "VALIDATED->APPROVED":
    "A user with permission to publish has been notified and can now publish this dataset.",
  "APPROVED->PUBLISHED": createElement(PublishedDatasetToastBody),
  "PUBLISHED->APPROVED":
    "The dataset has been unpublished and returned to Approved. A publisher can publish it again when ready.",
  "VALIDATED->INTERNAL_ONLY":
    "The dataset is now marked as Internal Only. To publish it, move it back to Approved.",
  "APPROVED->INTERNAL_ONLY":
    "The dataset is now marked as Internal Only. To publish it, move it back to Approved.",
  "INTERNAL_ONLY->APPROVED":
    "The dataset has been restored to Approved. A user with permission to publish has been notified and can now publish this dataset.",
  "PUBLISHED->DEPRECATED": "The dataset has been deprecated and marked as no longer current.",
  "INTERNAL_ONLY->DEPRECATED": "The dataset has been deprecated and marked as no longer current.",
  "COMPLETED->DRAFT":
    "The dataset has been moved back to Draft and the creator has been notified so they can edit.",
  "VALIDATED->DRAFT":
    "The dataset has been moved back to Draft and the creator has been notified so they can edit.",
  "APPROVED->DRAFT":
    "The dataset has been moved back to Draft and the creator has been notified so they can edit.",
  "PUBLISHED->DRAFT":
    "The dataset has been moved back to Draft and the creator has been notified so they can edit.",
};

export const getDatasetStatusAlertContent = (
  newStatus: string,
  previousStatus?: string,
): DatasetStatusAlertContent => {
  const formattedNewStatus = formatStatus(newStatus);
  if (!previousStatus) {
    const title = `Status changed to ${formattedNewStatus}`;
    return {
      title,
      body: `The dataset status is now ${formattedNewStatus}.`,
      message: title,
    };
  }

  const formattedOldStatus = formatStatus(previousStatus);
  const title = `Status changed from ${formattedOldStatus} to ${formattedNewStatus}`;
  const key = `${previousStatus}->${newStatus}`;
  const body = transitionBodies[key] ?? `The dataset status is now ${formattedNewStatus}.`;

  return { title, body, message: title };
};
