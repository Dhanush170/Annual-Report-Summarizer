/**
 * ChatSidebar.jsx
 * Full chat interface — messages list + input box.
 * Auto-scrolls to latest message. Supports clearing history.
 */
import { useState, useRef, useEffect } from 'react'
import { api } from '../../api/client'

export default function ChatSidebar({ company, year }) {
  const [messages, setMessages] = useState([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const bottomRef               = useRef()

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const { answer } = await api.sendMessage(company, year, text)
      setMessages(prev => [...prev, { role: 'assistant', content: answer }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Could not get a response. Please try again.',
        error: true,
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleClear = async () => {
    await api.clearChat(company, year).catch(() => {})
    setMessages([])
  }

  return (
    <div className="chat-shell">
      {/* Header */}
      <div className="chat-head">
        <div>
          <div className="chat-title">Chat</div>
          <div className="chat-subtitle">
            Ask anything about this report
          </div>
        </div>
        {messages.length > 0 && (
          <button onClick={handleClear} className="btn-outline" style={{ fontSize: '12px', padding: '6px 10px' }}>
            Clear
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div style={{ fontSize: '26px', marginBottom: '10px' }}>◎</div>
            Ask about financials, risks, strategy, or anything in the report.
            <div className="chat-quick">
              {[
                'What was the total revenue this year?',
                'What are the top 3 risks flagged?',
                "What did the CEO say about growth?",
              ].map(q => (
                <button
                  key={q}
                  onClick={() => { setInput(q); }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`fade-in chat-bubble ${msg.role === 'user' ? 'user' : 'assistant'} ${msg.error ? 'error' : ''}`}
          >
            {msg.content}
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="fade-in" style={{ display: 'flex', gap: '4px', padding: '8px 4px', alignItems: 'center' }}>
            {[0, 1, 2].map(i => (
              <div key={i} style={{
                width: 7, height: 7,
                borderRadius: '50%',
                background: 'var(--text-muted)',
                animation: `fadeIn 0.6s ${i * 0.15}s ease infinite alternate`,
              }} />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input box */}
      <div className="chat-compose">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything... (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || loading}
          className={input.trim() && !loading ? 'btn-primary chat-send' : 'btn-outline chat-send'}
        >
          ➤
        </button>
      </div>
    </div>
  )
}
