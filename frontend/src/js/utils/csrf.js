/**
 * Get CSRF token from various sources
 * @returns {string|null} CSRF token or null if not found
 */
export function getCsrfToken() {
  // Try multiple ways to get CSRF token
  const token =
    document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.querySelector('meta[name=csrf-token]')?.content ||
    document.querySelector('[name=csrf-token]')?.content;
  return token || null;
}

