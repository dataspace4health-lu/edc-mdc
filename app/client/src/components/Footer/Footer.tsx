import { useState, useEffect } from "react";
import FooterBase from "./FooterBase";
import { ResourceUserType } from "../../types";
import client from "../../zodiosClient/client";

interface MetadataFooterProps {
  user: ResourceUserType | null;
}

export default function MetadataFooter({ user }: MetadataFooterProps) {
  const [supportPanelOpen, setSupportPanelOpen] = useState(false);
  const [technicalSupportMessage, setTechnicalSupportMessage] = useState(
    "For technical support, contact tech@lnds.lu",
  );

  const showNewFooterLayout = user?.feature_options?.enable_multi_tenants;

  useEffect(() => {
    const fetchTechnicalSupportMessage = async () => {
      try {
        const response = await client.get_ui_config_api_v1_ui_config_get({
          withCredentials: true,
        });
        // @ts-expect-error 'response' is of type 'unknown'.
        if (response.technical_support_message) {
          // @ts-expect-error 'response' is of type 'unknown'.
          setTechnicalSupportMessage(response.technical_support_message);
        }
      } catch (error) {
        console.error("Error fetching technical support message:", error);
      }
    };

    fetchTechnicalSupportMessage();
  }, []);

  return (
    <FooterBase hideLogo={!showNewFooterLayout}>
      <div className='relative flex w-full md:w-auto justify-center md:justify-start'>
        <div className='flex items-center space-x-2'>
          <a
            href='https://mindig_lu.gitlab.io/DCAT-AP-LU/'
            target='_blank'
            rel='noopener noreferrer'
            className='text-lnds-gray dark:text-gray-400 hover:text-lnds-dark-blue dark:hover:text-white hover:underline'
          >
            DCAT-AP-LU
          </a>

          <span className='text-lnds-gray dark:text-gray-400'>|</span>

          <button
            type='button'
            onClick={() => setSupportPanelOpen(!supportPanelOpen)}
            className={`${
              supportPanelOpen
                ? "text-lnds-dark-blue underline dark:text-white"
                : "text-lnds-gray dark:text-gray-400"
            } cursor-pointer hover:text-lnds-dark-blue dark:hover:text-white hover:underline bg-transparent border-none p-0 font-inherit`}
          >
            Support
          </button>
        </div>
        {supportPanelOpen && (
          <div className='absolute bottom-8 left-0 right-0 p-4 w-full md:w-72 section-lnds-color rounded border border-lnds-color z-10'>
            <p className='text-sm'>{technicalSupportMessage}</p>
          </div>
        )}
      </div>
    </FooterBase>
  );
}
