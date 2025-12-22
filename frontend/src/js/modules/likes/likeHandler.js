/**
 * Centralized like button handler using event delegation
 * Works for dynamically added buttons
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
 * Handle like button click using event delegation
 */
async function handleLike(button) {
  const postId = button.dataset.postId || button.id?.replace('like-btn-', '');

  if (!postId) {
    console.error('Like button missing data-post-id or id attribute');
    return;
  }

  // Prevent double-click
  if (button.dataset.processing === 'true') {
    return;
  }

  button.dataset.processing = 'true';

  try {
    const likesSpan = document.getElementById(`likes-count-${postId}`);
    await toggleLike(postId, button, likesSpan);
  } catch (error) {
    console.error('Error toggling like:', error);
  } finally {
    button.dataset.processing = 'false';
  }
}

// Event delegation - catches clicks on like buttons anywhere in document
document.addEventListener('click', function(e) {
  // Check if click is on like button or inside it
  const btn = e.target.closest('.like-btn, [id^="like-btn-"], [data-like-btn]');
  if (btn) {
    e.preventDefault();
    e.stopPropagation();
    handleLike(btn);
  }
});
