import { Info } from 'lucide-react'

/**
 * HelpText Component
 *
 * Displays explanatory text below form fields.
 * Provides context and guidance for user input.
 *
 * @param {Object} props
 * @param {string} props.children - The help text to display
 * @param {string} props.variant - Visual style: 'default', 'info', 'warning', 'error' (default: 'default')
 * @param {boolean} props.showIcon - Show icon before text (default: false)
 */
export default function HelpText({
  children,
  variant = 'default',
  showIcon = false
}) {
  // Style classes based on variant
  const variantClasses = {
    default: 'text-gray-600 dark:text-gray-400',
    info: 'text-blue-600 dark:text-blue-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    error: 'text-red-600 dark:text-red-400'
  }

  const iconClasses = {
    default: 'text-gray-500 dark:text-gray-400',
    info: 'text-blue-500 dark:text-blue-400',
    warning: 'text-yellow-500 dark:text-yellow-400',
    error: 'text-red-500 dark:text-red-400'
  }

  return (
    <div
      className={`
        flex items-start mt-1.5 text-sm leading-relaxed
        ${variantClasses[variant]}
      `}
      role="note"
      aria-live="polite"
    >
      {showIcon && (
        <Info
          className={`h-4 w-4 mr-1.5 mt-0.5 flex-shrink-0 ${iconClasses[variant]}`}
          aria-hidden="true"
        />
      )}
      <span>{children}</span>
    </div>
  )
}
