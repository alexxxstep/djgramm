/**
 * DOM utility functions
 * Caches DOM queries to improve performance
 */

const domCache = new Map();

/**
 * Get element by ID with caching
 * @param {string} id - Element ID
 * @param {boolean} useCache - Use cache (default: true)
 * @returns {HTMLElement|null}
 */
export function getById(id, useCache = true) {
  if (!id) return null;

  if (useCache && domCache.has(id)) {
    return domCache.get(id);
  }

  const element = document.getElementById(id);
  if (element && useCache) {
    domCache.set(id, element);
  }

  return element;
}

/**
 * Query selector with caching
 * @param {string} selector - CSS selector
 * @param {boolean} useCache - Use cache (default: true)
 * @returns {HTMLElement|null}
 */
export function querySelector(selector, useCache = true) {
  if (!selector) return null;

  if (useCache && domCache.has(selector)) {
    const cached = domCache.get(selector);
    // Verify element still exists in DOM
    if (cached && document.contains(cached)) {
      return cached;
    }
    // Remove from cache if element no longer exists
    domCache.delete(selector);
  }

  const element = document.querySelector(selector);
  if (element && useCache) {
    domCache.set(selector, element);
  }

  return element;
}

/**
 * Query selector all (not cached, returns NodeList)
 * @param {string} selector - CSS selector
 * @returns {NodeList}
 */
export function querySelectorAll(selector) {
  return document.querySelectorAll(selector);
}

/**
 * Clear DOM cache
 */
export function clearCache() {
  domCache.clear();
}

/**
 * Remove element from cache
 * @param {string} key - Cache key (ID or selector)
 */
export function removeFromCache(key) {
  domCache.delete(key);
}

