/**
 * TranslatePanel.jsx
 * Language dropdown + Translate button.
 * Calls onTranslate(languageCode) when submitted.
 */
import { useState, useEffect } from 'react'
import { api } from '../../api/client'

export default function TranslatePanel({ onTranslate, loading }) {
  const [languages, setLanguages] = useState({})
  const [selected, setSelected]   = useState('en')

  useEffect(() => {
    api.getLanguages().then(setLanguages).catch(() => {})
  }, [])

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
      <span style={{ fontSize: '16px' }}>🌐</span>
      <select
        value={selected}
        onChange={e => setSelected(e.target.value)}
        style={{ fontSize: '13px', padding: '7px 10px', minWidth: 150 }}
      >
        {Object.entries(languages).map(([name, code]) => (
          <option key={code} value={code}>{name}</option>
        ))}
      </select>
      <button
        onClick={() => onTranslate(selected)}
        disabled={loading || selected === 'en'}
        className="btn-outline"
        style={{ padding: '8px 14px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: 6 }}
      >
        {loading && <span className="spinner" style={{ width: 13, height: 13 }} />}
        Translate
      </button>
      {selected !== 'en' && !loading && (
        <button
          onClick={() => { setSelected('en'); onTranslate('en') }}
          className="btn-outline"
          style={{ padding: '8px 12px', fontSize: '12px' }}
        >
          Reset
        </button>
      )}
    </div>
  )
}