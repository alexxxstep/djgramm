/**
 * Event Manager
 * Centralized event handling for communication between modules
 */

class EventManager {
  constructor() {
    this.listeners = new Map();
  }

  /**
   * Subscribe to event
   * @param {string} eventName - Event name
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  on(eventName, callback) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, []);
    }

    this.listeners.get(eventName).push(callback);

    // Return unsubscribe function
    return () => this.off(eventName, callback);
  }

  /**
   * Unsubscribe from event
   * @param {string} eventName - Event name
   * @param {Function} callback - Callback function
   */
  off(eventName, callback) {
    if (!this.listeners.has(eventName)) {
      return;
    }

    const callbacks = this.listeners.get(eventName);
    const index = callbacks.indexOf(callback);

    if (index > -1) {
      callbacks.splice(index, 1);
    }

    // Clean up if no listeners
    if (callbacks.length === 0) {
      this.listeners.delete(eventName);
    }
  }

  /**
   * Emit event
   * @param {string} eventName - Event name
   * @param {*} data - Event data
   */
  emit(eventName, data = null) {
    if (!this.listeners.has(eventName)) {
      return;
    }

    const callbacks = this.listeners.get(eventName);

    // Call all callbacks
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event listener for ${eventName}:`, error);
      }
    });
  }

  /**
   * Subscribe to event once
   * @param {string} eventName - Event name
   * @param {Function} callback - Callback function
   */
  once(eventName, callback) {
    const wrappedCallback = (data) => {
      callback(data);
      this.off(eventName, wrappedCallback);
    };

    this.on(eventName, wrappedCallback);
  }

  /**
   * Clear all listeners for event
   * @param {string} eventName - Event name (optional)
   */
  clear(eventName = null) {
    if (eventName) {
      this.listeners.delete(eventName);
    } else {
      this.listeners.clear();
    }
  }
}

// Export singleton instance
export const eventManager = new EventManager();

// Export default
export default eventManager;

