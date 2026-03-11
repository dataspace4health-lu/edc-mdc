import { SearchInput } from "@lnds-lu/design-system";

interface SearchBarProps {
  searchTerm: string;
  onSearch: (term: string) => void;
  placeholder: string;
}

const SearchBar: React.FC<SearchBarProps> = ({ searchTerm, onSearch, placeholder }) => {
  return (
    <div className='p-4 border-b border-lnds-color'>
      <div className='relative'>
        <SearchInput
          className='md:w-full'
          withoutBtn={true}
          placeholder={placeholder}
          query={searchTerm}
          onSearch={onSearch}
          size='small'
        />
      </div>
    </div>
  );
};

export default SearchBar;
