// src/App.jsx
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useSessionStore } from './store/sessionStore'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import SessionSetup from './pages/SessionSetup'
import DiscoveryFlow from './pages/DiscoveryFlow'

/**
 * ProtectedRoute
 * Redirects to /login if not authenticated.
 * For dev mode, allows dev-token to pass through.
 */
function ProtectedRoute({ children }) {
  const authToken = useSessionStore((s) => s.authToken)
  if (!authToken) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/session-setup"
          element={
            <ProtectedRoute>
              <SessionSetup />
            </ProtectedRoute>
          }
        />

        <Route
          path="/discovery"
          element={
            <ProtectedRoute>
              <DiscoveryFlow />
            </ProtectedRoute>
          }
        />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
