import { useState, useEffect } from "react";
import { appAlerts } from "../../utils/appAlerts";
import { Button, Card, CardHeading } from "@lnds-lu/design-system";
import {
  PlusCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  MagnifyingGlassIcon,
  ServerIcon,
} from "@heroicons/react/24/solid";
import { useLoaderData } from "react-router";
import EmptyScreen from "../../components/EmptyScreen";
import { useAlert, SearchInput } from "@lnds-lu/design-system";
import { AnimatePresence } from "framer-motion";
import { ResourceDataService } from "../../types";
import DataServiceLoader from "./loader";
import DataServiceForm from "./DataServiceForm";
import DataServiceItem from "./DataServiceItem";
import { usePageTitle } from "../../hooks/usePageTitle";

const DataServiceManagement: React.FC = () => {
  usePageTitle("Data Services");
  const [isFormExpanded, setIsFormExpanded] = useState(false);
  const [current, setCurrent] = useState<ResourceDataService | null>(null);
  const [services, setServices] = useState<ResourceDataService[]>([]);
  const fetchedData = (useLoaderData() as Awaited<ReturnType<typeof DataServiceLoader>>) || [];
  const [searchTerm, setSearchTerm] = useState("");
  const { setAlert } = useAlert();
  const [formKey, setFormKey] = useState(0);

  useEffect(() => {
    if (fetchedData) {
      setServices(fetchedData);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = async (service: ResourceDataService) => {
    if (service.id) {
      try {
        setServices((prev) => prev.filter((s) => s.id !== service.id));
        setFormKey((prev) => prev + 1);
        setAlert(appAlerts.dataServiceDeleted());
        setCurrent(null);
      } catch (error) {
        // @ts-expect-error 'error' is of type 'unknown'
        if (error.status === 400) {
          setAlert(appAlerts.dataServiceDeleteBlockedInUse());
        } else {
          setAlert(appAlerts.dataServiceDeleteFailed());
        }
      }
    }
  };

  const handleServiceCreated = (newService: ResourceDataService) => {
    setServices((prev) => [newService, ...prev]);
    setCurrent(null);
    setFormKey((prev) => prev + 1);
    setIsFormExpanded(false);
    setAlert(appAlerts.dataServiceCreated());
  };

  const handleServiceUpdated = (updatedService: ResourceDataService) => {
    setServices((prev) =>
      prev.map((service) => (service.id === updatedService.id ? updatedService : service)),
    );
    setCurrent(null);
    setFormKey((prev) => prev + 1);
    setIsFormExpanded(false);
    setAlert(appAlerts.dataServiceUpdated());
  };

  const handleCancel = () => {
    setCurrent(null);
    setFormKey((prev) => prev + 1);
    setIsFormExpanded(false);
  };

  const filteredServices = services.filter(
    (service) =>
      service.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.endpoints.some(
        (endpoint) =>
          endpoint.endpoint_url.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (endpoint.endpoint_description &&
            endpoint.endpoint_description.toLowerCase().includes(searchTerm.toLowerCase())),
      ),
  );

  return (
    <div className='my-6 mx-6 max-w-2xl lg:max-w-4xl md:mx-auto'>
      <Card className='p-8' key={formKey}>
        <div
          className={`rounded-t flex flex-row justify-between items-center section-lnds-color ${
            isFormExpanded ? "mb-4" : ""
          }`}
        >
          <CardHeading
            label={`${current ? "Edit" : "Add"} Data Service`}
            Icon={PlusCircleIcon}
            className='flex'
          />
          {!current && (
            <Button
              btnType='transparent'
              label={isFormExpanded ? "Collapse Form" : "Expand Form"}
              onClick={() => setIsFormExpanded(!isFormExpanded)}
              Icon={isFormExpanded ? ChevronUpIcon : ChevronDownIcon}
            />
          )}
        </div>

        <AnimatePresence>
          {(isFormExpanded || current) && (
            <DataServiceForm
              currentService={current}
              onServiceCreated={handleServiceCreated}
              onServiceUpdated={handleServiceUpdated}
              onCancel={handleCancel}
              onDelete={handleDelete}
            />
          )}
        </AnimatePresence>
      </Card>

      <div className='mt-6'>
        <Card className='flex flex-col h-full px-0'>
          <div className='p-4 flex justify-between items-center'>
            <div className='flex items-center gap-2'>
              <ServerIcon className='h-5 w-5 heading-lnds-color' />
              <h2 className='text-2xl font-semibold heading-lnds-color'>
                Data Services{" "}
                <span className='text-sm bg-lnds-purple text-white px-2 py-0.5 rounded-full ml-2'>
                  {filteredServices.length}
                </span>
              </h2>
            </div>
            <Button
              Icon={PlusCircleIcon}
              label='New Service'
              onClick={() => {
                setCurrent(null);
                setIsFormExpanded(true);
                setFormKey((prev) => prev + 1);
              }}
            />
          </div>

          <div className='p-4 border-b border-lnds-color'>
            <div className='relative'>
              <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
                <MagnifyingGlassIcon className='h-4 w-4 text-gray-500' />
              </div>
              <SearchInput
                className='md:w-full'
                withoutBtn={true}
                placeholder='Search data services...'
                query={searchTerm}
                onSearch={setSearchTerm}
                size='small'
              />
            </div>
          </div>

          <div className='flex-grow overflow-y-auto' style={{ height: "calc(40vh)" }}>
            {filteredServices.length > 0 ? (
              <div>
                {filteredServices
                  .sort((a, b) => a.title.toLowerCase().localeCompare(b.title.toLowerCase()))
                  .map((service) => (
                    <DataServiceItem
                      key={service.id}
                      service={service}
                      isSelected={current?.id === service.id}
                      onClick={() => {
                        setIsFormExpanded(true);
                        setFormKey((prev) => prev + 1);
                        setCurrent(service);
                      }}
                    />
                  ))}
              </div>
            ) : (
              <div className='p-4'>
                <EmptyScreen message='No data services found' Icon={ServerIcon} />
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DataServiceManagement;
