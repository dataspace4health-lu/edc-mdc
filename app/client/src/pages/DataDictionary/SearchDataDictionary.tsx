import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { ResourceDataDictionaryEntry } from "../../types";
import { SearchInput } from "@lnds-lu/design-system";

interface SearchDataDictionaryProps {
  onSearchResults: (query: string) => void;
  dataDictionaries: ResourceDataDictionaryEntry[];
}

export default function SearchDataDictionary({
  onSearchResults,
  dataDictionaries,
}: Readonly<SearchDataDictionaryProps>) {
  const [searchParams, setParams] = useSearchParams();
  const [userInputQuery, setUserInputQuery] = useState(searchParams.get("query") || "");
  const [filteredResults, setFilteredResults] = useState<ResourceDataDictionaryEntry[]>([]);

  useEffect(() => {
    setUserInputQuery(searchParams.get("query") || "");
  }, [searchParams]);

  useEffect(() => {
    const filtered = dataDictionaries.filter((entry) =>
      entry.field_name.toLowerCase().includes(userInputQuery.toLowerCase()),
    );
    setFilteredResults(filtered);
  }, [userInputQuery, dataDictionaries]);

  const handleSearch = (query: string) => {
    setUserInputQuery(query);
    setParams({ query });
    onSearchResults(query);
  };

  return (
    <div className='flex justify-center flex-col items-center mb-4'>
      <SearchInput
        placeholder='Search data dictionary'
        query={userInputQuery}
        onSearch={handleSearch}
        size='small'
      />
      {userInputQuery?.length > 0 && filteredResults.length > 0 && (
        <div className='p-3 text-lnds-gray'>
          {filteredResults.length} of {dataDictionaries.length} entries found.
        </div>
      )}
    </div>
  );
}
