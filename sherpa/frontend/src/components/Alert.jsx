import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react'

/**
 * Alert Component
 *
 * A reusable alert component with consistent styling for different alert types.
 * Follows the design pattern established in the application.
 *
 * Props:
 * - type: 'success' | 'error' | 'warning' | 'info' (required)
 * - children: Alert message content (required)
 * - className: Additional CSS classes (optional)
 */
function Alert({ type = 'info', children, className = '' }) {
  // Define alert styles based on type
  const styles = {
    success: {
      container: 'bg-green-50 border border-green-200 text-green-800',
      icon: <CheckCircle className="h-5 w-5 flex-shrink-0" />
    },
    error: {
      container: 'bg-red-50 border border-red-200 text-red-700',
      icon: <XCircle className="h-5 w-5 flex-shrink-0" />
    },
    warning: {
      container: 'bg-yellow-50 border border-yellow-200 text-yellow-800',
      icon: <AlertTriangle className="h-5 w-5 flex-shrink-0" />
    },
    info: {
      container: 'bg-blue-50 border border-blue-200 text-blue-800',
      icon: <Info className="h-5 w-5 flex-shrink-0" />
    }
  }

  const selectedStyle = styles[type] || styles.info

  return (
    <div className={`p-4 rounded-md flex items-start gap-3 ${selectedStyle.container} ${className}`}>
      {selectedStyle.icon}
      <div className="flex-1">
        {children}
      </div>
    </div>
  )
}

export default Alert
