/**
 * App.jsx
 * Top-level router + auth guard.
 *
 * Routes:
 *   /login                        → Login page (public)
 *   /auth/callback?token=...      → Reads JWT from URL, stores it, redirects to /
 *   /                             → Dashboard (protected)
 *   /report/:company/:year        → ReportView (protected)
 *   /compare/:company             → Compare (protected)
 *
 * Auth guard: any protected route redirects to /login if no valid session.
 */
import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import { useState } from 'react'

import Login      from './pages/Login'
import Dashboard  from './pages/Dashboard'
import ReportView from './pages/ReportView'
import Compare    from './pages/Compare'
import ComplianceNoticeModal from './components/Auth/ComplianceNoticeModal'

// ── Handles the Google OAuth redirect — reads token from URL ──
function AuthCallback({ loginWithToken }) {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const [statusText, setStatusText] = useState('Signing you in...')

  useEffect(() => {
    let mounted = true

    const completeOAuth = async () => {
    const token = params.get('token')
      if (!token) {
        navigate('/login', { replace: true })
        return
      }

      try {
        if (mounted) setStatusText('Verifying your session...')
        await loginWithToken(token, { verifyWithServer: false })
        if (mounted) navigate('/', { replace: true })
      } catch (_) {
        if (mounted) {
          setStatusText('Sign-in failed. Redirecting...')
          setTimeout(() => navigate('/login', { replace: true }), 700)
        }
      }
    }

    completeOAuth()

    return () => {
      mounted = false
    }
  }, [])

  return (
    <div style={{
      height: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', color: 'var(--text-muted)',
      flexDirection: 'column', gap: 16,
    }}>
      <span className="spinner" style={{ width: 28, height: 28 }} />
      <span style={{ fontSize: 14 }}>{statusText}</span>
    </div>
  )
}

// ── Route guard: redirects to /login if not authenticated ──
function Protected({ element, user, loading }) {
  if (loading) {
    return (
      <div style={{
        height: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center',
      }}>
        <span className="spinner" style={{ width: 28, height: 28 }} />
      </div>
    )
  }
  return user ? element : <Navigate to="/login" replace />
}

// ── Root app with router ──
export default function App() {
  const { user, loading, loginWithToken, signIn, signUp, logout } = useAuth()
  const [showCompliance, setShowCompliance] = useState(false)

  useEffect(() => {
    if (!loading && user) {
      const acknowledged = sessionStorage.getItem('ars_compliance_ack_v1')
      setShowCompliance(!acknowledged)
    }
  }, [user, loading])

  const acknowledgeCompliance = () => {
    sessionStorage.setItem('ars_compliance_ack_v1', 'true')
    setShowCompliance(false)
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route
          path="/login"
          element={
            user && !loading
              ? <Navigate to="/" replace />
              : <Login onSignIn={signIn} onSignUp={signUp} />
          }
        />

        {/* OAuth callback — must be public */}
        <Route path="/auth/callback" element={<AuthCallback loginWithToken={loginWithToken} />} />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <Protected
              loading={loading}
              user={user}
              element={<Dashboard user={user} onLogout={logout} />}
            />
          }
        />
        <Route
          path="/report/:company/:year"
          element={
            <Protected
              loading={loading}
              user={user}
              element={<ReportView user={user} onLogout={logout} />}
            />
          }
        />
        <Route
          path="/compare/:company"
          element={
            <Protected
              loading={loading}
              user={user}
              element={<Compare user={user} />}
            />
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <ComplianceNoticeModal open={showCompliance} onAcknowledge={acknowledgeCompliance} />
    </BrowserRouter>
  )
}
