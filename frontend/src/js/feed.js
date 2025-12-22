// Feed page functionality
// Like buttons are now handled by event delegation in likeHandler.js
// This file is kept for backward compatibility and potential future feed-specific logic

// Export initialization function for dynamic import
export function initFeed() {
    // Like buttons are handled by event delegation in likeHandler.js
    // No initialization needed here
    console.log('Feed module loaded');
}

// Auto-initialize when loaded directly (not via dynamic import)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFeed);
} else {
    initFeed();
}
