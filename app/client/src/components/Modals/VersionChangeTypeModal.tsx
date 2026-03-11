import { useState } from "react";
import { DocumentDuplicateIcon, XMarkIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import { Modal } from "./Modal";

export type VersionChangeType = "METADATA_ONLY" | "UNDERLYING_DATA";

interface VersionChangeTypeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (changeType: VersionChangeType) => Promise<void> | void;
}

export function VersionChangeTypeModal({
  isOpen,
  onClose,
  onConfirm,
}: Readonly<VersionChangeTypeModalProps>) {
  const [selectedType, setSelectedType] = useState<VersionChangeType | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleClose = () => {
    if (isSubmitting) return;
    setSelectedType(null);
    onClose();
  };

  const handleConfirm = async () => {
    if (!selectedType || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onConfirm(selectedType);
      setSelectedType(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal.Frame open={isOpen} onClose={handleClose}>
      <Modal.Head className='flex items-center' onClose={handleClose}>
        <DocumentDuplicateIcon className='h-6 w-6 mr-2 icon-lnds-color' />
        Create Dataset Version
      </Modal.Head>
      <Modal.Body>
        <div className='space-y-5'>
          <p className='text-sm text-lnds-color'>What changed in this new version?</p>

          <fieldset className='space-y-3 border-none p-0 m-0'>
            <legend className='sr-only'>Version change type</legend>

            <label className='flex items-start gap-3 p-3 rounded border border-lnds-color cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700'>
              <input
                type='radio'
                name='version-change-type'
                value='METADATA_ONLY'
                checked={selectedType === "METADATA_ONLY"}
                onChange={() => setSelectedType("METADATA_ONLY")}
                disabled={isSubmitting}
                className='mt-1'
              />
              <span>
                <span className='block font-medium text-lnds-color'>Metadata only</span>
                <span className='block text-sm text-lnds-color'>
                  Only metadata changed. Version and Version Notes fields are optional.
                </span>
              </span>
            </label>

            <label className='flex items-start gap-3 p-3 rounded border border-lnds-color cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700'>
              <input
                type='radio'
                name='version-change-type'
                value='UNDERLYING_DATA'
                checked={selectedType === "UNDERLYING_DATA"}
                onChange={() => setSelectedType("UNDERLYING_DATA")}
                disabled={isSubmitting}
                className='mt-1'
              />
              <span>
                <span className='block font-medium text-lnds-color'>Data and metadata changed</span>
                <span className='block text-sm text-lnds-color'>
                  Underlying data changed, and metadata changed. Version and Version Notes fields
                  are required.
                </span>
              </span>
            </label>
          </fieldset>

          <div className='flex justify-end gap-2'>
            <Button
              label='Cancel'
              Icon={XMarkIcon}
              btnType='secondary'
              onClick={handleClose}
              className={isSubmitting ? "opacity-50 pointer-events-none" : ""}
            />
            <Button
              label='Create Draft Version'
              Icon={DocumentDuplicateIcon}
              btnType='primary'
              onClick={handleConfirm}
              className={!selectedType || isSubmitting ? "opacity-50 pointer-events-none" : ""}
            />
          </div>
        </div>
      </Modal.Body>
    </Modal.Frame>
  );
}
