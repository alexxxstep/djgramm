// Follow/Unfollow button functionality
import { getCsrfToken } from './utils/csrf.js';
import { ajaxPost, showLoading, hideLoading } from './utils/ajax.js';

// Export initialization function for dynamic import
export function initFollow() {
    function initFollowButtons() {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            console.warn('CSRF token not found');
            return;
        }

        const buttons = document.querySelectorAll('.follow-btn');
        console.log('Found follow buttons:', buttons.length);

        buttons.forEach(btn => {
            // Remove any existing listeners to avoid duplicates
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);

            newBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                e.stopPropagation();

                const username = this.dataset.username;
                const isFollowing = this.dataset.following === 'true';

                console.log('Follow button clicked:', username, 'isFollowing:', isFollowing);

                // Disable button during request
                showLoading(this);

                try {
                    const data = await ajaxPost(`/profile/${username}/follow/`, {}, {
                        errorMessage: 'Failed to follow/unfollow user. Please try again.'
                    });
                    console.log('Response data:', data);

                    if (data.error) {
                        alert(data.error);
                        hideLoading(this);
                        return;
                    }

                    // Update button text and style
                    const newText = data.is_following ? 'Unfollow' : 'Follow';
                    if (data.is_following) {
                        this.textContent = newText;
                        this.dataset.following = 'true';
                        this.dataset.originalText = newText; // Update original text for hideLoading
                        this.classList.remove('bg-primary', 'text-white', 'hover:bg-opacity-90');
                        this.classList.add('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
                    } else {
                        this.textContent = newText;
                        this.dataset.following = 'false';
                        this.dataset.originalText = newText; // Update original text for hideLoading
                        this.classList.remove('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
                        this.classList.add('bg-primary', 'text-white', 'hover:bg-opacity-90');
                    }

                    // Update followers count if element exists
                    const followersCountEl = document.getElementById('followers-count');
                    if (followersCountEl) {
                        followersCountEl.textContent = data.followers_count;
                    }

                    // Update all follow buttons for this user (in case there are multiple on page)
                    document.querySelectorAll(`.follow-btn[data-username="${username}"]`).forEach(btn => {
                        if (btn !== this) {
                            btn.textContent = newText;
                            btn.dataset.following = data.is_following ? 'true' : 'false';
                            if (data.is_following) {
                                btn.classList.remove('bg-primary', 'text-white', 'hover:bg-opacity-90');
                                btn.classList.add('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
                            } else {
                                btn.classList.remove('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
                                btn.classList.add('bg-primary', 'text-white', 'hover:bg-opacity-90');
                            }
                        }
                    });

                    // Hide loading indicator after successful update
                    hideLoading(this);
                } catch (error) {
                    // Error already handled in ajaxPost
                    hideLoading(this);
                }
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFollowButtons);
    } else {
        initFollowButtons();
    }
}

// Auto-initialize when loaded directly (not via dynamic import)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFollow);
} else {
    initFollow();
}

