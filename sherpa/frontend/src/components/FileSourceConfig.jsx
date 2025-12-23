import { useState, useEffect } from 'react'
import { Folder, Plus, Trash2, CheckCircle, AlertCircle } from 'lucide-react'
import api from '../lib/api'

function FileSourceConfig() {
  const [fileSources, setFileSources] = useState([])
  const [newPath, setNewPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [validationError, setValidationError] = useState('')

  useEffect(() => {
    loadFileSources()
  }, [])

  const loadFileSources = async () => {
    try {
      const response = await api.get('/api/file-sources')
      setFileSources(response.data.file_sources || [])
    } catch (err) {
      console.error('Error loading file sources:', err)
    }
  }

  const validatePath = (path) => {
    if (!path || path.trim() === '') {
      return 'Path is required'
    }
    if (!path.startsWith('./') && !path.startsWith('/')) {
      return 'Path must be absolute or start with ./'
    }
    return ''
  }

  const handleAddSource = async () => {
    // Validate path
    const validationErr = validatePath(newPath)
    if (validationErr) {
      setValidationError(validationErr)
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')
    setValidationError('')

    try {
      const response = await api.post('/api/file-sources', {
        path: newPath.trim()
      })

      setSuccess(response.data.message || 'File source added successfully')
      setNewPath('')
      await loadFileSources()

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add file source')
      setTimeout(() => setError(''), 5000)
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveSource = async (path) => {
    if (!confirm(`Remove file source: ${path}?`)) {
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await api.delete('/api/file-sources', {
        data: { path }
      })

      setSuccess(response.data.message || 'File source removed successfully')
      await loadFileSources()

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove file source')
      setTimeout(() => setError(''), 5000)
    } finally {
      setLoading(false)
    }
  }

  const handlePathChange = (e) => {
    setNewPath(e.target.value)
    setValidationError('')
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <div className="flex items-center mb-4">
        <Folder className="w-5 h-5 mr-2 text-blue-600" />
        <h2 className="text-xl font-semibold">File Sources</h2>
      </div>

      <p className="text-gray-600 mb-4">
        Configure local file paths for spec files
      </p>

      {/* Success Banner */}
      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md flex items-center">
          <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
          <span className="text-green-700">{success}</span>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Add New Source */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Spec Directory Path
        </label>
        <div className="flex gap-2">
          <div className="flex-1">
            <input
              type="text"
              value={newPath}
              onChange={handlePathChange}
              placeholder="./specs or /absolute/path/to/specs"
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                validationError ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={loading}
            />
            {validationError && (
              <p className="mt-1 text-sm text-red-600">{validationError}</p>
            )}
          </div>
          <button
            onClick={handleAddSource}
            disabled={loading || !newPath.trim()}
            className="btn-primary flex items-center gap-2 px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Adding...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4" />
                Add Directory
              </>
            )}
          </button>
        </div>
      </div>

      {/* Configured Sources List */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">
          Configured Sources ({fileSources.length})
        </h3>
        {fileSources.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-md border border-gray-200">
            <Folder className="w-12 h-12 mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500">No file sources configured</p>
            <p className="text-sm text-gray-400 mt-1">Add a directory path above to get started</p>
          </div>
        ) : (
          <div className="space-y-2">
            {fileSources.map((path, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-md border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center gap-2 flex-1">
                  <Folder className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-800 font-mono text-sm">{path}</span>
                  <CheckCircle className="w-4 h-4 text-green-600" aria-label="Active" />
                </div>
                <button
                  onClick={() => handleRemoveSource(path)}
                  disabled={loading}
                  className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Remove source"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Help Text */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>Tip:</strong> Spec files in configured directories will be automatically loaded when running sessions.
          Use relative paths (./specs) or absolute paths (/home/user/specs).
        </p>
      </div>
    </div>
  )
}

export default FileSourceConfig
