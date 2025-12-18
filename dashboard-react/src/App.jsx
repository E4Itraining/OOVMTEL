import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { DashboardProvider, useDashboard } from './context/DashboardContext'
import { I18nProvider } from './i18n'
import Layout from './components/Layout'
import WelcomePage from './pages/WelcomePage'
import CommandCenter from './pages/CommandCenter'
import GlobalView from './pages/GlobalView'
import TechnicalView from './pages/TechnicalView'
import BusinessKPIView from './pages/BusinessKPIView'
import AIAssistant from './pages/AIAssistant'
import DetailedView from './pages/DetailedView'
import GrafanaView from './pages/GrafanaView'
import OpenSearchView from './pages/OpenSearchView'
import KafkaView from './pages/KafkaView'
import ObservabilityRemediationView from './pages/ObservabilityRemediationView'
import SecurityComplianceView from './pages/SecurityComplianceView'

// Wrapper to handle onboarding redirect
function OnboardingGuard({ children }) {
  const { hasCompletedOnboarding } = useDashboard()

  if (!hasCompletedOnboarding) {
    return <Navigate to="/welcome" replace />
  }

  return children
}

function AppRoutes() {
  return (
    <Routes>
      {/* Welcome/Onboarding - no layout */}
      <Route path="/welcome" element={<WelcomePage />} />

      {/* Main app with layout */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/command-center" replace />} />
        <Route path="command-center" element={<CommandCenter />} />
        <Route path="dashboard" element={<GlobalView />} />
        <Route path="technical" element={<TechnicalView />} />
        <Route path="business-kpi" element={<BusinessKPIView />} />
        <Route path="assistant" element={<AIAssistant />} />
        <Route path="details/:service" element={<DetailedView />} />
        <Route path="grafana" element={<GrafanaView />} />
        <Route path="opensearch" element={<OpenSearchView />} />
        <Route path="kafka" element={<KafkaView />} />
        <Route path="observability" element={<ObservabilityRemediationView />} />
        <Route path="security" element={<SecurityComplianceView />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <I18nProvider>
      <DashboardProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </DashboardProvider>
    </I18nProvider>
  )
}

export default App
