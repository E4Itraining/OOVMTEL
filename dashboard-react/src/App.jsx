import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
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

function App() {
  return (
    <I18nProvider>
      <DashboardProvider>
        <FavoritesProvider>
          <OnboardingProvider>
            <WidgetsProvider>
              <BrowserRouter>
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
                  </Route>
                </Routes>
              </BrowserRouter>
            </WidgetsProvider>
          </OnboardingProvider>
        </FavoritesProvider>
      </DashboardProvider>
    </I18nProvider>
  )
}

export default App
