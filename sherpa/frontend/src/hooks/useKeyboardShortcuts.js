import { useEffect } from 'react';

/**
 * Custom hook for handling global keyboard shortcuts
 * @param {Object} shortcuts - Object mapping keys to callback functions
 * @param {Object} options - Configuration options
 * @param {boolean} options.enabled - Whether shortcuts are enabled (default: true)
 * @param {Array<string>} options.ignoreElements - Elements to ignore (default: ['INPUT', 'TEXTAREA', 'SELECT'])
 *
 * @example
 * useKeyboardShortcuts({
 *   '/': () => focusSearch(),
 *   'Escape': () => closeModal(),
 *   'n': () => newSession(),
 * });
 */
export function useKeyboardShortcuts(shortcuts, options = {}) {
  const { enabled = true, ignoreElements = ['INPUT', 'TEXTAREA', 'SELECT'] } = options;

  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event) => {
      // Ignore if user is typing in an input field
      if (ignoreElements.includes(event.target.tagName)) {
        // Allow Escape key even in input fields
        if (event.key !== 'Escape') {
          return;
        }
      }

      // Check for modifier keys
      const hasModifier = event.ctrlKey || event.metaKey || event.altKey;

      // Don't handle shortcuts with modifiers (except Shift for special chars like ?)
      if (hasModifier && event.key !== '?') {
        return;
      }

      // Find and execute the shortcut
      const shortcut = shortcuts[event.key];
      if (shortcut && typeof shortcut === 'function') {
        event.preventDefault();
        shortcut(event);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcuts, enabled, ignoreElements]);
}

/**
 * Hook to handle a single keyboard shortcut
 * @param {string} key - The key to listen for
 * @param {Function} callback - Function to call when key is pressed
 * @param {Object} options - Configuration options
 */
export function useKeyboardShortcut(key, callback, options = {}) {
  return useKeyboardShortcuts({ [key]: callback }, options);
}

export default useKeyboardShortcuts;
