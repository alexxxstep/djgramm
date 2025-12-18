/**
 * Unit tests for csrf.js
 */

import { getCsrfToken } from '../../src/js/utils/csrf.js';

describe('csrf.js', () => {
  beforeEach(() => {
    // Remove existing meta tag
    const existing = document.querySelector('meta[name="csrf-token"]');
    if (existing) {
      existing.remove();
    }
  });

  it('should get CSRF token from meta tag', () => {
    const meta = document.createElement('meta');
    meta.name = 'csrf-token';
    meta.content = 'test-token-123';
    document.head.appendChild(meta);

    const token = getCsrfToken();

    expect(token).toBe('test-token-123');
  });

  it('should return null if meta tag does not exist', () => {
    const token = getCsrfToken();

    expect(token).toBeNull();
  });

  it('should return null if meta tag has no content', () => {
    const meta = document.createElement('meta');
    meta.name = 'csrf-token';
    meta.content = '';
    document.head.appendChild(meta);

    const token = getCsrfToken();

    expect(token).toBe('');
  });
});
