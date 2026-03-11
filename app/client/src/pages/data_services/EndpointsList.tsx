import { Button, InputField, TextArea, Card } from "@lnds-lu/design-system";
import { TrashIcon } from "@heroicons/react/24/solid";
import { motion, AnimatePresence } from "framer-motion";
import { ResourceDataServiceEndpoint } from "../../types";
import AddButton from "../../components/AddButton";

interface EndpointsListProps {
  endpoints: ResourceDataServiceEndpoint[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formErrors: any;
  onAddEndpoint: () => void;
  onDeleteEndpoint: (index: number) => void;
}

const EndpointsList: React.FC<EndpointsListProps> = ({
  endpoints,
  formErrors,
  onAddEndpoint,
  onDeleteEndpoint,
}) => {
  return (
    <div>
      <div className='flex justify-between items-center mb-4'>
        <h3 className='text-lg font-semibold heading-lnds-color'>
          Endpoints{" "}
          <span className='text-sm bg-lnds-purple text-white px-2 py-0.5 rounded-full ml-2'>
            {endpoints.length}
          </span>
        </h3>
      </div>

      {formErrors?.endpoints && (
        <div className='text-lnds-red mb-4'>
          {formErrors.endpoints.map((error: string, index: number) => (
            <p key={`error-${index}-${error.slice(0, 20)}`}>{error}</p>
          ))}
        </div>
      )}

      <AnimatePresence>
        {endpoints.map((endpoint, index) => (
          <motion.div
            key={`endpoint-${index}-${endpoint.endpoint_url || "new"}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className='mb-4 p-4 border border-lnds-color'>
              <div className='flex justify-between items-start mb-3'>
                <h4 className='text-md font-medium'>Endpoint #{index + 1}</h4>
                <Button
                  btnType='transparent'
                  className='p-1 text-lnds-red'
                  Icon={TrashIcon}
                  onClick={() => onDeleteEndpoint(index)}
                />
              </div>

              <div className='flex flex-col gap-4'>
                <InputField
                  name={`endpoints[${index}].endpoint_url`}
                  label='URL'
                  info='The endpoint URL (e.g., https://api.example.com/data)'
                  defaultValue={endpoint.endpoint_url}
                  type='url'
                  required
                  errors={formErrors[`endpoints[${index}].endpoint_url`]}
                />
                <TextArea
                  name={`endpoints[${index}].endpoint_description`}
                  label='Description'
                  info='A brief description of what this endpoint provides'
                  defaultValue={endpoint.endpoint_description || ""}
                  errors={formErrors[`endpoints[${index}].endpoint_description`]}
                />
              </div>
            </Card>
          </motion.div>
        ))}
      </AnimatePresence>
      <AddButton label='Add Endpoint' currentCount={endpoints.length} onAdd={onAddEndpoint} />
    </div>
  );
};

export default EndpointsList;
