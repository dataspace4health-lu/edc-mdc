import { useLocation } from '@docusaurus/router';

export function useScopedSearch() {
  const location = useLocation();
  
  // Determine current section based on pathname
  const getCurrentSection = () => {
    const pathname = location.pathname;
    
    if (pathname.startsWith('/user-guide/')) {
      return 'user-guide';
    } else if (pathname.startsWith('/system-admin/')) {
      return 'system-admin';
    } else if (pathname.startsWith('/developer/')) {
      return 'developer';
    }
    return 'all'; // For home page and other pages
  };
  
  // Filter search results based on current section
  const filterSearchResults = (results) => {
    const currentSection = getCurrentSection();
    
    if (currentSection === 'all') {
      return results; // Show all results on home page
    }
    
    return results.filter(result => {
      const resultPath = result.route || result.url || '';
      
      switch (currentSection) {
        case 'user-guide':
          return resultPath.startsWith('/user-guide/');
        case 'system-admin':
          return resultPath.startsWith('/system-admin/');
        case 'developer':
          return resultPath.startsWith('/developer/');
        default:
          return true;
      }
    });
  };
  
  return {
    currentSection: getCurrentSection(),
    filterSearchResults,
  };
}