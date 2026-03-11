import { useEffect, useState } from "react";
import { Card, SearchInput } from "@lnds-lu/design-system";
import { useUrlState } from "../../hooks/useUrlState";
import { XMarkIcon } from "@heroicons/react/24/solid";

interface SearchPanelProps {
  query: string | "";
  placeholder: string;
  noBorder?: boolean;
}

export default function SearchPanel(props: Readonly<SearchPanelProps>) {
  const { query, placeholder, noBorder } = props;
  const [userInputQuery, setUserInputQuery] = useState(query);
  const { generateUrl } = useUrlState();

  useEffect(() => {
    setUserInputQuery(query);
  }, [query]);

  const handleSearch = (query: string) => {
    window.location.href = generateUrl({ query });
  };

  const handleResetSearch = () => {
    setUserInputQuery("");
    window.location.href = generateUrl({ query: "" });
  };

  return (
    <Card className={`w-full ${noBorder ? "border-none" : ""}`}>
      <div className='flex justify-center flex-col items-center'>
        <div className='relative w-full'>
          <SearchInput
            placeholder={placeholder}
            query={userInputQuery}
            onSearch={handleSearch}
            size='large'
          />
          {userInputQuery && (
            <XMarkIcon
              onClick={handleResetSearch}
              className='absolute right-12 top-1/2 transform -translate-y-1/2 cursor-pointer text-gray-500 hover:text-red-500 hover:scale-125 transition-all duration-200'
              style={{ width: "1.75rem", height: "1.5rem" }}
            />
          )}
        </div>
      </div>
    </Card>
  );
}
