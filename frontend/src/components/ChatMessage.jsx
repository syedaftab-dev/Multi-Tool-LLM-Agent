import { Bot, User, Clock, Wrench } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isError = message.isError

  return (
    <div className={`message ${isUser ? 'user' : 'assistant'} ${isError ? 'error' : ''}`}>
      <div className={`message-avatar ${isUser ? 'user-avatar' : 'assistant-avatar'}`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
        <ReactMarkdown
          components={{
            // Style code blocks
            code({ node, inline, className, children, ...props }) {
              return inline ? (
                <code className="inline-code" {...props}>{children}</code>
              ) : (
                <pre className="code-block">
                  <code className={className} {...props}>{children}</code>
                </pre>
              )
            },
          }}
        >
          {message.content}
        </ReactMarkdown>

        {/* Metadata bar for assistant messages */}
        {!isUser && !isError && (message.tools_used?.length > 0 || message.processing_time_ms) && (
          <div className="message-meta">
            {message.tools_used?.length > 0 && (
              <span className="meta-item">
                <Wrench size={12} />
                {message.tools_used.join(', ')}
              </span>
            )}
            {message.processing_time_ms && (
              <span className="meta-item">
                <Clock size={12} />
                {(message.processing_time_ms / 1000).toFixed(1)}s
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage
