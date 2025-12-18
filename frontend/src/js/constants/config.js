/**
 * Application constants and configuration
 */

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  LIKE_POST: (postId) => `/post/${postId}/like/`,
  COMMENT_POST: (postId) => `/post/${postId}/comment/`,
  DELETE_COMMENT: (postId, commentId) => `/post/${postId}/comment/${commentId}/delete/`,
  EDIT_COMMENT: (postId, commentId) => `/post/${postId}/comment/${commentId}/edit/`,
  FOLLOW_USER: (username) => `/profile/${username}/follow/`,
};

/**
 * Selectors
 */
export const SELECTORS = {
  LIKE_BUTTON: '.like-btn',
  FOLLOW_BUTTON: '.follow-btn',
  COMMENT_INPUT: '#comment-input',
  COMMENT_FORM: '#comment-form',
  COMMENTS_LIST: '#comments-list',
  POST_MENU: '.post-menu',
  THEME_TOGGLE: '#theme-toggle',
};

/**
 * Event names
 */
export const EVENTS = {
  THEME_CHANGED: 'theme:changed',
  POST_LIKED: 'post:liked',
  COMMENT_ADDED: 'comment:added',
  COMMENT_DELETED: 'comment:deleted',
  USER_FOLLOWED: 'user:followed',
};

/**
 * Configuration values
 */
export const CONFIG = {
  DEBOUNCE_DELAY: 300,
  THROTTLE_DELAY: 1000,
  MAX_COMMENT_LENGTH: 500,
  MAX_FILES: 10,
  AJAX_TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  THEME: 'djgramm-theme',
  USER_PREFERENCES: 'djgramm-user-preferences',
};

