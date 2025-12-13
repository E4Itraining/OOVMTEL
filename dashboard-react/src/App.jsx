import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { DashboardProvider } from './context/DashboardContext'
import Layout from './components/Layout'
import GlobalView from './pages/GlobalView'
import DetailedView from './pages/DetailedView'
import GrafanaView from './pages/GrafanaView'
import OpenSearchView from './pages/OpenSearchView'
import KafkaView from './pages/KafkaView'

function App() {
  return (
    <DashboardProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<GlobalView />} />
            <Route path="details/:service" element={<DetailedView />} />
            <Route path="grafana" element={<GrafanaView />} />
            <Route path="opensearch" element={<OpenSearchView />} />
            <Route path="kafka" element={<KafkaView />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DashboardProvider>
  )
}

export default App
