import { useEffect, useState } from "react";
import { Modal } from "./Modal";
import { CheckCircleIcon } from "@heroicons/react/24/solid";

type DatasetCreatedAchievementModalProps = {
  isOpen: boolean;
  title: string;
};

const DatasetCreatedAchievementModal = ({ isOpen, title }: DatasetCreatedAchievementModalProps) => {
  const [dots, setDots] = useState("");

  useEffect(() => {
    if (isOpen) {
      const interval = setInterval(() => {
        setDots((prev) => {
          if (prev.length >= 3) {
            return "";
          }
          return prev + ".";
        });
      }, 500); // Change dots every 500ms

      return () => clearInterval(interval);
    }
  }, [isOpen]);

  return (
    <Modal.Frame open={isOpen} onClose={() => {}}>
      <Modal.Body className='text-center py-16 px-8'>
        <div className='flex flex-col items-center space-y-8'>
          <div className='relative'>
            <div className='w-32 h-32 bg-lnds-green/20 rounded-full flex items-center justify-center animate-pulse shadow-2xl'>
              <CheckCircleIcon className='w-20 h-20 text-lnds-green animate-bounce' />
            </div>

            <div className='absolute -top-4 -left-4 w-4 h-4 bg-lnds-yellow rounded-full animate-ping'></div>
            <div className='absolute -top-2 -right-6 w-3 h-3 bg-lnds-blue rounded-full animate-ping delay-200'></div>
            <div className='absolute -bottom-4 -right-2 w-4 h-4 bg-lnds-purple rounded-full animate-ping delay-500'></div>
            <div className='absolute -bottom-2 -left-6 w-3 h-3 bg-secondary rounded-full animate-ping delay-700'></div>
            <div className='absolute top-2 -left-8 w-2 h-2 bg-lnds-yellow rounded-full animate-ping delay-300'></div>
            <div className='absolute top-8 -right-8 w-2 h-2 bg-lnds-green rounded-full animate-ping delay-600'></div>
            <div className='absolute -bottom-6 left-4 w-2 h-2 bg-lnds-blue rounded-full animate-ping delay-900'></div>
            <div className='absolute -bottom-8 right-6 w-3 h-3 bg-lnds-purple rounded-full animate-ping delay-1000'></div>

            <div className='absolute inset-0 w-32 h-32 border-4 border-lnds-green/30 rounded-full animate-ping'></div>
          </div>

          <div className='space-y-6 max-w-lg'>
            <div className='space-y-2'>
              <h2 className='text-3xl md:text-4xl font-bold label-lnds-color leading-tight'>
                Dataset Created Successfully!
              </h2>
            </div>

            <div className='bg-lnds-blue/10 border-l-4 border-lnds-blue p-4 rounded-r-lg'>
              <h3 className='text-lg font-semibold text-lnds-color'>{title}</h3>
            </div>

            <p className='text-lnds-color text-lg'>
              Redirecting to complete your dataset setup{dots}
            </p>

            <div className='bg-lnds-yellow/20 border-2 border-lnds-yellow rounded-lg p-4 text-left shadow-md'>
              <p className='text-lnds-color font-bold uppercase tracking-wide text-sm'>
                Next Steps
              </p>
              <p className='text-lnds-color font-semibold mt-1'>
                Do not stop at dataset metadata. Complete these sections next:
              </p>
              <ul className='mt-2 list-disc list-inside text-lnds-color font-medium space-y-1'>
                <li>Distributions</li>
                <li>Data Dictionary</li>
                <li>Dataset Relations</li>
              </ul>
            </div>
          </div>
        </div>
      </Modal.Body>
    </Modal.Frame>
  );
};

export default DatasetCreatedAchievementModal;
