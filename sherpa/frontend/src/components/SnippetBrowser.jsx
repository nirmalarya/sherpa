import { useState } from 'react'
import { Search, Code, Copy, Check } from 'lucide-react'

/**
 * SnippetBrowser Component
 *
 * A reusable component for browsing, searching, and managing code snippets.
 * Features:
 * - Search functionality to filter snippets by title/description
 * - Category filtering (all, security, python, react, testing, api, git)
 * - Snippet cards displaying title, category, and description preview
 * - Click snippet to view full content in modal
 * - Copy to clipboard functionality
 * - Add to project functionality
 *
 * @param {Object} props
 * @param {Array} props.snippets - Array of snippet objects
 * @param {Function} props.onAddToProject - Callback when adding snippet to project
 */
function SnippetBrowser({ snippets = [], onAddToProject }) {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [selectedSnippet, setSelectedSnippet] = useState(null)
  const [copied, setCopied] = useState(false)

  const handleSearch = () => {
    // Search is handled by filteredSnippets - this is for manual trigger
    // The filtering happens automatically via the filteredSnippets computed value
  }

  const handleCopy = (content) => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleAddClick = (e, snippet) => {
    e.stopPropagation()
    if (onAddToProject) {
      onAddToProject(snippet)
    }
  }

  // Filter snippets by category and search term
  const filteredSnippets = snippets
    .filter(snippet => {
      // Category filter
      if (category !== 'all' && snippet.category !== category) {
        return false
      }
      // Search filter
      const searchTerm = search.toLowerCase()
      if (searchTerm) {
        const title = (snippet.title || snippet.name || '').toLowerCase()
        const description = (snippet.description || '').toLowerCase()
        return title.includes(searchTerm) || description.includes(searchTerm)
      }
      return true
    })

  const categories = ['all', 'security', 'python', 'react', 'testing', 'api', 'git']

  return (
    <div>
      {/* Search and Filters */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search snippets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="input w-full pl-10"
              />
            </div>
          </div>
          <button onClick={handleSearch} className="btn-primary">
            Search
          </button>
        </div>

        <div className="flex gap-2 mt-4 flex-wrap">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                category === cat
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Snippets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSnippets.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            No snippets found. Try adjusting your search or filter.
          </div>
        ) : (
          filteredSnippets.map((snippet, index) => (
            <div
              key={index}
              className="card hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedSnippet(snippet)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Code className="h-5 w-5 text-primary-600" />
                  <h3 className="font-semibold">{snippet.title || snippet.name}</h3>
                </div>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded">{snippet.category}</span>
              </div>
              <p className="text-sm text-gray-600 line-clamp-3">{snippet.description}</p>
              {onAddToProject && (
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={(e) => handleAddClick(e, snippet)}
                    className="text-xs btn-secondary flex-1"
                  >
                    Add to Project
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Snippet Preview Modal */}
      {selectedSnippet && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200 flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold">{selectedSnippet.title || selectedSnippet.name}</h2>
                <p className="text-gray-600 mt-1">{selectedSnippet.description}</p>
              </div>
              <button
                onClick={() => setSelectedSnippet(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="relative">
                <button
                  onClick={() => handleCopy(selectedSnippet.content)}
                  className="absolute top-2 right-2 btn-secondary flex items-center gap-2"
                >
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                  <code>{selectedSnippet.content}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SnippetBrowser
