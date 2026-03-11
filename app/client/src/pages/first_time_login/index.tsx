import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import { LNDSLoader } from "../../components/LNDSLoader";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../../zodiosClient/client";
import { usePageTitle } from "../../hooks/usePageTitle";
// import { ResourceUserType } from "../../types";

const FirstTimeLogin = () => {
  usePageTitle("First Time Login");
  // const [user, setUser] = useState<ResourceUserType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [contactMessage, setContactMessage] = useState("");

  useEffect(() => {
    const fetchContactMessage = async () => {
      try {
        const response = await client.get_ui_config_api_v1_ui_config_get({
          withCredentials: true,
        });
        // @ts-expect-error 'response' is of type 'unknown'.
        setContactMessage(response.unauthorised_message);
      } catch (error) {
        console.error("Error fetching contact message:", error);
      } finally {
        setIsLoading(false);
      }
      // const user: ResourceUserType = await client.get_user_api_v1_user_get({
      //   withCredentials: true,
      // });

      // setUser(user);
    };

    fetchContactMessage();
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
            Thank you for your first login!
          </h1>
          <p className='mb-6 text-xl font-bold'>
            You cannot yet access this application, though your account has now been created.
          </p>
          <p className='mb-6'>{contactMessage}</p>
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

export default FirstTimeLogin;
