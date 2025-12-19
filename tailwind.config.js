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
  // Using default extractor - Tailwind's default extractor works well with HTML
  // Django template syntax {% %} and {{ }} don't interfere with class="..." parsing
  // Safelist critical classes - ensures they're always included
  // This guarantees CSS generation even if Tailwind doesn't detect all classes
  safelist: [
    // Pattern 1: Base color utilities (without variants - Tailwind handles variants automatically)
    {
      pattern: /^(bg|text|border)-(gray|primary|secondary|white|black|red|green|blue)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
    // Pattern 2: Spacing utilities
    {
      pattern: /^(p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap|space-x|space-y)-[0-9]+$/,
    },
    // Pattern 3: Sizing utilities
    {
      pattern: /^(w|h|max-w|min-w|max-h|min-h|min-h-screen)-[0-9]+$/,
    },
    // Pattern 4: Layout utilities
    {
      pattern: /^(flex|grid|block|hidden|inline|inline-block|items-|justify-|text-|font-|rounded|shadow|border|transition|duration|z-|sticky|relative|absolute|fixed|object-|aspect-|opacity)/,
    },
    // Specific classes that are definitely used (explicit list for guaranteed generation)
    'flex', 'grid', 'block', 'hidden', 'inline', 'inline-block',
    'flex-col', 'flex-row', 'flex-1', 'flex-shrink-0',
    'items-center', 'items-start', 'items-end', 'justify-between', 'justify-center', 'justify-start',
    'max-w-2xl', 'max-w-4xl', 'max-w-5xl', 'mx-auto', 'px-4', 'py-2', 'py-4', 'py-6',
    'mb-2', 'mb-4', 'mb-8', 'mt-2', 'mt-4', 'gap-4', 'gap-8', 'space-x-4', 'space-x-8', 'space-y-6',
    'w-full', 'h-full', 'w-10', 'h-10', 'w-12', 'h-12', 'w-32', 'h-32', 'w-40', 'h-40',
    'min-h-screen', 'aspect-square',
    'bg-white', 'bg-gray-50', 'bg-gray-100', 'bg-gray-200', 'bg-gray-300', 'bg-gray-400', 'bg-gray-500',
    'bg-gray-600', 'bg-gray-700', 'bg-gray-800', 'bg-gray-900', 'bg-primary', 'bg-secondary',
    'text-white', 'text-gray-50', 'text-gray-100', 'text-gray-200', 'text-gray-300', 'text-gray-400', 'text-gray-500',
    'text-gray-600', 'text-gray-700', 'text-gray-800', 'text-gray-900', 'text-primary',
    'dark:bg-gray-50', 'dark:bg-gray-100', 'dark:bg-gray-200', 'dark:bg-gray-300', 'dark:bg-gray-400', 'dark:bg-gray-500',
    'dark:bg-gray-600', 'dark:bg-gray-700', 'dark:bg-gray-800', 'dark:bg-gray-900',
    'dark:text-gray-50', 'dark:text-gray-100', 'dark:text-gray-200', 'dark:text-gray-300', 'dark:text-gray-400', 'dark:text-gray-500',
    'dark:text-gray-600', 'dark:text-gray-700', 'dark:text-gray-800', 'dark:text-gray-900',
    'border', 'border-b', 'border-gray-100', 'border-gray-200', 'border-gray-300', 'border-gray-600', 'border-gray-700', 'border-gray-800',
    'dark:border-gray-700', 'dark:border-gray-800',
    'rounded', 'rounded-lg', 'rounded-xl', 'rounded-full',
    'shadow-sm', 'shadow-md', 'shadow-lg',
    'hover:bg-gray-50', 'hover:bg-gray-100', 'hover:bg-gray-300', 'hover:bg-gray-700', 'hover:shadow-md', 'hover:shadow-lg', 'hover:opacity-75', 'hover:opacity-100', 'hover:underline',
    'dark:hover:bg-gray-600', 'dark:hover:bg-gray-700', 'dark:hover:shadow-lg',
    'transition-colors', 'transition-all', 'duration-200', 'duration-300',
    'font-light', 'font-semibold', 'font-bold', 'text-sm', 'text-lg', 'text-xl', 'text-2xl', 'text-5xl',
    'sticky', 'top-0', 'z-50', 'z-10',
    'object-cover', 'object-contain', 'overflow-hidden',
    'bg-gradient-to-r', 'bg-gradient-to-br', 'from-primary', 'to-secondary', 'bg-clip-text', 'text-transparent',
    'group', 'group-hover:opacity-75', 'group-hover:opacity-100',
    'whitespace-pre-line',
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
