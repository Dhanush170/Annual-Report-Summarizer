/**
 * SectionCard.jsx
 * Displays one section's summary text in a clean card.
 * Shows a loading skeleton while summaries are being fetched.
 */

export default function SectionCard({ label, text, isActive }) {
  if (!text) {
    // Loading skeleton
    return (
      <div className="section-card">
        <div style={{ height: 14, width: '40%', background: 'var(--border)', borderRadius: 4, marginBottom: 14 }} />
        {[100, 85, 92, 70].map((w, i) => (
          <div key={i} style={{
            height: 11, width: `${w}%`, background: 'var(--border-light)',
            borderRadius: 3, marginBottom: 8, opacity: 0.6 - i * 0.1
          }} />
        ))}
      </div>
    )
  }

  // Split text to find and highlight the "Insight:" line
  const insightIdx = text.indexOf('Insight:')
  const mainText   = insightIdx > -1 ? text.slice(0, insightIdx).trim() : text
  const insight    = insightIdx > -1 ? text.slice(insightIdx).trim() : null

  return (
    <div
      className={`fade-up section-card ${isActive ? 'active' : ''}`}
    >
      {/* Section label */}
      <div className="section-label">
        {label}
      </div>

      {/* Main summary */}
      <p className="section-text">
        {mainText}
      </p>

      {/* Insight line — highlighted */}
      {insight && (
        <div className="section-insight">
          💡 {insight.replace(/^Insight:\s*/i, '')}
        </div>
      )}
    </div>
  )
}