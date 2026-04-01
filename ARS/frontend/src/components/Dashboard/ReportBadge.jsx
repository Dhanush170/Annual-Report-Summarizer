/**
 * ReportBadge.jsx
 * Clickable year pill on a company card.
 * Navigates to ReportView when clicked.
 */
import { useNavigate } from 'react-router-dom'

export default function ReportBadge({ company, year, onDelete, deleting }) {
  const navigate = useNavigate()

  return (
    <div className="report-row">
      <div className="report-year">FY {year}</div>
      <div className="report-actions">
        <button
          className="report-open"
          onClick={() => navigate(`/report/${encodeURIComponent(company)}/${year}`)}
        >
          Open
        </button>
        <button
          className="report-delete"
          disabled={deleting}
          onClick={() => onDelete?.(company, year)}
          title="Delete all artifacts for this report year"
        >
          {deleting ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    </div>
  )
}