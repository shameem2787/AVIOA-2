import React, { useState, useRef, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { sendMessage, uploadDocument, addMessage } from '../../store/chatSlice'
import './CopilotPanel.css'

export default function CopilotPanel() {
  const dispatch = useDispatch()
  const { messages, loading } = useSelector((s) => s.chat)
  const inv = useSelector((s) => s.investigation.current)
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const fileRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = () => {
    const text = input.trim()
    if (!text || loading) return
    dispatch(addMessage({ role: 'user', content: text }))
    setInput('')
    const history = messages.map((m) => ({ role: m.role, content: m.content }))
    dispatch(sendMessage({
      message: text,
      investigationId: inv?.id,
      history,
    }))
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFile = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    dispatch(addMessage({
      role: 'user',
      content: `Uploaded document: ${file.name}`,
    }))
    dispatch(uploadDocument({ file, investigationId: inv?.id }))
    e.target.value = ''
  }

  return (
    <div className="copilot">
      <div className="copilot-header">
        <div className="copilot-title">
          <span className="copilot-icon">◈</span>
          <div>
            <strong>RCA Copilot</strong>
            <span className="copilot-sub">Powered by LangGraph · Groq</span>
          </div>
        </div>
      </div>

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg msg-${m.role}`}>
            <div className="msg-bubble">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="msg msg-assistant">
            <div className="msg-bubble typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="composer">
        <input
          type="file"
          ref={fileRef}
          accept=".pdf,.txt,.eml,.msg"
          style={{ display: 'none' }}
          onChange={handleFile}
        />
        <button
          className="attach-btn"
          title="Upload PDF or text"
          onClick={() => fileRef.current?.click()}
          disabled={loading}
        >
          📎
        </button>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Paste deviation text, email, or type a correction…"
          rows={1}
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          →
        </button>
      </div>
    </div>
  )
}
