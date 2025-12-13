import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { DashboardProvider } from './context/DashboardContext'
import { I18nProvider } from './i18n'
import Layout from './components/Layout'
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
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<GlobalView />} />
              <Route path="details/:service" element={<DetailedView />} />
              <Route path="grafana" element={<GrafanaView />} />
              <Route path="opensearch" element={<OpenSearchView />} />
              <Route path="kafka" element={<KafkaView />} />
              <Route path="observability" element={<ObservabilityRemediationView />} />
              <Route path="security" element={<SecurityComplianceView />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </DashboardProvider>
    </I18nProvider>
  )
}

export default App
