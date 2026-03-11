import { ReactNode } from "react";
import { Modal } from "./Modal";
import { PencilIcon, ArrowLeftIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import DatasetCreatedAchievementModal from "./DatasetCreatedAchievementModal";

type PreviewModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onContinueEditing: () => void;
  onSaveDraft: () => Promise<void>;
  title: string;
  showAchievement?: boolean;
  children: ReactNode;
};

export const PreviewModal = ({
  isOpen,
  onClose,
  onContinueEditing,
  onSaveDraft,
  title,
  children,
  showAchievement = false,
}: PreviewModalProps) => {
  return (
    <>
      <Modal.Frame open={isOpen} onClose={onClose}>
        <Modal.Head className='flex items-center justify-between' onClose={onClose}>
          <div className='flex items-center'>{`Preview: ${title}`}</div>
        </Modal.Head>
        <Modal.Body className='max-h-[60vh]'>{children}</Modal.Body>
        <div className='sticky py-4 px-6 gap-3 flex justify-center md:justify-end items-center border-t my-4 border-t border-lnds-color'>
          <Button
            btnType='transparent'
            Icon={ArrowLeftIcon}
            label='Continue Editing'
            onClick={onContinueEditing}
          />
          <Button className='h-10' label='Save as Draft' onClick={onSaveDraft} Icon={PencilIcon} />
        </div>
      </Modal.Frame>
      <DatasetCreatedAchievementModal isOpen={showAchievement} title={title} />
    </>
  );
};
