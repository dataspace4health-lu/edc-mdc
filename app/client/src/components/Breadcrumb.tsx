interface BreadcrumbProps {
  firstLevel: string;
  firstLevelLink: string;
  location: string;
}

const Breadcrumb = ({ firstLevel, firstLevelLink, location }: BreadcrumbProps) => {
  return (
    <div className='mb-4'>
      <nav className='text-lnds-gray'>
        <ol className='flex space-x-1'>
          <li className='flex items-center'>
            <a
              href={firstLevelLink}
              className='hover:text-lnds-dark-blue dark:hover:text-white hover:underline'
            >
              {firstLevel}
            </a>
            <span className='mx-2'>/</span>
          </li>

          <li className='flex items-center'>
            <span>{location}</span>
          </li>
        </ol>
      </nav>
    </div>
  );
};

export default Breadcrumb;
