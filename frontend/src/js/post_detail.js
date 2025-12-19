// Post detail page functionality
import { getCsrfToken } from './utils/csrf.js';
import { ajaxPost } from './utils/ajax.js';
// Like buttons are handled by event delegation in likeHandler.js

// Prevent multiple initializations
let isInitialized = false;

// Export initialization function for dynamic import
export function initPostDetail() {
    if (isInitialized) {
        console.warn('post_detail.js: Already initialized, skipping');
        return;
    }

    // Check if we're on a post detail page
    // Must have comments-section OR post-menu OR be on /post/<id>/ URL
    const isPostDetailPage = document.getElementById('comments-section') ||
                             document.querySelector('.post-menu') ||
                             window.location.pathname.match(/^\/post\/\d+\/?$/);

    if (!isPostDetailPage) {
        console.log('post_detail.js: Not a post detail page, skipping');
        return;
    }

    isInitialized = true;
    console.log('post_detail.js: Initializing...');

    // =========================================================================
    // LIKE BUTTON
    // =========================================================================
    // Like buttons are now handled by event delegation in likeHandler.js
    // No initialization needed here
    function initLikeButton() {
        console.log('post_detail.js: Like buttons handled by event delegation');
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
        if (!menuContainer) {
            console.warn('post_detail.js: Post menu not found');
            return;
        }

        const toggleBtn = menuContainer.querySelector('.menu-toggle');
        const dropdown = menuContainer.querySelector('.menu-dropdown');

        if (!toggleBtn || !dropdown) {
            console.warn('post_detail.js: Menu toggle or dropdown not found');
            return;
        }

        console.log('post_detail.js: Post menu initialized');

        // Remove any existing listeners
        const newToggleBtn = toggleBtn.cloneNode(true);
        toggleBtn.parentNode.replaceChild(newToggleBtn, toggleBtn);

        newToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('post_detail.js: Menu toggle clicked');
            dropdown.classList.toggle('hidden');
            console.log('post_detail.js: Menu dropdown hidden:', dropdown.classList.contains('hidden'));
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!menuContainer.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });

        // Close menu on Escape key
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
        // Get commentInput reference once at the start
        let commentInput = document.getElementById('comment-input');

        // Apply dark mode styles to comment input - FORCE white text in dark mode
        function updateCommentInputStyles() {
            if (!commentInput) {
                commentInput = document.getElementById('comment-input');
                if (!commentInput) return;
            }

            const isDark = document.documentElement.classList.contains('dark');

            if (isDark) {
                // FORCE white text - multiple methods with maximum specificity
                commentInput.style.setProperty('color', '#ffffff', 'important');
                commentInput.style.color = '#ffffff';

                // Remove any conflicting Tailwind classes
                commentInput.classList.remove('text-gray-900', 'text-gray-800', 'text-gray-700');

                // Create/update dynamic style tag with maximum specificity
                let style = document.getElementById('comment-input-dark-styles');
                if (!style) {
                    style = document.createElement('style');
                    style.id = 'comment-input-dark-styles';
                    document.head.appendChild(style);
                }
                style.textContent = `
                    html.dark #comment-input,
                    html.dark input#comment-input,
                    html.dark form#comment-form input#comment-input,
                    .dark #comment-input,
                    .dark input#comment-input,
                    .dark form#comment-form input#comment-input {
                        color: #ffffff !important;
                    }
                    html.dark #comment-input::placeholder,
                    .dark #comment-input::placeholder {
                        color: #9ca3af !important;
                    }
                `;
            } else {
                // Light mode - dark text
                commentInput.style.setProperty('color', '#111827', 'important');
                commentInput.style.color = '#111827';

                // Remove any conflicting Tailwind classes
                commentInput.classList.remove('text-white', 'text-gray-200', 'text-gray-100');

                const existingStyle = document.getElementById('comment-input-dark-styles');
                if (existingStyle) {
                    existingStyle.remove();
                }
            }
        }

        // Update styles on theme change
        const observer = new MutationObserver(() => {
            updateCommentInputStyles();
        });
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class']
        });

        // Initial update
        updateCommentInputStyles();

        // Also update when input is focused or typed (in case styles were overridden)
        if (commentInput) {
            // Force update on focus
            commentInput.addEventListener('focus', () => {
                updateCommentInputStyles();
                // Double-check after a short delay
                setTimeout(() => {
                    const isDark = document.documentElement.classList.contains('dark');
                    if (isDark) {
                        commentInput.style.setProperty('color', '#ffffff', 'important');
                        commentInput.classList.remove('text-gray-900', 'text-gray-800', 'text-gray-700');
                    } else {
                        commentInput.style.setProperty('color', '#111827', 'important');
                        commentInput.classList.remove('text-white', 'text-gray-200', 'text-gray-100');
                    }
                }, 10);
            });

            // Ensure text color is correct while typing
            commentInput.addEventListener('input', () => {
                const isDark = document.documentElement.classList.contains('dark');
                if (isDark) {
                    commentInput.style.setProperty('color', '#ffffff', 'important');
                    commentInput.style.color = '#ffffff';
                }
            });

            // Also check on blur (in case something changed)
            commentInput.addEventListener('blur', () => {
                updateCommentInputStyles();
            });

            // Periodic check (every 500ms) to ensure styles are applied
            setInterval(() => {
                if (!commentInput) return;
                const isDark = document.documentElement.classList.contains('dark');
                const currentColor = window.getComputedStyle(commentInput).color;

                if (isDark) {
                    // If color is not white (rgb(255, 255, 255)), force it
                    if (currentColor !== 'rgb(255, 255, 255)' && currentColor !== '#ffffff') {
                        commentInput.style.setProperty('color', '#ffffff', 'important');
                        commentInput.style.color = '#ffffff';
                        commentInput.classList.remove('text-gray-900', 'text-gray-800', 'text-gray-700');
                    }
                } else {
                    // Light mode - ensure dark text
                    const darkColor = 'rgb(17, 24, 39)'; // #111827
                    if (currentColor === 'rgb(255, 255, 255)' || currentColor === '#ffffff') {
                        commentInput.style.setProperty('color', '#111827', 'important');
                        commentInput.style.color = '#111827';
                        commentInput.classList.remove('text-white', 'text-gray-200', 'text-gray-100');
                    }
                }
            }, 500);

            // Also check on blur (in case something changed)
            commentInput.addEventListener('blur', () => {
                updateCommentInputStyles();
            });
        }

        // Try to get POST_ID from window or from button dataset
        let postId = window.POST_ID;

        // Fallback: try to get from like button dataset
        if (!postId) {
            const likeBtn = document.querySelector('.like-btn');
            if (likeBtn) {
                postId = likeBtn.dataset.postId;
                if (postId) {
                    window.POST_ID = postId; // Cache it
                    console.log('post_detail.js: POST_ID found from button dataset for comments:', postId);
                }
            }
        }

        const commentForm = document.getElementById('comment-form');
        // commentInput already declared above, reuse it
        if (!commentInput) {
            commentInput = document.getElementById('comment-input');
        }
        const postBtn = document.getElementById('post-comment-btn');
        const commentsList = document.getElementById('comments-list');
        const commentsCount = document.getElementById('comments-count');
        const noComments = document.getElementById('no-comments');
        const commentsSection = document.getElementById('comments-section');
        const commentToggleBtn = document.querySelector('.comment-toggle-btn');

        if (!commentForm || !postId) {
            console.warn('post_detail.js: Comment form or POST_ID not found. Comment form:', !!commentForm, 'POST_ID:', postId);
            return;
        }

        console.log('post_detail.js: Initializing comments for post', postId);

        // Remove any existing listeners to avoid duplicates
        const newCommentForm = commentForm.cloneNode(true);
        commentForm.parentNode.replaceChild(newCommentForm, commentForm);

        // Get new references after cloning
        const newCommentInput = document.getElementById('comment-input');
        const newPostBtn = document.getElementById('post-comment-btn');

        if (!newCommentInput || !newPostBtn) {
            console.error('post_detail.js: Failed to get comment input or button after cloning');
            return;
        }

        newCommentInput.addEventListener('input', function() {
            newPostBtn.disabled = !this.value.trim();
        });

        if (commentToggleBtn) {
            commentToggleBtn.addEventListener('click', function() {
                newCommentInput.focus();
                commentsSection.scrollTop = commentsSection.scrollHeight;
            });
        }

        let isSubmitting = false;
        let lastSubmittedText = ''; // Track last submitted text to prevent duplicates
        let lastSubmitTime = 0; // Track last submit time

        // Initialize global Set for tracking processed comment IDs
        if (!window.processedCommentIds) {
            window.processedCommentIds = new Set();
        }

        // Mark existing comments as processed (from server)
        const existingComments = commentsList.querySelectorAll('.comment-item');
        let markedCount = 0;
        existingComments.forEach(commentEl => {
            const commentId = commentEl.getAttribute('data-comment-id');
            if (commentId) {
                const id = parseInt(commentId);
                if (!isNaN(id)) {
                    window.processedCommentIds.add(id);
                    markedCount++;
                }
            }
        });
        console.log('post_detail.js: Marked', markedCount, 'existing comments as processed out of', existingComments.length, 'total comments');

        // Debug: log all existing comment IDs
        if (existingComments.length > 0) {
            const ids = Array.from(existingComments).map(el => el.getAttribute('data-comment-id')).filter(Boolean);
            console.log('post_detail.js: Existing comment IDs:', ids);
        }

        // Use a flag to ensure handler is only added once
        if (newCommentForm.dataset.handlerAttached === 'true') {
            console.warn('post_detail.js: Comment form handler already attached, skipping');
            return;
        }
        newCommentForm.dataset.handlerAttached = 'true';
        console.log('post_detail.js: Comment form handler attached');

        // Store reference to prevent multiple submissions
        let submitInProgress = false;

        newCommentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Prevent multiple simultaneous submissions
            if (submitInProgress) {
                console.warn('post_detail.js: Submit already in progress, blocking duplicate');
                return;
            }

            const text = newCommentInput.value.trim();
            const currentTime = Date.now();

            // Check if submitting same text within 2 seconds (prevent double submission)
            if (text === lastSubmittedText && (currentTime - lastSubmitTime) < 2000) {
                console.warn('post_detail.js: Duplicate submission detected - same text submitted too quickly');
                return;
            }

            if (!text || isSubmitting) {
                console.log('post_detail.js: Comment submission blocked - empty text or already submitting. isSubmitting:', isSubmitting);
                return;
            }

            // Set flags BEFORE async operation
            submitInProgress = true;
            isSubmitting = true;
            lastSubmittedText = text;
            lastSubmitTime = currentTime;

            console.log('post_detail.js: Starting comment submission, text:', text.substring(0, 50));
            newPostBtn.disabled = true;
            const originalBtnText = newPostBtn.textContent;
            newPostBtn.textContent = 'Posting...';

            try {
                console.log('post_detail.js: Sending comment to server...');
                const data = await ajaxPost(`/post/${postId}/comment/`, { text: text }, {
                    errorMessage: 'Failed to post comment. Please try again.'
                });

                if (data.success) {
                    const commentId = parseInt(data.comment.id);
                    console.log('post_detail.js: Comment posted successfully, ID:', commentId, 'Type:', typeof commentId);

                    // Initialize Set if not exists
                    if (!window.processedCommentIds) {
                        window.processedCommentIds = new Set();
                    }

                    // IMMEDIATELY check and mark as processed to prevent race conditions
                    // This must happen BEFORE any DOM checks
                    if (window.processedCommentIds.has(commentId)) {
                        console.warn('post_detail.js: Comment ID already in processed set (race condition detected), skipping. ID:', commentId);
                        console.warn('post_detail.js: Processed IDs:', Array.from(window.processedCommentIds));
                        newCommentInput.value = '';
                        isSubmitting = false;
                        submitInProgress = false;
                        newPostBtn.disabled = false;
                        newPostBtn.textContent = originalBtnText;
                        return;
                    }

                    // Mark as processed IMMEDIATELY after receiving response
                    window.processedCommentIds.add(commentId);
                    console.log('post_detail.js: Added comment ID to processed set:', commentId);

                    // Check if comment already exists in DOM by ID (shouldn't happen, but double-check)
                    const existingCommentById = commentsList.querySelector(`[data-comment-id="${commentId}"]`);
                    if (existingCommentById) {
                        console.warn('post_detail.js: Comment already exists in DOM (unexpected), skipping. Comment ID:', commentId);
                        newCommentInput.value = '';
                        isSubmitting = false;
                        submitInProgress = false;
                        newPostBtn.disabled = false;
                        newPostBtn.textContent = originalBtnText;
                        return;
                    }


                    if (noComments) noComments.remove();

                    const comment = data.comment;
                    const avatarHtml = comment.author_avatar
                        ? `<img src="${comment.author_avatar}" alt="${comment.author}" class="w-8 h-8 rounded-full object-cover">`
                        : `<div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-semibold">${comment.author.charAt(0).toUpperCase()}</div>`;

                    const commentHtml = `
                        <div class="flex space-x-3 mb-4 comment-item" data-comment-id="${comment.id}">
                            <a href="/profile/${comment.author}/">${avatarHtml}</a>
                            <div class="flex-1">
                                <p class="comment-text text-gray-800 dark:text-gray-200 text-sm">
                                    <a href="/profile/${comment.author}/" class="font-semibold mr-1">${comment.author}</a>
                                    <span class="comment-text-content">${comment.text}</span>
                                </p>
                                <div class="flex items-center space-x-3 mt-1">
                                    <span class="text-gray-400 dark:text-gray-500 text-xs">Just now</span>
                                    <button class="edit-comment-btn text-gray-400 dark:text-gray-500 hover:text-primary text-xs" data-comment-id="${comment.id}">Edit</button>
                                    <button class="delete-comment-btn text-gray-400 dark:text-gray-500 hover:text-red-500 text-xs" data-comment-id="${comment.id}">Delete</button>
                                </div>
                            </div>
                        </div>
                    `;

                    // Final check before inserting
                    const finalCheck = commentsList.querySelector(`[data-comment-id="${comment.id}"]`);
                    if (finalCheck) {
                        console.warn('post_detail.js: Comment appeared in DOM during processing, skipping. ID:', commentId);
                        newCommentInput.value = '';
                        isSubmitting = false;
                        submitInProgress = false;
                        newPostBtn.disabled = false;
                        newPostBtn.textContent = originalBtnText;
                        return;
                    }

                    commentsList.insertAdjacentHTML('beforeend', commentHtml);
                    console.log('post_detail.js: Comment inserted into DOM, ID:', commentId);

                    // Update comments count display
                    if (commentsCount) {
                        commentsCount.textContent = data.comments_count;
                        if (data.comments_count > 0) {
                            commentsCount.classList.remove('hidden');
                        } else {
                            commentsCount.classList.add('hidden');
                        }
                    }

                    newCommentInput.value = '';
                    commentsSection.scrollTop = commentsSection.scrollHeight;

                    // Re-initialize edit/delete buttons for the new comment
                    const newComment = commentsList.querySelector(`[data-comment-id="${comment.id}"]`);
                    if (newComment) {
                        const deleteBtn = newComment.querySelector('.delete-comment-btn');
                        const editBtn = newComment.querySelector('.edit-comment-btn');
                        if (deleteBtn) {
                            deleteBtn.addEventListener('click', () => deleteComment(comment.id));
                        }
                        if (editBtn) {
                            editBtn.addEventListener('click', () => startEditComment(comment.id));
                        }

                        // Force apply correct styles based on theme
                        const isDark = document.documentElement.classList.contains('dark');
                        const commentText = newComment.querySelector('.comment-text');
                        const commentTextContent = newComment.querySelector('.comment-text-content');

                        if (isDark) {
                            // Dark mode: light text
                            if (commentText) {
                                commentText.classList.add('dark:text-gray-200');
                                commentText.style.setProperty('color', '#e5e7eb', 'important');
                            }
                            if (commentTextContent) {
                                commentTextContent.style.setProperty('color', '#e5e7eb', 'important');
                            }
                        } else {
                            // Light mode: dark text (ensure it's dark)
                            if (commentText) {
                                commentText.style.setProperty('color', '#1f2937', 'important'); // text-gray-800 - темний текст
                            }
                            if (commentTextContent) {
                                commentTextContent.style.setProperty('color', '#1f2937', 'important'); // text-gray-800 - темний текст
                            }
                        }
                    }

                    // Reset flags after successful submission
                    isSubmitting = false;
                    submitInProgress = false;
                } else {
                    // If data.success is false, reset flags
                    isSubmitting = false;
                    submitInProgress = false;
                }
            } catch (error) {
                console.error('post_detail.js: Error posting comment:', error);
                // Reset flags on error so user can retry
                lastSubmittedText = '';
                lastSubmitTime = 0;
            } finally {
                // ALWAYS reset flags in finally block to ensure form is usable again
                isSubmitting = false;
                submitInProgress = false;
                newPostBtn.disabled = !newCommentInput.value.trim();
                newPostBtn.textContent = originalBtnText;
            }
        });

        async function deleteComment(commentId) {
            try {
                const data = await ajaxPost(`/post/${postId}/comment/${commentId}/delete/`, {}, {
                    errorMessage: 'Failed to delete comment. Please try again.'
                });

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
                <input type="text" class="edit-input w-full text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary" value="${currentText}" maxlength="500">
                <div class="flex space-x-2 mt-1">
                    <button type="button" class="save-edit-btn text-primary text-xs font-semibold">Save</button>
                    <button type="button" class="cancel-edit-btn text-gray-400 dark:text-gray-500 text-xs">Cancel</button>
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
                const data = await ajaxPost(`/post/${postId}/comment/${commentId}/edit/`, { text: newText }, {
                    errorMessage: 'Failed to edit comment. Please try again.'
                });

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
    initLikeButton();
    initImageCarousel();
    initPostMenu();
    initComments();
    console.log('post_detail.js: All features initialized');
}

// Auto-initialize when loaded directly (not via dynamic import)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const isPostDetailPage = document.getElementById('comments-section') ||
                                 document.querySelector('.post-menu') ||
                                 window.location.pathname.match(/^\/post\/\d+\/?$/);
        if (isPostDetailPage) {
            initPostDetail();
        }
    });
} else {
    const isPostDetailPage = document.getElementById('comments-section') ||
                             document.querySelector('.post-menu') ||
                             window.location.pathname.match(/^\/post\/\d+\/?$/);
    if (isPostDetailPage) {
        initPostDetail();
    }
}

