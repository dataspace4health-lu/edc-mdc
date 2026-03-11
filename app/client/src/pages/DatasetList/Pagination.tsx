import { Link } from "react-router-dom";
import { DropdownSelect } from "@lnds-lu/design-system";
import { useUrlState } from "../../hooks/useUrlState";

const PAGE_SIZES = [10, 20, 50, 250];

const Pagination = ({
  currentPage,
  totalPages,
  pageSize,
  query,
  status,
}: {
  currentPage: number;
  totalPages: number;
  pageSize: number;
  query?: string;
  status?: string;
}) => {
  const { generateUrl } = useUrlState();

  if (totalPages <= 1) return null;

  const pageNumbers = [];
  const maxVisiblePages = 5;

  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pageNumbers.push(i);
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handlePageSizeChange = (selectedPageSize: any) => {
    window.location.href = generateUrl({
      query,
      status,
      page: 1,
      pageSize: Number(selectedPageSize.value),
    });
  };

  return (
    <div className='flex justify-center items-center my-4'>
      <Link
        to={generateUrl({ query, status, page: 1, pageSize })}
        className={`mx-1 px-3 py-1 rounded ${
          currentPage === 1
            ? "text-gray-400 cursor-not-allowed"
            : "text-lnds-blue hover:bg-lnds-dark-blue hover:text-white"
        }`}
      >
        &laquo;
      </Link>
      <Link
        to={generateUrl({ query, status, page: Math.max(1, currentPage - 1), pageSize })}
        className={`mx-1 px-3 py-1 rounded ${
          currentPage === 1
            ? "text-gray-400 cursor-not-allowed"
            : "text-lnds-blue hover:bg-lnds-dark-blue hover:text-white"
        }`}
      >
        &lt;
      </Link>

      {pageNumbers.map((number) => (
        <Link
          key={number}
          to={generateUrl({ query, status, page: number, pageSize })}
          className={`mx-1 px-3 py-1 rounded ${
            currentPage === number
              ? "bg-lnds-blue text-white"
              : "text-lnds-blue hover:bg-lnds-dark-blue hover:text-white"
          }`}
        >
          {number}
        </Link>
      ))}

      <Link
        to={generateUrl({
          query,
          status,
          page: Math.min(totalPages, currentPage + 1),
          pageSize,
        })}
        className={`mx-1 px-3 py-1 rounded ${
          currentPage === totalPages
            ? "text-gray-400 cursor-not-allowed"
            : "text-lnds-blue hover:bg-lnds-dark-blue hover:text-white"
        }`}
      >
        &gt;
      </Link>
      <Link
        to={generateUrl({ query, status, page: totalPages, pageSize })}
        className={`mx-1 px-3 py-1 rounded ${
          currentPage === totalPages
            ? "text-gray-400 cursor-not-allowed"
            : "text-lnds-blue hover:bg-lnds-dark-blue hover:text-white"
        }`}
      >
        &raquo;
      </Link>

      <div className='ml-4'>
        <DropdownSelect
          isMulti={false}
          name='pageSize'
          defaultValue={pageSize.toString()}
          options={PAGE_SIZES.map((size) => ({
            label: `${size} per page`,
            value: size.toString(),
          }))}
          onChange={handlePageSizeChange}
        />
      </div>
    </div>
  );
};

export default Pagination;
