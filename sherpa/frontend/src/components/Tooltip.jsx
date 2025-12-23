import { useState } from 'react'
import { HelpCircle } from 'lucide-react'

/**
 * Tooltip Component
 *
 * Displays helpful hints when hovering over elements.
 * Fully accessible with ARIA attributes.
 *
 * @param {Object} props
 * @param {string} props.content - The tooltip text to display
 * @param {React.ReactNode} props.children - The element to attach the tooltip to
 * @param {string} props.position - Position of tooltip: 'top', 'bottom', 'left', 'right' (default: 'top')
 * @param {boolean} props.showIcon - Show help icon instead of wrapping children (default: false)
 */
export default function Tooltip({
  content,
  children,
  position = 'top',
  showIcon = false
}) {
  const [isVisible, setIsVisible] = useState(false)

  // Position classes for tooltip
  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2'
  }

  // Arrow classes for visual pointer
  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-900 dark:border-t-gray-700',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-900 dark:border-b-gray-700',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-900 dark:border-l-gray-700',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-gray-900 dark:border-r-gray-700'
  }

  const handleMouseEnter = () => setIsVisible(true)
  const handleMouseLeave = () => setIsVisible(false)
  const handleFocus = () => setIsVisible(true)
  const handleBlur = () => setIsVisible(false)

  return (
    <div
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleFocus}
      onBlur={handleBlur}
    >
      {/* Trigger element */}
      <div
        className="inline-flex items-center"
        tabIndex={0}
        role="button"
        aria-label={`Help: ${content}`}
        aria-describedby={isVisible ? 'tooltip-content' : undefined}
      >
        {showIcon ? (
          <HelpCircle
            className="h-4 w-4 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 cursor-help transition-colors"
            aria-hidden="true"
          />
        ) : (
          children
        )}
      </div>

      {/* Tooltip content */}
      {isVisible && (
        <div
          id="tooltip-content"
          role="tooltip"
          className={`
            absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 dark:bg-gray-700
            rounded-lg shadow-lg whitespace-nowrap max-w-xs
            ${positionClasses[position]}
            animate-fade-in
          `}
        >
          {content}
          {/* Arrow pointing to trigger element */}
          <div
            className={`
              absolute w-0 h-0 border-4 border-transparent
              ${arrowClasses[position]}
            `}
            aria-hidden="true"
          />
        </div>
      )}
    </div>
  )
}
