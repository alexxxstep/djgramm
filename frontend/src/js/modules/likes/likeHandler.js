/**
 * Centralized like button handler
 * Eliminates code duplication between feed.js and post_detail.js
 */

import { ajaxPost } from '../../utils/ajax.js';

/**
 * Update like button UI state
 * @param {HTMLElement} button - Like button element
 * @param {HTMLElement} likesSpan - Likes count span element
 * @param {Object} data - Response data from server
 */
export function updateLikeUI(button, likesSpan, data) {
  const svg = button.querySelector('svg');

  // Update likes count
  if (likesSpan) {
    likesSpan.textContent = data.likes_count;

    // Show/hide based on count
    if (data.likes_count > 0) {
      likesSpan.classList.remove('hidden');
    } else {
      likesSpan.classList.add('hidden');
    }
  }

  // Update button state
  if (data.liked) {
    button.classList.add('text-red-500');
    if (svg) {
      svg.setAttribute('fill', 'currentColor');
    }
  } else {
    button.classList.remove('text-red-500');
    if (svg) {
      svg.setAttribute('fill', 'none');
    }
  }
}

/**
 * Toggle like for a post
 * @param {string|number} postId - Post ID
 * @param {HTMLElement} button - Like button element
 * @param {HTMLElement} likesSpan - Likes count span element (optional)
 * @returns {Promise<Object>} Response data
 */
export async function toggleLike(postId, button, likesSpan = null) {
  // Get likes span if not provided
  if (!likesSpan) {
    likesSpan = document.getElementById(`likes-count-${postId}`);
  }

  // Show loading state
  const originalDisabled = button.disabled;
  const originalOpacity = button.style.opacity;
  const originalCursor = button.style.cursor;

  button.disabled = true;
  button.style.opacity = '0.6';
  button.style.cursor = 'wait';

  try {
    const data = await ajaxPost(`/post/${postId}/like/`, {}, {
      errorMessage: 'Failed to like post. Please try again.'
    });

    // Update UI
    updateLikeUI(button, likesSpan, data);

    return data;
  } catch (error) {
    // Restore original state on error
    const svg = button.querySelector('svg');
    const wasLiked = button.classList.contains('text-red-500');

    if (wasLiked) {
      button.classList.add('text-red-500');
      if (svg) {
        svg.setAttribute('fill', 'currentColor');
      }
    } else {
      button.classList.remove('text-red-500');
      if (svg) {
        svg.setAttribute('fill', 'none');
      }
    }
    throw error;
  } finally {
    // Always restore button state
    button.disabled = originalDisabled;
    button.style.opacity = originalOpacity;
    button.style.cursor = originalCursor;
  }
}

/**
 * Initialize like buttons
 * @param {string} selector - CSS selector for like buttons (default: '.like-btn')
 * @param {Object} options - Options
 * @param {boolean} options.skipPostDetail - Skip initialization on post detail pages
 */
export function initLikeButtons(selector = '.like-btn', options = {}) {
  const { skipPostDetail = false } = options;

  // Skip if on post detail page
  if (skipPostDetail) {
    const isPostDetailUrl = window.location.pathname.match(/^\/post\/\d+\/?$/);
    const hasCommentsSection = document.getElementById('comments-section');
    const hasPostMenu = document.querySelector('.post-menu');

    if (isPostDetailUrl || (hasCommentsSection && hasPostMenu)) {
      return;
    }
  }

  document.querySelectorAll(selector).forEach(btn => {
    // Skip if handler already attached
    if (btn.dataset.handlerAttached === 'true' || btn.dataset.postDetailHandler === 'true') {
      return;
    }

    btn.dataset.handlerAttached = 'true';

    btn.addEventListener('click', async function(e) {
      e.preventDefault();
      e.stopPropagation();

      const button = this;
      const postId = button.dataset.postId;

      if (!postId) {
        console.warn('Like button: postId not found');
        return;
      }

      // Check if already processing
      if (button.dataset.processing === 'true') {
        return;
      }

      button.dataset.processing = 'true';

      try {
        await toggleLike(postId, button);
      } catch (error) {
        console.error('Error toggling like:', error);
      } finally {
        button.dataset.processing = 'false';
      }
    }, { once: false, passive: false });
  });
}

