import React from 'react'
import { useSelector } from 'react-redux'
import './Layout.css'

export default function Layout({ children }) {
  const status = useSelector((s) => s.investigation.status)
  const current = useSelector((s) => s.investigation.current)

  const statusLabel = () => {
    if (status === 'extracting') return 'Extracting…'
    if (current?.is_committed) return 'Committed'
    if (current?.status === 'Ready for Review') return 'Ready for Review'
    if (current?.status === 'Under Investigation') return 'Under Investigation'
    if (current) return current.status || 'Draft'
    return 'Awaiting Intake'
  }

  const statusClass = () => {
    if (status === 'extracting') return 'status-extracting'
    if (current?.is_committed || current?.status === 'Ready for Review') return 'status-ready'
    if (current) return 'status-active'
    return 'status-idle'
  }

  return (
    <div className="app-shell">
      <header className="topbar glass">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div className="brand-text">
            <span className="brand-name">AIVOA</span>
            <span className="brand-sub">Root Cause Analysis</span>
          </div>
        </div>

        <div className="topbar-center">
          <span className="module-label">API & FDF Quality System · RCA Module</span>
        </div>

        <div className="topbar-right">
          <div className={`status-pill ${statusClass()}`}>
            <span className="status-dot" />
            {statusLabel()}
          </div>
        </div>
      </header>
      {children}
    </div>
  )
}
