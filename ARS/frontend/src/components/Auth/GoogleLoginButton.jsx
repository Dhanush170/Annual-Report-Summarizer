/**
 * GoogleLoginButton.jsx
 * Single button that redirects the browser to the FastAPI Google OAuth flow.
 * No client-side OAuth SDK needed — the backend handles the full redirect dance.
 */

const S = {
  btn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    width: '100%',
    padding: '12px 18px',
    background: 'linear-gradient(180deg, #1d2f4d 0%, #18263f 100%)',
    color: '#dbeafe',
    borderRadius: '12px',
    fontFamily: 'var(--font-body)',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    border: '1px solid rgba(113, 168, 255, 0.35)',
    boxShadow: '0 16px 36px rgba(11, 20, 35, 0.45)',
    transition: 'all 0.18s ease',
    letterSpacing: '-0.01em',
  }
}

// Google's official "G" logo SVG
function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 48 48">
      <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.2l6.7-6.7C35.8 2.5 30.2 0 24 0 14.7 0 6.7 5.5 2.7 13.5l7.8 6C12.5 13.4 17.8 9.5 24 9.5z"/>
      <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.2-.4-4.7H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17.3z"/>
      <path fill="#FBBC05" d="M10.5 28.5c-.5-1.5-.8-3.2-.8-4.9s.3-3.3.8-4.8l-7.8-6C.9 15.9 0 19.8 0 24s.9 8.1 2.7 11.5l7.8-7z"/>
      <path fill="#34A853" d="M24 48c6.2 0 11.5-2 15.3-5.5l-7.5-5.8c-2.1 1.4-4.8 2.3-7.8 2.3-6.2 0-11.5-3.9-13.5-9.5l-7.8 7C6.7 42.5 14.7 48 24 48z"/>
    </svg>
  )
}

export default function GoogleLoginButton() {
  const handleLogin = () => {
    // Redirect browser to FastAPI's /auth/login endpoint
    // FastAPI will then redirect to Google, and Google will call /auth/callback
    window.location.href = 'http://localhost:8000/auth/login'
  }

  return (
    <button
      style={S.btn}
      onClick={handleLogin}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-1px)'
        e.currentTarget.style.boxShadow = '0 20px 38px rgba(11, 20, 35, 0.55)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = '0 16px 36px rgba(11, 20, 35, 0.45)'
      }}
    >
      <GoogleIcon />
      Continue with Google
    </button>
  )
}

