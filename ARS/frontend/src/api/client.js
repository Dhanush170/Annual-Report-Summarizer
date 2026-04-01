/**
 * client.js
 * Central Axios instance for all API calls.
 * - Base URL points to FastAPI backend (proxied via Vite in dev)
 * - Automatically attaches the JWT Bearer token to every request
 * - Returns response.data directly so callers don't unwrap it manually
 */
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',   // Vite proxy forwards /api → http://localhost:8000
  timeout: 300000,   // 5 min timeout (pipeline can take up to 3 min)
})

// ── Request interceptor: inject JWT on every call ──
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('ars_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: unwrap .data, handle 401 globally ──
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage and redirect to login
      localStorage.removeItem('ars_token')
      localStorage.removeItem('ars_user')
      window.location.href = '/login'
    }
    // Bubble the error so individual call sites can handle it
    return Promise.reject(error.response?.data || error)
  }
)

// ── Typed API helpers used by hooks and pages ──

export const api = {

  // Auth
  signUp: (name, email, password)          => client.post('/auth/signup', { name, email, password }),
  signIn: (email, password)                => client.post('/auth/signin', { email, password }),
  getMe: ()                              => client.get('/auth/me'),

  // Reports
  listReports: ()                        => client.get('/reports/'),
  deleteReport: (company, year)          => client.delete(`/reports/${encodeURIComponent(company)}/${encodeURIComponent(year)}`),

  // Pipeline
  runPipeline: (formData)                => client.post('/pipeline/run', formData),
  getJobStatus: (jobId)                  => client.get(`/pipeline/status/${jobId}`),

  // Summaries
  getSummaries: (company, year)          => client.get(`/summaries/${encodeURIComponent(company)}/${year}`),
  resummarize: (company, year)           => client.post(`/summaries/${encodeURIComponent(company)}/${year}/resummarize`),

  // Translation
  getLanguages: ()                       => client.get('/translate/languages'),
  translate: (company, year, langCode)   => client.post('/translate/', {
    company, year, target_language_code: langCode
  }),

  // Audio
  generateAudio: (company, year, sectionKey, langCode = 'en') =>
    client.post('/audio/generate', {
      company, year,
      section_key:   sectionKey,
      language_code: langCode
    }),

  // Compare
  compare: (company, yearA, yearB)       => client.post('/compare/', {
    company, year_a: yearA, year_b: yearB
  }),

  // Chat
  sendMessage: (company, year, message)  => client.post('/chat/message', {
    company, year, message
  }),
  clearChat: (company, year)             => client.post('/chat/clear', { company, year }),
}

export default client