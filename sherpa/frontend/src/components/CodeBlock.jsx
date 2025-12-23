import { useEffect, useRef, useState } from 'react'
import { Copy, Check } from 'lucide-react'
import Prism from 'prismjs'
import 'prismjs/themes/prism-tomorrow.css'

// Import common language grammars
import 'prismjs/components/prism-javascript'
import 'prismjs/components/prism-typescript'
import 'prismjs/components/prism-jsx'
import 'prismjs/components/prism-tsx'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-bash'
import 'prismjs/components/prism-json'
import 'prismjs/components/prism-css'
import 'prismjs/components/prism-markdown'
import 'prismjs/components/prism-yaml'
import 'prismjs/components/prism-sql'
import 'prismjs/components/prism-diff'

/**
 * CodeBlock Component
 *
 * A syntax-highlighted code block with the following features:
 * - Syntax highlighting using Prism.js with Tomorrow Night theme
 * - Line numbers for better code navigation
 * - Copy to clipboard functionality
 * - Monospace font with proper formatting
 * - Horizontal scrolling for long lines
 * - Language detection or manual specification
 * - Dark mode support
 *
 * @param {Object} props
 * @param {string} props.code - The code content to display
 * @param {string} props.language - Programming language (auto-detected if not provided)
 * @param {boolean} props.showLineNumbers - Whether to show line numbers (default: true)
 * @param {boolean} props.showCopyButton - Whether to show copy button (default: true)
 * @param {string} props.className - Additional CSS classes
 */
function CodeBlock({
  code = '',
  language = 'javascript',
  showLineNumbers = true,
  showCopyButton = true,
  className = ''
}) {
  const codeRef = useRef(null)
  const [copied, setCopied] = useState(false)

  // Auto-detect language from code content if not specified
  const detectLanguage = (codeContent) => {
    if (!codeContent) return 'javascript'

    // Check for common patterns
    if (codeContent.includes('def ') || codeContent.includes('import ')) return 'python'
    if (codeContent.includes('function ') || codeContent.includes('const ') || codeContent.includes('let ')) return 'javascript'
    if (codeContent.includes('interface ') || codeContent.includes(': string') || codeContent.includes(': number')) return 'typescript'
    if (codeContent.includes('<') && codeContent.includes('/>')) return 'jsx'
    if (codeContent.includes('SELECT ') || codeContent.includes('FROM ')) return 'sql'
    if (codeContent.includes('```')) return 'markdown'
    if (codeContent.includes('#!/bin/bash') || codeContent.includes('#!/bin/sh')) return 'bash'
    if (codeContent.startsWith('{') || codeContent.startsWith('[')) return 'json'
    if (codeContent.includes('.class') || codeContent.includes('#id')) return 'css'

    return language
  }

  const detectedLanguage = detectLanguage(code)

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current)
    }
  }, [code, detectedLanguage])

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const lineCount = code.split('\n').length
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1)

  return (
    <div className={`relative code-block-container ${className}`}>
      {/* Copy Button */}
      {showCopyButton && (
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 z-10 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm font-medium transition-colors flex items-center gap-2 shadow-lg"
          aria-label="Copy code to clipboard"
        >
          {copied ? (
            <>
              <Check className="h-4 w-4" />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy className="h-4 w-4" />
              <span>Copy</span>
            </>
          )}
        </button>
      )}

      {/* Code Block with Line Numbers */}
      <div className="code-block-wrapper overflow-x-auto rounded-lg bg-gray-900">
        <div className="flex">
          {/* Line Numbers Column */}
          {showLineNumbers && (
            <div className="flex-shrink-0 select-none border-r border-gray-700 bg-gray-800 text-gray-500 text-right pr-4 pl-2 py-4">
              {lineNumbers.map((num) => (
                <div key={num} className="leading-6 font-mono text-xs">
                  {num}
                </div>
              ))}
            </div>
          )}

          {/* Code Column */}
          <div className="flex-1 overflow-x-auto">
            <pre className={`language-${detectedLanguage} !bg-gray-900 !text-gray-100 !my-0 !p-4`}>
              <code
                ref={codeRef}
                className={`language-${detectedLanguage} !font-mono !text-sm leading-6`}
              >
                {code}
              </code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CodeBlock
