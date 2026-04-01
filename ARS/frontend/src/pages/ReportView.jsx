import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import SectionTabs from '../components/Summary/SectionTabs'
import SectionCard from '../components/Summary/SectionCard'
import TranslatePanel from '../components/Summary/TranslatePanel'
import AudioPlayer from '../components/Summary/AudioPlayer'
import ChatSidebar from '../components/Chat/ChatSidebar'

export default function ReportView({ user, onLogout }) {
  const { company, year } = useParams()
  const navigate          = useNavigate()

  const [data, setData]               = useState(null)       // raw API response
  const [displayedSummaries, setDisplayed] = useState(null)  // may be translated
  const [activeSection, setActive]    = useState(null)
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState(null)
  const [translating, setTranslating] = useState(false)
  const [resummarizing, setResummarizing] = useState(false)
  const [currentLang, setCurrentLang] = useState('en')

  const loadSummaries = async () => {
    setLoading(true)
    setError(null)
    try {
      const d = await api.getSummaries(decodeURIComponent(company), year)
      setData(d)
      setDisplayed(d.summaries)
      setCurrentLang('en')
      setActive(prev => {
        if (prev && d.summaries[prev]) return prev
        return Object.keys(d.summaries)[0] || null
      })
    } catch {
      setError('Failed to load summaries.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSummaries()
  }, [company, year])

  const handleTranslate = async (langCode) => {
    if (langCode === 'en') {
      setDisplayed(data.summaries)
      setCurrentLang('en')
      return
    }
    setTranslating(true)
    try {
      const { translated } = await api.translate(decodeURIComponent(company), year, langCode)
      // Merge translated text into the existing summaries structure
      const merged = {}
      for (const [key, val] of Object.entries(data.summaries)) {
        merged[key] = { ...val, text: translated[key] || val.text }
      }
      setDisplayed(merged)
      setCurrentLang(langCode)
    } catch (e) {
      alert('Translation failed. Try again.')
    } finally {
      setTranslating(false)
    }
  }

  const decodedCompany = decodeURIComponent(company)

  const handleResummarize = async () => {
    const confirmed = window.confirm(
      `Re-summarize ${decodedCompany} ${year} now? This will replace the current summaries.`
    )
    if (!confirmed) return

    setResummarizing(true)
    try {
      const refreshed = await api.resummarize(decodedCompany, year)
      setData(refreshed)
      setDisplayed(refreshed.summaries)
      setCurrentLang('en')
      setActive(prev => {
        if (prev && refreshed.summaries[prev]) return prev
        return Object.keys(refreshed.summaries)[0] || null
      })
      alert(`Summaries regenerated for ${decodedCompany} ${year}.`)
    } catch (e) {
      const detail = e?.detail || 'Failed to re-summarize report. Please try again.'
      alert(detail)
    } finally {
      setResummarizing(false)
    }
  }

  return (
    <div className="report-shell">

      {/* Nav */}
      <nav className="report-nav">
        <button
          onClick={() => navigate('/')}
          className="nav-back"
        >
          ← Dashboard
        </button>
        <span className="nav-sep">|</span>
        <span className="report-company">
          {decodedCompany}
        </span>
        <span className="report-year-pill">
          {year}
        </span>
        <div className="report-nav-spacer" />
        <button
          className="btn-outline"
          onClick={() => navigate(`/compare/${encodeURIComponent(decodedCompany)}`)}
        >
          Compare Years
        </button>
        <button
          className="btn-outline"
          onClick={handleResummarize}
          disabled={resummarizing || loading}
          title="Generate fresh summaries using cached report data"
        >
          {resummarizing ? 'Resummarizing...' : `Resummarize ${year}`}
        </button>
      </nav>

      {/* Main: summaries + chat sidebar */}
      <div className="report-main">
        <div className="report-left">
          {data && (
            <div className="report-toolbar">
              <TranslatePanel onTranslate={handleTranslate} loading={translating} />
              <div className="report-toolbar-divider" />
              <AudioPlayer
                company={decodedCompany}
                year={year}
                sections={data?.summaries || {}}
                currentLanguage={currentLang}
              />
            </div>
          )}

          {data && (
            <div className="report-tabs-wrap">
              <SectionTabs
                sections={data.summaries}
                activeKey={activeSection}
                onSelect={setActive}
              />
            </div>
          )}

          <div className="report-scroll">
          {loading && (
            <div className="surface-note" style={{ textAlign: 'center', paddingTop: '40px' }}>
              <span className="spinner" style={{ width: 24, height: 24 }} />
              <div style={{ marginTop: 14, fontSize: '13px' }}>Loading summaries...</div>
            </div>
          )}
          {error && (
            <div className="surface-note" style={{ borderColor: 'rgba(255, 111, 118, 0.4)', color: '#ffb8bc' }}>
              {error}
            </div>
          )}
          {displayedSummaries && Object.entries(displayedSummaries).map(([key, val]) => (
            <SectionCard
              key={key}
              label={val.label}
              text={val.text}
              isActive={key === activeSection}
            />
          ))}
        </div>
        </div>

        <div className="report-chat">
          <ChatSidebar company={decodedCompany} year={year} />
        </div>
      </div>
    </div>
  )
}