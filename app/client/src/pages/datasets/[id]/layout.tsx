import { useLoaderData } from "react-router";
import Breadcrumb from "../../../components/Breadcrumb";
import { RightSidebar } from "../../../components/RightSidebar";
import { LeftSidebarWithLinks } from "../../../components/LeftSidebarWithLinks";
import { Outlet, useLocation } from "react-router-dom";
import { ResourceDatasetType } from "../../../types";
import IncorrectRelationFlashMessage from "../../../components/IncorrectRelationFlashMessage";
import { useState } from "react";

export default function DatasetLayout() {
  const dataset = useLoaderData() as ResourceDatasetType;
  const path = useLocation().pathname;
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const getSelectedSection = () => {
    if (path.includes("distributions")) {
      return "Distributions";
    } else if (path.includes("dictionaries")) {
      return "Data Dictionary";
    } else if (path.includes("relations")) {
      return "Relations";
    } else if (path.includes("qualified-attributions")) {
      return "Qualified Attributions";
    } else {
      return "Edit Dataset";
    }
  };

  const selected = getSelectedSection();

  const triggerActivityLogRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className='relative min-h-screen'>
      {dataset && (
        <LeftSidebarWithLinks
          datasetTitle={dataset.title}
          datasetId={dataset.id}
          selected={selected}
        />
      )}
      <div
        className={`p-4 transition-all duration-300 ${
          isRightSidebarOpen ? "lg:mr-[320px]" : ""
        } lg:ml-[312px]`}
      >
        {dataset && <Breadcrumb location={selected} firstLevelLink='/' firstLevel='Home' />}
        <IncorrectRelationFlashMessage dataset={dataset} />
        <Outlet context={{ dataset, triggerActivityLogRefresh }} />
      </div>

      {dataset && (
        <RightSidebar
          entityId={dataset.id}
          entityType='dataset'
          className='border-l border-lnds-color'
          defaultIsOpen={true}
          onSidebarToggle={setIsRightSidebarOpen}
          refreshTrigger={refreshTrigger}
        />
      )}
    </div>
  );
}
