import { useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  CircleStackIcon,
  TableCellsIcon,
  LinkIcon,
  BuildingOfficeIcon,
  ArrowRightOnRectangleIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ShareIcon,
} from "@heroicons/react/24/solid";
import { LeftSidebar, Button } from "@lnds-lu/design-system";
import { Modal } from "./Modals/Modal";
import { useLeftSidebar } from "../context/LeftSidebarContext";
import { useUnsaved } from "../context/UnSavedChangesContext";

const getLinkClass = (isSelected: boolean) => {
  return `flex items-center text-lg hover:bg-lnds-dark-blue hover:text-white px-4 py-2 rounded ${
    isSelected ? "bg-lnds-purple text-white" : "text-lnds-color"
  }`;
};

const NAV_ITEMS = [
  {
    id: `edit`,
    path: `edit`,
    label: "Edit Dataset",
    icon: CircleStackIcon,
    selectedKey: `Edit Dataset`,
  },
  {
    id: `distributions`,
    path: `distributions`,
    label: "Distributions",
    icon: ShareIcon,
    selectedKey: `Distributions`,
  },
  {
    id: `dictionaries`,
    path: `dictionaries`,
    label: "Data Dictionary",
    icon: TableCellsIcon,
    selectedKey: `Data Dictionary`,
  },
  {
    id: `relations`,
    path: `relations`,
    label: "Dataset Relations",
    icon: LinkIcon,
    selectedKey: `Relations`,
  },
  {
    id: `qualified-attributions`,
    path: `qualified-attributions`,
    label: "Qualified Attributions",
    icon: BuildingOfficeIcon,
    selectedKey: `Qualified Attributions`,
  },
] as const;

interface LeftSidebarWithLinksProps {
  datasetId: number;
  datasetTitle: string;
  selected: string;
}

export function LeftSidebarWithLinks(props: Readonly<LeftSidebarWithLinksProps>) {
  const { datasetId, datasetTitle, selected } = props;
  const navigate = useNavigate();
  const { isSidebarOpen, setSidebarOpen } = useLeftSidebar();
  const { isUnSaved, setIsUnSaved } = useUnsaved();

  const [pendingPath, setPendingPath] = useState<string | null>(null);

  const handleLinkClick = useCallback(
    (e: React.MouseEvent, to: string) => {
      if (isUnSaved) {
        e.preventDefault();
        setPendingPath(to);
      } else {
        setSidebarOpen(false);
        navigate(to);
      }
    },
    [isUnSaved, setSidebarOpen, navigate],
  );

  const confirmLeave = useCallback(() => {
    if (!pendingPath) return;
    setIsUnSaved(false);
    setSidebarOpen(false);
    navigate(pendingPath);
    setPendingPath(null);
  }, [pendingPath, setIsUnSaved, setSidebarOpen, navigate]);

  const cancelLeave = useCallback(() => {
    setPendingPath(null);
  }, []);

  return (
    <>
      <LeftSidebar isOpen={isSidebarOpen}>
        <h2 className='text-base lg:text-md font-serif text-lnds-color py-4 flex flex-col items-center justify-center mb-4 border-b border-lnds-color'>
          <CircleStackIcon className='h-12 w-12 lg:h-16 lg:w-16 label-lnds-color mb-2' />
          <span className='text-center'>{datasetTitle}</span>
        </h2>
        <nav className='space-y-2 p-2' role='navigation' aria-label='Dataset navigation'>
          {NAV_ITEMS.map(({ id, path, label, icon: Icon, selectedKey }) => {
            const to = `/datasets/${datasetId}/${path}`;
            return (
              <Link
                key={id}
                to={to}
                className={getLinkClass(selected === selectedKey)}
                onClick={(e) => handleLinkClick(e, to)}
                aria-current={selected === selectedKey ? `page` : undefined}
              >
                <Icon className='h-6 w-6 mr-2' aria-hidden='true' />
                {label}
              </Link>
            );
          })}
        </nav>
      </LeftSidebar>
      <Modal.Frame
        open={!!pendingPath}
        onClose={cancelLeave}
        className='max-w-md mx-auto rounded-2xl overflow-hidden shadow-xl'
        aria-labelledby='unsaved-changes-title'
        aria-describedby='unsaved-changes-description'
      >
        <Modal.Body className='text-center py-12 px-8'>
          <div className='flex flex-col items-center space-y-6'>
            <div className='relative' aria-label='Warning'>
              <div className='w-20 h-20 bg-lnds-purple/20 rounded-full flex items-center justify-center shadow-lg'>
                <ExclamationTriangleIcon className='w-12 h-12 text-lnds-purple' />
              </div>
            </div>
            <div className='space-y-4 max-w-sm'>
              <h2 id='unsaved-changes-title' className='text-2xl font-bold label-lnds-color'>
                Unsaved Changes
              </h2>

              <div className='bg-lnds-purple/10 border-l-4 border-lnds-purple p-4 rounded-r-lg'>
                <p id='unsaved-changes-description' className='text-lnds-color text-base'>
                  You have <span className='font-semibold'>unsaved changes</span> that will be lost
                  if you leave now.
                </p>
              </div>

              <p className='text-lnds-color text-sm'>Continue anyway?</p>
            </div>
            <fieldset className='flex space-x-3 pt-2 border-none p-0 m-0'>
              <legend className='sr-only'>Navigation options</legend>
              <Button
                btnType='secondary'
                label='Stay'
                Icon={XMarkIcon}
                onClick={cancelLeave}
                className='px-6 py-2'
                aria-describedby='stay-button-description'
              />
              <span id='stay-button-description' className='sr-only'>
                Cancel navigation and stay on current page
              </span>

              <Button
                btnType='danger'
                label='Leave'
                Icon={ArrowRightOnRectangleIcon}
                onClick={confirmLeave}
                className='px-6 py-2'
                aria-describedby='leave-button-description'
              />
              <span id='leave-button-description' className='sr-only'>
                Discard changes and navigate away
              </span>
            </fieldset>
          </div>
        </Modal.Body>
      </Modal.Frame>
    </>
  );
}
