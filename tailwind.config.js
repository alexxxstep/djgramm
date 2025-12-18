/** @type {import('tailwindcss').Config} */
const path = require('path');

module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    // In Docker: src is mounted at /app, so templates are at /app/templates
    // On host: templates are at src/templates (relative to project root)
    path.resolve(__dirname, 'src/templates/**/*.html'),
    path.resolve(__dirname, 'src/app/templatetags/**/*.py'),
    path.resolve(__dirname, 'frontend/src/js/**/*.js'),
    // Fallback for Docker (when __dirname is /app)
    path.resolve(__dirname, 'templates/**/*.html'),
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
