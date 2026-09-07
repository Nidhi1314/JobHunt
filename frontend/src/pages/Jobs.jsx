import { useState, useEffect } from 'react'

const API = 'http://localhost:8000/api'

const TYPE_BADGE = { Product: 'badge-product', Startup: 'badge-startup', MNC: 'badge-mnc', Service: 'badge-service' }

export default function Jobs() {
  const [jobs, setJobs]       = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch]   = useState('')
  const [company, setCompany] = useState('')
  const [sort, setSort]       = useState('score')

  useEffect(() => {
    fetch(`${API}/jobs?limit=100`)
      .then(r => r.json())
      .then(data => { setJobs(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const companies = [...new Set(jobs.map(j => j.company))].sort()

  const filtered = jobs
    .filter(j => !search || j.title?.toLowerCase().includes(search.toLowerCase()))
    .filter(j => !company || j.company === company)
    .sort((a, b) => sort === 'score'
      ? (b.relevance_score || 0) - (a.relevance_score || 0)
      : new Date(b.first_seen) - new Date(a.first_seen)
    )

  if (loading) return (
    <div style={{ textAlign: 'center', paddingTop: 80 }}>
      <div className="spinner" style={{ width: 40, height: 40 }} />
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <h2>Job <span className="gradient-text">Listings</span></h2>
        <p>{filtered.length} jobs found across {companies.length} companies</p>
      </div>

      <div className="filter-bar">
        <input
          className="form-input"
          placeholder="🔍  Search by title..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select className="form-select" value={company} onChange={e => setCompany(e.target.value)}>
          <option value="">All Companies</option>
          {companies.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select className="form-select" value={sort} onChange={e => setSort(e.target.value)}>
          <option value="score">Sort: Relevance</option>
          <option value="date">Sort: Newest</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💼</div>
          <p>No jobs match your filters</p>
        </div>
      ) : (
        <div className="jobs-grid">
          {filtered.map(job => <JobCard key={job.id} job={job} />)}
        </div>
      )}
    </div>
  )
}

function JobCard({ job }) {
  const score   = job.relevance_score || 0
  const tier    = score >= 8 ? 'high' : score >= 6 ? 'mid' : 'low'
  const initials = job.company?.slice(0, 2).toUpperCase() || '?'
  const salary  = job.salary_min
    ? `₹${job.salary_min}–${job.salary_max} LPA`
    : 'Salary not listed'

  return (
    <div className={`job-card ${tier}`}>
      <div className="job-company-avatar">{initials}</div>
      <div className="job-info">
        <div className="job-title">{job.title}</div>
        <div className="job-meta">
          <span>🏢 {job.company}</span>
          <span>📍 {job.location || 'India'}</span>
          <span>💼 {job.work_mode || 'Not specified'}</span>
        </div>
        <div style={{ marginTop: 6 }}>
          <span className={`badge ${TYPE_BADGE[job.company_type] || 'badge-service'}`}>
            {job.company_type || 'Company'}
          </span>
          <span style={{ marginLeft: 8, fontSize: 12, color: 'var(--accent)', fontWeight: 600 }}>
            {salary}
          </span>
        </div>
      </div>
      <div className="job-right">
        <span className="score-badge">⭐ {score.toFixed(1)}</span>
        <a href={job.url} target="_blank" rel="noreferrer" className="apply-btn">
          Apply Now →
        </a>
      </div>
    </div>
  )
}
