/**
 * Unit tests for ajax.js
 * Run with: npm test
 */

import { ajaxGet, ajaxPost } from '../src/js/utils/ajax.js';
import { errorHandler } from '../src/js/utils/errorHandler.js';

// Mock fetch
global.fetch = jest.fn();

// Mock errorHandler
jest.mock('../src/js/utils/errorHandler.js', () => ({
  errorHandler: {
    handle: jest.fn(),
    handleAjaxError: jest.fn(),
  },
}));

describe('ajax.js', () => {
  beforeEach(() => {
    fetch.mockClear();
    errorHandler.handle.mockClear();
    errorHandler.handleAjaxError.mockClear();
  });

  describe('ajaxGet', () => {
    it('should make GET request successfully', async () => {
      const mockData = { success: true, data: 'test' };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await ajaxGet('/api/test');

      expect(fetch).toHaveBeenCalledWith('/api/test', expect.any(Object));
      expect(result).toEqual(mockData);
    });

    it('should handle network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(ajaxGet('/api/test')).rejects.toThrow();
      expect(errorHandler.handle).toHaveBeenCalled();
    });

    it('should handle HTTP errors', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ error: 'Not found' }),
      });

      errorHandler.handleAjaxError.mockResolvedValueOnce({});

      await expect(ajaxGet('/api/test')).rejects.toThrow();
      expect(errorHandler.handleAjaxError).toHaveBeenCalled();
    });
  });

  describe('ajaxPost', () => {
    it('should make POST request successfully', async () => {
      const mockData = { success: true };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await ajaxPost('/api/test', { key: 'value' });

      expect(fetch).toHaveBeenCalledWith(
        '/api/test',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ key: 'value' }),
        })
      );
      expect(result).toEqual(mockData);
    });

    it('should include CSRF token in headers', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await ajaxPost('/api/test', {});

      expect(fetch).toHaveBeenCalledWith(
        '/api/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-CSRFToken': expect.any(String),
          }),
        })
      );
    });
  });
});

