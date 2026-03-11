import { appAlerts } from "../utils/appAlerts";
import {
  DocumentCheckIcon,
  CheckCircleIcon,
  ClipboardDocumentCheckIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  LockClosedIcon,
  XMarkIcon,
  ArchiveBoxIcon,
  CloudArrowUpIcon,
  ArrowUturnLeftIcon,
  InformationCircleIcon,
} from "@heroicons/react/24/solid";
import DatasetStatus from "./DatasetStatus";
import NextStepsButton from "./NextStepsButton";
import { Button, useAlert } from "@lnds-lu/design-system";
import { TextArea } from "@lnds-lu/design-system";
import { ResourceDatasetType, DatasetStatusEnum } from "../types";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useAuthenticSourceLabels } from "../context/AuthenticSourceLabelsContext";
import { useDatasets } from "../context/DatasetsContext";
import { useOnTrigger } from "../utils/updateDatasetStatusButtonEvents";

interface UpdateDatasetStatusButtonProps {
  dataset: ResourceDatasetType;
  updateDatasetLocally: (dataset: ResourceDatasetType) => void;
  onCommentsRefresh: () => void;
  onFrontOfficeUploadStart: () => void;
  setShowApprovalWorkflow: (show: boolean) => void;
  metadataAccuracyReviewed: boolean;
  publicationDecisionMade: boolean;
  onResetApprovalWorkflow?: () => void;
}

