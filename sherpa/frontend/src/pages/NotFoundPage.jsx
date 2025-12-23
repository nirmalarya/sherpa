import { Link } from 'react-router-dom'
import { Home, AlertCircle } from 'lucide-react'

function NotFoundPage() {
  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        {/* Icon */}
        <div className="flex justify-center mb-6">
          <AlertCircle className="h-24 w-24 text-primary-600" aria-label="Page not found icon" />
        </div>

        {/* 404 Error */}
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>

        {/* Error Message */}
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Page Not Found
        </h2>

        {/* Helpful Message */}
        <p className="text-gray-600 mb-8">
          Sorry, we couldn&apos;t find the page you&apos;re looking for. The page may have been moved or doesn&apos;t exist.
        </p>

        {/* Link Back to Home */}
        <Link
          to="/"
          className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
        >
          <Home className="h-5 w-5 mr-2" aria-hidden="true" />
          Back to Home
        </Link>

        {/* Additional Help */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            You can also navigate using the menu above to find what you&apos;re looking for.
          </p>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage
