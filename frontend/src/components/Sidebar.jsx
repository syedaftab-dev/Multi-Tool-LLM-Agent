import { Calculator, BookOpen, Clock, Trash2, ChevronLeft, Circle } from 'lucide-react'

const toolIcons = {
  'Calculator': Calculator,
  'Knowledge Base': BookOpen,
  'DateTime': Clock,
}

function Sidebar({ model, setModel, temperature, setTemperature, tools, onClear, backendStatus, isOpen, onToggle }) {
  const statusColors = {
    connected: '#4ade80',
    disconnected: '#f87171',
    checking: '#facc15',
    error: '#f87171',
  }

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <button className="sidebar-toggle" onClick={onToggle} title="Toggle sidebar">
        <ChevronLeft size={18} />
      </button>

      <div className="sidebar-content">
        {/* Header */}
        <div className="sidebar-header">
          <h2>Configuration</h2>
          <div className="status-indicator">
            <Circle
              size={8}
              fill={statusColors[backendStatus]}
              color={statusColors[backendStatus]}
            />
            <span className="status-text">
              {backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Model Config */}
        <div className="config-section">
          <label className="config-label" htmlFor="model-input">Model</label>
          <input
            id="model-input"
            type="text"
            className="config-input"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="e.g., llama3.2, phi3"
          />
        </div>

        <div className="config-section">
          <label className="config-label" htmlFor="temp-slider">
            Temperature
            <span className="config-value">{temperature.toFixed(2)}</span>
          </label>
          <input
            id="temp-slider"
            type="range"
            className="config-slider"
            min="0"
            max="1"
            step="0.05"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
          />
          <div className="slider-labels">
            <span>Focused</span>
            <span>Creative</span>
          </div>
        </div>

        <div className="sidebar-divider" />

        {/* Tools */}
        <div className="tools-section">
          <h3>Available Tools</h3>
          {tools.map((tool) => {
            const Icon = toolIcons[tool.name] || BookOpen
            return (
              <div key={tool.name} className="tool-card">
                <div className="tool-icon-wrapper">
                  <Icon size={18} />
                </div>
                <div className="tool-info">
                  <span className="tool-name">{tool.name}</span>
                  <span className="tool-desc">{tool.description}</span>
                </div>
                <span className="tool-badge">Active</span>
              </div>
            )
          })}
        </div>

        <div className="sidebar-divider" />

        {/* Clear button */}
        <button className="clear-btn" onClick={onClear} id="clear-conversation-btn">
          <Trash2 size={16} />
          Clear Conversation
        </button>

        {/* Footer */}
        <div className="sidebar-footer">
          <p>Smart Assistant v1.0</p>
          <p>Runs locally on your machine</p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
