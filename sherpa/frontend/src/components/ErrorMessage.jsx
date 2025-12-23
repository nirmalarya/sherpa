import { useState } from 'react'
import { XCircle, X, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react'

/**
 * ErrorMessage Component
 *
 * A comprehensive error display component with user-friendly messages.
 * Features:
 * - Dismissible with X button
 * - Optional retry functionality
 * - Technical details hidden by default with expand option
 * - Clean, accessible design
 *
 * Props:
 * - message: User-friendly error message (required)
 * - technicalDetails: Technical error details (optional)
 * - onDismiss: Callback when error is dismissed (optional)
 * - onRetry: Callback for retry action (optional)
 * - className: Additional CSS classes (optional)
 */
function ErrorMessage({
  message,
  technicalDetails = null,
  onDismiss = null,
  onRetry = null,
  className = ''
}) {
  const [showDetails, setShowDetails] = useState(false)

  return (
    <div className={`bg-red-50 border border-red-200 rounded-md p-4 ${className}`}>
      <div className="flex items-start gap-3">
        {/* Error Icon */}
        <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" aria-label="Error icon" />

        {/* Content */}
        <div className="flex-1">
          {/* User-friendly message */}
          <p className="text-sm font-medium text-red-800">
            {message}
          </p>

          {/* Technical details toggle */}
          {technicalDetails && (
            <div className="mt-2">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center gap-1 text-xs text-red-700 hover:text-red-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1 rounded"
                aria-expanded={showDetails}
              >
                {showDetails ? (
                  <>
                    <ChevronUp className="h-3 w-3" />
                    <span>Hide technical details</span>
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-3 w-3" />
                    <span>Show technical details</span>
                  </>
                )}
              </button>

              {/* Technical details content */}
              {showDetails && (
                <div className="mt-2 p-3 bg-red-100 border border-red-200 rounded text-xs font-mono text-red-900 overflow-x-auto">
                  {technicalDetails}
                </div>
              )}
            </div>
          )}

          {/* Retry button */}
          {onRetry && (
            <div className="mt-3">
              <button
                onClick={onRetry}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-red-700 bg-red-100 hover:bg-red-200 border border-red-300 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Retry</span>
              </button>
            </div>
          )}
        </div>

        {/* Dismiss button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1 rounded"
            aria-label="Dismiss error"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  )
}

export default ErrorMessage
