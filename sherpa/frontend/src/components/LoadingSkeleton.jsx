/**
 * LoadingSkeleton Component
 *
 * Provides skeleton loading screens for better perceived performance.
 * Displays placeholder content while data is being fetched.
 *
 * Variants:
 * - card: Skeleton for snippet cards (knowledge page)
 * - table: Skeleton for table rows (sessions page)
 * - list: Skeleton for list items
 *
 * Props:
 * @param {string} variant - Type of skeleton ('card', 'table', 'list')
 * @param {number} count - Number of skeleton items to display (default: 3)
 * @param {string} className - Additional CSS classes
 */

function LoadingSkeleton({ variant = 'card', count = 3, className = '' }) {
  // Render multiple skeleton items
  const items = Array.from({ length: count }, (_, i) => i)

  // Card skeleton (for snippet cards)
  if (variant === 'card') {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}>
        {items.map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2 flex-1">
                <div className="h-5 w-5 bg-gray-200 rounded"></div>
                <div className="h-5 bg-gray-200 rounded w-2/3"></div>
              </div>
              <div className="h-6 w-16 bg-gray-200 rounded"></div>
            </div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-full"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6"></div>
            </div>
            <div className="mt-3">
              <div className="h-8 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Table skeleton (for session rows)
  if (variant === 'table') {
    return (
      <div className={`space-y-2 ${className}`}>
        {items.map((i) => (
          <div key={i} className="animate-pulse flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/6"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/6"></div>
            <div className="h-6 w-20 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  // List skeleton (for simple lists)
  if (variant === 'list') {
    return (
      <div className={`space-y-3 ${className}`}>
        {items.map((i) => (
          <div key={i} className="animate-pulse flex items-center gap-3">
            <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Default skeleton
  return (
    <div className={`space-y-4 ${className}`}>
      {items.map((i) => (
        <div key={i} className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      ))}
    </div>
  )
}

export default LoadingSkeleton
