import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from '@docusaurus/router';
import './SearchBar.css';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();
  const searchRef = useRef(null);
  const resultsRef = useRef(null);

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
  const filterResults = (searchResults) => {
    const currentSection = getCurrentSection();
    
    if (currentSection === 'all') {
      return searchResults; // Show all results on home page
    }
    
    return searchResults.filter(result => {
      // Check both route and url properties for the path
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

  // Search function with fallback loading
  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    setIsLoading(true);
    setIsOpen(true);

    try {
      // Debug logging
      console.log('Performing search for:', searchQuery);
      console.log('Search index available:', !!window.lunrIndex);
      console.log('Search docs available:', !!window.lunrSearchDoc);
      
      // If search is not available, try to manually load the search data
      if (!window.lunrIndex || !window.lunrSearchDoc) {
        console.log('Attempting to manually load search data...');
        
        try {
          // Try to load search docs and index manually
          const [searchDocsResponse, searchIndexResponse] = await Promise.all([
            fetch('/search-doc.json'),
            fetch('/lunr-index.json')
          ]);
          
          if (searchDocsResponse.ok && searchIndexResponse.ok) {
            const searchDocs = await searchDocsResponse.json();
            const searchIndex = await searchIndexResponse.json();
            
            // Import lunr if not available
            if (typeof lunr === 'undefined') {
              // Try to load lunr from CDN as fallback
              await new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://unpkg.com/lunr@2.3.9/lunr.min.js';
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
              });
            }
            
            // Initialize search manually
            if (typeof lunr !== 'undefined') {
              window.lunrSearchDoc = searchDocs.searchDocs;
              window.lunrIndex = lunr.Index.load(searchIndex);
              console.log('Search data loaded manually');
            }
          }
        } catch (loadError) {
          console.error('Failed to manually load search data:', loadError);
        }
      }

      if (window.lunrSearchDoc) {
        console.log('Search docs count:', Object.keys(window.lunrSearchDoc).length);
      }

      // Use the global search function if available
      if (window.lunrIndex && window.lunrSearchDoc) {
        const searchResults = window.lunrIndex.search(searchQuery);
        console.log('Raw search results:', searchResults.length);
        
        const formattedResults = searchResults.map(result => {
          const doc = window.lunrSearchDoc[result.ref];
          return {
            id: result.ref,
            title: doc.title || 'Untitled',
            content: doc.content || '',
            route: doc.url, // Use 'url' from the document structure
            url: doc.url,
            score: result.score
          };
        });
        
        const filteredResults = filterResults(formattedResults);
        console.log('Filtered results:', filteredResults.length);
        setResults(filteredResults.slice(0, 8)); // Limit to 8 results
      } else {
        console.error('Search index still not available after manual loading attempt');
        setResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle input change with debouncing
  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query, location.pathname]); // Re-search when location changes

  // Handle click outside to close results
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getSectionLabel = () => {
    const section = getCurrentSection();
    switch (section) {
      case 'user-guide':
        return 'User Guide';
      case 'system-admin':
        return 'System Admin Guide';
      case 'developer':
        return 'Developer Guide';
      default:
        return 'All Documentation';
    }
  };

  return (
    <div className="navbar__search" ref={searchRef}>
      <div className="navbar__search-input-wrapper">
        <input
          type="search"
          placeholder={`Search ${getSectionLabel()}...`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query && setIsOpen(true)}
          className="navbar__search-input"
        />
        {query && (
          <button
            className="navbar__search-clear"
            onClick={() => {
              setQuery('');
              setResults([]);
              setIsOpen(false);
            }}
          >
            ✕
          </button>
        )}
      </div>
      
      {isOpen && (query || isLoading) && (
        <div className="navbar__search-results" ref={resultsRef}>
          <div className="navbar__search-results-header">
            <span className="navbar__search-results-section">
              Searching in: {getSectionLabel()}
            </span>
          </div>
          
          {isLoading ? (
            <div className="navbar__search-result-item loading">
              Searching...
            </div>
          ) : results.length > 0 ? (
            results.map((result, index) => (
              <a
                key={result.id || index}
                href={result.route}
                className="navbar__search-result-item"
                onClick={() => setIsOpen(false)}
              >
                <div className="navbar__search-result-title">
                  {result.title}
                </div>
                <div className="navbar__search-result-content">
                  {result.content && result.content.substring(0, 100)}...
                </div>
              </a>
            ))
          ) : query ? (
            <div className="navbar__search-result-item no-results">
              No results found in {getSectionLabel()}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}