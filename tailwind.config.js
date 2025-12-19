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
    contentPaths.push(path.join(templatePath, '**/*.html'));
    console.log(`[Tailwind] Found templates at: ${templatePath}`);
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

// Fallback - catch all HTML files (safety net)
contentPaths.push(path.resolve(__dirname, '**/*.html'));

console.log(`[Tailwind] Content paths: ${contentPaths.length} paths configured`);

module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: contentPaths,
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
