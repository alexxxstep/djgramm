import { getCsrfToken } from './csrf.js';
import { errorHandler } from './errorHandler.js';
import { CONFIG } from '../constants/config.js';

/**
 * Default options for AJAX requests
 */
const DEFAULT_OPTIONS = {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: CONFIG.AJAX_TIMEOUT,
};

/**
 * Show loading indicator
 * @param {HTMLElement} element - Element to show loading on
 */
function showLoading(element) {
  if (element) {
    element.disabled = true;
    const originalText = element.textContent;
    element.dataset.originalText = originalText;
    element.textContent = '...';
  }
}

/**
 * Hide loading indicator
 * @param {HTMLElement} element - Element to hide loading on
 */
function hideLoading(element) {
  if (element && element.dataset.originalText) {
    element.disabled = false;
    element.textContent = element.dataset.originalText;
    delete element.dataset.originalText;
  }
}

/**
 * Handle AJAX errors
 * @param {Error} error - Error object
 * @param {string} defaultMessage - Default error message
 * @param {Object} context - Error context
 */
function handleError(error, defaultMessage = 'Something went wrong. Please try again.', context = {}) {
  errorHandler.handle(error, {
    ...context,
    defaultMessage,
  });
}

/**
 * Make AJAX GET request
 * @param {string} url - Request URL
 * @param {Object} options - Request options
 * @returns {Promise<Object>} Response data
 */
export async function ajaxGet(url, options = {}) {
  const csrfToken = getCsrfToken();
  const headers = {
    ...DEFAULT_OPTIONS.headers,
    ...(options.headers || {}),
  };

  if (csrfToken && options.method !== 'GET') {
    headers['X-CSRFToken'] = csrfToken;
  }

  try {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers,
      ...options,
    });

    if (!response.ok) {
      await errorHandler.handleAjaxError(response, {
        url,
        method: options.method || 'GET',
      });
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      // Network error
      handleError(error, 'Network error. Please check your connection.', { url });
    } else {
      handleError(error, options.errorMessage, { url });
    }
    throw error;
  }
}

/**
 * Make AJAX POST request
 * @param {string} url - Request URL
 * @param {Object} data - Request data
 * @param {Object} options - Request options
 * @returns {Promise<Object>} Response data
 */
export async function ajaxPost(url, data = {}, options = {}) {
  const csrfToken = getCsrfToken();
  if (!csrfToken) {
    console.warn('CSRF token not found');
  }

  const headers = {
    ...DEFAULT_OPTIONS.headers,
    'X-CSRFToken': csrfToken,
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
      ...options,
    });

    if (!response.ok) {
      await errorHandler.handleAjaxError(response, {
        url,
        method: 'POST',
        data,
      });
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      // Network error
      handleError(error, 'Network error. Please check your connection.', { url });
    } else {
      handleError(error, options.errorMessage, { url, data });
    }
    throw error;
  }
}

/**
 * Make AJAX request with loading indicator
 * @param {string} url - Request URL
 * @param {Object} options - Request options
 * @param {HTMLElement} loadingElement - Element to show loading on
 * @returns {Promise<Object>} Response data
 */
export async function ajaxWithLoading(url, options = {}, loadingElement = null) {
  showLoading(loadingElement);
  try {
    const result = await ajaxPost(url, options.data || {}, options);
    return result;
  } finally {
    hideLoading(loadingElement);
  }
}

export { showLoading, hideLoading, handleError };

