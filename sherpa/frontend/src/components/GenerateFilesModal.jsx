import { useState, useEffect, useRef } from 'react'
import { X, Check } from 'lucide-react'

/**
 * GenerateFilesModal - Modal dialog for generating instruction files for interactive agents
 *
 * Props:
 * - isOpen: boolean - Controls modal visibility
 * - onClose: () => void - Callback when modal is closed
 * - onSuccess: (result) => void - Callback when files generated successfully
 */
function GenerateFilesModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    target_directory: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const modalRef = useRef(null)
  const firstInputRef = useRef(null)

  // Focus first input when modal opens
  useEffect(() => {
    if (isOpen && firstInputRef.current) {
      firstInputRef.current.focus()
    }
  }, [isOpen])

  // Handle Escape key to close modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && !loading) {
        handleClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, loading])

  // Trap focus within modal
  useEffect(() => {
    if (!isOpen || !modalRef.current) return

    const modal = modalRef.current
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }

    modal.addEventListener('keydown', handleTabKey)
    return () => modal.removeEventListener('keydown', handleTabKey)
  }, [isOpen])

  if (!isOpen) return null

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Prepare request body - target_directory is optional
      const body = formData.target_directory ? { target_directory: formData.target_directory } : {}

      const response = await fetch('http://localhost:8001/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate files')
      }

      const data = await response.json()

      // Reset form
      setFormData({
        target_directory: ''
      })

      // Call success callback with result data
      if (onSuccess) {
        onSuccess(data.data || data)
      }

      // Close modal
      onClose()
    } catch (err) {
      console.error('Error generating files:', err)
      setError(err.message || 'Failed to generate files')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    if (!loading) {
      setError('')
      onClose()
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div ref={modalRef} className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 animate-slideUp">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Generate Files</h2>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Target Directory */}
          <div>
            <label htmlFor="target_directory" className="block text-sm font-medium text-gray-700 mb-1">
              Target Directory
            </label>
            <input
              ref={firstInputRef}
              type="text"
              id="target_directory"
              name="target_directory"
              value={formData.target_directory}
              onChange={handleChange}
              placeholder="Leave empty for current directory"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Optional: Specify where to generate files (defaults to current directory)
            </p>
          </div>

          {/* Files to Generate */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Files to Generate
            </label>
            <div className="space-y-2 bg-gray-50 rounded-md p-3">
              <div className="flex items-center">
                <Check className="h-4 w-4 text-green-600 mr-2" />
                <span className="text-sm text-gray-700">.cursor/rules/00-sherpa-knowledge.md</span>
              </div>
              <div className="flex items-center">
                <Check className="h-4 w-4 text-green-600 mr-2" />
                <span className="text-sm text-gray-700">CLAUDE.md</span>
              </div>
              <div className="flex items-center">
                <Check className="h-4 w-4 text-green-600 mr-2" />
                <span className="text-sm text-gray-700">copilot-instructions.md</span>
              </div>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-sm text-blue-800">
              All files will be generated with organizational knowledge from your code snippets
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </>
              ) : (
                'Generate Files'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default GenerateFilesModal
