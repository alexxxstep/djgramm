/** @type {import('tailwindcss').Config} */
const path = require('path');
const fs = require('fs');

// Determine template paths - check both Docker and host paths
const templatePaths = [];
const possibleTemplatePaths = [
  path.resolve(__dirname, 'src/templates/**/*.html'), // Host development
  path.resolve(__dirname, 'templates/**/*.html'), // Docker (src/ copied to /app)
];

// Add paths that exist
possibleTemplatePaths.forEach(templatePath => {
  const basePath = templatePath.replace('/**/*.html', '');
  if (fs.existsSync(basePath)) {
    templatePaths.push(templatePath);
  }
});

// Always include JS files
const jsPath = path.resolve(__dirname, 'frontend/src/js/**/*.js');
const templatetagsPath = path.resolve(__dirname, 'src/app/templatetags/**/*.py');

module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    ...templatePaths,
    jsPath,
    templatetagsPath,
    // Fallback patterns
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
