import React from 'react'
import Layout from './components/Layout/Layout'
import RCAForm from './components/Form/RCAForm'
import CopilotPanel from './components/Chat/CopilotPanel'
import './styles/app.css'

export default function App() {
  return (
    <Layout>
      <div className="workspace">
        <section className="form-pane liquid">
          <RCAForm />
        </section>
        <section className="copilot-pane glass-strong">
          <CopilotPanel />
        </section>
      </div>
    </Layout>
  )
}
