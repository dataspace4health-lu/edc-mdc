import { useState, useEffect, useRef } from "react";
import { ChevronDownIcon } from "@heroicons/react/24/solid";

type DatasetDetailsTabProps = {
  tabList: string[];
  currentTab: string;
  setCurrentTab: (tab: string) => void;
};

export const DatasetDetailsTab = ({
  tabList,
  currentTab,
  setCurrentTab,
}: DatasetDetailsTabProps) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [maxVisibleTabs, setMaxVisibleTabs] = useState(5);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        // mobile breakpoint
        setMaxVisibleTabs(3);
      } else {
        setMaxVisibleTabs(5);
      }
    };

    handleResize(); // Set initial value
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const shouldUseDropdown = tabList.length > 6;
  const visibleTabs = shouldUseDropdown ? tabList.slice(0, maxVisibleTabs) : tabList;
  const hiddenTabs = shouldUseDropdown ? tabList.slice(maxVisibleTabs) : [];
  const hasHiddenTabs = hiddenTabs.length > 0;

  const currentTabIsHidden = hiddenTabs.includes(currentTab);

  useEffect(() => {
    if (tabList.length > 0 && !tabList.includes(currentTab)) {
      setCurrentTab(tabList[0]);
    }
  }, [currentTab, setCurrentTab, tabList]);

  const handleTabClick = (tab: string) => {
    setCurrentTab(tab);
    setShowDropdown(false);
  };

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  return (
    <div className='border-b border-lnds-color mb-4'>
      <div className='flex'>
        {/* Visible tabs */}
        <ul className='flex text-center text-lnds-color'>
          {visibleTabs.map((tab) => (
            <li key={tab}>
              <button
                className={`inline-block p-4 rounded-t-lg hover:bg-lnds-dark-blue hover:text-white whitespace-nowrap transition-colors duration-200 ${
                  currentTab === tab ? "bg-lnds-purple text-white" : ""
                }`}
                onClick={(ev) => {
                  ev.preventDefault();
                  handleTabClick(tab);
                }}
              >
                {tab}
              </button>
            </li>
          ))}
        </ul>

        {/* More dropdown */}
        {hasHiddenTabs && (
          <div className='relative' ref={dropdownRef}>
            <button
              className={`inline-flex items-center gap-1 p-4 rounded-t-lg hover:bg-lnds-dark-blue hover:text-white transition-colors duration-200 text-lnds-color ${
                currentTabIsHidden ? "bg-lnds-purple text-white" : ""
              }`}
              onClick={toggleDropdown}
              aria-expanded={showDropdown}
              aria-haspopup='true'
            >
              <span className={`${currentTabIsHidden ? "text-white" : ""}`}>More</span>
              <ChevronDownIcon className={`w-4 h-4 ${currentTabIsHidden ? "text-white" : ""}`} />
            </button>

            {/* Dropdown menu */}
            {showDropdown && (
              <div className='absolute top-full left-0 right-0 section-lnds-color border border-lnds-color rounded-b-lg z-50 min-w-48'>
                <ul className='py-1'>
                  {hiddenTabs.map((tab) => (
                    <li key={tab}>
                      <button
                        className={`block px-4 py-3 text-left hover:bg-lnds-dark-blue hover:text-white transition-colors duration-200 ${
                          currentTab === tab ? "bg-lnds-purple text-white" : "text-lnds-color"
                        }`}
                        onClick={(ev) => {
                          ev.preventDefault();
                          handleTabClick(tab);
                        }}
                      >
                        {tab}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
