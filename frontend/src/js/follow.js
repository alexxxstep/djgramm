/**
 * Follow/Unfollow using event delegation
 * Works for dynamically added buttons
 */
import { getCsrfToken } from './utils/csrf.js';
import { ajaxPost } from './utils/ajax.js';
import { showLoading, hideLoading } from './utils/ajax.js';

(function () {
  'use strict';

  /**
   * Handle follow/unfollow button click
   */
  async function handleFollow(button) {
    const username = button.dataset.username;
    if (!username) {
      console.error('Follow button missing data-username attribute');
      return;
    }

    const isFollowing = button.dataset.following === 'true';
    const url = `/profile/${username}/follow/`;

    // Show loading state
    showLoading(button);

    try {
      const data = await ajaxPost(
        url,
        {},
        {
          errorMessage: 'Failed to follow/unfollow user. Please try again.',
        }
      );

      if (data.error) {
        alert(data.error);
        return;
      }

      // Update button state
      const newIsFollowing = data.is_following;
      const newText = newIsFollowing ? 'Unfollow' : 'Follow';

      // Hide loading first, then update text
      hideLoading(button);

      // Update button state
      button.dataset.following = newIsFollowing ? 'true' : 'false';
      button.textContent = newText;
      // Update originalText for future hideLoading calls
      button.dataset.originalText = newText;

      // Update button classes
      if (newIsFollowing) {
        button.classList.remove(
          'bg-primary',
          'text-white',
          'hover:bg-opacity-90'
        );
        button.classList.add(
          'bg-gray-200',
          'dark:bg-gray-700',
          'text-gray-700',
          'dark:text-gray-300',
          'hover:bg-gray-300',
          'dark:hover:bg-gray-600'
        );
      } else {
        button.classList.remove(
          'bg-gray-200',
          'dark:bg-gray-700',
          'text-gray-700',
          'dark:text-gray-300',
          'hover:bg-gray-300',
          'dark:hover:bg-gray-600'
        );
        button.classList.add('bg-primary', 'text-white', 'hover:bg-opacity-90');
      }

      // Update all follow buttons for this user (in case there are multiple on page)
      document
        .querySelectorAll(`.follow-btn[data-username="${username}"]`)
        .forEach((btn) => {
          if (btn !== button) {
            btn.dataset.following = newIsFollowing ? 'true' : 'false';
            btn.textContent = newText;
            btn.dataset.originalText = newText;
            if (newIsFollowing) {
              btn.classList.remove(
                'bg-primary',
                'text-white',
                'hover:bg-opacity-90'
              );
              btn.classList.add(
                'bg-gray-200',
                'dark:bg-gray-700',
                'text-gray-700',
                'dark:text-gray-300',
                'hover:bg-gray-300',
                'dark:hover:bg-gray-600'
              );
            } else {
              btn.classList.remove(
                'bg-gray-200',
                'dark:bg-gray-700',
                'text-gray-700',
                'dark:text-gray-300',
                'hover:bg-gray-300',
                'dark:hover:bg-gray-600'
              );
              btn.classList.add(
                'bg-primary',
                'text-white',
                'hover:bg-opacity-90'
              );
            }
          }
        });

      // Update followers count if element exists
      const followersCountEl = document.getElementById('followers-count');
      if (followersCountEl && data.followers_count !== undefined) {
        followersCountEl.textContent = data.followers_count;
      }
    } catch (error) {
      console.error('Follow error:', error);
      // Error already handled in ajaxPost
      hideLoading(button);
    }
  }

  // Event delegation - catches clicks on .follow-btn anywhere in document
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.follow-btn');
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      handleFollow(btn);
    }
  });
})();
