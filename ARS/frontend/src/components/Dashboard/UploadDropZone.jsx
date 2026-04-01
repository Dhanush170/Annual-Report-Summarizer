/**
 * UploadDropZone.jsx
 * Drag-and-drop PDF uploader with company name + year inputs.
 * Handles the full upload → pipeline → poll cycle.
 * Calls onSuccess(company, year) when pipeline finishes.
 */
import { useState, useRef, useCallback } from 'react'
import { useReport } from '../../hooks/useReport'

const STATUS_LABEL = {
  queued:  'Queued...',
  running: 'Processing report...',
  done:    'Done!',
  error:   'Failed',
}

export default function UploadDropZone({ onSuccess }) {
  const [file, setFile]         = useState(null)
  const [company, setCompany]   = useState('')
  const [year, setYear]         = useState('')
  const [dragging, setDragging] = useState(false)
  const [status, setStatus]     = useState(null)   // null | 'uploading' | job status string
  const [error, setError]       = useState(null)
  const [progress, setProgress] = useState(null)
  const inputRef                = useRef()
  const { upload, pollJob }     = useReport()

  const handleFile = useCallback((f) => {
    if (f && f.type === 'application/pdf') {
      setFile(f)
      setError(null)
    } else {
      setError('Please upload a PDF file.')
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }, [handleFile])

  const handleSubmit = async () => {
  if (!file || !company.trim() || !year.trim()) {
    setError('Please fill in company name, year, and upload a PDF.')
    return
  }
  setError(null)
  setStatus('uploading')

  try {
    const jobId = await upload({
      file,
      company: company.trim(),
      year: year.trim(),
      forceReindex: true,
      forceResummarize: false,
    })

    setStatus('queued')

    await pollJob(jobId, (s) => {
      setProgress(s)
      setStatus(s.status)
      if (s.status === 'error') {
        setError(`Pipeline failed: ${s.error || 'Check the backend terminal for details.'}`)
      }
    })

    setFile(null)
    setCompany('')
    setYear('')
    setStatus(null)
    setProgress(null)
    onSuccess(company.trim(), year.trim())

  } catch (e) {
    const msg = e?.error || e?.detail || (typeof e === 'string' ? e : null) || 'Pipeline failed. Check the backend terminal for details.'
    setError(msg)
    setStatus(null)
  }
}

  const isRunning = status && status !== null && status !== 'error'

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      padding: '24px',
    }}>
      <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '16px' }}>
        Upload New Report
      </div>

      {/* Drop zone */}
      <div
        onClick={() => !isRunning && inputRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragging ? 'var(--accent)' : file ? 'var(--emerald)' : 'var(--border)'}`,
          borderRadius: 'var(--radius-sm)',
          padding: '28px 20px',
          textAlign: 'center',
          cursor: isRunning ? 'default' : 'pointer',
          background: dragging ? 'rgba(88,166,255,0.05)' : file ? 'rgba(63,185,80,0.05)' : 'transparent',
          transition: 'all 0.18s ease',
          marginBottom: '16px',
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files[0])}
        />
        <div style={{ fontSize: '28px', marginBottom: '8px' }}>
          {file ? '📄' : '⬆️'}
        </div>
        <div style={{ fontSize: '14px', fontWeight: '500' }}>
          {file ? file.name : 'Drop PDF here or click to browse'}
        </div>
        {file && (
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            {(file.size / 1024 / 1024).toFixed(1)} MB
          </div>
        )}
      </div>

      {/* Inputs row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px', gap: '10px', marginBottom: '14px' }}>
        <input
          placeholder="Company name  (e.g. TCS)"
          value={company}
          onChange={e => setCompany(e.target.value)}
          disabled={isRunning}
          style={{ width: '100%' }}
        />
        <input
          placeholder="Year"
          value={year}
          onChange={e => setYear(e.target.value)}
          disabled={isRunning}
          maxLength={4}
        />
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={isRunning || !file}
        style={{
          width: '100%',
          padding: '11px',
          background: isRunning ? 'var(--bg-hover)' : 'var(--accent)',
          color: isRunning ? 'var(--text-muted)' : '#0d1117',
          borderRadius: 'var(--radius-sm)',
          fontWeight: '600',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
        }}
      >
        {isRunning && <span className="spinner" style={{ width: 15, height: 15 }} />}
        {isRunning ? (STATUS_LABEL[status] || 'Processing...') : 'Summarize Report'}
      </button>

      {/* Progress note */}
      {isRunning && (
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '10px' }}>
          New documents take 1–3 minutes. Cached reports load instantly.
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          marginTop: '12px', padding: '10px 14px',
          background: 'var(--red-dim)', border: '1px solid var(--red)',
          borderRadius: 'var(--radius-sm)', fontSize: '13px', color: 'var(--red)'
        }}>
          {error}
        </div>
      )}
    </div>
  )
}
