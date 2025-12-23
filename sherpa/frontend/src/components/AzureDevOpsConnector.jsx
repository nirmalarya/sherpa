import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Loader, AlertCircle, RefreshCw } from 'lucide-react'
import api from '../lib/api'

function AzureDevOpsConnector() {
  const [config, setConfig] = useState({
    organization: '',
    project: '',
    pat: ''
  })
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [testing, setTesting] = useState(false)
  const [saving, setSaving] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [validationErrors, setValidationErrors] = useState({})
  const [syncStatus, setSyncStatus] = useState(null)

  // Load sync status on component mount
  useEffect(() => {
    loadSyncStatus()
  }, [])

  const loadSyncStatus = async () => {
    try {
      const response = await api.get('/api/azure-devops/status')
      setSyncStatus(response.data)
    } catch (error) {
      console.error('Failed to load sync status:', error)
    }
  }

  const handleSync = async () => {
    setSyncing(true)
    setConnectionStatus(null)

    try {
      const response = await api.post('/api/azure-devops/sync')
      setConnectionStatus({
        success: true,
        message: response.data.message || 'Sync completed successfully!'
      })
      // Reload sync status after successful sync
      await loadSyncStatus()
    } catch (error) {
      setConnectionStatus({
        success: false,
        message: error.response?.data?.detail || 'Sync failed. Please check your configuration.'
      })
    } finally {
      setSyncing(false)
    }
  }

  const validateForm = () => {
    const errors = {}

    // Validate organization URL
    if (!config.organization.trim()) {
      errors.organization = 'Organization URL is required'
    } else if (!config.organization.startsWith('https://dev.azure.com/')) {
      errors.organization = 'URL must start with https://dev.azure.com/'
    }

    // Validate project name
    if (!config.project.trim()) {
      errors.project = 'Project name is required'
    } else if (config.project.length < 2) {
      errors.project = 'Project name must be at least 2 characters'
    }

    // Validate PAT
    if (!config.pat.trim()) {
      errors.pat = 'Personal Access Token is required'
    } else if (config.pat.length < 20) {
      errors.pat = 'PAT appears to be invalid (too short)'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleTestConnection = async () => {
    // Validate before testing
    if (!validateForm()) {
      return
    }

    setTesting(true)
    setConnectionStatus(null)

    try {
      // Extract organization name from URL if full URL provided
      const orgName = config.organization.replace('https://dev.azure.com/', '').replace(/\/$/, '')

      await api.post('/api/azure-devops/connect', {
        organization: orgName,
        project: config.project,
        pat: config.pat
      })
      setConnectionStatus({
        success: true,
        message: 'Connection successful! Azure DevOps is configured correctly.'
      })
    } catch (error) {
      setConnectionStatus({
        success: false,
        message: error.response?.data?.message || 'Connection failed. Please check your credentials.'
      })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    // Validate before saving
    if (!validateForm()) {
      return
    }

    setSaving(true)

    try {
      // Extract organization name from URL if full URL provided
      const orgName = config.organization.replace('https://dev.azure.com/', '').replace(/\/$/, '')

      await api.post('/api/azure-devops/save-config', {
        organization: orgName,
        project: config.project,
        pat: config.pat
      })
      setConnectionStatus({
        success: true,
        message: 'Configuration saved successfully!'
      })
    } catch (error) {
      setConnectionStatus({
        success: false,
        message: error.response?.data?.message || 'Failed to save configuration'
      })
    } finally {
      setSaving(false)
    }
  }

  const handleInputChange = (field, value) => {
    setConfig({ ...config, [field]: value })

    // Clear validation error for this field when user starts typing
    if (validationErrors[field]) {
      setValidationErrors({ ...validationErrors, [field]: undefined })
    }
  }

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Azure DevOps</h2>
      <p className="text-gray-600 mb-6">
        Connect to Azure DevOps to sync work items and track progress
      </p>

      <div className="space-y-4">
        {/* Organization URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Organization URL <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            placeholder="https://dev.azure.com/your-org"
            value={config.organization}
            onChange={(e) => handleInputChange('organization', e.target.value)}
            className={`input w-full ${validationErrors.organization ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
            aria-invalid={!!validationErrors.organization}
            aria-describedby={validationErrors.organization ? 'org-error' : undefined}
          />
          {validationErrors.organization && (
            <div id="org-error" className="mt-1 flex items-center gap-1 text-sm text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>{validationErrors.organization}</span>
            </div>
          )}
        </div>

        {/* Project Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Project Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            placeholder="YourProject"
            value={config.project}
            onChange={(e) => handleInputChange('project', e.target.value)}
            className={`input w-full ${validationErrors.project ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
            aria-invalid={!!validationErrors.project}
            aria-describedby={validationErrors.project ? 'project-error' : undefined}
          />
          {validationErrors.project && (
            <div id="project-error" className="mt-1 flex items-center gap-1 text-sm text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>{validationErrors.project}</span>
            </div>
          )}
        </div>

        {/* Personal Access Token */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Personal Access Token (PAT) <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            placeholder="Enter your PAT"
            value={config.pat}
            onChange={(e) => handleInputChange('pat', e.target.value)}
            className={`input w-full ${validationErrors.pat ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
            aria-invalid={!!validationErrors.pat}
            aria-describedby={validationErrors.pat ? 'pat-error' : undefined}
          />
          {validationErrors.pat ? (
            <div id="pat-error" className="mt-1 flex items-center gap-1 text-sm text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>{validationErrors.pat}</span>
            </div>
          ) : (
            <p className="text-xs text-gray-500 mt-1">
              Requires: Work Items (Read, Write), Code (Read)
            </p>
          )}
        </div>

        {/* Connection Status Message */}
        {connectionStatus && (
          <div
            className={`p-4 rounded-lg flex items-center gap-2 ${
              connectionStatus.success
                ? 'bg-green-50 text-green-800'
                : 'bg-red-50 text-red-800'
            }`}
            role="alert"
          >
            {connectionStatus.success ? (
              <CheckCircle className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
            ) : (
              <XCircle className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
            )}
            <span>{connectionStatus.message}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleTestConnection}
            disabled={testing || saving || syncing}
            className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Test Azure DevOps connection"
          >
            {testing ? (
              <Loader className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <CheckCircle className="h-4 w-4" aria-hidden="true" />
            )}
            {testing ? 'Testing...' : 'Test Connection'}
          </button>
          <button
            onClick={handleSave}
            disabled={testing || saving || syncing}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Save Azure DevOps configuration"
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>

        {/* Sync Status Section */}
        {syncStatus && syncStatus.configured && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Sync Status</h3>

            <div className="space-y-3">
              {/* Last Sync Time */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Last Sync:</span>
                <span className="text-sm font-medium text-gray-900">
                  {syncStatus.last_sync
                    ? new Date(syncStatus.last_sync).toLocaleString()
                    : 'Never synced'}
                </span>
              </div>

              {/* Sync Status Indicator */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Status:</span>
                <div className="flex items-center gap-2">
                  {syncStatus.status === 'success' && (
                    <>
                      <CheckCircle className="h-4 w-4 text-green-600" aria-hidden="true" />
                      <span className="text-sm font-medium text-green-600">Connected</span>
                    </>
                  )}
                  {syncStatus.status === 'never_synced' && (
                    <>
                      <AlertCircle className="h-4 w-4 text-yellow-600" aria-hidden="true" />
                      <span className="text-sm font-medium text-yellow-600">Never Synced</span>
                    </>
                  )}
                  {syncStatus.status === 'error' && (
                    <>
                      <XCircle className="h-4 w-4 text-red-600" aria-hidden="true" />
                      <span className="text-sm font-medium text-red-600">Error</span>
                    </>
                  )}
                </div>
              </div>

              {/* Manual Sync Button */}
              <div className="pt-2">
                <button
                  onClick={handleSync}
                  disabled={testing || saving || syncing}
                  className="btn-secondary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Sync with Azure DevOps"
                >
                  {syncing ? (
                    <Loader className="h-4 w-4 animate-spin" aria-hidden="true" />
                  ) : (
                    <RefreshCw className="h-4 w-4" aria-hidden="true" />
                  )}
                  {syncing ? 'Syncing...' : 'Sync Now'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AzureDevOpsConnector
