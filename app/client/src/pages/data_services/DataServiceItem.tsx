import { ServerIcon, GlobeAltIcon, InformationCircleIcon } from "@heroicons/react/24/solid";
import { ResourceDataService } from "../../types";

interface DataServiceItemProps {
  service: ResourceDataService;
  isSelected: boolean;
  clickable?: boolean;
  onClick: () => void;
}

const DataServiceItem: React.FC<DataServiceItemProps> = ({
  service,
  isSelected,
  onClick,
  clickable = true,
}) => {
  return (
    <div
      className={`group transition-all duration-200 ${
        clickable ? "hover:border-l-4 border-b hover:border-l-lnds-dark-blue cursor-pointer" : ""
      } ${
        isSelected
          ? "border-l-4 border-l-lnds-purple dark:border-b-gray-700 bg-gradient-to-r from-lnds-purple/10 to-transparent"
          : "border-l-transparent border-lnds-color"
      }`}
      onClick={onClick}
    >
      <div className='p-5 transition-all duration-200'>
        <div className='flex items-center justify-between mb-3'>
          <div className='flex items-center'>
            <div className='p-2 rounded-lg mr-3 border border-lnds-color text-lnds-color transition-colors duration-200'>
              <ServerIcon className='h-5 w-5' />
            </div>
            <h3 className='font-semibold text-lg heading-lnds-color transition-colors duration-200'>
              {service.title}
            </h3>
          </div>
          <span className='px-3 py-1 rounded-full text-xs font-medium flex items-center bg-lnds-purple text-white transition-colors duration-200'>
            {service.endpoints.length} endpoint{service.endpoints.length !== 1 ? "s" : ""}
          </span>
        </div>

        {/* Endpoints list */}
        <div className='ml-12 space-y-2'>
          {service.endpoints.slice(0, 2).map((endpoint, index) => (
            <div
              key={`${endpoint.endpoint_url}-${index}`}
              className='rounded-md p-2 transition-all duration-200 border border-lnds-color'
            >
              <div className='flex items-start'>
                <GlobeAltIcon className='h-4 w-4 mt-0.5 mr-2 flex-shrink-0 text-lnds-color' />
                <div className='overflow-hidden'>
                  <p className='text-sm font-medium truncate text-lnds-color'>
                    {endpoint.endpoint_url}
                  </p>

                  {endpoint.endpoint_description && (
                    <div className='flex items-start mt-1'>
                      <InformationCircleIcon className='h-3.5 w-3.5 text-gray-400 mt-0.5 mr-1.5 flex-shrink-0' />
                      <p className='text-xs text-gray-500 line-clamp-2'>
                        {endpoint.endpoint_description}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {service.endpoints.length > 2 && (
            <div className='text-xs font-medium pl-2 text-lnds-gray flex items-center'>
              <span className='inline-block w-4 h-0.5 bg-current mr-2'></span>
              {service.endpoints.length - 2} more endpoint
              {service.endpoints.length - 2 > 1 ? "s" : ""} available
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataServiceItem;
