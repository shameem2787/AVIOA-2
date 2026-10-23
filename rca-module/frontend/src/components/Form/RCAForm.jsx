import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { commitInvestigation } from '../../store/investigationSlice'
import Section from './Section'
import Field from './Field'
import './RCAForm.css'

export default function RCAForm() {
  const dispatch = useDispatch()
  const inv = useSelector((s) => s.investigation.current)
  const status = useSelector((s) => s.investigation.status)

  const handleCommit = () => {
    if (inv?.id) {
      dispatch(commitInvestigation(inv.id))
    }
  }

  const empty = !inv

  return (
    <div className="rca-form">
      <div className="form-header">
        <div>
          <h1>Root Cause Analysis</h1>
          <p className="form-subtitle">Deviation Investigation · Evidence · CAPA</p>
        </div>
        {inv?.deviation_id && (
          <div className="dev-id font-mono">{inv.deviation_id}</div>
        )}
      </div>

      <div className="form-scroll">
        {empty && status !== 'extracting' && (
          <div className="empty-state">
            <div className="empty-icon">◇</div>
            <h3>No active investigation</h3>
            <p>
              Use the RCA Copilot on the right to paste a deviation description,
              email, or upload a PDF. The form will populate automatically.
            </p>
          </div>
        )}

        {status === 'extracting' && (
          <div className="empty-state extracting">
            <div className="spinner" />
            <h3>Analysing input…</h3>
            <p>Extracting fields, running structured investigation, preparing CAPA suggestions.</p>
          </div>
        )}

        {inv && (
          <>
            {/* 1. Identification */}
            <Section number="01" title="Incident Identification">
              <div className="grid-2">
                <Field label="Deviation / Investigation ID" value={inv.deviation_id} />
                <Field label="Severity" value={inv.severity} highlight={inv.severity} />
                <Field label="Date of Occurrence" value={inv.date_of_occurrence} />
                <Field label="Date Reported" value={inv.date_reported} />
                <Field label="Product / Material" value={inv.product_name} />
                <Field label="Batch / Lot Number" value={inv.batch_lot} />
                <Field label="Area / Equipment" value={inv.area_equipment} />
                <Field label="Process Step" value={inv.process_step} />
              </div>
              {inv.title && (
                <Field label="Title" value={inv.title} full />
              )}
            </Section>

            {/* 2. Details */}
            <Section number="02" title="Incident Details">
              <Field label="Description of Event" value={inv.description} multiline full />
              <div className="grid-2">
                <Field label="Affected Quantity" value={inv.affected_quantity} />
                <Field label="Immediate Actions Taken" value={inv.immediate_actions} />
              </div>
              {inv.impact_summary && (
                <Field label="Impact Summary" value={inv.impact_summary} multiline full />
              )}
            </Section>

            {/* 3. Investigation Method */}
            <Section number="03" title="Investigation Approach">
              <Field label="Method" value={inv.investigation_method || '5 Whys + Fishbone'} />
              
              {inv.five_whys && inv.five_whys.length > 0 && (
                <div className="whys-block">
                  <h4>5 Whys Chain</h4>
                  <ol className="whys-list">
                    {inv.five_whys.map((w, i) => (
                      <li key={i}>
                        <span className="why-q">{w.why || `Why ${i + 1}?`}</span>
                        <span className="why-a">{w.answer}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {inv.fishbone && (
                <div className="fishbone-block">
                  <h4>Fishbone Factors</h4>
                  <div className="fishbone-grid">
                    {['man', 'machine', 'material', 'method', 'measurement', 'environment'].map((cat) => (
                      <div key={cat} className="fish-cat">
                        <span className="fish-label">{cat}</span>
                        <ul>
                          {(inv.fishbone[cat] || []).map((f, i) => (
                            <li key={i}>{f}</li>
                          ))}
                          {(!inv.fishbone[cat] || inv.fishbone[cat].length === 0) && (
                            <li className="empty-factor">—</li>
                          )}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Section>

            {/* 4. Root Cause */}
            <Section number="04" title="Root Cause Analysis">
              {inv.potential_root_causes && inv.potential_root_causes.length > 0 ? (
                <div className="causes-list">
                  {inv.potential_root_causes.map((rc, i) => (
                    <div key={i} className="cause-card">
                      <div className="cause-header">
                        <span className="cause-title">{rc.cause}</span>
                        <span className={`confidence conf-${(rc.confidence || 'medium').toLowerCase()}`}>
                          {rc.confidence || 'Medium'}
                        </span>
                      </div>
                      {rc.evidence && <p className="cause-evidence">{rc.evidence}</p>}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="placeholder-text">Root causes will appear after AI analysis.</p>
              )}

              {inv.contributing_factors && inv.contributing_factors.length > 0 && (
                <div className="contrib-block">
                  <h4>Contributing Factors</h4>
                  <ul>
                    {inv.contributing_factors.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}

              {inv.missing_evidence && inv.missing_evidence.length > 0 && (
                <div className="missing-block">
                  <h4>Missing / Required Evidence</h4>
                  <ul>
                    {inv.missing_evidence.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Section>

            {/* 5. CAPA */}
            <Section number="05" title="CAPA Recommendations">
              {inv.capa_summary && (
                <Field label="Summary" value={inv.capa_summary} multiline full />
              )}

              {inv.corrective_actions && inv.corrective_actions.length > 0 && (
                <div className="capa-group">
                  <h4>Corrective Actions</h4>
                  {inv.corrective_actions.map((a, i) => (
                    <div key={i} className="capa-item">
                      <div className="capa-action">{a.action}</div>
                      <div className="capa-meta">
                        <span>{a.owner || 'QA'}</span>
                        {a.due_date && <span>· {a.due_date}</span>}
                      </div>
                      {a.rationale && <p className="capa-rationale">{a.rationale}</p>}
                    </div>
                  ))}
                </div>
              )}

              {inv.preventive_actions && inv.preventive_actions.length > 0 && (
                <div className="capa-group">
                  <h4>Preventive Actions</h4>
                  {inv.preventive_actions.map((a, i) => (
                    <div key={i} className="capa-item">
                      <div className="capa-action">{a.action}</div>
                      <div className="capa-meta">
                        <span>{a.owner || 'QA'}</span>
                        {a.due_date && <span>· {a.due_date}</span>}
                      </div>
                      {a.rationale && <p className="capa-rationale">{a.rationale}</p>}
                    </div>
                  ))}
                </div>
              )}
            </Section>

            {inv.ai_risk_notes && (
              <Section number="06" title="AI Notes">
                <p className="ai-notes">{inv.ai_risk_notes}</p>
              </Section>
            )}
          </>
        )}
      </div>

      {inv && (
        <div className="form-footer">
          <button
            className="commit-btn"
            onClick={handleCommit}
            disabled={inv.is_committed || !inv.id}
          >
            {inv.is_committed ? 'Investigation Committed' : 'Commit Investigation'}
          </button>
        </div>
      )}
    </div>
  )
}
