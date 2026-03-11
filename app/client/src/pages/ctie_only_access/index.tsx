import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import { usePageTitle } from "../../hooks/usePageTitle";
import { Link } from "react-router-dom";

const CtieOnlyAccess = () => {
  usePageTitle("CTIE Access Information");
  return (
    <div className='flex flex-col h-screen'>
      <div className='flex-1 flex items-center justify-center p-3 flex-col'>
        <div className='text-center w-full max-w-2xl text-lnds-color'>
          <h1 className='text-2xl md:text-3xl lg:text-4xl font-bold mb-6'>
            The access to the CDSP MDC for your organisation has now been moved to the CTIE
            infrastructure.
          </h1>
          <p className='mb-6'>
            The new URL to access this application is{" "}
            <a
              href='https://metadata-cdsp.intranet.etat.lu'
              className='text-blue-600 hover:underline font-semibold'
            >
              https://metadata-cdsp.intranet.etat.lu
            </a>
            .
          </p>
          <p className='mb-6'>
            All your metadata records have been migrated automatically from the LNDS to the CTIE
            instance and remain exactly as you have submitted them on the previous instance.
          </p>
          <p className='mb-6'>
            Please contact your Inventory Coordinator, who can inform you about the IAM roles that
            need to be requested to access this new instance. If your organisation does not have an
            Inventory Coordinator yet or you are an Inventory Coordinator but are unsure how to
            proceed, please reach out to the Ministry for Digitalisation at{" "}
            <a
              href='mailto:data@digital.etat.lu'
              className='text-blue-600 hover:underline font-semibold'
            >
              data@digital.etat.lu
            </a>{" "}
            for help.
          </p>
        </div>
        <div className='mt-8'>
          <Link to='/logout'>
            <Button onClick={() => {}} Icon={ArrowRightOnRectangleIcon} label='Logout' />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default CtieOnlyAccess;
