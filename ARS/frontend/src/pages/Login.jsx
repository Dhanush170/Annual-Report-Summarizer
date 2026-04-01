import { useState } from 'react'
import GoogleLoginButton from '../components/Auth/GoogleLoginButton'

export default function Login({ onSignIn, onSignUp }) {
  const [mode, setMode] = useState('signin')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const isSignUp = mode === 'signup'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!email.trim() || !password.trim()) {
      setError('Email and password are required.')
      return
    }

    if (isSignUp) {
      if (!name.trim()) {
        setError('Name is required for registration.')
        return
      }
      if (password.length < 8) {
        setError('Password must be at least 8 characters.')
        return
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match.')
        return
      }
    }

    setSubmitting(true)
    try {
      if (isSignUp) {
        await onSignUp(name.trim(), email.trim(), password)
      } else {
        await onSignIn(email.trim(), password)
      }
    } catch (err) {
      setError(err?.detail || err?.error || 'Authentication failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-aurora" />
      <div className="auth-layout fade-up">
        <section className="auth-story">
          <div className="auth-badge">ARS Platform</div>
          <h1>Annual report intelligence for sharp decision making.</h1>
          <p>
            Upload, summarize, compare, and chat with annual reports in a focused workflow tailored for financial analysis.
          </p>
          <div className="auth-story-grid">
            <div>
              <span>Fast ingestion</span>
              <strong>1-3 minutes pipeline</strong>
            </div>
            <div>
              <span>Cross-year deltas</span>
              <strong>Section-level insights</strong>
            </div>
            <div>
              <span>Voice summaries</span>
              <strong>Section or full report audio</strong>
            </div>
          </div>
        </section>

        <section className="auth-panel">
          <div className="auth-brand">Annual Report Summarizer</div>
          <div className="auth-tabs">
            <button className={mode === 'signin' ? 'tab active' : 'tab'} onClick={() => setMode('signin')}>
              Sign In
            </button>
            <button className={mode === 'signup' ? 'tab active' : 'tab'} onClick={() => setMode('signup')}>
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {isSignUp && (
              <label>
                Full Name
                <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Aarav Mehta" />
              </label>
            )}

            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
              />
            </label>

            {isSignUp && (
              <label>
                Confirm Password
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                />
              </label>
            )}

            {error && <div className="auth-error">{error}</div>}

            <button className="btn-primary" type="submit" disabled={submitting}>
              {submitting ? 'Please wait...' : isSignUp ? 'Create Account' : 'Continue'}
            </button>
          </form>

          <div className="auth-separator">or continue with</div>
          <GoogleLoginButton />

          <p className="auth-footnote">
            By signing in, you agree to use ARS for compliant annual report analysis workflows.
          </p>
        </section>
      </div>
    </div>
  )
}