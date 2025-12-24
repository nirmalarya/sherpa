import { createContext, useContext, useState, useCallback } from 'react'
import Toast from '../components/Toast'

const ToastContext = createContext(null)

/**
 * Toast Context Provider
 * Manages global toast notifications
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  /**
   * Show a toast notification
   * @param {string} type - 'success', 'error', 'warning', or 'info'
   * @param {string} message - The message to display
   * @param {number} duration - How long to show the toast (ms), 0 = no auto-dismiss
   */
  const showToast = useCallback((type, message, duration = 5000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, type, message, duration }])
    return id
  }, [])

  const dismissToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  // Convenience methods
  const success = useCallback((message, duration) => {
    return showToast('success', message, duration)
  }, [showToast])

  const error = useCallback((message, duration) => {
    return showToast('error', message, duration)
  }, [showToast])

  const warning = useCallback((message, duration) => {
    return showToast('warning', message, duration)
  }, [showToast])

  const info = useCallback((message, duration) => {
    return showToast('info', message, duration)
  }, [showToast])

  const value = {
    showToast,
    dismissToast,
    success,
    error,
    warning,
    info
  }

  return (
    <ToastContext.Provider value={value}>
      {children}

      {/* Toast Container */}
      <div
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2"
        aria-live="polite"
        aria-atomic="false"
      >
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            id={toast.id}
            type={toast.type}
            message={toast.message}
            duration={toast.duration}
            onDismiss={dismissToast}
          />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

/**
 * Hook to use toast notifications
 * @returns {Object} Toast context methods
 */
export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
