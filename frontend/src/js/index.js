// Main entry point for DJGramm JavaScript
// Uses dynamic imports for lazy loading

// Import CSS (handled by webpack)
import '../css/main.css';

// Import theme first (must be loaded immediately)
import './theme.js';

// Export utilities for potential use in other modules
export { getCsrfToken } from './utils/csrf.js';
export { ajaxGet, ajaxPost, ajaxWithLoading } from './utils/ajax.js';
export { errorHandler } from './utils/errorHandler.js';
export { eventManager } from './utils/eventManager.js';

/**
 * Lazy load modules based on current page
 */
function loadPageModules() {
  const path = window.location.pathname;

  // Feed pages - load feed and follow modules
  if (path === '/' || path.startsWith('/feed') || path.startsWith('/profile/')) {
    import(/* webpackChunkName: "feed" */ './feed.js')
      .then(module => {
        if (module.initFeed) module.initFeed();
      })
      .catch(err => {
        console.error('Failed to load feed module:', err);
      });

    import(/* webpackChunkName: "follow" */ './follow.js')
      .then(module => {
        if (module.initFollow) module.initFollow();
      })
      .catch(err => {
        console.error('Failed to load follow module:', err);
      });
  }

  // Post detail page - load post_detail module
  if (path.match(/^\/post\/\d+\/?$/)) {
    import(/* webpackChunkName: "post-detail" */ './post_detail.js')
      .then(module => {
        if (module.initPostDetail) module.initPostDetail();
      })
      .catch(err => {
        console.error('Failed to load post_detail module:', err);
      });
  }

  // Post form page - load post_form module
  if (path === '/post/new/' || path.match(/^\/post\/\d+\/edit\/?$/)) {
    import(/* webpackChunkName: "post-form" */ './post_form.js')
      .then(module => {
        if (module.initPostForm) module.initPostForm();
      })
      .catch(err => {
        console.error('Failed to load post_form module:', err);
      });
  }
}

// Load modules when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadPageModules);
} else {
  loadPageModules();
}
