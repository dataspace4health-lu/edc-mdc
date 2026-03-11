import { SunIcon, MoonIcon } from "@heroicons/react/24/solid";

interface DarkModeLinkProps {
  isDarkMode: boolean;
  onChangeDarkMode: () => void;
}

export default function DarkModeLink(props: Readonly<DarkModeLinkProps>) {
  const { isDarkMode, onChangeDarkMode } = props;
  return (
    <button
      id='dark-mode-link'
      onClick={onChangeDarkMode}
      aria-label={`Toggle ${isDarkMode ? "light" : "dark"} mode`}
      className='hover:bg-lnds-dark-blue hover:text-white flex items-center px-4 py-2 space-x-1 w-full'
    >
      {isDarkMode ? <SunIcon className='h-5 w-5' /> : <MoonIcon className='h-5 w-5' />}
      <span>{isDarkMode ? "Light" : "Dark"} Mode</span>
    </button>
  );
}
