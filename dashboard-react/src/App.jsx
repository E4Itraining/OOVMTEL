import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { DashboardProvider } from './context/DashboardContext'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { FavoritesProvider } from './components/FavoritesSystem'
import { I18nProvider } from './i18n'
import Layout from './components/Layout'
import WelcomePage from './pages/WelcomePage'
import LoginPage from './pages/LoginPage'
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

// Protected Route component
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-industrial-darker flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/welcome" element={<WelcomePage />} />

      {/* Protected Routes with Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
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

      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <I18nProvider>
      <ThemeProvider>
        <AuthProvider>
          <DashboardProvider>
            <FavoritesProvider>
              <BrowserRouter>
                <AppRoutes />
              </BrowserRouter>
            </FavoritesProvider>
          </DashboardProvider>
        </AuthProvider>
      </ThemeProvider>
    </I18nProvider>
  )
}

export default App
