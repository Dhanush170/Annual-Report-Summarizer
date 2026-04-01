/**
 * useAuth.js
 * Manages Google OAuth login state + JWT token lifecycle.
 *
 * Token storage: localStorage (survives page refreshes)
 * Token is read by client.js interceptor on every API call.
 *
 * Usage:
 *   const { user, loading, logout } = useAuth()
 */
import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'

function decodeJwtPayload(token) {
  try {
    const payload = token.split('.')[1]
    if (!payload) return null
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join('')
    )
    return JSON.parse(json)
  } catch (_) {
    return null
  }
}

export function useAuth() {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)  // true while verifying token on startup

  const setSession = useCallback((token, userData) => {
    localStorage.setItem('ars_token', token)
    sessionStorage.removeItem('ars_compliance_ack_v1')
    setUser(userData)
    localStorage.setItem('ars_user', JSON.stringify(userData))
  }, [])

  // ── On mount: restore session from localStorage ──
  useEffect(() => {
    const token = localStorage.getItem('ars_token')
    const saved = localStorage.getItem('ars_user')

    if (!token) {
      setLoading(false)
      return
    }

    if (saved) {
      // Optimistically restore from cache so UI doesn't flash
      try { setUser(JSON.parse(saved)) } catch (_) {}
    }

    // Verify token is still valid against the backend
    api.getMe()
      .then((data) => {
        setUser(data)
        localStorage.setItem('ars_user', JSON.stringify(data))
      })
      .catch(() => {
        // Token invalid/expired — clear everything
        localStorage.removeItem('ars_token')
        localStorage.removeItem('ars_user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  // ── Called from /auth/callback page after Google redirects back ──
  const loginWithToken = useCallback(async (token, opts = { verifyWithServer: true }) => {
    setLoading(true)
    localStorage.setItem('ars_token', token)
    sessionStorage.removeItem('ars_compliance_ack_v1')

    if (!opts.verifyWithServer) {
      const payload = decodeJwtPayload(token)
      if (payload?.email) {
        const fastUser = {
          email: payload.email,
          name: payload.name || payload.email,
          picture: payload.picture || null,
          auth_provider: payload.auth_provider || 'google',
        }
        setUser(fastUser)
        localStorage.setItem('ars_user', JSON.stringify(fastUser))
        setLoading(false)
        return fastUser
      }
    }

    try {
      const data = await api.getMe()
      setUser(data)
      localStorage.setItem('ars_user', JSON.stringify(data))
      return data
    } catch (_) {
      localStorage.removeItem('ars_token')
      localStorage.removeItem('ars_user')
      setUser(null)
      throw new Error('OAuth session verification failed.')
    } finally {
      setLoading(false)
    }
  }, [])

  const signIn = useCallback(async (email, password) => {
    const data = await api.signIn(email, password)
    setSession(data.access_token, data.user)
    return data.user
  }, [setSession])

  const signUp = useCallback(async (name, email, password) => {
    const data = await api.signUp(name, email, password)
    setSession(data.access_token, data.user)
    return data.user
  }, [setSession])

  const logout = useCallback(() => {
    localStorage.removeItem('ars_token')
    localStorage.removeItem('ars_user')
    sessionStorage.removeItem('ars_compliance_ack_v1')
    setUser(null)
  }, [])

  return { user, loading, loginWithToken, signIn, signUp, logout }
}