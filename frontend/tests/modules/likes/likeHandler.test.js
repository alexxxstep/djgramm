/**
 * Unit tests for likeHandler.js
 */

import { toggleLike, updateLikeUI, initLikeButtons } from '../../src/js/modules/likes/likeHandler.js';
import { ajaxPost } from '../../src/js/utils/ajax.js';

// Mock ajaxPost
jest.mock('../../src/js/utils/ajax.js', () => ({
  ajaxPost: jest.fn(),
}));

describe('likeHandler.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    ajaxPost.mockClear();
  });

  describe('updateLikeUI', () => {
    it('should update button and span when liked', () => {
      const button = document.createElement('button');
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      button.appendChild(svg);

      const span = document.createElement('span');
      span.classList.add('hidden');
      span.textContent = '0';

      const data = { liked: true, likes_count: 5 };

      updateLikeUI(button, span, data);

      expect(button.classList.contains('text-red-500')).toBe(true);
      expect(svg.getAttribute('fill')).toBe('currentColor');
      expect(span.textContent).toBe('5');
      expect(span.classList.contains('hidden')).toBe(false);
    });

    it('should update button and span when unliked', () => {
      const button = document.createElement('button');
      button.classList.add('text-red-500');
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('fill', 'currentColor');
      button.appendChild(svg);

      const span = document.createElement('span');
      span.textContent = '5';

      const data = { liked: false, likes_count: 0 };

      updateLikeUI(button, span, data);

      expect(button.classList.contains('text-red-500')).toBe(false);
      expect(svg.getAttribute('fill')).toBe('none');
      expect(span.textContent).toBe('0');
      expect(span.classList.contains('hidden')).toBe(true);
    });
  });

  describe('toggleLike', () => {
    it('should make POST request and update UI', async () => {
      const button = document.createElement('button');
      const span = document.createElement('span');
      span.id = 'likes-count-123';
      document.body.appendChild(button);
      document.body.appendChild(span);

      const mockData = { liked: true, likes_count: 1 };
      ajaxPost.mockResolvedValueOnce(mockData);

      const result = await toggleLike('123', button, span);

      expect(ajaxPost).toHaveBeenCalledWith('/post/123/like/', {}, expect.any(Object));
      expect(result).toEqual(mockData);
      expect(button.classList.contains('text-red-500')).toBe(true);
    });

    it('should handle errors gracefully', async () => {
      const button = document.createElement('button');
      const error = new Error('Network error');
      ajaxPost.mockRejectedValueOnce(error);

      await expect(toggleLike('123', button)).rejects.toThrow();
    });
  });

  describe('initLikeButtons', () => {
    it('should initialize like buttons', () => {
      const button = document.createElement('button');
      button.className = 'like-btn';
      button.dataset.postId = '123';
      document.body.appendChild(button);

      initLikeButtons('.like-btn', { skipPostDetail: true });

      expect(button.dataset.handlerAttached).toBe('true');
    });

    it('should skip initialization on post detail pages', () => {
      window.location.pathname = '/post/123/';

      const button = document.createElement('button');
      button.className = 'like-btn';
      document.body.appendChild(button);

      initLikeButtons('.like-btn', { skipPostDetail: true });

      expect(button.dataset.handlerAttached).toBeUndefined();
    });
  });
});

