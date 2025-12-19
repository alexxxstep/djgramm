/** @type {import('tailwindcss').Config} */
const path = require('path');
const fs = require('fs');

// Build content paths array with proper resolution
// This ensures Tailwind finds templates in both Docker and local environments
const contentPaths = [];

// Templates paths - check both Docker and host locations
const templatePaths = [
  path.resolve(__dirname, 'templates'), // Docker: src/templates copied to /app/templates
  path.resolve(__dirname, 'src/templates'), // Host development
];

// Add template paths that exist
templatePaths.forEach(templatePath => {
  if (fs.existsSync(templatePath)) {
    // Use specific path - Tailwind will handle glob pattern
    contentPaths.push(path.join(templatePath, '**/*.html'));
    console.log(`[Tailwind] Found templates at: ${templatePath}`);

    // Debug: List found templates
    try {
      const glob = require('glob');
      const found = glob.sync(path.join(templatePath, '**/*.html'));
      console.log(`[Tailwind] Found ${found.length} HTML files in ${templatePath}`);
    } catch (e) {
      // glob not available, skip debug
    }
  }
});

// Templatetags paths
const templatetagsPaths = [
  path.resolve(__dirname, 'app/templatetags'), // Docker
  path.resolve(__dirname, 'src/app/templatetags'), // Host
];

templatetagsPaths.forEach(templatetagsPath => {
  if (fs.existsSync(templatetagsPath)) {
    contentPaths.push(path.join(templatetagsPath, '**/*.py'));
    console.log(`[Tailwind] Found templatetags at: ${templatetagsPath}`);
  }
});

// JavaScript files (always exists)
contentPaths.push(path.resolve(__dirname, 'frontend/src/js/**/*.js'));

console.log(`[Tailwind] Content paths: ${contentPaths.length} paths configured`);

module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: contentPaths,
  // Safelist critical classes that might be dynamically generated
  // This ensures they're always included even if Tailwind doesn't detect them
  safelist: [
    // Layout
    'flex', 'grid', 'block', 'hidden', 'inline', 'inline-block',
    // Spacing
    'p-2', 'p-4', 'px-4', 'py-2', 'py-4', 'py-6', 'mb-2', 'mb-4', 'mt-2', 'mt-4',
    // Sizing
    'w-full', 'h-full', 'max-w-4xl', 'max-w-5xl', 'mx-auto',
    // Colors - light mode
    'bg-gray-50', 'bg-gray-100', 'bg-gray-200', 'bg-gray-300', 'bg-gray-400', 'bg-gray-500',
    'bg-gray-600', 'bg-gray-700', 'bg-gray-800', 'bg-gray-900',
    'text-gray-50', 'text-gray-100', 'text-gray-200', 'text-gray-300', 'text-gray-400', 'text-gray-500',
    'text-gray-600', 'text-gray-700', 'text-gray-800', 'text-gray-900',
    // Colors - dark mode
    'dark:bg-gray-50', 'dark:bg-gray-100', 'dark:bg-gray-200', 'dark:bg-gray-300', 'dark:bg-gray-400', 'dark:bg-gray-500',
    'dark:bg-gray-600', 'dark:bg-gray-700', 'dark:bg-gray-800', 'dark:bg-gray-900',
    'dark:text-gray-50', 'dark:text-gray-100', 'dark:text-gray-200', 'dark:text-gray-300', 'dark:text-gray-400', 'dark:text-gray-500',
    'dark:text-gray-600', 'dark:text-gray-700', 'dark:text-gray-800', 'dark:text-gray-900',
    // Borders
    'border', 'border-gray-200', 'border-gray-700', 'dark:border-gray-700',
    // Rounded
    'rounded', 'rounded-lg', 'rounded-xl', 'rounded-full',
    // Shadows
    'shadow-sm', 'shadow-lg',
    // Hover states
    'hover:bg-gray-100', 'hover:bg-gray-700', 'dark:hover:bg-gray-700',
    // Transitions
    'transition-colors', 'duration-200',
    // Typography
    'font-semibold', 'font-bold', 'text-sm', 'text-lg', 'text-xl', 'text-2xl',
    // Custom colors
    'bg-primary', 'bg-secondary', 'text-primary',
    // Patterns for dynamic classes
    {
      pattern: /^(bg|text|border|hover:bg|dark:bg|dark:text|dark:border)-(gray|primary|secondary)-\d+$/,
    },
  ],
  theme: {
    extend: {
      colors: {
        primary: '#E1306C',
        secondary: '#405DE6',
      },
    },
  },
  plugins: [],
};
