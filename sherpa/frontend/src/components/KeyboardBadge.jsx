/**
 * Keyboard Badge Component
 *
 * Displays a keyboard shortcut badge (e.g., "N", "G", "?")
 *
 * @param {Object} props
 * @param {string} props.shortcut - The keyboard shortcut to display
 * @param {string} props.className - Additional CSS classes (optional)
 */
function KeyboardBadge({ shortcut, className = '' }) {
  return (
    <kbd className={`ml-auto px-2 py-1 text-xs font-semibold text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded shadow-sm ${className}`}>
      {shortcut}
    </kbd>
  )
}

export default KeyboardBadge
