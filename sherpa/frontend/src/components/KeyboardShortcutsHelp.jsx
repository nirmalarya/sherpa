import { X } from 'lucide-react';

/**
 * Keyboard Shortcuts Help Modal
 *
 * Displays available keyboard shortcuts in a modal dialog.
 * Triggered by pressing '?' key.
 *
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether the modal is open
 * @param {Function} props.onClose - Function to call when modal is closed
 */
function KeyboardShortcutsHelp({ isOpen, onClose }) {
  if (!isOpen) return null;

  const shortcuts = [
    {
      category: 'General',
      items: [
        { key: '?', description: 'Show keyboard shortcuts' },
        { key: 'Esc', description: 'Close modal / Clear search' },
      ]
    },
    {
      category: 'Navigation',
      items: [
        { key: 'h', description: 'Go to Home page' },
        { key: 's', description: 'Go to Sessions page' },
        { key: 'k', description: 'Go to Knowledge page' },
        { key: 'o', description: 'Go to Sources page' },
      ]
    },
    {
      category: 'Actions',
      items: [
        { key: 'n', description: 'New session' },
        { key: 'g', description: 'Generate files' },
        { key: '/', description: 'Focus search' },
      ]
    },
    {
      category: 'Theme',
      items: [
        { key: 'd', description: 'Toggle dark mode' },
      ]
    }
  ];

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="keyboard-shortcuts-title"
      >
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2
              id="keyboard-shortcuts-title"
              className="text-2xl font-bold text-gray-900 dark:text-white"
            >
              Keyboard Shortcuts
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              aria-label="Close"
            >
              <X size={24} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {shortcuts.map((section) => (
              <div key={section.category}>
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                  {section.category}
                </h3>
                <div className="space-y-2">
                  {section.items.map((shortcut) => (
                    <div
                      key={shortcut.key}
                      className="flex items-center justify-between py-2"
                    >
                      <span className="text-gray-700 dark:text-gray-300">
                        {shortcut.description}
                      </span>
                      <kbd className="px-3 py-1.5 text-sm font-semibold text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm">
                        {shortcut.key}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
              Press <kbd className="px-2 py-1 text-xs font-semibold bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded">?</kbd> anytime to view shortcuts
            </p>
          </div>
        </div>
      </div>
    </>
  );
}

export default KeyboardShortcutsHelp;
