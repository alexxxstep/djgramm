// Post detail page functionality
(function() {
    // Get CSRF token
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.content || '';
    }

    // =========================================================================
    // LIKE BUTTON
    // =========================================================================
    function initLikeButton() {
        const likeBtn = document.querySelector('.like-btn');
        if (!likeBtn) return;

        const postId = likeBtn.dataset.postId;
        const csrfToken = getCSRFToken();

        likeBtn.addEventListener('click', async function() {
            try {
                const response = await fetch(`/post/${postId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();

                const likesSpan = document.getElementById(`likes-count-${postId}`);
                const svg = likeBtn.querySelector('svg');

                if (likesSpan) {
                    likesSpan.textContent = data.likes_count;

                    // Show/hide based on count
                    if (data.likes_count > 0) {
                        likesSpan.classList.remove('hidden');
                    } else {
                        likesSpan.classList.add('hidden');
                    }
                }

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
    }

    // =========================================================================
    // IMAGE CAROUSEL
    // =========================================================================
    function initImageCarousel() {
        const images = document.querySelectorAll('.carousel-image');
        const dots = document.querySelectorAll('.carousel-dot');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const currentImageSpan = document.getElementById('current-image');

        if (images.length <= 1) return;

        let currentIndex = 0;

        function showImage(index) {
            images.forEach(img => img.classList.add('hidden'));
            images[index].classList.remove('hidden');

            dots.forEach((dot, i) => {
                if (i === index) {
                    dot.classList.remove('bg-white/50');
                    dot.classList.add('bg-white');
                } else {
                    dot.classList.remove('bg-white');
                    dot.classList.add('bg-white/50');
                }
            });

            if (currentImageSpan) {
                currentImageSpan.textContent = index + 1;
            }

            currentIndex = index;
        }

        function nextImage() {
            const newIndex = (currentIndex + 1) % images.length;
            showImage(newIndex);
        }

        function prevImage() {
            const newIndex = (currentIndex - 1 + images.length) % images.length;
            showImage(newIndex);
        }

        if (nextBtn) nextBtn.addEventListener('click', nextImage);
        if (prevBtn) prevBtn.addEventListener('click', prevImage);

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => showImage(index));
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') nextImage();
            if (e.key === 'ArrowLeft') prevImage();
        });

        // Touch swipe support
        let touchStartX = 0;
        let touchEndX = 0;
        const carousel = document.getElementById('image-carousel');

        if (carousel) {
            carousel.addEventListener('touchstart', (e) => {
                touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });

            carousel.addEventListener('touchend', (e) => {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            }, { passive: true });
        }

        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    nextImage();
                } else {
                    prevImage();
                }
            }
        }
    }

    // =========================================================================
    // POST MENU (Edit/Delete)
    // =========================================================================
    function initPostMenu() {
        const menuContainer = document.querySelector('.post-menu');
        if (!menuContainer) return;

        const toggleBtn = menuContainer.querySelector('.menu-toggle');
        const dropdown = menuContainer.querySelector('.menu-dropdown');

        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });

        document.addEventListener('click', function(e) {
            if (!menuContainer.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                dropdown.classList.add('hidden');
            }
        });
    }

    // =========================================================================
    // COMMENTS
    // =========================================================================
    function initComments() {
        const postId = window.POST_ID;
        const commentForm = document.getElementById('comment-form');
        const commentInput = document.getElementById('comment-input');
        const postBtn = document.getElementById('post-comment-btn');
        const commentsList = document.getElementById('comments-list');
        const commentsCount = document.getElementById('comments-count');
        const noComments = document.getElementById('no-comments');
        const commentsSection = document.getElementById('comments-section');
        const commentToggleBtn = document.querySelector('.comment-toggle-btn');
        const csrfToken = getCSRFToken();

        if (!commentForm || !postId) return;

        commentInput.addEventListener('input', function() {
            postBtn.disabled = !this.value.trim();
        });

        if (commentToggleBtn) {
            commentToggleBtn.addEventListener('click', function() {
                commentInput.focus();
                commentsSection.scrollTop = commentsSection.scrollHeight;
            });
        }

        commentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const text = commentInput.value.trim();
            if (!text) return;

            postBtn.disabled = true;
            try {
                const response = await fetch(`/post/${postId}/comment/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text: text })
                });
                const data = await response.json();

                if (data.success) {
                    if (noComments) noComments.remove();

                    const comment = data.comment;
                    const avatarHtml = comment.author_avatar
                        ? `<img src="${comment.author_avatar}" alt="${comment.author}" class="w-8 h-8 rounded-full object-cover">`
                        : `<div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-semibold">${comment.author.charAt(0).toUpperCase()}</div>`;

                    const commentHtml = `
                        <div class="flex space-x-3 mb-4 comment-item" data-comment-id="${comment.id}">
                            <a href="/profile/${comment.author}/">${avatarHtml}</a>
                            <div class="flex-1">
                                <p class="comment-text text-gray-800 text-sm">
                                    <a href="/profile/${comment.author}/" class="font-semibold mr-1">${comment.author}</a>
                                    <span class="comment-text-content">${comment.text}</span>
                                </p>
                                <div class="flex items-center space-x-3 mt-1">
                                    <span class="text-gray-400 text-xs">Just now</span>
                                    <button class="edit-comment-btn text-gray-400 hover:text-primary text-xs" data-comment-id="${comment.id}">Edit</button>
                                    <button class="delete-comment-btn text-gray-400 hover:text-red-500 text-xs" data-comment-id="${comment.id}">Delete</button>
                                </div>
                            </div>
                        </div>
                    `;
                    commentsList.insertAdjacentHTML('beforeend', commentHtml);

                    // Update comments count display
                    commentsCount.textContent = data.comments_count;
                    if (data.comments_count > 0) {
                        commentsCount.classList.remove('hidden');
                    } else {
                        commentsCount.classList.add('hidden');
                    }

                    commentInput.value = '';
                    commentsSection.scrollTop = commentsSection.scrollHeight;

                    const newComment = commentsList.querySelector(`[data-comment-id="${comment.id}"]`);
                    const deleteBtn = newComment.querySelector('.delete-comment-btn');
                    const editBtn = newComment.querySelector('.edit-comment-btn');
                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', () => deleteComment(comment.id));
                    }
                    if (editBtn) {
                        editBtn.addEventListener('click', () => startEditComment(comment.id));
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
            postBtn.disabled = !commentInput.value.trim();
        });

        async function deleteComment(commentId) {
            try {
                const response = await fetch(`/post/${postId}/comment/${commentId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();

                if (data.success) {
                    const commentEl = commentsList.querySelector(`[data-comment-id="${commentId}"]`);
                    if (commentEl) commentEl.remove();

                    // Update comments count display
                    commentsCount.textContent = data.comments_count;
                    if (data.comments_count > 0) {
                        commentsCount.classList.remove('hidden');
                    } else {
                        commentsCount.classList.add('hidden');
                        commentsList.innerHTML = '<p class="text-gray-400 text-sm text-center py-4" id="no-comments">No comments yet</p>';
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function startEditComment(commentId) {
            const commentEl = commentsList.querySelector(`[data-comment-id="${commentId}"]`);
            if (!commentEl) return;

            const textContent = commentEl.querySelector('.comment-text-content');
            const currentText = textContent.textContent.trim();

            const editForm = document.createElement('div');
            editForm.className = 'edit-form mt-2';
            editForm.innerHTML = `
                <input type="text" class="edit-input w-full text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-primary" value="${currentText}" maxlength="500">
                <div class="flex space-x-2 mt-1">
                    <button type="button" class="save-edit-btn text-primary text-xs font-semibold">Save</button>
                    <button type="button" class="cancel-edit-btn text-gray-400 text-xs">Cancel</button>
                </div>
            `;

            textContent.classList.add('hidden');
            textContent.parentNode.appendChild(editForm);

            const editInput = editForm.querySelector('.edit-input');
            editInput.focus();
            editInput.setSelectionRange(editInput.value.length, editInput.value.length);

            editForm.querySelector('.save-edit-btn').addEventListener('click', () => saveEditComment(commentId, editInput.value));
            editForm.querySelector('.cancel-edit-btn').addEventListener('click', () => cancelEditComment(commentId));

            editInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    saveEditComment(commentId, editInput.value);
                } else if (e.key === 'Escape') {
                    cancelEditComment(commentId);
                }
            });
        }

        async function saveEditComment(commentId, newText) {
            newText = newText.trim();
            if (!newText) return;

            try {
                const response = await fetch(`/post/${postId}/comment/${commentId}/edit/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text: newText })
                });
                const data = await response.json();

                if (data.success) {
                    const commentEl = commentsList.querySelector(`[data-comment-id="${commentId}"]`);
                    const textContent = commentEl.querySelector('.comment-text-content');
                    const editForm = commentEl.querySelector('.edit-form');

                    textContent.textContent = data.text;
                    textContent.classList.remove('hidden');
                    if (editForm) editForm.remove();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function cancelEditComment(commentId) {
            const commentEl = commentsList.querySelector(`[data-comment-id="${commentId}"]`);
            if (!commentEl) return;

            const textContent = commentEl.querySelector('.comment-text-content');
            const editForm = commentEl.querySelector('.edit-form');

            textContent.classList.remove('hidden');
            if (editForm) editForm.remove();
        }

        document.querySelectorAll('.delete-comment-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteComment(btn.dataset.commentId));
        });
        document.querySelectorAll('.edit-comment-btn').forEach(btn => {
            btn.addEventListener('click', () => startEditComment(btn.dataset.commentId));
        });
    }

    // Initialize all
    function init() {
        initLikeButton();
        initImageCarousel();
        initPostMenu();
        initComments();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

