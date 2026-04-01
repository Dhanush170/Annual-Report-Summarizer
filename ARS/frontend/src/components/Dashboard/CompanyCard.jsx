/**
 * CompanyCard.jsx
 * Displays a company with all its available report years as clickable badges.
 */
import ReportBadge from './ReportBadge'

// Generate a consistent color from a string (for the avatar)
function strToColor(str) {
  const colors = ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff', '#ff7b72']
  let hash = 0
  for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

export default function CompanyCard({ company, years, onDeleteYear, deletingKey }) {
  const color   = strToColor(company)
  const initial = company.charAt(0).toUpperCase()

  return (
    <div
      className="fade-up company-card"
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'rgba(108,167,255,0.4)'
        e.currentTarget.style.boxShadow = '0 24px 48px rgba(5, 13, 24, 0.55)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {/* Header row: avatar + company name */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: 40, height: 40,
          borderRadius: 10,
          background: `${color}22`,
          border: `1.5px solid ${color}55`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '16px', fontWeight: '700', color,
          fontFamily: 'var(--font-brand)',
          flexShrink: 0,
        }}>
          {initial}
        </div>
        <div>
          <div style={{ fontWeight: '700', fontSize: '16px', letterSpacing: '-0.01em' }}>
            {company}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '1px' }}>
            {years.length} {years.length === 1 ? 'report' : 'reports'} available
          </div>
        </div>
      </div>

      {/* Year badges */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {years.map(year => (
          <ReportBadge
            key={year}
            company={company}
            year={year}
            onDelete={onDeleteYear}
            deleting={deletingKey === `${company}:${year}`}
          />
        ))}
      </div>
    </div>
  )
}