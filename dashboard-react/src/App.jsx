import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { DashboardProvider } from './context/DashboardContext'
import { I18nProvider } from './i18n'
import { FavoritesProvider } from './components/FavoritesSystem'
import { OnboardingProvider } from './components/OnboardingTour'
import { WidgetsProvider } from './components/DashboardWidgets'
import OnboardingTour from './components/OnboardingTour'
import Layout from './components/Layout'
import WelcomePage from './pages/WelcomePage'
import CommandCenter from './pages/CommandCenter'
import TechnicalView from './pages/TechnicalView'
import BusinessKPIView from './pages/BusinessKPIView'
import AIAssistant from './pages/AIAssistant'
import GlobalView from './pages/GlobalView'
import DetailedView from './pages/DetailedView'
import GrafanaView from './pages/GrafanaView'
import OpenSearchView from './pages/OpenSearchView'
import KafkaView from './pages/KafkaView'
import ObservabilityRemediationView from './pages/ObservabilityRemediationView'
import SecurityComplianceView from './pages/SecurityComplianceView'
import ImpactAnalysisView from './pages/ImpactAnalysisView'
import DPODashboardView from './pages/DPODashboardView'
import ComplianceDashboardView from './pages/ComplianceDashboardView'
import RSEDashboardView from './pages/RSEDashboardView'
import GreenITDashboardView from './pages/GreenITDashboardView'
import SOCDashboardView from './pages/SOCDashboardView'
import MLOpsDashboardView from './pages/MLOpsDashboardView'

// Component to check if user should be redirected to welcome page
function PersonaGuard({ children }) {
  const location = useLocation()
  const selectedPersona = localStorage.getItem('selectedPersona')

  // If no persona selected and not already on welcome page, redirect to welcome
  if (!selectedPersona && location.pathname !== '/welcome') {
    return <Navigate to="/welcome" replace />
  }

  return children
}

function App() {
  return (
    <I18nProvider>
      <DashboardProvider>
        <FavoritesProvider>
          <OnboardingProvider>
            <WidgetsProvider>
              <BrowserRouter>
                <PersonaGuard>
                  <Routes>
                    {/* Welcome/Onboarding Page - No Layout */}
                    <Route path="/welcome" element={<WelcomePage />} />

                    {/* Main App with Layout */}
                    <Route path="/" element={<Layout />}>
                      <Route index element={<CommandCenter />} />
                      <Route path="command-center" element={<CommandCenter />} />
                      <Route path="technical" element={<TechnicalView />} />
                      <Route path="business-kpi" element={<BusinessKPIView />} />
                      <Route path="ai-assistant" element={<AIAssistant />} />
                      <Route path="dashboard" element={<GlobalView />} />
                      <Route path="details/:service" element={<DetailedView />} />
                      <Route path="grafana" element={<GrafanaView />} />
                      <Route path="opensearch" element={<OpenSearchView />} />
                      <Route path="kafka" element={<KafkaView />} />
                      <Route path="observability" element={<ObservabilityRemediationView />} />
                      <Route path="security" element={<SecurityComplianceView />} />
                      <Route path="impact-analysis" element={<ImpactAnalysisView />} />
                      {/* Role-specific dashboards */}
                      <Route path="dpo-dashboard" element={<DPODashboardView />} />
                      <Route path="compliance-dashboard" element={<ComplianceDashboardView />} />
                      <Route path="rse-dashboard" element={<RSEDashboardView />} />
                      <Route path="greenit-dashboard" element={<GreenITDashboardView />} />
                      <Route path="soc-dashboard" element={<SOCDashboardView />} />
                      <Route path="mlops-dashboard" element={<MLOpsDashboardView />} />
                    </Route>
                  </Routes>
                </PersonaGuard>
              </BrowserRouter>
            </WidgetsProvider>
          </OnboardingProvider>
        </FavoritesProvider>
      </DashboardProvider>
    </I18nProvider>
  )
}

export default App
