/**
 * Unit tests for eventManager.js
 */

import { eventManager } from '../../src/js/utils/eventManager.js';

describe('eventManager.js', () => {
  beforeEach(() => {
    eventManager.clear();
  });

  describe('on/off/emit', () => {
    it('should subscribe and emit events', () => {
      const callback = jest.fn();
      eventManager.on('test-event', callback);

      eventManager.emit('test-event', { data: 'test' });

      expect(callback).toHaveBeenCalledWith({ data: 'test' });
    });

    it('should unsubscribe from events', () => {
      const callback = jest.fn();
      eventManager.on('test-event', callback);
      eventManager.off('test-event', callback);

      eventManager.emit('test-event');

      expect(callback).not.toHaveBeenCalled();
    });

    it('should return unsubscribe function', () => {
      const callback = jest.fn();
      const unsubscribe = eventManager.on('test-event', callback);

      unsubscribe();
      eventManager.emit('test-event');

      expect(callback).not.toHaveBeenCalled();
    });
  });

  describe('once', () => {
    it('should call callback only once', () => {
      const callback = jest.fn();
      eventManager.once('test-event', callback);

      eventManager.emit('test-event');
      eventManager.emit('test-event');

      expect(callback).toHaveBeenCalledTimes(1);
    });
  });

  describe('clear', () => {
    it('should clear all listeners for specific event', () => {
      const callback = jest.fn();
      eventManager.on('test-event', callback);
      eventManager.clear('test-event');

      eventManager.emit('test-event');

      expect(callback).not.toHaveBeenCalled();
    });

    it('should clear all listeners if no event specified', () => {
      const callback1 = jest.fn();
      const callback2 = jest.fn();
      eventManager.on('event1', callback1);
      eventManager.on('event2', callback2);
      eventManager.clear();

      eventManager.emit('event1');
      eventManager.emit('event2');

      expect(callback1).not.toHaveBeenCalled();
      expect(callback2).not.toHaveBeenCalled();
    });
  });

  describe('error handling', () => {
    it('should handle errors in callbacks gracefully', () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation();
      const callback = jest.fn(() => {
        throw new Error('Callback error');
      });

      eventManager.on('test-event', callback);
      eventManager.emit('test-event');

      expect(callback).toHaveBeenCalled();
      expect(consoleError).toHaveBeenCalled();

      consoleError.mockRestore();
    });
  });
});

