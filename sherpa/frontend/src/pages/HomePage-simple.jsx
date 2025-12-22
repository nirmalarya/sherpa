import { Plus, FileText, Activity } from 'lucide-react'

function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Monitor your autonomous coding sessions</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <button className="card flex items-center p-6 hover:shadow-md transition-shadow">
          <Plus className="h-8 w-8 text-primary-600" />
          <div className="ml-4 text-left">
            <h3 className="text-lg font-semibold">New Session</h3>
            <p className="text-sm text-gray-600">Start autonomous coding session</p>
          </div>
        </button>

        <button className="card flex items-center p-6 hover:shadow-md transition-shadow">
          <FileText className="h-8 w-8 text-primary-600" />
          <div className="ml-4 text-left">
            <h3 className="text-lg font-semibold">Generate Files</h3>
            <p className="text-sm text-gray-600">Create instruction files for agents</p>
          </div>
        </button>
      </div>

      {/* Active Sessions */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Active Sessions</h2>
        <div className="card text-center py-12">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No active sessions</h3>
          <p className="text-gray-600">Start a new session to begin coding</p>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Activity</h2>
        <div className="card">
          <p className="text-gray-600">Activity feed will appear here</p>
        </div>
      </div>
    </div>
  )
}

export default HomePage
