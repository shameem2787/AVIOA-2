import React from 'react'
import './Field.css'

export default function Field({ label, value, multiline, full, highlight }) {
  const isEmpty = value === null || value === undefined || value === ''
  const display = isEmpty ? '—' : value

  const severityClass = () => {
    if (!highlight) return ''
    const s = String(highlight).toLowerCase()
    if (s.includes('critical')) return 'sev-critical'
    if (s.includes('major')) return 'sev-major'
    if (s.includes('minor')) return 'sev-minor'
    return ''
  }

  return (
    <div className={`field ${full ? 'full' : ''} ${severityClass()}`}>
      <label>{label}</label>
      {multiline ? (
        <div className={`field-value multiline ${isEmpty ? 'empty' : ''}`}>{display}</div>
      ) : (
        <div className={`field-value ${isEmpty ? 'empty' : ''}`}>{display}</div>
      )}
    </div>
  )
}
