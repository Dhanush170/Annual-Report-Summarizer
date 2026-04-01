/**
 * useReport.js
 * Manages report list, upload flow, and pipeline job polling.
 *
 * Usage:
 *   const { reports, loadReports, upload, jobStatus } = useReport()
 */
import { useState, useCallback } from 'react'
import { api } from '../api/client'

export function useReport() {
  const [reports, setReports]       = useState({})   // { "TCS": ["2023","2024"], ... }
  const [loadingReports, setLoading] = useState(false)
  const [jobStatus, setJobStatus]   = useState(null) // null | {status, job_id, company, year}
  const [uploadError, setUploadError] = useState(null)

  // ── Fetch all stored reports from backend ──
  const loadReports = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.listReports()
      setReports(data || {})
    } catch (e) {
      console.error('Failed to load reports:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  // ── Upload PDF + start pipeline ──
  // Returns job_id or throws
  const upload = useCallback(async ({ file, company, year, forceReindex, forceResummarize }) => {
    setUploadError(null)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('company', company)
    formData.append('year', year)
    formData.append('force_reindex', forceReindex ? 'true' : 'false')
    formData.append('force_resummarize', forceResummarize ? 'true' : 'false')

    const { job_id } = await api.runPipeline(formData)
    return job_id
  }, [])

  // ── Poll a job until done/error ──
  // Calls onProgress(status) on each tick, resolves when done.
  const pollJob = useCallback((jobId, onProgress) => {
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const status = await api.getJobStatus(jobId)
          onProgress(status)
          if (status.status === 'done') {
            clearInterval(interval)
            resolve(status)
          } else if (status.status === 'error') {
            clearInterval(interval)
            reject(new Error(status.error || 'Pipeline failed'))
          }
        } catch (e) {
          clearInterval(interval)
          reject(e)
        }
      }, 3000)   // poll every 3 seconds
    })
  }, [])

  const deleteReport = useCallback(async (company, year) => {
    return api.deleteReport(company, year)
  }, [])

  return {
    reports,
    loadingReports,
    jobStatus,
    uploadError,
    setUploadError,
    loadReports,
    upload,
    pollJob,
    deleteReport,
  }
}