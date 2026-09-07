import { useState, useEffect } from 'react'

const API = 'http://localhost:8000/api'

export default function Pipeline() {
  const [logs, setLogs]       = useState([])
  const [running, setRunning] = useState(false)
  const [result, setResult]   = useState(null)

  const fetchLogs = () =>
    fetch(`${API}/pipeline/status`)
      .then(r => r.json())
      .then(setLogs)
      .catch(() => {})

  useEffect(() => { fetchLogs() }, [])

  const handleRun = async () => {
    setRunning(true)
    setResult(null)
    try {
      const res = await fetch(`${API}/pipeline/run-and-email`, { method: 'POST' })
      const data = await res.json()
      setResult(data)
      fetchLogs()
    } catch (e) {
      setResult({ error: 'Pipeline failed — is the backend running?' })
    }
    setRunning(false)
  }

  return (
    <div>
      <div className="page-header">
        <h2>AI <span className="gradient-text">Pipeline</span></h2>
        <p>Run the 4-agent pipeline manually or view past runs</p>
      </div>

      {/* Trigger */}
      <div className="pipeline-trigger">
        <div style={{ fontSize: 48, marginBottom: 12 }}>🤖</div>
        <h3>Run Pipeline Now</h3>
        <p>Crawl all 10 companies → Filter → Research salaries → Email results</p>
        <button className="run-btn" onClick={handleRun} disabled={running}>
          {running
            ? <span>⏳ Running... (takes ~2 min)</span>
            : '🚀 Start Pipeline'}
        </button>
        {running && (
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 16 }}>
            Crawling companies → filtering with Groq → researching salaries → sending email...
          </p>
        )}
      </div>

      {/* Result */}
      {result && (
        <div className="card" style={{ marginBottom: 20, borderColor: result.error ? 'var(--danger)' : 'var(--success)' }}>
          {result.error ? (
            <p style={{ color: 'var(--danger)' }}>❌ {result.error}</p>
          ) : (
            <div style={{ display: 'flex', gap: 32 }}>
              <div>
                <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--primary)' }}>{result.jobs_crawled}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Crawled</div>
              </div>
              <div>
                <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--success)' }}>{result.jobs_new}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>New Jobs</div>
              </div>
              <div>
                <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--accent)' }}>{result.email_sent ? '✅' : '❌'}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Email Sent</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Logs */}
      <div className="card">
        <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16 }}>
          Run History
        </h3>
        {logs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No runs yet — trigger one above!</p>
          </div>
        ) : logs.map(log => (
          <div className="log-item" key={log.id}>
            <div className={`log-status ${log.status}`} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 600 }}>
                {new Date(log.started_at).toLocaleString('en-IN')}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Crawled {log.jobs_crawled} · Filtered {log.jobs_after_filter} · {log.jobs_new} new
                {log.error_message && ` · ❌ ${log.error_message}`}
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {log.email_sent && <span style={{ fontSize: 12, color: 'var(--success)' }}>📧 Emailed</span>}
              <span className={`badge ${log.status === 'success' ? 'badge-product' : 'badge-service'}`}>
                {log.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
