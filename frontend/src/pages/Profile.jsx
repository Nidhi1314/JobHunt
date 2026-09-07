import { useState, useEffect } from 'react'

const API = 'http://localhost:8000/api'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [saving, setSaving]   = useState(false)
  const [saved, setSaved]     = useState(false)

  useEffect(() => {
    fetch(`${API}/profile`)
      .then(r => r.json())
      .then(setProfile)
      .catch(() => {})
  }, [])

  const handleChange = (key, val) => setProfile(p => ({ ...p, [key]: val }))

  const handleSave = async () => {
    setSaving(true)
    try {
      await fetch(`${API}/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (e) {}
    setSaving(false)
  }

  if (!profile) return (
    <div style={{ textAlign: 'center', paddingTop: 80 }}>
      <div className="spinner" style={{ width: 40, height: 40 }} />
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <h2>Your <span className="gradient-text">Profile</span></h2>
        <p>Configure your job preferences — these drive the AI filters</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>

        {/* Hard Filters */}
        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 20 }}>
            🔴 Hard Filters
          </h3>
          <div className="form-group">
            <label className="form-label">Graduation Year *</label>
            <input
              className="form-input"
              value={profile.grad_year || ''}
              onChange={e => handleChange('grad_year', e.target.value)}
              placeholder="e.g. 2025"
            />
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              Jobs for a different batch are auto-discarded
            </p>
          </div>
          <div className="form-group">
            <label className="form-label">Alert Email</label>
            <input
              className="form-input"
              type="email"
              value={profile.alert_email || ''}
              onChange={e => handleChange('alert_email', e.target.value)}
              placeholder="your@gmail.com"
            />
          </div>
        </div>

        {/* Soft Filters */}
        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 20 }}>
            🟡 Soft Filters (LLM Scored)
          </h3>
          <div className="form-group">
            <label className="form-label">Preferred Roles (comma-separated)</label>
            <input
              className="form-input"
              value={profile.preferred_roles || ''}
              onChange={e => handleChange('preferred_roles', e.target.value)}
              placeholder="SDE, Data Analyst, ML Engineer"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Minimum Salary (LPA)</label>
            <input
              className="form-input"
              type="number"
              value={profile.min_salary_lpa || 0}
              onChange={e => handleChange('min_salary_lpa', parseFloat(e.target.value))}
              placeholder="e.g. 6"
            />
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 20 }}>
            📍 Location & Mode
          </h3>
          <div className="form-group">
            <label className="form-label">Preferred Locations (comma-separated)</label>
            <input
              className="form-input"
              value={profile.preferred_locations || ''}
              onChange={e => handleChange('preferred_locations', e.target.value)}
              placeholder="Bangalore, Hyderabad, Remote"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Work Mode Preference</label>
            <select
              className="form-select"
              value={profile.preferred_work_mode || ''}
              onChange={e => handleChange('preferred_work_mode', e.target.value)}
            >
              <option value="">Any</option>
              <option value="Remote">Remote</option>
              <option value="Hybrid">Hybrid</option>
              <option value="On-site">On-site</option>
            </select>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 20 }}>
            ⚙️ AI Settings
          </h3>
          <div className="form-group">
            <label className="form-label">Company Type Preference</label>
            <select
              className="form-select"
              value={profile.preferred_company_types || ''}
              onChange={e => handleChange('preferred_company_types', e.target.value)}
            >
              <option value="">Any</option>
              <option value="Product">Product</option>
              <option value="Startup">Startup</option>
              <option value="MNC">MNC</option>
              <option value="Service">Service</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Min Relevance Score to Email (0–10)</label>
            <input
              className="form-input"
              type="number"
              min="0" max="10" step="0.5"
              value={profile.relevance_threshold || 5}
              onChange={e => handleChange('relevance_threshold', parseFloat(e.target.value))}
            />
          </div>
        </div>

      </div>

      <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? '⏳ Saving...' : saved ? '✅ Saved!' : '💾 Save Profile'}
        </button>
      </div>
    </div>
  )
}
