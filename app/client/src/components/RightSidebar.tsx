import { ClockIcon } from "@heroicons/react/24/solid";
import { useEffect, useRef, useState } from "react";
import { ActivityLogList } from "./Modals/ActivityLogList";
import { ResourceOrganisation, ResourceRoleType } from "../types";

interface RightSidebarProps {
  entityId?: number | null;
  entityType: "dataset" | "organisation" | "user_assignment" | "authentic_source_label";
  className?: string;
  onSidebarToggle?: (isOpen: boolean) => void;
  defaultIsOpen?: boolean;
  refreshTrigger?: number;
  organisations?: ResourceOrganisation[];
  roles?: ResourceRoleType[];
}

export function RightSidebar(props: Readonly<RightSidebarProps>) {
  const {
    entityId = null,
    entityType,
    className,
    onSidebarToggle,
    defaultIsOpen = true,
    refreshTrigger,
    organisations = [],
    roles = [],
  } = props;
  const [showSidebar, setShowSidebar] = useState(defaultIsOpen);
  const [transitionEnabled, setTransitionEnabled] = useState(true);

  const previousWidth = useRef(window.innerWidth);

  useEffect(() => {
    const updateWidth = () => {
      const width = document.documentElement.clientWidth;

      if (previousWidth.current > 768 && width <= 768) {
        setTransitionEnabled(false);
      } else {
        setTransitionEnabled(true);
      }

      previousWidth.current = width;
    };
    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  const handleToggle = () => {
    const newState = !showSidebar;
    setShowSidebar(newState);
    onSidebarToggle?.(newState);
  };

  return (
    <aside
      className={`fixed md:fixed lg:fixed top-0 right-0 h-screen bg-white pt-16
        ${showSidebar ? "translate-x-0" : "translate-x-full"} 
        ${transitionEnabled ? "transition-transform duration-300 ease-in-out" : ""} 
        ${className}`}
    >
      <button
        className='absolute -left-12 top-24 rounded-l-lg border border-lnds-color section-lnds-color w-12 py-2 flex flex-col items-center justify-center hover:bg-lnds-dark-blue group'
        onClick={handleToggle}
        aria-label={showSidebar ? "Hide activity log" : "Show activity log"}
      >
        <ClockIcon className='h-6 w-6 fill-lnds-gray dark:fill-white group-hover:fill-white' />
        <span className='text-xs text-lnds-gray dark:text-white group-hover:text-white mt-0.5'>
          Log
        </span>
      </button>
      <div className={`section-lnds-color text-white h-full overflow-y-auto w-[320px] p-6`}>
        <div className='rounded-t flex flex-row items-center mb-8'>
          <ClockIcon className='h-7 w-7 text-lnds-blue mr-2' />
          <h1 className='text-xl md:text-2xl text-lnds-blue flex items-center font-bold'>
            Activity Log
          </h1>
        </div>
        <div className='pb-20 md:pb-0'>
          <ActivityLogList
            entityId={entityId}
            entityType={entityType}
            refreshTrigger={refreshTrigger}
            organisations={organisations}
            roles={roles}
          />
        </div>
      </div>
    </aside>
  );
}
