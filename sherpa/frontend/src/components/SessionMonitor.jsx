import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Loader, WifiOff } from 'lucide-react'

/**
 * SessionMonitor Component
 *
 * Establishes an SSE (Server-Sent Events) connection to monitor session progress in real-time.
 * Automatically reconnects on connection loss and handles cleanup on unmount.
 *
 * @param {Object} props
 * @param {string} props.sessionId - The ID of the session to monitor
 * @param {Function} props.onProgress - Callback function called when progress updates are received
 * @param {Function} props.onComplete - Optional callback when session completes
 * @param {Function} props.onError - Optional callback when an error occurs
 */
function SessionMonitor({ sessionId, onProgress, onComplete, onError }) {
  const [connectionStatus, setConnectionStatus] = useState('connecting') // connecting, connected, error, disconnected
  const [reconnectAttempt, setReconnectAttempt] = useState(0)
  const [lastEventTime, setLastEventTime] = useState(null)

  useEffect(() => {
    if (!sessionId) return

    let es = null
    let reconnectTimeout = null

    const connect = () => {
      try {
        // Close existing connection if any
        if (es) {
          es.close()
        }

        // Create new EventSource connection
        es = new EventSource(`http://localhost:8001/api/sessions/${sessionId}/progress`)

        // Connection opened
        es.onopen = () => {
          console.log('[SessionMonitor] SSE connection opened')
          setConnectionStatus('connected')
          setReconnectAttempt(0)
        }

        // Message received
        es.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('[SessionMonitor] Progress update received:', data)
            setLastEventTime(new Date())

            // Call the onProgress callback with the data
            if (onProgress) {
              onProgress(data)
            }

            // Check if session is complete
            if (data.status === 'completed' && onComplete) {
              onComplete(data)
            }
          } catch (parseError) {
            console.error('[SessionMonitor] Error parsing SSE data:', parseError)
          }
        }

        // Error handling
        es.onerror = (error) => {
          console.error('[SessionMonitor] SSE connection error:', error)
          setConnectionStatus('error')

          // Call error callback if provided
          if (onError) {
            onError(error)
          }

          // Close the connection
          es.close()

          // Attempt to reconnect with exponential backoff
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempt), 30000) // Max 30 seconds
          console.log(`[SessionMonitor] Reconnecting in ${delay}ms (attempt ${reconnectAttempt + 1})`)

          reconnectTimeout = setTimeout(() => {
            setReconnectAttempt(prev => prev + 1)
            connect()
          }, delay)
        }

        // Handle specific event types
        es.addEventListener('progress', (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('[SessionMonitor] Progress event:', data)
            if (onProgress) {
              onProgress(data)
            }
          } catch (parseError) {
            console.error('[SessionMonitor] Error parsing progress event:', parseError)
          }
        })

        es.addEventListener('complete', (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('[SessionMonitor] Session complete:', data)
            setConnectionStatus('disconnected')
            if (onComplete) {
              onComplete(data)
            }
          } catch (parseError) {
            console.error('[SessionMonitor] Error parsing complete event:', parseError)
          }
        })

        es.addEventListener('error', (event) => {
          console.error('[SessionMonitor] Error event received:', event)
          setConnectionStatus('error')
          if (onError) {
            onError(event)
          }
        })

      } catch (error) {
        console.error('[SessionMonitor] Error creating EventSource:', error)
        setConnectionStatus('error')
        if (onError) {
          onError(error)
        }
      }
    }

    // Initial connection
    connect()

    // Cleanup function
    return () => {
      console.log('[SessionMonitor] Cleaning up SSE connection')
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
      if (es) {
        es.close()
      }
    }
  }, [sessionId, reconnectAttempt]) // reconnectAttempt in dependencies to trigger reconnection

  // Render connection status indicator
  const renderStatusIndicator = () => {
    switch (connectionStatus) {
      case 'connecting':
        return (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Loader className="h-4 w-4 animate-spin" />
            <span>Connecting to session monitor...</span>
          </div>
        )
      case 'connected':
        return (
          <div className="flex items-center gap-2 text-sm text-green-600">
            <CheckCircle className="h-4 w-4" />
            <span>Live monitoring active</span>
            {lastEventTime && (
              <span className="text-xs text-gray-500">
                (Last update: {lastEventTime.toLocaleTimeString()})
              </span>
            )}
          </div>
        )
      case 'error':
        return (
          <div className="flex items-center gap-2 text-sm text-red-600">
            <XCircle className="h-4 w-4" />
            <span>Connection error - attempting to reconnect...</span>
            {reconnectAttempt > 0 && (
              <span className="text-xs text-gray-500">
                (Attempt {reconnectAttempt})
              </span>
            )}
          </div>
        )
      case 'disconnected':
        return (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <WifiOff className="h-4 w-4" />
            <span>Session monitoring ended</span>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
      {renderStatusIndicator()}
    </div>
  )
}

export default SessionMonitor
