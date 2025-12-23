import { useState } from 'react'
import { X } from 'lucide-react'

/**
 * NewSessionModal - Modal dialog for creating new autonomous coding sessions
 *
 * Props:
 * - isOpen: boolean - Controls modal visibility
 * - onClose: () => void - Callback when modal is closed
 * - onSuccess: (session) => void - Callback when session created successfully
 */
function NewSessionModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    spec_file: '',
    total_features: '',
    work_item_id: '',
    git_branch: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validate required fields
      if (!formData.spec_file) {
        setError('Spec file is required')
        setLoading(false)
        return
      }

      // Prepare request body
      const body = {
        spec_file: formData.spec_file,
        total_features: formData.total_features ? parseInt(formData.total_features) : 100,
        work_item_id: formData.work_item_id || null,
        git_branch: formData.git_branch || null
      }

      const response = await fetch('http://localhost:8001/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create session')
      }

      const data = await response.json()

      // Reset form
      setFormData({
        spec_file: '',
        total_features: '',
        work_item_id: '',
        git_branch: ''
      })

      // Call success callback with session data
      if (onSuccess) {
        onSuccess(data)
      }

      // Close modal
      onClose()
    } catch (err) {
      console.error('Error creating session:', err)
      setError(err.message || 'Failed to create session')
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">New Session</h2>
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
          {/* Spec File */}
          <div>
            <label htmlFor="spec_file" className="block text-sm font-medium text-gray-700 mb-1">
              Spec File <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="spec_file"
              name="spec_file"
              value={formData.spec_file}
              onChange={handleChange}
              placeholder="e.g., app_spec.txt"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              Path to the application specification file
            </p>
          </div>

          {/* Total Features */}
          <div>
            <label htmlFor="total_features" className="block text-sm font-medium text-gray-700 mb-1">
              Total Features
            </label>
            <input
              type="number"
              id="total_features"
              name="total_features"
              value={formData.total_features}
              onChange={handleChange}
              placeholder="100"
              min="1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Expected number of features (default: 100)
            </p>
          </div>

          {/* Work Item ID */}
          <div>
            <label htmlFor="work_item_id" className="block text-sm font-medium text-gray-700 mb-1">
              Work Item ID
            </label>
            <input
              type="text"
              id="work_item_id"
              name="work_item_id"
              value={formData.work_item_id}
              onChange={handleChange}
              placeholder="e.g., WI-12345"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Optional Azure DevOps work item ID
            </p>
          </div>

          {/* Git Branch */}
          <div>
            <label htmlFor="git_branch" className="block text-sm font-medium text-gray-700 mb-1">
              Git Branch
            </label>
            <input
              type="text"
              id="git_branch"
              name="git_branch"
              value={formData.git_branch}
              onChange={handleChange}
              placeholder="e.g., feature/new-feature"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Optional git branch for this session
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
                  Creating...
                </>
              ) : (
                'Create Session'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default NewSessionModal
