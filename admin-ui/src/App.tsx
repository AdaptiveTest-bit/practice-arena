import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { TemplateList } from './pages/TemplateList'
import { TemplateEditor } from './pages/TemplateEditor'
import { ReviewQueue } from './pages/ReviewQueue'
import { CoverageDashboard } from './pages/CoverageDashboard'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/templates" element={<TemplateList />} />
        <Route path="/templates/new" element={<TemplateEditor />} />
        <Route path="/templates/:id/edit" element={<TemplateEditor />} />
        <Route path="/review" element={<ReviewQueue />} />
        <Route path="/coverage" element={<CoverageDashboard />} />
      </Routes>
    </Layout>
  )
}

export default App
