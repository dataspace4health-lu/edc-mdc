import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

if (ExecutionEnvironment.canUseDOM) {
  // Initialize search when the page loads
  const initializeSearch = async () => {
    try {
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        await new Promise(resolve => {
          document.addEventListener('DOMContentLoaded', resolve);
        });
      }

      // Check if search is already initialized
      if (window.lunrIndex && window.lunrSearchDoc) {
        console.log('Lunr search already initialized');
        return;
      }

      // Try to load search data
      const maxRetries = 10;
      let retries = 0;
      
      const checkSearchReady = () => {
        if (window.lunrIndex && window.lunrSearchDoc) {
          console.log('Lunr search initialized and ready for scoped search');
          console.log('Search docs count:', Object.keys(window.lunrSearchDoc).length);
          return true;
        }
        
        retries++;
        if (retries < maxRetries) {
          // Check again in 100ms if not ready
          setTimeout(checkSearchReady, 100);
        } else {
          console.warn('Lunr search initialization timed out after', maxRetries * 100, 'ms');
        }
        return false;
      };
      
      checkSearchReady();
    } catch (error) {
      console.error('Error initializing search:', error);
    }
  };

  // Initialize immediately if DOM is ready, otherwise wait for it
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSearch);
  } else {
    initializeSearch();
  }
}