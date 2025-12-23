import { useState, useEffect } from 'react'
import api from '../lib/api'
import AzureDevOpsConnector from '../components/AzureDevOpsConnector'
import FileSourceConfig from '../components/FileSourceConfig'

function SourcesPage() {
  const [syncStatus, setSyncStatus] = useState(null)

  useEffect(() => {
    fetchSyncStatus()
  }, [])

  const fetchSyncStatus = async () => {
    try {
      const response = await api.get('/api/azure-devops/status')
      setSyncStatus(response.data)
    } catch (error) {
      console.error('Error fetching sync status:', error)
    }
  }


  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Sources</h1>
        <p className="mt-2 text-gray-600">Configure external sources for specs and work items</p>
      </div>

      {/* Azure DevOps Configuration */}
      <div className="mb-6">
        <AzureDevOpsConnector />
      </div>

      {/* Sync Status */}
      {syncStatus && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Sync Status</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Last Sync:</span>
              <span className="font-medium">
                {syncStatus.last_sync ? new Date(syncStatus.last_sync).toLocaleString() : 'Never'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className={`font-medium ${
                syncStatus.status === 'success' ? 'text-green-600' : 'text-red-600'
              }`}>
                {syncStatus.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Work Items Synced:</span>
              <span className="font-medium">{syncStatus.work_items_count || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* File Source Configuration */}
      <div className="mt-6">
        <FileSourceConfig />
      </div>
    </div>
  )
}

export default SourcesPage
