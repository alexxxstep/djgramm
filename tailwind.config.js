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
  content: {
    files: contentPaths,
    // Custom extractor for Django templates
    // Tailwind's default extractor may not properly handle Django template syntax
    // We need to extract classes from class="..." attributes even with {% %} tags
    extract: {
      // For HTML files (Django templates)
      html: (content) => {
        // Extract all class attributes, handling both single and double quotes
        // This works even with Django template tags like {% url %} and {{ variables }}
        const classRegex = /class\s*=\s*["']([^"']+)["']/g;
        const classes = [];
        let match;

        while ((match = classRegex.exec(content)) !== null) {
          // Split by spaces to get individual classes
          const classList = match[1].split(/\s+/).filter(c => c.trim());
          classes.push(...classList);
        }

        // Also try to find classes in Django template tags that might contain class attributes
        // This handles cases like: {% if condition %}class="..."{% endif %}
        const templateClassRegex = /{%[^%]*class\s*=\s*["']([^"']+)["'][^%]*%}/g;
        while ((match = templateClassRegex.exec(content)) !== null) {
          const classList = match[1].split(/\s+/).filter(c => c.trim());
          classes.push(...classList);
        }

        const uniqueClasses = [...new Set(classes)];
        console.log(`[Tailwind Extractor] Found ${uniqueClasses.length} unique classes in HTML`);

        return uniqueClasses.join(' ');
      },
      // For Python files (templatetags)
      py: (content) => {
        // Extract class names from Python strings that might contain Tailwind classes
        const stringRegex = /['"]([^'"]*class[^'"]*)['"]/g;
        const classes = [];
        let match;

        while ((match = stringRegex.exec(content)) !== null) {
          const text = match[1];
          // Look for class="..." patterns in strings
          const classMatch = text.match(/class\s*=\s*["']([^"']+)["']/);
          if (classMatch) {
            const classList = classMatch[1].split(/\s+/).filter(c => c.trim());
            classes.push(...classList);
          }
        }

        return [...new Set(classes)].join(' ');
      },
    },
  },
  // Safelist critical classes - ensures they're always included
  // This is necessary because Tailwind may not detect all classes in Django templates
  // Using aggressive patterns to guarantee all needed classes are generated
  safelist: [
    // Pattern 1: All color utilities (bg, text, border) with all shades
    {
      pattern: /^(bg|text|border)-(gray|primary|secondary|white|black|red|green|blue)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
    // Pattern 2: Dark mode color variants
    {
      pattern: /^dark:(bg|text|border)-(gray|primary|secondary|white|black|red|green|blue)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
    // Pattern 3: Hover color variants
    {
      pattern: /^hover:(bg|text|border)-(gray|primary|secondary|white|black|red|green|blue)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
    // Pattern 4: Dark hover variants
    {
      pattern: /^dark:hover:(bg|text|border)-(gray|primary|secondary|white|black|red|green|blue)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
    // Pattern 5: Spacing utilities (all numbers)
    {
      pattern: /^(p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap|space-x|space-y)-[0-9]+$/,
    },
    // Pattern 6: Sizing utilities (all numbers)
    {
      pattern: /^(w|h|max-w|min-w|max-h|min-h|min-h-screen)-[0-9]+$/,
    },
    // Pattern 7: Layout and utility classes
    {
      pattern: /^(flex|grid|block|hidden|inline|inline-block|items-|justify-|text-|font-|rounded|shadow|border|transition|duration|z-|sticky|relative|absolute|fixed|object-|aspect-|opacity|group-hover|hover|dark|bg-gradient|from-|to-|bg-clip|text-transparent)/,
    },
    // Specific classes that are definitely used
    'flex', 'grid', 'block', 'hidden', 'inline', 'inline-block',
    'flex-col', 'flex-row', 'flex-1', 'flex-shrink-0',
    'items-center', 'items-start', 'justify-between', 'justify-center', 'justify-start',
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
