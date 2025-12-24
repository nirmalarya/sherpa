import { useEffect } from 'react'
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react'

/**
 * Toast Notification Component
 * Displays temporary notifications with auto-dismiss
 */
function Toast({ id, type = 'info', message, duration = 5000, onDismiss }) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onDismiss(id)
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [id, duration, onDismiss])

  // Get icon and colors based on type
  const getTypeStyles = (type) => {
    switch (type) {
      case 'success':
        return {
          icon: <CheckCircle className="h-5 w-5" aria-hidden="true" />,
          bgColor: 'bg-green-50 dark:bg-green-900/20',
          borderColor: 'border-green-200 dark:border-green-800',
          iconColor: 'text-green-600 dark:text-green-400',
          textColor: 'text-green-900 dark:text-green-100'
        }
      case 'error':
        return {
          icon: <XCircle className="h-5 w-5" aria-hidden="true" />,
          bgColor: 'bg-red-50 dark:bg-red-900/20',
          borderColor: 'border-red-200 dark:border-red-800',
          iconColor: 'text-red-600 dark:text-red-400',
          textColor: 'text-red-900 dark:text-red-100'
        }
      case 'warning':
        return {
          icon: <AlertTriangle className="h-5 w-5" aria-hidden="true" />,
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
          borderColor: 'border-yellow-200 dark:border-yellow-800',
          iconColor: 'text-yellow-600 dark:text-yellow-400',
          textColor: 'text-yellow-900 dark:text-yellow-100'
        }
      default: // info
        return {
          icon: <Info className="h-5 w-5" aria-hidden="true" />,
          bgColor: 'bg-blue-50 dark:bg-blue-900/20',
          borderColor: 'border-blue-200 dark:border-blue-800',
          iconColor: 'text-blue-600 dark:text-blue-400',
          textColor: 'text-blue-900 dark:text-blue-100'
        }
    }
  }

  const styles = getTypeStyles(type)

  return (
    <div
      role="alert"
      aria-live="polite"
      className={`${styles.bgColor} ${styles.borderColor} ${styles.textColor} border rounded-lg shadow-lg p-4 flex items-start gap-3 min-w-[320px] max-w-md animate-slide-in`}
    >
      <div className={`flex-shrink-0 ${styles.iconColor}`}>
        {styles.icon}
      </div>
      <div className="flex-grow min-w-0">
        <p className="text-sm font-medium whitespace-pre-line">{message}</p>
      </div>
      <button
        onClick={() => onDismiss(id)}
        className={`flex-shrink-0 ${styles.iconColor} hover:opacity-70 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 rounded`}
        aria-label="Dismiss notification"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  )
}

export default Toast
