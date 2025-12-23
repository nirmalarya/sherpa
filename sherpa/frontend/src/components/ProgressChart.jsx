import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

/**
 * ProgressChart Component
 *
 * Displays a Recharts visualization of session progress over time.
 * Shows completion percentage on the Y-axis and time on the X-axis.
 *
 * @param {Object} props
 * @param {Array} props.data - Array of data points with timestamp and completion percentage
 *   Example: [{ timestamp: '10:00', completionPercent: 20, completed: 5, total: 25 }, ...]
 * @param {number} props.height - Height of chart in pixels (default: 300)
 */
function ProgressChart({ data = [], height = 300 }) {
  // If no data, show empty state
  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200"
        style={{ height: `${height}px` }}
      >
        <p className="text-gray-500 text-sm">No progress data available yet</p>
      </div>
    )
  }

  /**
   * Custom tooltip component for displaying data point details on hover
   */
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-900">
            {data.completionPercent}% Complete
          </p>
          <p className="text-xs text-gray-600 mt-1">
            {data.completed} / {data.total} features
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {data.timestamp}
          </p>
        </div>
      )
    }
    return null
  }

  /**
   * Format Y-axis labels to show percentage symbol
   */
  const formatYAxis = (value) => `${value}%`

  /**
   * Format X-axis labels to show shortened time
   */
  const formatXAxis = (value) => {
    // If the value is a full timestamp, extract just the time
    if (value && value.includes(':')) {
      const parts = value.split(' ')
      return parts[parts.length - 1] // Return just the time portion
    }
    return value
  }

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="timestamp"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickFormatter={formatXAxis}
            stroke="#9ca3af"
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickFormatter={formatYAxis}
            stroke="#9ca3af"
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="completionPercent"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ProgressChart
