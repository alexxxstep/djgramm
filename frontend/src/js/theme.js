/**
 * Theme toggle using event delegation
 * Works for dynamically added buttons
 */
(function() {
  'use strict';

  const STORAGE_KEY = 'djgramm-theme';
  const DARK_CLASS = 'dark';

  /**
   * Get preferred theme from localStorage or system preference
   */
  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') {
      return stored;
    }
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  /**
   * Apply theme to document
   */
  function setTheme(theme) {
    const html = document.documentElement;
    if (theme === 'dark') {
      html.classList.add(DARK_CLASS);
    } else {
      html.classList.remove(DARK_CLASS);
    }
    localStorage.setItem(STORAGE_KEY, theme);
    updateButtonIcon(theme);
  }

  /**
   * Update theme button icon visibility
   */
  function updateButtonIcon(theme) {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    const sunIcon = btn.querySelector('.sun-icon');
    const moonIcon = btn.querySelector('.moon-icon');

    if (sunIcon && moonIcon) {
      if (theme === 'dark') {
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
        btn.setAttribute('aria-label', 'Switch to light theme');
        btn.setAttribute('title', 'Switch to light theme');
      } else {
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
        btn.setAttribute('aria-label', 'Switch to dark theme');
        btn.setAttribute('title', 'Switch to dark theme');
      }
    }
  }

  /**
   * Toggle between dark and light theme
   */
  function toggleTheme() {
    const current = document.documentElement.classList.contains(DARK_CLASS) ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    setTheme(next);
  }

  // Event delegation - catches clicks on #theme-toggle anywhere in document
  document.addEventListener('click', function(e) {
    const btn = e.target.closest('#theme-toggle');
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      toggleTheme();
    }
  });

  // Initialize theme on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTheme(getPreferredTheme());
    });
  } else {
    setTheme(getPreferredTheme());
  }

  // Listen for system theme changes (only if user hasn't set preference)
  if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem(STORAGE_KEY)) {
        setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  // Export for potential external use
  window.themeSwitcher = {
    toggle: toggleTheme,
    getTheme: () => document.documentElement.classList.contains(DARK_CLASS) ? 'dark' : 'light',
    setTheme: setTheme,
  };
})();
