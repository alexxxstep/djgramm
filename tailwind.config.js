/** @type {import('tailwindcss').Config} */
const path = require('path');

module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    // Templates - try all possible paths (Docker and host)
    path.resolve(__dirname, 'templates/**/*.html'), // Docker: src/templates copied to /app/templates
    path.resolve(__dirname, 'src/templates/**/*.html'), // Host development
    // Templatetags - try all possible paths
    path.resolve(__dirname, 'app/templatetags/**/*.py'), // Docker: src/app/templatetags copied to /app/app/templatetags
    path.resolve(__dirname, 'src/app/templatetags/**/*.py'), // Host development
    // JavaScript files
    path.resolve(__dirname, 'frontend/src/js/**/*.js'),
    // Fallback - catch all HTML files
    path.resolve(__dirname, '**/*.html'),
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
