import { useState, useRef, useEffect } from 'react'
import { Send, Menu, Bot, User } from 'lucide-react'
import ChatMessage from './ChatMessage'

function ChatArea({ messages, isLoading, onSend, sidebarOpen, onToggleSidebar }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onSend(input.trim())
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <main className={`chat-area ${sidebarOpen ? '' : 'full-width'}`}>
      {/* Header */}
      <header className="chat-header">
        <div className="chat-header-left">
          {!sidebarOpen && (
            <button className="menu-btn" onClick={onToggleSidebar} title="Open sidebar">
              <Menu size={20} />
            </button>
          )}
          <div className="header-content">
            <h1 className="header-title">Smart Assistant</h1>
            <p className="header-subtitle">Your personal assistant for calculations, knowledge lookups, and more</p>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">
              <Bot size={48} />
            </div>
            <h2>Start a Conversation</h2>
            <p>Ask me anything! Try math calculations, tech topics, or current time.</p>
            <div className="suggestion-chips">
              <button className="chip" onClick={() => onSend('What is 2^10 + sqrt(144)?')}>
                Calculate 2^10 + sqrt(144)
              </button>
              <button className="chip" onClick={() => onSend('Tell me about Python')}>
                What is Python?
              </button>
              <button className="chip" onClick={() => onSend('What day is it today?')}>
                What day is today?
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar assistant-avatar">
              <Bot size={18} />
            </div>
            <div className="message-bubble assistant-bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <input
            ref={inputRef}
            id="chat-input"
            type="text"
            className="chat-input"
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            autoComplete="off"
          />
          <button
            type="submit"
            className={`send-btn ${input.trim() && !isLoading ? 'active' : ''}`}
            disabled={!input.trim() || isLoading}
            id="send-message-btn"
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </main>
  )
}

export default ChatArea
