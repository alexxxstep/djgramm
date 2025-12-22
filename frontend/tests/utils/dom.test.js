/**
 * Unit tests for dom.js
 */

import {
  getById,
  querySelector,
  querySelectorAll,
  clearCache,
  removeFromCache,
} from '../../src/js/utils/dom.js';

describe('dom.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    clearCache();
  });

  describe('getById', () => {
    it('should get element by ID', () => {
      const element = document.createElement('div');
      element.id = 'test-id';
      document.body.appendChild(element);

      const result = getById('test-id');

      expect(result).toBe(element);
    });

    it('should cache element', () => {
      const element = document.createElement('div');
      element.id = 'test-id';
      document.body.appendChild(element);

      const result1 = getById('test-id');
      const result2 = getById('test-id');

      expect(result1).toBe(result2);
      expect(result1).toBe(element);
    });

    it('should return null for non-existent ID', () => {
      const result = getById('non-existent');

      expect(result).toBeNull();
    });
  });

  describe('querySelector', () => {
    it('should query selector', () => {
      const element = document.createElement('div');
      element.className = 'test-class';
      document.body.appendChild(element);

      const result = querySelector('.test-class');

      expect(result).toBe(element);
    });

    it('should cache selector result', () => {
      const element = document.createElement('div');
      element.className = 'test-class';
      document.body.appendChild(element);

      const result1 = querySelector('.test-class');
      const result2 = querySelector('.test-class');

      expect(result1).toBe(result2);
    });

    it('should return null for non-existent selector', () => {
      const result = querySelector('.non-existent');

      expect(result).toBeNull();
    });
  });

  describe('querySelectorAll', () => {
    it('should query all matching elements', () => {
      const element1 = document.createElement('div');
      element1.className = 'test-class';
      const element2 = document.createElement('div');
      element2.className = 'test-class';
      document.body.appendChild(element1);
      document.body.appendChild(element2);

      const result = querySelectorAll('.test-class');

      expect(result.length).toBe(2);
    });
  });

  describe('clearCache', () => {
    it('should clear all cached elements', () => {
      const element = document.createElement('div');
      element.id = 'test-id';
      document.body.appendChild(element);

      getById('test-id');
      clearCache();

      // Cache should be cleared, but element still exists
      const result = getById('test-id', false);
      expect(result).toBe(element);
    });
  });

  describe('removeFromCache', () => {
    it('should remove specific key from cache', () => {
      const element = document.createElement('div');
      element.id = 'test-id';
      document.body.appendChild(element);

      getById('test-id');
      removeFromCache('test-id');

      // Element should still be retrievable
      const result = getById('test-id', false);
      expect(result).toBe(element);
    });
  });
});
