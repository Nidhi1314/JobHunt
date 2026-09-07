import { useState, useEffect } from 'react'

const API = 'http://localhost:8000/api'

export default function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/jobs?limit=5`).then(r => r.json()).catch(() => []),
      fetch(`${API}/pipeline/status`).then(r => r.json()).catch(() => []),
    ]).then(([j, l]) => {
      setJobs(j)
      setLogs(l)
      setLoading(false)
    })
  }, [])

  const lastRun = logs[0]
  const totalJobs = jobs.length

  const stats = [
    { icon: '💼', label: 'Jobs in DB',    value: totalJobs,                      color: '#6366f1' },
    { icon: '🆕', label: 'Last Run New',  value: lastRun?.jobs_new ?? '—',        color: '#22c55e' },
    { icon: '🔍', label: 'Last Crawled',  value: lastRun?.jobs_crawled ?? '—',    color: '#f59e0b' },
    { icon: '📧', label: 'Email Sent',    value: lastRun?.email_sent ? 'Yes':'No', color: '#22d3ee' },
  ]

  if (loading) return (
    <div style={{ textAlign: 'center', paddingTop: 80 }}>
      <div className="spinner" style={{ width: 40, height: 40 }} />
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard <span className="gradient-text">Overview</span></h2>
        <p>Welcome back — here's your job hunt at a glance</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {stats.map(s => (
          <div className="stat-card" key={s.label}>
            <div className="stat-icon" style={{ background: `${s.color}22` }}>
              {s.icon}
            </div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Recent jobs */}
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1 }}>
          Recent Jobs
        </h3>
        {jobs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <p>No jobs yet — run the pipeline first!</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {jobs.map(job => <MiniJobCard key={job.id} job={job} />)}
          </div>
        )}
      </div>

      {/* Run logs */}
      <div className="card">
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1 }}>
          Recent Pipeline Runs
        </h3>
        {logs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">⏳</div>
            <p>No runs yet</p>
          </div>
        ) : logs.map(log => (
          <div className="log-item" key={log.id}>
            <div className={`log-status ${log.status}`} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 600 }}>
                {new Date(log.started_at).toLocaleString()}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                {log.jobs_crawled} crawled · {log.jobs_new} new · Email: {log.email_sent ? '✅' : '❌'}
              </div>
            </div>
            <span className={`badge ${log.status === 'success' ? 'badge-product' : 'badge-service'}`}>
              {log.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function MiniJobCard({ job }) {
  const score = job.relevance_score || 0
  const tier = score >= 8 ? 'high' : score >= 6 ? 'mid' : 'low'
  const initials = job.company?.slice(0, 2).toUpperCase() || '?'

  return (
    <div className={`job-card ${tier}`}>
      <div className="job-company-avatar">{initials}</div>
      <div className="job-info">
        <div className="job-title">{job.title}</div>
        <div className="job-meta">
          <span>🏢 {job.company}</span>
          <span>📍 {job.location || 'India'}</span>
        </div>
      </div>
      <div className="job-right">
        <span className="score-badge">⭐ {score.toFixed(1)}</span>
        <a href={job.url} target="_blank" rel="noreferrer" className="apply-btn">Apply</a>
      </div>
    </div>
  )
}
