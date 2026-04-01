/**
 * YearSelector.jsx
 * Two dropdowns (Year A, Year B) + Compare button.
 * Populated from the list of available years for the company.
 */

export default function YearSelector({ years, yearA, yearB, onYearAChange, onYearBChange, onCompare, loading }) {
  const valid = yearA && yearB && yearA !== yearB

  return (
    <div className="year-selector fade-up">
      <div style={{ fontSize: '14px', fontWeight: '500', color: 'var(--text-muted)', marginRight: 4 }}>
        Compare:
      </div>

      <select
        value={yearA}
        onChange={e => onYearAChange(e.target.value)}
        style={{ fontSize: '14px', padding: '8px 12px', minWidth: 100 }}
      >
        <option value="">Year A</option>
        {years.map(y => <option key={y} value={y}>{y}</option>)}
      </select>

      <span style={{ color: 'var(--text-muted)', fontWeight: '600' }}>→</span>

      <select
        value={yearB}
        onChange={e => onYearBChange(e.target.value)}
        style={{ fontSize: '14px', padding: '8px 12px', minWidth: 100 }}
      >
        <option value="">Year B</option>
        {years.map(y => <option key={y} value={y}>{y}</option>)}
      </select>

      <button
        onClick={onCompare}
        disabled={!valid || loading}
        className={valid && !loading ? 'btn-primary' : 'btn-outline'}
        style={{ padding: '9px 18px', display: 'flex', alignItems: 'center', gap: 8 }}
      >
        {loading && <span className="spinner" style={{ width: 14, height: 14 }} />}
        {loading ? 'Comparing...' : 'Generate Delta Report'}
      </button>

      {yearA && yearB && yearA === yearB && (
        <span style={{ fontSize: '13px', color: 'var(--amber)' }}>
          ⚠️ Please select two different years.
        </span>
      )}
    </div>
  )
}