import { useState, useEffect } from 'react'
import api from '../lib/api'
import SnippetBrowser from '../components/SnippetBrowser'

function KnowledgePage() {
  const [snippets, setSnippets] = useState([])

  useEffect(() => {
    fetchSnippets()
  }, [])

  const fetchSnippets = async () => {
    try {
      const response = await api.get('/api/snippets')
      setSnippets(response.data.snippets || [])
    } catch (error) {
      console.error('Error fetching snippets:', error)
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
      alert('Snippet added to project!')
    } catch (error) {
      console.error('Error adding snippet:', error)
      alert('Failed to add snippet to project')
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="mt-2 text-gray-600">Browse and search code snippets</p>
      </div>

      <SnippetBrowser
        snippets={snippets}
        onAddToProject={handleAddToProject}
      />
    </div>
  )
}

export default KnowledgePage
