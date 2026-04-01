/**
 * DeltaSection.jsx
 * Renders one section's delta comparison with side-by-side summaries + structured delta.
 * Parses the **bold label** format from the LLM response.
 */

function parseDelta(text) {
  // Parse "**Label:** value" lines into structured items
  const lines  = text.split('\n').filter(l => l.trim())
  const parsed = []
  for (const line of lines) {
    const match = line.match(/^\*\*(.+?):\*\*\s*(.+)/)
    if (match) {
      parsed.push({ label: match[1], value: match[2] })
    } else if (line.trim()) {
      parsed.push({ label: null, value: line.trim() })
    }
  }
  return parsed
}

const DELTA_COLORS = {
  'What Improved':        { bg: 'var(--emerald-dim)', border: 'var(--emerald)', text: 'var(--emerald)' },
  'What Declined':        { bg: 'var(--red-dim)',     border: 'var(--red)',     text: 'var(--red)' },
  'New Developments':     { bg: 'var(--accent-dim)',  border: 'var(--accent)',  text: 'var(--accent)' },
  'Dropped/De-emphasized':{ bg: 'var(--amber-dim)',   border: 'var(--amber)',   text: 'var(--amber)' },
  'Trend Signal':         { bg: 'rgba(188,140,255,0.1)', border: '#bc8cff',    text: '#bc8cff' },
}

export default function DeltaSection({ label, deltaText, summaryA, summaryB, yearA, yearB }) {
  const rows = parseDelta(deltaText || '')

  return (
    <div className="fade-up delta-card">
      {/* Section header */}
      <div className="delta-head">
        <span style={{ fontWeight: '600', fontSize: '14px' }}>{label}</span>
      </div>

      {/* Side-by-side summaries */}
      <div className="delta-summaries">
        {[{ year: yearA, text: summaryA }, { year: yearB, text: summaryB }].map(({ year, text }, i) => (
          <div key={year} className="delta-col">
            <div className="delta-year">
              {year}
            </div>
            {text ? (
              <p style={{ fontSize: '13px', lineHeight: '1.65', color: 'var(--text)', margin: 0 }}>
                {text}
              </p>
            ) : null}
          </div>
        ))}
      </div>

      {/* Delta rows */}
      <div className="delta-body">
        {rows.map((row, i) => {
          const style = DELTA_COLORS[row.label] || {}
          return (
            <div key={i} className="delta-row" style={row.label ? {
              background: style.bg,
              borderColor: `${style.border}30`,
            } : {}}>
              {row.label && (
                <span className="delta-tag" style={{ color: style.text }}>
                  {row.label}
                </span>
              )}
              <span style={{ fontSize: '13px', lineHeight: '1.6', color: 'var(--text)' }}>
                {row.value}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
