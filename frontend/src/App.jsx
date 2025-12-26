import { useState, useRef, useEffect, useCallback } from 'react'
import './App.css'

// Polling interval in ms - animation duration matches this
const POLL_INTERVAL = 2000

// Hook for smooth animated value transitions
function useAnimatedValue(target, duration = POLL_INTERVAL) {
  const [display, setDisplay] = useState(target)
  const animationRef = useRef(null)
  const startTimeRef = useRef(null)
  const startValueRef = useRef(target)
  const targetRef = useRef(target)

  useEffect(() => {
    // Only restart animation if target changed significantly
    if (Math.abs(target - targetRef.current) < 0.01) return
    
    startValueRef.current = display
    targetRef.current = target
    startTimeRef.current = performance.now()

    const animate = (currentTime) => {
      const elapsed = currentTime - startTimeRef.current
      const progress = Math.min(elapsed / duration, 1)
      
      // Smooth ease-in-out with exponential smoothing
      const eased = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2
      
      const newValue = startValueRef.current + (targetRef.current - startValueRef.current) * eased
      setDisplay(newValue)

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate)
      }
    }

    animationRef.current = requestAnimationFrame(animate)

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [target, duration])

  return display
}

// Color gradient function (green → yellow → red)
function getColor(value, thresholds) {
  const [low, mid, high] = thresholds
  
  if (value <= low) {
    return 'hsl(120, 70%, 50%)' // Green
  } else if (value <= mid) {
    // Green to Yellow
    const ratio = (value - low) / (mid - low)
    const hue = 120 - (ratio * 60) // 120 (green) → 60 (yellow)
    return `hsl(${hue}, 80%, 50%)`
  } else if (value <= high) {
    // Yellow to Red
    const ratio = (value - mid) / (high - mid)
    const hue = 60 - (ratio * 60) // 60 (yellow) → 0 (red)
    return `hsl(${hue}, 85%, 50%)`
  } else {
    return 'hsl(0, 90%, 50%)' // Red
  }
}

// Telemetry Panel Component
function TelemetryPanel({ status }) {
  const cpu = useAnimatedValue(status.cpu || 0)
  const memory = useAnimatedValue(status.memory || 0)
  const load1m = useAnimatedValue(status.load_avg?.['1m'] || 0)
  const load5m = useAnimatedValue(status.load_avg?.['5m'] || 0)
  const load15m = useAnimatedValue(status.load_avg?.['15m'] || 0)
  const temp = useAnimatedValue(status.temperature || 0)

  const metrics = [
    { label: 'CPU', value: cpu, unit: '%', thresholds: [50, 80, 95], decimals: 0 },
    { label: 'MEM', value: memory, unit: '%', thresholds: [60, 85, 95], decimals: 0 },
    { label: 'LOAD', value: load1m, unit: '', thresholds: [4, 8, 12], decimals: 2 },
    { label: 'TEMP', value: temp, unit: '°C', thresholds: [60, 80, 90], decimals: 0 },
  ]

  return (
    <div className="telemetry-panel">
      {metrics.map(m => (
        <div key={m.label} className="telemetry-metric">
          <span className="telemetry-label">{m.label}</span>
          <span 
            className="telemetry-value"
            style={{ color: getColor(m.value, m.thresholds) }}
          >
            {m.value.toFixed(m.decimals)}{m.unit}
          </span>
        </div>
      ))}
      <div className="telemetry-load-detail">
        <span className="telemetry-sub" style={{ color: getColor(load5m, [4, 8, 12]) }}>
          5m: {load5m.toFixed(2)}
        </span>
        <span className="telemetry-sub" style={{ color: getColor(load15m, [4, 8, 12]) }}>
          15m: {load15m.toFixed(2)}
        </span>
      </div>
    </div>
  )
}

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'andy-os Online. How can I help you?' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState({ 
    cpu: 0, 
    memory: 0, 
    load_avg: { '1m': 0, '5m': 0, '15m': 0 },
    temperature: 0,
    status: 'healthy', 
    mode: 'Performance' 
  })
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Randomize theme hue on mount
    const hue = Math.floor(Math.random() * 360)
    document.documentElement.style.setProperty('--theme-hue', hue)
  }, [])

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('/api/status')
        if (res.ok) {
          const data = await res.json()
          setStatus(data)
        }
      } catch (e) {
        console.error("Failed to fetch status", e)
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }))
      const payload = {
        message: userMsg.content,
        history: [...history, userMsg]
      }

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const data = await response.json()
      
      const agentMsg = { 
        role: 'assistant', 
        content: data.response,
        tool_output: data.tool_output 
      }
      setMessages(prev => [...prev, agentMsg])

    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { role: 'system', content: 'Error connecting to andy-os.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-title">
          <h1>andy-os</h1>
          <TelemetryPanel status={status} />
        </div>
        <div className={`status-indicator ${isLoading ? 'loading-pulse' : 'online'}`}></div>
      </header>
      
      <main className="chat-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
              {msg.tool_output && (
                  <div className="tool-output">
                      <div className="tool-label">Tool Result</div>
                      <pre>{JSON.stringify(msg.tool_output, null, 2)}</pre>
                  </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <span className="dot"></span><span className="dot"></span><span className="dot"></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <footer className="input-area">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter command or message..."
            autoFocus
          />
          <button type="submit" disabled={isLoading}>
            Send
          </button>
        </form>
      </footer>
    </div>
  )
}

export default App
