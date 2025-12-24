import { useState, useEffect } from 'react'
import api from '../lib/api'
import SnippetBrowser from '../components/SnippetBrowser'
import Alert from '../components/Alert'
import ErrorMessage from '../components/ErrorMessage'
import Breadcrumb from '../components/Breadcrumb'

function KnowledgePage() {
  const [snippets, setSnippets] = useState([])
  const [loading, setLoading] = useState(true)
  const [alert, setAlert] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSnippets()
  }, [])

  const fetchSnippets = async () => {
    try {
      setLoading(true)
      setError(null) // Clear any previous errors
      const response = await api.get('/api/snippets')
      const loadedSnippets = response.data.data?.snippets || []
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
    } catch (err) {
      console.error('Error fetching snippets:', err)

      // Use mock data for testing when API fails
      const mockSnippets = [
        {
          name: 'React useState Hook',
          title: 'React useState Hook',
          category: 'react',
          description: 'Example of using the useState hook in React for state management',
          content: `import { useState } from 'react'

function Counter() {
  const [count, setCount] = useState(0)

  const increment = () => {
    setCount(count + 1)
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  )
}

export default Counter`,
          language: 'jsx',
          tags: ['react', 'hooks', 'state']
        },
        {
          name: 'Python Async Function',
          title: 'Python Async Function',
          category: 'python',
          description: 'Example of async/await pattern in Python for concurrent operations',
          content: `import asyncio

async def fetch_data(url):
    """Fetch data asynchronously"""
    await asyncio.sleep(1)
    return {"url": url, "data": "some data"}

async def main():
    # Concurrent execution
    results = await asyncio.gather(
        fetch_data("https://api.example.com/1"),
        fetch_data("https://api.example.com/2"),
        fetch_data("https://api.example.com/3")
    )
    return results

if __name__ == "__main__":
    asyncio.run(main())`,
          language: 'python',
          tags: ['python', 'async', 'asyncio']
        },
        {
          name: 'REST API Endpoint',
          title: 'REST API Endpoint',
          category: 'api',
          description: 'FastAPI endpoint example with validation and error handling',
          content: `from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.fetch_one(
        "SELECT * FROM users WHERE id = ?",
        user_id
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@app.post("/users")
async def create_user(user: User):
    user_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        user_id, user.name, user.email
    )
    return {"id": user_id, "message": "User created"}`,
          language: 'python',
          tags: ['api', 'fastapi', 'rest']
        }
      ]

      setSnippets(mockSnippets)
      setError({
        message: 'Unable to load code snippets. Please check your connection and try again.',
        technicalDetails: `${err.message}\n\nEndpoint: GET /api/snippets\nTimestamp: ${new Date().toISOString()}\n\nNote: Displaying mock data for testing.`
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAddToProject = async (snippet) => {
    try {
      setError(null) // Clear any previous errors
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
    } catch (err) {
      console.error('Error adding snippet:', err)
      setError({
        message: 'Unable to add snippet to project. Please try again.',
        technicalDetails: `${err.message}\n\nEndpoint: POST /api/snippets\nSnippet: ${snippet.name || snippet.title}\nTimestamp: ${new Date().toISOString()}`
      })
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumb
        items={[
          { label: 'Home', path: '/' },
          { label: 'Knowledge' }
        ]}
      />

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="mt-2 text-gray-600">Browse and search code snippets</p>
      </div>

      {/* Error Messages */}
      {error && (
        <ErrorMessage
          message={error.message}
          technicalDetails={error.technicalDetails}
          onDismiss={() => setError(null)}
          onRetry={fetchSnippets}
          className="mb-6"
        />
      )}

      {/* Alert Messages (for warnings and successes) */}
      {alert && (
        <div className="mb-6">
          <Alert type={alert.type}>
            {alert.message}
          </Alert>
        </div>
      )}

      <SnippetBrowser
        snippets={snippets}
        loading={loading}
        onAddToProject={handleAddToProject}
      />
    </div>
  )
}

export default KnowledgePage
