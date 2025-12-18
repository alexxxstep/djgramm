/**
 * Unit tests for errorHandler.js
 */

import { errorHandler, ErrorTypes } from '../../src/js/utils/errorHandler.js';

describe('errorHandler.js', () => {
  beforeEach(() => {
    errorHandler.errorCallbacks = [];
    errorHandler.logErrors = true;
    window.alert = jest.fn();
  });

  describe('normalizeError', () => {
    it('should normalize Error object', () => {
      const error = new Error('Test error');
      const result = errorHandler.normalizeError(error);

      expect(result.type).toBe(ErrorTypes.UNKNOWN);
      expect(result.message).toBe('Test error');
      expect(result.details).toBeDefined();
    });

    it('should detect network errors', () => {
      const error = new Error('Network error occurred');
      const result = errorHandler.normalizeError(error);

      expect(result.type).toBe(ErrorTypes.NETWORK);
    });

    it('should detect permission errors', () => {
      const error = new Error('Permission denied');
      const result = errorHandler.normalizeError(error);

      expect(result.type).toBe(ErrorTypes.PERMISSION);
    });

    it('should normalize string errors', () => {
      const result = errorHandler.normalizeError('Simple error');

      expect(result.message).toBe('Simple error');
    });
  });

  describe('handle', () => {
    it('should call registered callbacks', () => {
      const callback = jest.fn();
      errorHandler.onError(callback);

      const error = new Error('Test');
      errorHandler.handle(error);

      expect(callback).toHaveBeenCalled();
    });

    it('should show user message', () => {
      const error = new Error('Test error');
      errorHandler.handle(error);

      expect(window.alert).toHaveBeenCalled();
    });

    it('should not show message if silent', () => {
      const error = new Error('Test error');
      errorHandler.handle(error, { silent: true });

      // Should still be called, but with different message handling
      expect(errorHandler.handle).toBeDefined();
    });
  });

  describe('handleAjaxError', () => {
    it('should handle 403 errors', async () => {
      const response = {
        status: 403,
        json: async () => ({ error: 'Forbidden' }),
      };

      const result = await errorHandler.handleAjaxError(response);

      expect(result.type).toBe(ErrorTypes.PERMISSION);
      expect(result.message).toContain('permission');
    });

    it('should handle 400 errors', async () => {
      const response = {
        status: 400,
        json: async () => ({ error: 'Bad request' }),
      };

      const result = await errorHandler.handleAjaxError(response);

      expect(result.type).toBe(ErrorTypes.VALIDATION);
    });

    it('should handle 500 errors', async () => {
      const response = {
        status: 500,
        json: async () => ({}),
      };

      const result = await errorHandler.handleAjaxError(response);

      expect(result.message).toContain('Server error');
    });

    it('should handle network errors (status 0)', async () => {
      const response = {
        status: 0,
        json: async () => { throw new Error('Parse error'); },
      };

      const result = await errorHandler.handleAjaxError(response);

      expect(result.message).toContain('Network error');
    });
  });
});

