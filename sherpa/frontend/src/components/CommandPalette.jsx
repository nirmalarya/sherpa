import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { X, Search, Home, List, BookOpen, Settings, Plus, FileText, ChevronRight } from 'lucide-react'

/**
 * CommandPalette - Keyboard-accessible command palette for quick navigation and actions
 *
 * Opens with Ctrl+K (or Cmd+K on Mac)
 * Closes with Escape
 * Navigate with arrow keys
 * Select with Enter
 */
function CommandPalette({ isOpen, onClose }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const modalRef = useRef(null)
  const searchInputRef = useRef(null)
  const navigate = useNavigate()

  // Define available commands
  const commands = [
    {
      id: 'home',
      label: 'Go to Home',
      description: 'Dashboard with active sessions',
      icon: Home,
      action: () => navigate('/')
    },
    {
      id: 'sessions',
      label: 'Go to Sessions',
      description: 'View all sessions',
      icon: List,
      action: () => navigate('/sessions')
    },
    {
      id: 'knowledge',
      label: 'Go to Knowledge',
      description: 'Browse code snippets',
      icon: BookOpen,
      action: () => navigate('/knowledge')
    },
    {
      id: 'sources',
      label: 'Go to Sources',
      description: 'Configure data sources',
      icon: Settings,
      action: () => navigate('/sources')
    },
    {
      id: 'new-session',
      label: 'New Session',
      description: 'Start autonomous coding session',
      icon: Plus,
      action: () => {
        navigate('/')
        // Trigger new session modal after navigation
        setTimeout(() => {
          const newSessionButton = document.querySelector('[data-action="new-session"]')
          if (newSessionButton) newSessionButton.click()
        }, 100)
      }
    },
    {
      id: 'generate-files',
      label: 'Generate Files',
      description: 'Create instruction files for agents',
      icon: FileText,
      action: () => {
        navigate('/')
        // Trigger generate files modal after navigation
        setTimeout(() => {
          const generateButton = document.querySelector('[data-action="generate-files"]')
          if (generateButton) generateButton.click()
        }, 100)
      }
    }
  ]

  // Filter commands based on search query
  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cmd.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Focus search input when modal opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus()
      setSearchQuery('')
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev =>
            prev < filteredCommands.length - 1 ? prev + 1 : prev
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => prev > 0 ? prev - 1 : prev)
          break
        case 'Enter':
          e.preventDefault()
          if (filteredCommands[selectedIndex]) {
            executeCommand(filteredCommands[selectedIndex])
          }
          break
        case 'Escape':
          e.preventDefault()
          handleClose()
          break
        default:
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, selectedIndex, filteredCommands])

  // Reset selected index when search query changes
  useEffect(() => {
    setSelectedIndex(0)
  }, [searchQuery])

  // Scroll selected item into view
  useEffect(() => {
    const selectedElement = modalRef.current?.querySelector('[data-selected="true"]')
    if (selectedElement) {
      selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [selectedIndex])

  if (!isOpen) return null

  const executeCommand = (command) => {
    command.action()
    handleClose()
  }

  const handleClose = () => {
    setSearchQuery('')
    setSelectedIndex(0)
    onClose()
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 pt-[20vh] animate-fadeIn"
      onClick={handleClose}
      role="presentation"
      aria-hidden="false"
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-2xl max-w-2xl w-full mx-4 animate-slideUp"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="command-palette-title"
        aria-describedby="command-palette-description"
      >
        {/* Hidden title for screen readers */}
        <h2 id="command-palette-title" className="sr-only">Command Palette</h2>
        <p id="command-palette-description" className="sr-only">
          Search and execute commands. Use arrow keys to navigate, Enter to select, and Escape to close.
        </p>

        {/* Search Input */}
        <div className="flex items-center border-b border-gray-200 px-4 py-3">
          <Search className="h-5 w-5 text-gray-400 mr-3" aria-hidden="true" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Type a command or search..."
            className="flex-1 outline-none text-gray-900 placeholder-gray-400 focus:ring-0"
            aria-label="Search commands"
            aria-controls="command-palette-results"
            aria-autocomplete="list"
            aria-activedescendant={filteredCommands[selectedIndex] ? `command-${filteredCommands[selectedIndex].id}` : undefined}
          />
          <button
            onClick={handleClose}
            className="ml-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2 rounded"
            aria-label="Close command palette"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        {/* Commands List */}
        <div
          id="command-palette-results"
          className="max-h-96 overflow-y-auto"
          role="listbox"
          aria-label="Available commands"
        >
          {filteredCommands.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500" role="status">
              No commands found for "{searchQuery}"
            </div>
          ) : (
            <div className="py-2">
              {filteredCommands.map((command, index) => {
                const Icon = command.icon
                const isSelected = index === selectedIndex

                return (
                  <button
                    key={command.id}
                    id={`command-${command.id}`}
                    data-selected={isSelected}
                    onClick={() => executeCommand(command)}
                    onMouseEnter={() => setSelectedIndex(index)}
                    className={`w-full flex items-center px-4 py-3 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-600 ${
                      isSelected ? 'bg-primary-50 border-l-4 border-primary-600' : ''
                    }`}
                    role="option"
                    aria-selected={isSelected}
                    aria-label={`${command.label}: ${command.description}`}
                  >
                    <Icon className={`h-5 w-5 mr-3 ${isSelected ? 'text-primary-600' : 'text-gray-400'}`} aria-hidden="true" />
                    <div className="flex-1 text-left">
                      <div className={`text-sm font-medium ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                        {command.label}
                      </div>
                      <div className="text-xs text-gray-500">
                        {command.description}
                      </div>
                    </div>
                    {isSelected && (
                      <ChevronRight className="h-4 w-4 text-primary-600" aria-hidden="true" />
                    )}
                  </button>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer with keyboard hints */}
        <div className="border-t border-gray-200 px-4 py-2 bg-gray-50 text-xs text-gray-500 flex items-center justify-between" role="note" aria-label="Keyboard shortcuts">
          <div className="flex items-center space-x-4">
            <span><kbd className="px-2 py-1 bg-white border border-gray-300 rounded" aria-label="Arrow up and down keys">↑</kbd> <kbd className="px-2 py-1 bg-white border border-gray-300 rounded">↓</kbd> Navigate</span>
            <span><kbd className="px-2 py-1 bg-white border border-gray-300 rounded" aria-label="Enter key">↵</kbd> Select</span>
            <span><kbd className="px-2 py-1 bg-white border border-gray-300 rounded" aria-label="Escape key">Esc</kbd> Close</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CommandPalette