export default function UpdateDatasetStatusButton(props: Readonly<UpdateDatasetStatusButtonProps>) {
  const {
    dataset,
    updateDatasetLocally,
    onCommentsRefresh,
    onFrontOfficeUploadStart,
    setShowApprovalWorkflow,
    metadataAccuracyReviewed,
    publicationDecisionMade,
    onResetApprovalWorkflow,
  } = props;
  const { setAlert } = useAlert();
  const [selectedTrigger, setSelectedTrigger] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  const [nextStepsOpenSignal, setNextStepsOpenSignal] = useState(0);
  const [nextStepsErrors, setNextStepsErrors] = useState<string[]>([]);
  const { user } = useAuth();
  const { updateDatasetStatus: updateDatasetStatusOnList } = useDatasets();
  const {
    showSaveEntriesBtn,
    showSaveLabelAssignmentsBtn,
    canAssignLabels,
    canReviewNoAuthenticSource,
    saveLabels,
    saveEntries,
    completeReview,
  } = useAuthenticSourceLabels();

  const updateSelectedTrigger = (trigger: string | null) => {
    setSelectedTrigger(trigger);
    if (trigger === "approve" && user?.feature_options?.enable_multi_tenants) {
      onResetApprovalWorkflow?.();
      setShowApprovalWorkflow(true);
    } else {
      setShowApprovalWorkflow(false);
    }
  };

  const frontOfficeUploadBtn =
    dataset.status === DatasetStatusEnum.PUBLISHED &&
    user?.feature_options.enable_upload_datasets_to_front_office &&
    user?.permissions?.includes("datasets:status-change:publish") ? (
      <Button
        Icon={CloudArrowUpIcon}
        btnType='primary'
        className='h-10 bg-pink-600 hover:bg-lnds-dark-blue'
        label='Push to Front Office'
        onClick={onFrontOfficeUploadStart}
      />
    ) : null;

  const onTrigger = useOnTrigger({
    user,
    dataset,
    comment,
    setComment,
    updateDatasetLocally,
    updateDatasetStatusOnList,
    onCommentsRefresh,
    setAlert,
    updateSelectedTrigger,
    onFrontOfficeUploadStart,
    openNextSteps: (errors = []) => {
      setNextStepsErrors(errors);
      setNextStepsOpenSignal((prev) => prev + 1);
    },
  });

  const handleCancel = () => {
    updateSelectedTrigger(null);
    setComment("");
    onResetApprovalWorkflow?.();
  };

  const approveLabel = user?.feature_options?.enable_multi_tenants
    ? "Begin Approval Process"
    : "Approve Dataset";
  const getButtonConfig = (trigger: string) => {
    const configs = {
      complete: {
        label: "Submit Dataset",
        Icon: CheckCircleIcon,
        className: "h-10 bg-violet-700",
      },
      back_to_draft: {
        label: "Revert to Draft",
        Icon: DocumentCheckIcon,
        className: "h-10",
        btnType: "secondary" as const,
      },
      validate: {
        label: "Validate Dataset",
        Icon: ClipboardDocumentCheckIcon,
        className: "h-10 bg-teal-700",
      },
      approve: {
        label: approveLabel,
        Icon: ShieldCheckIcon,
        className: "h-10 bg-green-700",
      },
      mark_internal: {
        label: "Mark as Internal",
        Icon: LockClosedIcon,
        className: "h-10 bg-yellow-700",
      },
      restore_approved: {
        label: "Approve for Publishing",
        Icon: ArrowUturnLeftIcon,
        className: "h-10 bg-green-700",
      },
      publish: {
        label: "Publish Dataset",
        Icon: GlobeAltIcon,
        className: "h-10 bg-blue-700",
      },
      unpublish: {
        label: "Unpublish",
        Icon: GlobeAltIcon,
        className: "h-10 bg-green-700",
      },
      deprecate: {
        label: "Deprecate",
        Icon: ArchiveBoxIcon,
        className: "h-10 bg-gray-700",
      },
    };
    return configs[trigger as keyof typeof configs];
  };

  const submitAuthenticSourceBtn =
    canAssignLabels(dataset.status, user) && showSaveLabelAssignmentsBtn ? (
      <Button
        Icon={ShieldCheckIcon}
        btnType='primary'
        label='Apply Label Assignments'
        onClick={async () => {
          await saveEntries(dataset.id);
          await saveLabels(dataset.id);
          setAlert(appAlerts.authenticSourceLabeled());
        }}
      />
    ) : showSaveEntriesBtn ? (
      <Button
        Icon={ShieldCheckIcon}
        btnType='primary'
        label='Confirm Authentic Sources'
        onClick={async () => {
          await saveEntries(dataset.id);
          setAlert(appAlerts.authenticSourceEntriesSaved());
        }}
      />
    ) : canReviewNoAuthenticSource(dataset, user) ? (
      <Button
        Icon={ShieldCheckIcon}
        btnType='primary'
        label='Contains No Authentic Sources'
        onClick={async () => {
          await completeReview(dataset.id);
          setAlert(appAlerts.authenticSourceMarkedNoSources());
        }}
      />
    ) : null;

  const nextTriggers = (dataset.status_triggers || []).filter(
    (trigger) => !(trigger === "mark_internal" && dataset.status === DatasetStatusEnum.VALIDATED),
  );

  const getAwaitingMessage = () => {
    switch (dataset.status) {
      case DatasetStatusEnum.COMPLETED:
        return "Awaiting validation";
      case DatasetStatusEnum.VALIDATED:
        return "Awaiting approval";
      case DatasetStatusEnum.APPROVED:
        return "Awaiting publication";
      default:
        return null;
    }
  };

  const awaitingMessage = getAwaitingMessage();
  const canConfirmApprove = metadataAccuracyReviewed && publicationDecisionMade;
  const canMarkInternalOnly = metadataAccuracyReviewed && !publicationDecisionMade;

  if (nextTriggers.length === 0) {
    return (
      <div className='py-4 px-6 border-t my-4 border-t border-lnds-color flex justify-between items-center'>
        <DatasetStatus dataset={dataset} />
        <div className='flex items-center space-x-3'>
          {awaitingMessage && (
            <div className='flex items-center space-x-2 border border-lnds-green rounded-lg px-4 py-2'>
              <InformationCircleIcon className='h-5 w-5 text-lnds-green' />
              <span className='text-sm text-lnds-color font-medium'>{awaitingMessage}</span>
            </div>
          )}
          {submitAuthenticSourceBtn}
          {frontOfficeUploadBtn}
          <NextStepsButton
            dataset={dataset}
            forceOpenSignal={nextStepsOpenSignal}
            forcedErrors={nextStepsErrors}
          />
        </div>
      </div>
    );
  }

  return (
    <div className='section-lnds-color flex items-center py-4 px-6 border-t border-lnds-color flex-shrink-0'>
      {!selectedTrigger && <DatasetStatus dataset={dataset} />}
      <div className='flex flex-grow items-end justify-end space-x-4'>
        {selectedTrigger && (
          <div className='flex-grow'>
            <div className='space-y-1'>
              <TextArea
                name='comment'
                label='Comment (optional)'
                info='Add an optional comment before proceeding'
                placeholder='Add your comment here...'
                defaultValue={comment}
                onChange={setComment}
              />
            </div>
          </div>
        )}

        {selectedTrigger ? (
          selectedTrigger === "approve" && user?.feature_options?.enable_multi_tenants ? (
            <div className='flex flex-col gap-2'>
              <div className='flex flex-wrap justify-end gap-2'>
                <Button
                  Icon={XMarkIcon}
                  btnType='secondary'
                  className='h-10 w-full sm:w-auto'
                  label='Cancel'
                  onClick={handleCancel}
                />
                {nextTriggers.includes("back_to_draft") && (
                  <Button
                    Icon={ArrowUturnLeftIcon}
                    btnType='secondary'
                    className='h-10 w-full sm:w-auto'
                    label='Revert to Draft'
                    onClick={() => onTrigger("back_to_draft")}
                  />
                )}
              </div>
              <div className='flex flex-wrap justify-end gap-2'>
                <Button
                  Icon={ShieldCheckIcon}
                  btnType='primary'
                  className={`h-10 w-full sm:w-auto bg-green-700 ${
                    canConfirmApprove ? "" : "opacity-50 cursor-not-allowed pointer-events-none"
                  }`}
                  label='Approve for Publishing'
                  onClick={canConfirmApprove ? () => onTrigger("approve") : undefined}
                />
                <Button
                  Icon={LockClosedIcon}
                  btnType='primary'
                  className={`h-10 w-full sm:w-auto bg-yellow-700 ${
                    canMarkInternalOnly ? "" : "opacity-50 cursor-not-allowed pointer-events-none"
                  }`}
                  label='Mark as Internal Only'
                  onClick={canMarkInternalOnly ? () => onTrigger("mark_internal") : undefined}
                />
              </div>
            </div>
          ) : (
            <div className='flex space-x-2'>
              <Button
                Icon={XMarkIcon}
                btnType='secondary'
                className='h-10'
                label='Cancel'
                onClick={handleCancel}
              />
              <Button
                {...getButtonConfig(selectedTrigger)}
                label={`${getButtonConfig(selectedTrigger)?.label}`}
                onClick={() => onTrigger(selectedTrigger)}
              />
            </div>
          )
        ) : (
          <div className='flex space-x-2'>
            {nextTriggers.map((trigger) => {
              const config = getButtonConfig(trigger);
              return (
                <Button key={trigger} {...config} onClick={() => updateSelectedTrigger(trigger)} />
              );
            })}
            {submitAuthenticSourceBtn}
            {frontOfficeUploadBtn}
            <NextStepsButton
              dataset={dataset}
              forceOpenSignal={nextStepsOpenSignal}
              forcedErrors={nextStepsErrors}
            />
          </div>
        )}
      </div>
    </div>
  );
}
