/**
 * Theme switcher module
 * Handles dark/light theme switching with localStorage persistence
 * and system preference detection
 */

(function () {
  'use strict';

  const THEME_STORAGE_KEY = 'djgramm-theme';
  const DARK_CLASS = 'dark';

  /**
   * Get system theme preference
   * @returns {string} 'dark' or 'light'
   */
  function getSystemTheme() {
    if (
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Get current theme from localStorage or system preference
   * @returns {string} 'dark' or 'light'
   */
  function getTheme() {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') {
      return stored;
    }
    return getSystemTheme();
  }

  /**
   * Apply theme to document
   * @param {string} theme - 'dark' or 'light'
   */
  function applyTheme(theme) {
    const html = document.documentElement;
    if (theme === 'dark') {
      html.classList.add(DARK_CLASS);
    } else {
      html.classList.remove(DARK_CLASS);
    }
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }

  /**
   * Toggle between dark and light theme
   */
  function toggleTheme() {
    const currentTheme = getTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    updateThemeButton(newTheme);
  }

  /**
   * Update theme button icon and aria-label
   * @param {string} theme - 'dark' or 'light'
   */
  function updateThemeButton(theme) {
    const button = document.getElementById('theme-toggle');
    if (!button) return;

    const sunIcon = button.querySelector('.sun-icon');
    const moonIcon = button.querySelector('.moon-icon');

    if (theme === 'dark') {
      // Show moon icon (dark mode active)
      if (sunIcon) sunIcon.classList.add('hidden');
      if (moonIcon) moonIcon.classList.remove('hidden');
      button.setAttribute('aria-label', 'Switch to light theme');
      button.setAttribute('title', 'Switch to light theme');
    } else {
      // Show sun icon (light mode active)
      if (sunIcon) sunIcon.classList.remove('hidden');
      if (moonIcon) moonIcon.classList.add('hidden');
      button.setAttribute('aria-label', 'Switch to dark theme');
      button.setAttribute('title', 'Switch to dark theme');
    }
  }

  /**
   * Initialize theme on page load
   */
  function initTheme() {
    const theme = getTheme();
    applyTheme(theme);
    updateThemeButton(theme);

    // Listen for system theme changes
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', (e) => {
        // Only update if user hasn't set a preference
        if (!localStorage.getItem(THEME_STORAGE_KEY)) {
          const newTheme = e.matches ? 'dark' : 'light';
          applyTheme(newTheme);
          updateThemeButton(newTheme);
        }
      });
    }
  }

  /**
   * Initialize theme switcher
   */
  function init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initTheme);
    } else {
      initTheme();
    }

    // Attach click handler to theme toggle button
    const button = document.getElementById('theme-toggle');
    if (button) {
      button.addEventListener('click', toggleTheme);
    }
  }

  // Auto-initialize
  init();

  // Export for potential external use
  window.themeSwitcher = {
    toggle: toggleTheme,
    getTheme: getTheme,
    setTheme: applyTheme,
  };
})();
