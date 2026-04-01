export default function ComplianceNoticeModal({ open, onAcknowledge }) {
  if (!open) return null

  return (
    <div className="notice-overlay">
      <div className="notice-modal fade-up" role="dialog" aria-modal="true" aria-label="ARS usage notice">
        <div className="notice-pill">Important Usage Notice</div>
        <h2>Use ARS only for eligible annual reports</h2>
        <p>
          This tool is intended only for summarizing annual reports of companies listed under NSE and BSE.
          Please ensure the report includes all 8 required sections for accurate analysis and comparisons.
        </p>
        <ul>
          <li>Business Information</li>
          <li>Corporate Information</li>
          <li>Chairman's Message</li>
          <li>Board's Report</li>
          <li>Shareholding Information</li>
          <li>Corporate Governance</li>
          <li>Management Discussion & Analysis</li>
          <li>Consolidated Financial Statements</li>
        </ul>
        <button className="btn-primary" onClick={onAcknowledge}>
          I Understand and Continue
        </button>
      </div>
    </div>
  )
}
