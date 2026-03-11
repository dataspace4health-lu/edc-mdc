import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import { LNDSLoader } from "../../components/LNDSLoader";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../../zodiosClient/client";
import { usePageTitle } from "../../hooks/usePageTitle";

const Unauthorised = () => {
  usePageTitle("Unauthorised");
  const [isLoading, setIsLoading] = useState(true);
  const [unauthorisedMessage, setUnauthorisedMessage] = useState("");

  useEffect(() => {
    const fetchUnauthorisedMessage = async () => {
      try {
        const response = await client.get_ui_config_api_v1_ui_config_get({
          withCredentials: true,
        });
        // @ts-expect-error 'response' is of type 'unknown'.
        setUnauthorisedMessage(response.unauthorised_message);
      } catch (error) {
        console.error("Error fetching unauthorised message:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUnauthorisedMessage();
  }, []);

  if (isLoading) {
    return (
      <div className='flex items-center justify-center min-h-[500px]'>
        <LNDSLoader />
      </div>
    );
  }

  return (
    <div className='flex flex-col h-screen'>
      <div className='flex-1 flex items-center justify-center p-3 flex-col'>
        <div className='text-center w-full max-w-md text-lnds-color'>
          <h1 className='text-2xl md:text-3xl lg:text-4xl font-bold mb-4'>
            You are not authorised to access this application
          </h1>
          <p className='mb-6'>
            Your account does not have the required permissions to use this application.
          </p>
          <p className='mb-6'>{unauthorisedMessage}</p>
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

export default Unauthorised;
