/**
 * SectionTabs.jsx
 * Horizontal scrollable tab bar for navigating between sections.
 */

const SECTION_ICONS = {
  business_information:   '🏢',
  corporate_information:  '👥',
  chairmans_message:      '✉️',
  boards_report:          '📋',
  shareholding_information:'📊',
  corporate_governance:   '⚖️',
  mda:                    '🔍',
  financial_statements:   '💰',
}

export default function SectionTabs({ sections, activeKey, onSelect }) {
  return (
    <div className="section-tabs">
      {Object.entries(sections).map(([key, { label }]) => {
        const active = key === activeKey
        return (
          <button
            key={key}
            onClick={() => onSelect(key)}
            className={active ? 'section-tab active' : 'section-tab'}
          >
            <span style={{ fontSize: '14px' }}>{SECTION_ICONS[key] || '📄'}</span>
            {label}
          </button>
        )
      })}
    </div>
  )
}