// Feed page functionality - Like buttons
(function() {
    function initLikes() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         document.querySelector('meta[name=csrf-token]')?.content;

        if (!csrfToken) return;

        document.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', async function() {
                const postId = this.dataset.postId;
                try {
                    const response = await fetch(`/post/${postId}/like/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json'
                        }
                    });
                    const data = await response.json();

                    // Update UI
                    const likesSpan = document.getElementById(`likes-count-${postId}`);
                    const likeBtn = document.getElementById(`like-btn-${postId}`);
                    const svg = likeBtn.querySelector('svg');

                    if (likesSpan) likesSpan.textContent = data.likes_count;

                    if (data.liked) {
                        likeBtn.classList.add('text-red-500');
                        svg.setAttribute('fill', 'currentColor');
                    } else {
                        likeBtn.classList.remove('text-red-500');
                        svg.setAttribute('fill', 'none');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLikes);
    } else {
        initLikes();
    }
})();

