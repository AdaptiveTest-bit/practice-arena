import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { TemplateList } from './pages/TemplateList'
import { UniversalTemplateEditor } from './pages/UniversalTemplateEditor'
import { ReviewQueue } from './pages/ReviewQueue'
import { CoverageDashboard } from './pages/CoverageDashboard'
import { GraphBuilder } from './pages/GraphBuilder'
import { FormulaList } from './pages/FormulaList'
import { FormulaBuilder } from './pages/FormulaBuilder'
import { MisconceptionsManager } from './pages/MisconceptionsManager'
import { ConceptsManager } from './pages/ConceptsManager'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        
        {/* Templates */}
        <Route path="/templates" element={<TemplateList />} />
        <Route path="/templates/new" element={<UniversalTemplateEditor />} />
        <Route path="/templates/:id/edit" element={<UniversalTemplateEditor />} />
        
        {/* Formulas - Gateway Feature */}
        <Route path="/formulas" element={<FormulaList />} />
        <Route path="/formulas/new" element={<FormulaBuilder />} />
        <Route path="/formulas/:id/edit" element={<FormulaBuilder />} />
        
        {/* Review & Coverage */}
        <Route path="/review" element={<ReviewQueue />} />
        <Route path="/coverage" element={<CoverageDashboard />} />
        <Route path="/graph" element={<GraphBuilder />} />
        
        {/* Content Management */}
        <Route path="/misconceptions" element={<MisconceptionsManager />} />
        <Route path="/concepts" element={<ConceptsManager />} />
      </Routes>
    </Layout>
  )
}

export default App
