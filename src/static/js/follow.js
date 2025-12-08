// Follow/Unfollow button functionality
(function() {
    function getCsrfToken() {
        // Try multiple ways to get CSRF token
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name=csrf-token]')?.content ||
                     document.querySelector('[name=csrf-token]')?.content;
        return token;
    }

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
                const originalText = this.textContent;
                this.disabled = true;
                this.textContent = '...';

                try {
                    const response = await fetch(`/profile/${username}/follow/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json',
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    console.log('Response data:', data);

                    if (data.error) {
                        alert(data.error);
                        this.disabled = false;
                        this.textContent = originalText;
                        return;
                    }

                    // Update button text and style
                    if (data.is_following) {
                        this.textContent = 'Unfollow';
                        this.dataset.following = 'true';
                        this.classList.remove('bg-primary', 'text-white', 'hover:bg-opacity-90');
                        this.classList.add('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
                    } else {
                        this.textContent = 'Follow';
                        this.dataset.following = 'false';
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
                            btn.textContent = data.is_following ? 'Unfollow' : 'Follow';
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
                } catch (error) {
                    console.error('Error:', error);
                    alert('Something went wrong. Please try again.');
                    this.textContent = originalText;
                } finally {
                    this.disabled = false;
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
})();

