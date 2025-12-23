import { useState, useEffect } from 'react'
import api from '../lib/api'
import SnippetBrowser from '../components/SnippetBrowser'
import Alert from '../components/Alert'

function KnowledgePage() {
  const [snippets, setSnippets] = useState([])
  const [alert, setAlert] = useState(null)

  useEffect(() => {
    fetchSnippets()
  }, [])

  const fetchSnippets = async () => {
    try {
      const response = await api.get('/api/snippets')
      const loadedSnippets = response.data.snippets || []
      setSnippets(loadedSnippets)

      // Show warning if no snippets available
      if (loadedSnippets.length === 0) {
        setAlert({
          type: 'warning',
          message: 'No code snippets found. Add snippets to your project or configure external sources.'
        })
      } else {
        setAlert(null)
      }
    } catch (error) {
      console.error('Error fetching snippets:', error)
      setAlert({ type: 'error', message: 'Failed to load snippets. Please try again.' })
    }
  }

  const handleAddToProject = async (snippet) => {
    try {
      // Create snippet with project source
      await api.post('/api/snippets', {
        name: snippet.name || snippet.title,
        category: snippet.category,
        source: 'project',
        content: snippet.content,
        language: snippet.language,
        tags: snippet.tags
      })
      setAlert({ type: 'success', message: `Snippet "${snippet.name || snippet.title}" added to project!` })

      // Auto-dismiss success alert after 3 seconds
      setTimeout(() => setAlert(null), 3000)
    } catch (error) {
      console.error('Error adding snippet:', error)
      setAlert({ type: 'error', message: 'Failed to add snippet to project. Please try again.' })
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="mt-2 text-gray-600">Browse and search code snippets</p>
      </div>

      {/* Alert Messages */}
      {alert && (
        <div className="mb-6">
          <Alert type={alert.type}>
            {alert.message}
          </Alert>
        </div>
      )}

      <SnippetBrowser
        snippets={snippets}
        onAddToProject={handleAddToProject}
      />
    </div>
  )
}

export default KnowledgePage
