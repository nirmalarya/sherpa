import { useState } from 'react'
import ErrorMessage from '../components/ErrorMessage'

/**
 * ErrorTestPage - A test page to demonstrate and verify ErrorMessage component
 * This page is for testing purposes only
 */
function ErrorTestPage() {
  const [showError1, setShowError1] = useState(false)
  const [showError2, setShowError2] = useState(false)
  const [showError3, setShowError3] = useState(false)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Error Handling Test Page</h1>
        <p className="mt-2 text-gray-600">Test different error scenarios</p>
      </div>

      <div className="space-y-6">
        {/* Test 1: Basic error with all features */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Test 1: Full-featured Error</h2>
          <p className="text-sm text-gray-600 mb-4">
            Error with dismissible, retry, and technical details
          </p>
          <button
            onClick={() => setShowError1(!showError1)}
            className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 mb-4"
          >
            {showError1 ? 'Hide' : 'Show'} Error
          </button>

          {showError1 && (
            <ErrorMessage
              message="Unable to load sessions. Please check your connection and try again."
              technicalDetails={`Network Error: Failed to fetch

Endpoint: GET /api/sessions
Status: 500 Internal Server Error
Timestamp: ${new Date().toISOString()}
Stack trace:
  at fetchSessions (HomePage.jsx:23)
  at useEffect (HomePage.jsx:17)`}
              onDismiss={() => setShowError1(false)}
              onRetry={() => alert('Retry clicked!')}
            />
          )}
        </div>

        {/* Test 2: Error without technical details */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Test 2: Simple Error</h2>
          <p className="text-sm text-gray-600 mb-4">
            Error without technical details
          </p>
          <button
            onClick={() => setShowError2(!showError2)}
            className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 mb-4"
          >
            {showError2 ? 'Hide' : 'Show'} Error
          </button>

          {showError2 && (
            <ErrorMessage
              message="Failed to create new session. Please try again."
              onDismiss={() => setShowError2(false)}
              onRetry={() => alert('Retry clicked!')}
            />
          )}
        </div>

        {/* Test 3: Error without dismiss or retry */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Test 3: Basic Error Message</h2>
          <p className="text-sm text-gray-600 mb-4">
            Error with no interactive elements (for critical errors)
          </p>
          <button
            onClick={() => setShowError3(!showError3)}
            className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 mb-4"
          >
            {showError3 ? 'Hide' : 'Show'} Error
          </button>

          {showError3 && (
            <ErrorMessage
              message="A critical error occurred. Please refresh the page."
              technicalDetails="Error: Cannot connect to database
Connection string: postgresql://localhost:5432
Retry attempts: 3/3 failed"
            />
          )}
        </div>

        {/* Feature Checklist */}
        <div className="card bg-blue-50 border-blue-200">
          <h2 className="text-xl font-bold mb-4">Feature Verification Checklist</h2>
          <div className="space-y-2 text-sm">
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              <span>Error message displayed with user-friendly text</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              <span>Error is dismissible (X button works)</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              <span>Retry option shown and functional</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              <span>Technical details hidden by default</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              <span>Technical details can be expanded/collapsed</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              <span>Proper visual styling (red theme)</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ErrorTestPage
