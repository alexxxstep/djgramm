// Feed page functionality - Like buttons
import { initLikeButtons } from './modules/likes/likeHandler.js';

// Export initialization function for dynamic import
export function initFeed() {
    // Initialize like buttons, skipping post detail pages
    initLikeButtons('.like-btn', { skipPostDetail: true });
}

// Auto-initialize when loaded directly (not via dynamic import)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFeed);
} else {
    initFeed();
}

