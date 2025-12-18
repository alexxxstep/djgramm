/**
 * Centralized error handling
 * Provides consistent error handling across the application
 */

/**
 * Error types
 */
export const ErrorTypes = {
  NETWORK: 'NETWORK',
  VALIDATION: 'VALIDATION',
  PERMISSION: 'PERMISSION',
  UNKNOWN: 'UNKNOWN',
};

/**
 * Error Handler Class
 */
class ErrorHandler {
  constructor() {
    this.errorCallbacks = [];
    this.logErrors = true;
  }

  /**
   * Register error callback
   * @param {Function} callback - Callback function
   */
  onError(callback) {
    this.errorCallbacks.push(callback);
  }

  /**
   * Handle error
   * @param {Error|Object} error - Error object
   * @param {Object} context - Error context
   */
  handle(error, context = {}) {
    const errorInfo = this.normalizeError(error, context);

    // Log error
    if (this.logErrors) {
      console.error('ErrorHandler:', errorInfo);
    }

    // Call registered callbacks
    this.errorCallbacks.forEach(callback => {
      try {
        callback(errorInfo);
      } catch (e) {
        console.error('Error in error callback:', e);
      }
    });

    // Show user-friendly message
    this.showUserMessage(errorInfo);

    return errorInfo;
  }

  /**
   * Normalize error to consistent format
   * @param {Error|Object} error - Error object
   * @param {Object} context - Error context
   * @returns {Object} Normalized error
   */
  normalizeError(error, context = {}) {
    let type = ErrorTypes.UNKNOWN;
    let message = 'Something went wrong. Please try again.';
    let details = null;

    if (error instanceof Error) {
      message = error.message || message;
      details = error.stack;

      // Detect error type
      if (error.message.includes('network') || error.message.includes('fetch')) {
        type = ErrorTypes.NETWORK;
      } else if (error.message.includes('permission') || error.message.includes('403')) {
        type = ErrorTypes.PERMISSION;
      } else if (error.message.includes('validation') || error.message.includes('400')) {
        type = ErrorTypes.VALIDATION;
      }
    } else if (typeof error === 'object' && error !== null) {
      message = error.message || error.error || message;
      type = error.type || type;
      details = error.details || details;
    } else if (typeof error === 'string') {
      message = error;
    }

    return {
      type,
      message,
      details,
      context,
      timestamp: new Date().toISOString(),
      originalError: error,
    };
  }

  /**
   * Show user-friendly error message
   * @param {Object} errorInfo - Normalized error info
   */
  showUserMessage(errorInfo) {
    // Try to show alert or notification
    // Can be extended to show toast notifications
    if (errorInfo.message && !errorInfo.context.silent) {
      // Use alert for now, can be replaced with toast library
      if (typeof window !== 'undefined' && window.alert) {
        window.alert(errorInfo.message);
      }
    }
  }

  /**
   * Handle AJAX errors specifically
   * @param {Response} response - Fetch response
   * @param {Object} context - Error context
   * @returns {Promise<Object>} Error info
   */
  async handleAjaxError(response, context = {}) {
    let message = 'Request failed. Please try again.';
    let type = ErrorTypes.NETWORK;

    try {
      const data = await response.json();
      message = data.error || data.message || message;

      if (response.status === 403 || response.status === 401) {
        type = ErrorTypes.PERMISSION;
        message = 'You do not have permission to perform this action.';
      } else if (response.status === 400) {
        type = ErrorTypes.VALIDATION;
        message = data.error || 'Invalid request. Please check your input.';
      } else if (response.status >= 500) {
        message = 'Server error. Please try again later.';
      }
    } catch (e) {
      // Failed to parse JSON
      if (response.status === 0) {
        message = 'Network error. Please check your connection.';
      } else {
        message = `Request failed with status ${response.status}.`;
      }
    }

    return this.handle(
      { type, message, status: response.status },
      { ...context, response }
    );
  }
}

// Export singleton instance
export const errorHandler = new ErrorHandler();

// Export default
export default errorHandler;

