import React from 'react'
import './Section.css'

export default function Section({ number, title, children }) {
  return (
    <section className="form-section">
      <div className="section-header">
        <span className="section-num">{number}</span>
        <h2>{title}</h2>
      </div>
      <div className="section-body">{children}</div>
    </section>
  )
}
