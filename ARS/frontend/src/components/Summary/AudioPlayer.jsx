/**
 * AudioPlayer.jsx
 * Generates and plays audio for a section or full report.
 */
import { useState } from 'react'
import { api } from '../../api/client'

export default function AudioPlayer({ company, year, sections, currentLanguage = 'en' }) {
  const [selectedSection, setSelectedSection] = useState('full_report')
  const [audioUrl, setAudioUrl]               = useState(null)
  const [loading, setLoading]                 = useState(false)
  const [error, setError]                     = useState(null)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    setAudioUrl(null)
    try {
      const { audio_url } = await api.generateAudio(
        company, year, selectedSection, currentLanguage
      )
      setAudioUrl(audio_url)
    } catch (e) {
      setError('Audio generation failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
      <span style={{ fontSize: '16px' }}>🔊</span>

      <select
        value={selectedSection}
        onChange={e => { setSelectedSection(e.target.value); setAudioUrl(null) }}
        style={{ fontSize: '13px', padding: '7px 10px', minWidth: 190 }}
      >
        <option value="full_report">Full Report</option>
        {Object.entries(sections).map(([key, { label }]) => (
          <option key={key} value={key}>{label}</option>
        ))}
      </select>

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="btn-outline"
        style={{ padding: '8px 14px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: 6 }}
      >
        {loading && <span className="spinner" style={{ width: 13, height: 13 }} />}
        {loading ? 'Generating...' : 'Generate Audio'}
      </button>

      {audioUrl && (
        <audio
          key={audioUrl}
          controls
          autoPlay
          style={{ height: 34, borderRadius: 8, filter: 'saturate(0.8)' }}
          src={audioUrl}
        />
      )}

      {error && (
        <span style={{ fontSize: '12px', color: 'var(--red)' }}>{error}</span>
      )}
    </div>
  )
}
