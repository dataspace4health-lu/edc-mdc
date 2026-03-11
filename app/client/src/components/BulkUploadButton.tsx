import React, { useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { ArrowUpTrayIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";

export default function BulkUploadButton() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const onBulkUploadClick = () => {
    fileInputRef.current?.click();
  };
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    e.target.value = "";
    if (location.pathname !== "/datasets/bulk-upload") {
      navigate("/datasets/bulk-upload");

      setTimeout(() => {
        window.dispatchEvent(new CustomEvent("bulk-upload-file-selected", { detail: file }));
      }, 50);
    } else {
      window.dispatchEvent(new CustomEvent("bulk-upload-file-selected", { detail: file }));
    }
  };

  return (
    <>
      <input
        type='file'
        accept='.xlsx,.xlsm'
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
      <Button
        label='Upload Excel file'
        Icon={ArrowUpTrayIcon}
        onClick={onBulkUploadClick}
        className='mr-4'
      />
    </>
  );
}
