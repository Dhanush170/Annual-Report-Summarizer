import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import CompanyCard from '../components/Dashboard/CompanyCard'
import UploadDropZone from '../components/Dashboard/UploadDropZone'
import { useReport } from '../hooks/useReport'

export default function Dashboard({ user, onLogout }) {
  const { reports, loadingReports, loadReports, deleteReport } = useReport()
  const [showUpload, setShowUpload] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleteConfirmText, setDeleteConfirmText] = useState('')
  const [deleting, setDeleting] = useState(false)
  const [deleteFeedback, setDeleteFeedback] = useState(null)
  const navigate = useNavigate()

  useEffect(() => { loadReports() }, [])

  const handleUploadSuccess = (company, year) => {
    loadReports()
    navigate(`/report/${encodeURIComponent(company)}/${year}`)
  }

  const companies = Object.entries(reports)

  const openDeleteDialog = (company, year) => {
    setDeleteTarget({ company, year })
    setDeleteConfirmText('')
  }

  const closeDeleteDialog = () => {
    if (deleting) return
    setDeleteTarget(null)
    setDeleteConfirmText('')
  }

  const handleDeleteConfirmed = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    setDeleteFeedback(null)
    try {
      const res = await deleteReport(deleteTarget.company, deleteTarget.year)
      if (res.status === 'not_found') {
        setDeleteFeedback('No artifacts were found for this report. It may already be deleted.')
      } else {
        setDeleteFeedback('Report artifacts deleted successfully.')
      }
      await loadReports()
      setTimeout(() => {
        setDeleteTarget(null)
        setDeleteFeedback(null)
      }, 900)
    } catch (e) {
      setDeleteFeedback(e?.detail || 'Delete failed. Please try again.')
    } finally {
      setDeleting(false)
    }
  }

  const deleteEnabled = deleteTarget && deleteConfirmText.trim() === deleteTarget.year

  return (
    <div className="dashboard-shell">
      <div className="dashboard-backdrop" />

      {/* Top nav */}
      <nav className="dashboard-nav">
        <div className="dashboard-brand">Annual Report Summarizer</div>
        <div className="dashboard-user">
          {user?.picture && (
            <img src={user.picture} alt="avatar" className="dashboard-avatar" />
          )}
          <span>{user?.name}</span>
          <button className="btn-outline" onClick={onLogout}>
            Sign out
          </button>
        </div>
      </nav>

      {/* Main content */}
      <div className="dashboard-content">

        {/* Header row */}
        <div className="dashboard-header">
          <div className="dashboard-title-wrap">
            <p className="dashboard-tagline">Report workspace</p>
            <h1>
              Your Reports
            </h1>
            <p>
              {companies.length > 0
                ? `${companies.length} ${companies.length === 1 ? 'company' : 'companies'} · ${Object.values(reports).flat().length} reports`
                : 'Upload your first annual report to get started'}
            </p>
          </div>
          <button className={showUpload ? 'btn-outline' : 'btn-primary'} onClick={() => setShowUpload(v => !v)}>
            {showUpload ? '✕ Cancel' : '+ Upload Report'}
          </button>
        </div>

        {/* Upload panel */}
        {showUpload && (
          <div className="fade-up" style={{ marginBottom: '32px', maxWidth: 520 }}>
            <UploadDropZone onSuccess={handleUploadSuccess} />
          </div>
        )}

        {/* Company grid */}
        {loadingReports ? (
          <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
            <span className="spinner" style={{ width: 24, height: 24 }} />
          </div>
        ) : companies.length === 0 ? (
          <div className="dashboard-empty">
            <div style={{ fontSize: '40px', marginBottom: '16px' }}>◧</div>
            No reports yet. Upload your first annual report above.
          </div>
        ) : (
          <div className="company-grid">
            {companies.map(([company, years]) => (
              <CompanyCard
                key={company}
                company={company}
                years={years}
                onDeleteYear={openDeleteDialog}
                deletingKey={deleteTarget ? `${deleteTarget.company}:${deleteTarget.year}` : null}
              />
            ))}
          </div>
        )}
      </div>

      {deleteTarget && (
        <div className="notice-overlay">
          <div className="danger-modal fade-up" role="dialog" aria-modal="true" aria-label="Delete report artifacts">
            <div className="notice-pill danger">Delete Report Artifacts</div>
            <h3>
              Delete {deleteTarget.company} ({deleteTarget.year})?
            </h3>
            <p>
              This will permanently delete vectorstore, chunks, generated audio, chat history, and saved summaries for this report year.
            </p>
            <p>
              To confirm, type the year <strong>{deleteTarget.year}</strong> below.
            </p>
            <input
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder={`Type ${deleteTarget.year} to confirm`}
            />
            {deleteFeedback && <div className="danger-feedback">{deleteFeedback}</div>}

            <div className="danger-actions">
              <button className="btn-outline" onClick={closeDeleteDialog} disabled={deleting}>Cancel</button>
              <button className="btn-danger" onClick={handleDeleteConfirmed} disabled={!deleteEnabled || deleting}>
                {deleting ? 'Deleting...' : 'Delete Permanently'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}