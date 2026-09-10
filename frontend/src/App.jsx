import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import Layout from './components/layout/Layout'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import AnalyzeECG from './pages/AnalyzeECG'
import Results from './pages/Results'
import History from './pages/History'
import AnalysisDetails from './pages/AnalysisDetails'
import Analytics from './pages/Analytics'
import ModelInfo from './pages/ModelInfo'
import Settings from './pages/Settings'
import Help from './pages/Help'

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analyze" element={<AnalyzeECG />} />
          <Route path="/results/:id" element={<Results />} />
          <Route path="/history" element={<History />} />
          <Route path="/history/:id" element={<AnalysisDetails />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/model" element={<ModelInfo />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ThemeProvider>
  )
}
