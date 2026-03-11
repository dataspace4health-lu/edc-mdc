import React from "react";
import LogoUrl from "./logos/lnds-logo.svg";
import DarkLogoUrl from "./logos/lnds-logo-dark.svg";
import MinDigiLight from "./logos/mindigi-light.png";
import MinDigiDark from "./logos/mindigi-dark.png";
import DataLuxLight from "./logos/data-luxembourg-light.png";
import DataLuxDark from "./logos/data-luxembourg-dark.png";

export type FooterBaseProps = {
  children: React.ReactNode;
  hideLogo?: boolean;
};

const FooterBase: React.FC<FooterBaseProps> = ({ children, hideLogo }) => {
  return (
    <footer className='section-lnds-color border-1 border-lnds-color sticky top-full z-50 flex min-h-16 flex-col items-center justify-between gap-3 border-t px-4 py-3 md:flex-row md:gap-4 md:px-6'>
      <div className='flex flex-col items-center gap-3 md:flex-row md:gap-4'>
        {!hideLogo && (
          <div className='flex items-center'>
            <img
              src={DataLuxLight}
              alt='Data Luxembourg'
              style={{ height: 48 }}
              className='object-contain transition-opacity hover:opacity-80 dark:hidden'
            />
            <img
              src={DataLuxDark}
              alt='Data Luxembourg'
              style={{ height: 48 }}
              className='hidden object-contain transition-opacity hover:opacity-80 dark:block'
            />
          </div>
        )}
        <div className='relative flex w-full justify-center md:w-auto md:justify-start'>
          {children}
        </div>
      </div>
      {!hideLogo ? (
        <section className='flex flex-wrap items-center justify-center gap-3 text-xs md:gap-4 md:text-sm'>
          <div className='flex items-center gap-2 md:gap-3'>
            <p className='font-medium'>Developed by</p>
            <a href='https://www.lnds.lu' target='_blank' rel='noreferrer'>
              <img
                src={LogoUrl}
                alt='LNDS Logo'
                style={{ height: 48 }}
                className='transition-opacity hover:opacity-80 dark:hidden'
              />
              <img
                src={DarkLogoUrl}
                alt='LNDS Logo'
                style={{ height: 48 }}
                className='hidden transition-opacity hover:opacity-80 dark:block'
              />
            </a>
          </div>
          <span className='font-medium text-lnds-gray dark:text-gray-400'>for</span>
          <a href='https://mindigital.gouvernement.lu/en.html' target='_blank' rel='noreferrer'>
            <img
              src={MinDigiLight}
              alt='Ministry of Digitalisation'
              style={{ height: 48 }}
              className='object-contain transition-opacity hover:opacity-80 dark:hidden'
            />
            <img
              src={MinDigiDark}
              alt='Ministry of Digitalisation'
              style={{ height: 48 }}
              className='hidden object-contain transition-opacity hover:opacity-80 dark:block'
            />
          </a>
        </section>
      ) : (
        <section className='flex items-center gap-2 text-xs md:text-sm'>
          <p className='font-medium'>Developed by</p>
          <a href='https://www.lnds.lu' target='_blank' rel='noreferrer'>
            <img
              src={LogoUrl}
              alt='LNDS Logo'
              style={{ height: 40 }}
              className='transition-opacity hover:opacity-80 dark:hidden'
            />
            <img
              src={DarkLogoUrl}
              alt='LNDS Logo'
              style={{ height: 40 }}
              className='hidden transition-opacity hover:opacity-80 dark:block'
            />
          </a>
        </section>
      )}
    </footer>
  );
};

export default FooterBase;
