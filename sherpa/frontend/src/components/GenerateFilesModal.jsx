import { useState } from 'react'
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
    project_name: '',
    include_cursor: true,
    include_claude: true,
    include_copilot: true
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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
      // Validate at least one file type selected
      if (!formData.include_cursor && !formData.include_claude && !formData.include_copilot) {
        setError('Please select at least one file type to generate')
        setLoading(false)
        return
      }

      // Prepare request body
      const body = {
        project_name: formData.project_name || 'My Project',
        file_types: {
          cursor: formData.include_cursor,
          claude: formData.include_claude,
          copilot: formData.include_copilot
        }
      }

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
        project_name: '',
        include_cursor: true,
        include_claude: true,
        include_copilot: true
      })

      // Call success callback with result data
      if (onSuccess) {
        onSuccess(data)
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
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
          {/* Project Name */}
          <div>
            <label htmlFor="project_name" className="block text-sm font-medium text-gray-700 mb-1">
              Project Name
            </label>
            <input
              type="text"
              id="project_name"
              name="project_name"
              value={formData.project_name}
              onChange={handleChange}
              placeholder="My Project"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Name for your project (optional)
            </p>
          </div>

          {/* File Types */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              File Types to Generate
            </label>
            <div className="space-y-2">
              {/* Cursor */}
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="include_cursor"
                  checked={formData.include_cursor}
                  onChange={handleChange}
                  disabled={loading}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Cursor (.cursor/rules/)
                </span>
                {formData.include_cursor && (
                  <Check className="ml-2 h-4 w-4 text-green-600" />
                )}
              </label>

              {/* Claude */}
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="include_claude"
                  checked={formData.include_claude}
                  onChange={handleChange}
                  disabled={loading}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Claude (CLAUDE.md)
                </span>
                {formData.include_claude && (
                  <Check className="ml-2 h-4 w-4 text-green-600" />
                )}
              </label>

              {/* Copilot */}
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="include_copilot"
                  checked={formData.include_copilot}
                  onChange={handleChange}
                  disabled={loading}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Copilot (copilot-instructions.md)
                </span>
                {formData.include_copilot && (
                  <Check className="ml-2 h-4 w-4 text-green-600" />
                )}
              </label>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-sm text-blue-800">
              Files will be generated with organizational knowledge from your code snippets
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
