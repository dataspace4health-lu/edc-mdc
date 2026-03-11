import { useState, useRef, useEffect, useCallback } from "react";
import { SearchInput } from "@lnds-lu/design-system";
import { LinkIcon } from "@heroicons/react/24/solid";
import client from "../../zodiosClient/client";

export interface LegislationResult {
  id: string;
  label: string;
  description: string;
  link: string;
}

type LegislationSource = "legilux" | "eurlex";

interface LegislationSearchProps {
  onSelect: (result: LegislationResult) => void;
  defaultSearchTerm?: string;
}

const LegislationSearch: React.FC<LegislationSearchProps> = ({
  onSelect,
  defaultSearchTerm = "",
}) => {
  const [source, setSource] = useState<LegislationSource>("legilux");
  const [searchTerm, setSearchTerm] = useState(defaultSearchTerm);
  const [results, setResults] = useState<LegislationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Reset search when source changes
  useEffect(() => {
    setSearchTerm("");
    setResults([]);
    setShowResults(false);
    setErrorMessage(null);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, [source]);

  // Search legislation
  const searchLegislation = useCallback(
    async (query: string) => {
      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      if (!query.trim()) {
        setResults([]);
        setShowResults(false);
        setErrorMessage(null);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setErrorMessage(null);
      abortControllerRef.current = new AbortController();

      try {
        let data: LegislationResult[];

        if (source === "legilux") {
          data = await client.search_legislation_api_v1_legilux_legislation_search_get({
            queries: { query },
            withCredentials: true,
          });
        } else {
          // EUR-Lex endpoint
          data = await client.search_legislation_api_v1_eurlex_legislation_search_get({
            queries: { query },
            withCredentials: true,
          });
        }

        setResults(data);
        setShowResults(true);
        setErrorMessage(null);
      } catch (error) {
        // Ignore abort errors
        if (error instanceof Error && error.name !== "AbortError") {
          console.error(`Error searching ${source}:`, error);
          setResults([]);
          setShowResults(true); // Show dropdown with error message

          // Extract error message from API response
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const apiError = error as any;
          if (apiError?.response?.data?.detail) {
            setErrorMessage(apiError.response.data.detail);
          } else {
            setErrorMessage(
              `Unable to search ${source === "legilux" ? "LegiLux" : "EUR-Lex"}. Please try again later.`,
            );
          }
        }
      } finally {
        setIsLoading(false);
      }
    },
    [source],
  );

  // Debounced search handler
  const handleSearch = useCallback(
    (query: string) => {
      // Cancel previous request if it's still running
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }

      // Clear previous timeout
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }

      // Only update searchTerm, don't trigger other state updates
      setSearchTerm(query);

      // If query is empty, clear results immediately
      if (!query.trim()) {
        setResults([]);
        setShowResults(false);
        setIsLoading(false);
        return;
      }

      // Debounce the actual search with 600ms delay
      // Don't set loading state until the debounce completes
      debounceTimeoutRef.current = setTimeout(() => {
        searchLegislation(query);
      }, 600);
    },
    [searchLegislation],
  );

  const handleSelectResult = (result: LegislationResult) => {
    onSelect(result);
    setSearchTerm("");
    setResults([]);
    setShowResults(false);
    setErrorMessage(null);
  };

  const handleSourceChange = (newSource: LegislationSource) => {
    setSource(newSource);
  };

  const getSourceDisplayName = () => {
    return source === "legilux" ? "LegiLux" : "EUR-Lex";
  };

  return (
    <div ref={containerRef} className='relative w-full'>
      <div className='mb-4'>
        <div className='label-lnds-color text-lg mb-2'>Legislation Source</div>
        <div className='flex gap-2'>
          <button
            type='button'
            onClick={() => handleSourceChange("legilux")}
            className={`px-4 py-2 rounded-md font-medium transition-colors text-white ${
              source === "legilux"
                ? "bg-lnds-purple"
                : "bg-transparent text-lnds-color hover:bg-lnds-dark-blue hover:text-white border border-lnds-color"
            }`}
          >
            LegiLux
          </button>
          <button
            type='button'
            onClick={() => handleSourceChange("eurlex")}
            className={`px-4 py-2 rounded-md font-medium transition-colors text-white ${
              source === "eurlex"
                ? "bg-lnds-purple"
                : "bg-transparent text-lnds-color hover:bg-lnds-dark-blue hover:text-white border border-lnds-color"
            }`}
          >
            EUR-Lex
          </button>
        </div>
      </div>

      <div>
        <div className='label-lnds-color text-lg mb-2 ml-2'>Search in {getSourceDisplayName()}</div>
        <SearchInput
          placeholder={`Search for applicable legislation in ${getSourceDisplayName()} to auto-populate label, description, and link`}
          query={searchTerm}
          onSearch={handleSearch}
          size='small'
          withoutBtn={true}
        />
      </div>

      {/* Results dropdown */}
      {showResults && (
        <div className='absolute z-50 w-full section-lnds-color border border-lnds-color rounded-md max-h-64 overflow-y-auto mt-1'>
          {isLoading ? (
            <div className='p-4 text-center text-lnds-light-gray'>
              <span>Searching {getSourceDisplayName()}...</span>
            </div>
          ) : errorMessage ? (
            <div className='p-4 text-center'>
              <div className='text-lnds-red font-medium mb-2'>⚠️ Service Error</div>
              <div className='text-sm text-lnds-color'>{errorMessage}</div>
            </div>
          ) : results.length > 0 ? (
            <ul>
              {results.map((result) => (
                <li
                  key={result.id}
                  onClick={() => handleSelectResult(result)}
                  className='px-4 py-3 cursor-pointer hover:bg-lnds-purple hover:text-white border-b border-lnds-color last:border-b-0'
                >
                  <div className='font-medium text-sm'>{result.label}</div>
                  <div className='text-xs text-lnds-light-gray mt-1'>{result.description}</div>
                  <div className='text-xs mt-1 truncate inline-flex items-center gap-1'>
                    <LinkIcon className='h-3 w-3' />
                    {result.link}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className='p-4 text-center text-lnds-light-gray'>
              <span>No results found in {getSourceDisplayName()}</span>
            </div>
          )}
        </div>
      )}

      <div className='flex items-center gap-3 my-4'>
        <div className='flex-1 border-t border-lnds-color'></div>
        <span className='text-sm text-lnds-light-gray'>Or enter manually</span>
        <div className='flex-1 border-t border-lnds-color'></div>
      </div>
    </div>
  );
};

export default LegislationSearch;
