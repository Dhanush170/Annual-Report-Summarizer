import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useReport } from '../hooks/useReport'
import YearSelector from '../components/Compare/YearSelector'
import DeltaSection from '../components/Compare/DeltaSection'

export default function Compare({ user }) {
  const { company }     = useParams()
  const navigate        = useNavigate()
  const { reports, loadReports } = useReport()

  const [yearA, setYearA]   = useState('')
  const [yearB, setYearB]   = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)

  const decodedCompany = decodeURIComponent(company)

  useEffect(() => { loadReports() }, [])

  const availableYears = reports[decodedCompany] || []

  const handleCompare = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await api.compare(decodedCompany, yearA, yearB)
      setResult(data)
    } catch (e) {
      setError(e?.detail || 'Comparison failed. Make sure both reports are processed.')
    } finally {
      setLoading(false)
    }
  }

  const SECTION_LABELS = {
    business_information:    'Business Information',
    corporate_information:   'Corporate Information',
    chairmans_message:       "Chairman's Message",
    boards_report:           "Board's Report",
    shareholding_information:'Shareholding Information',
    corporate_governance:    'Corporate Governance',
    mda:                     'Management Discussion & Analysis',
    financial_statements:    'Consolidated Financial Statements',
  }

  return (
    <div className="compare-shell">

      {/* Nav */}
      <nav className="compare-nav">
        <button
          onClick={() => navigate('/')}
          className="nav-back"
        >
          ← Dashboard
        </button>
        <span className="nav-sep">|</span>
        <span className="compare-company">{decodedCompany}</span>
        <span className="report-year-pill">Year-over-Year</span>
        <div className="compare-nav-spacer" />
      </nav>

      <div className="compare-content">

        {/* Header */}
        <div className="compare-header">
          <p className="dashboard-tagline">Delta analysis</p>
          <h1>
            Delta Report
          </h1>
          <p>
            Section-by-section comparison between two annual reports.
          </p>
        </div>

        {/* Year selector */}
        <YearSelector
          years={availableYears}
          yearA={yearA}
          yearB={yearB}
          onYearAChange={setYearA}
          onYearBChange={setYearB}
          onCompare={handleCompare}
          loading={loading}
        />

        {/* Loading */}
        {loading && (
          <div className="surface-note" style={{ marginTop: 16, textAlign: 'center', padding: 30 }}>
            <span className="spinner" style={{ width: 24, height: 24 }} />
            <div style={{ marginTop: 14, fontSize: '13px' }}>
              Comparing {yearA} → {yearB}... This takes about 30 seconds.
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="surface-note" style={{ marginTop: 16, borderColor: 'rgba(255, 111, 118, 0.4)', color: '#ffb8bc' }}>
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: 16 }}>

            {/* Executive overview */}
            <div className="compare-exec fade-up">
              <div className="compare-exec-title">Executive Overview</div>
              <p style={{ fontSize: '14px', lineHeight: '1.75', margin: 0 }}>
                {result.deltas.executive_delta}
              </p>
            </div>

            {/* Section-by-section deltas */}
            {Object.entries(SECTION_LABELS).map(([key, label]) => (
              result.deltas[key] && (
                <DeltaSection
                  key={key}
                  label={label}
                  deltaText={result.deltas[key]}
                  summaryA={result.deltas[`${key}_a`]}
                  summaryB={result.deltas[`${key}_b`]}
                  yearA={yearA}
                  yearB={yearB}
                />
              )
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
