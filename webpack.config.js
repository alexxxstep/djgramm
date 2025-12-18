const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const BundleAnalyzerPlugin =
  require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

const isProduction =
  process.env.NODE_ENV === 'production' ||
  process.argv.includes('--mode=production');
const isAnalyze = process.argv.includes('--analyze');

module.exports = {
  mode: isProduction ? 'production' : 'development',

  entry: {
    main: './frontend/src/js/index.js',
  },

  output: {
    path: path.resolve(__dirname, 'frontend/dist'),
    filename: isProduction ? '[name].[contenthash:8].js' : '[name].js',
    chunkFilename: isProduction ? '[name].[contenthash:8].chunk.js' : '[name].chunk.js',
    clean: true, // Clean output directory before each build
  },

  module: {
    rules: [
      // CSS with PostCSS (Tailwind)
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                config: path.resolve(__dirname, 'postcss.config.js'),
              },
            },
          },
        ],
      },
    ],
  },

  plugins: [
    new MiniCssExtractPlugin({
      filename: 'styles.css',
    }),
    ...(isAnalyze ? [new BundleAnalyzerPlugin()] : []),
  ],

  optimization: {
    minimize: isProduction,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: isProduction, // Remove console.log in production
            drop_debugger: isProduction,
            pure_funcs: isProduction ? ['console.log', 'console.info', 'console.debug'] : [],
          },
        },
        extractComments: false,
      }),
    ],
    // Tree shaking
    usedExports: true,
    sideEffects: false,
    // Code splitting
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
          reuseExistingChunk: true,
        },
        common: {
          name: 'common',
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
        utils: {
          test: /[\\/]frontend[\\/]src[\\/]js[\\/]utils[\\/]/,
          name: 'utils',
          priority: 8,
          reuseExistingChunk: true,
        },
      },
    },
  },

  // Source maps for debugging
  devtool: isProduction ? false : 'eval-source-map',

  // Resolve imports
  resolve: {
    extensions: ['.js', '.json'],
    alias: {
      '@': path.resolve(__dirname, 'frontend/src'),
    },
  },
};
