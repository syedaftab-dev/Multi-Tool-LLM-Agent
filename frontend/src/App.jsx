import { useState, useRef, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import './index.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [model, setModel] = useState('llama3.2')
  const [temperature, setTemperature] = useState(0.1)
  const [tools, setTools] = useState([])
  const [backendStatus, setBackendStatus] = useState('checking')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Fetch tools on mount
  useEffect(() => {
    fetchTools()
    checkHealth()
  }, [])

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_URL}/health`)
      if (res.ok) {
        setBackendStatus('connected')
      } else {
        setBackendStatus('error')
      }
    } catch {
      setBackendStatus('disconnected')
    }
  }

  const fetchTools = async () => {
    try {
      const res = await fetch(`${API_URL}/tools`)
      if (res.ok) {
        const data = await res.json()
        setTools(data)
      }
    } catch {
      setTools([
        { name: 'Calculator', description: 'Evaluates math expressions', status: 'active' },
        { name: 'Knowledge Base', description: 'Looks up tech/programming topics', status: 'active' },
        { name: 'DateTime', description: 'Returns current date and time', status: 'active' },
      ])
    }
  }

  const sendMessage = async (text) => {
    if (!text.trim() || isLoading) return

    const userMsg = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          model,
          temperature,
        }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to get response')
      }

      const data = await res.json()

      if (!sessionId) {
        setSessionId(data.session_id)
      }

      const assistantMsg = {
        role: 'assistant',
        content: data.response,
        tools_used: data.tools_used,
        processing_time_ms: data.processing_time_ms,
        turn: data.turn,
      }

      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg = {
        role: 'assistant',
        content: `**Error:** ${err.message}\n\nMake sure the backend is running:\n\`\`\`\nuvicorn backend.api:app --reload --port 8000\n\`\`\``,
        isError: true,
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const clearConversation = async () => {
    if (sessionId) {
      try {
        await fetch(`${API_URL}/sessions/${sessionId}`, { method: 'DELETE' })
      } catch { /* ignore */ }
    }
    setMessages([])
    setSessionId(null)
  }

  return (
    <div className="app-container">
      <Sidebar
        model={model}
        setModel={setModel}
        temperature={temperature}
        setTemperature={setTemperature}
        tools={tools}
        onClear={clearConversation}
        backendStatus={backendStatus}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <ChatArea
        messages={messages}
        isLoading={isLoading}
        onSend={sendMessage}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />
    </div>
  )
}

export default App
