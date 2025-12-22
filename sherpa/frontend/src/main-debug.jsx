import React from 'react'
import ReactDOM from 'react-dom/client'
import './styles/index.css'

// Simple test component
function TestApp() {
  return (
    <div style={{padding: '20px', backgroundColor: 'white', color: 'black'}}>
      <h1 style={{fontSize: '48px', color: 'red'}}>SHERPA TEST - React is Working!</h1>
      <p style={{fontSize: '24px'}}>If you see this, React is rendering correctly.</p>
    </div>
  )
}

const rootElement = document.getElementById('root')
console.log('Root element:', rootElement)

if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <TestApp />
    </React.StrictMode>,
  )
  console.log('React app rendered successfully')
} else {
  console.error('Root element not found!')
  document.body.innerHTML = '<h1 style="color: red; font-size: 48px;">ERROR: Root element not found!</h1>'
}
