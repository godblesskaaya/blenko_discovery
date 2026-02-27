// src/pages/Dashboard.jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSessionStore } from '../store/sessionStore'

const GRADE_COLORS = {
  unqualified: 'bg-gray-100 text-gray-600 border-gray-200',
  developing: 'bg-amber-50 text-amber-700 border-amber-200',
  qualified: 'bg-green-signal-bg text-green-signal border-green-200',
  hot: 'bg-purple-50 text-purple-700 border-purple-200',
}

const GRADE_DOT = {
  unqualified: 'bg-gray-400',
  developing: 'bg-amber-trigger',
  qualified: 'bg-green-signal',
  hot: 'bg-purple-600',
}

// Mock sessions for UI development — replace with API data in Phase 2
const MOCK_SESSIONS = [
  {
    id: '1',
    companyName: 'Hartwell Constructions',
    contactName: 'Mike Hartwell',
    persona: 'Executive Sponsor',
    overallScore: 34,
    grade: 'qualified',
    currentDimension: 'D3',
    lastActive: '2 hours ago',
    status: 'in_progress',
  },
  {
    id: '2',
    companyName: 'Riverstone Hospitality Group',
    contactName: 'Sarah Chen',
    persona: 'Champion',
    overallScore: 22,
    grade: 'developing',
    currentDimension: 'D2',
    lastActive: '1 day ago',
    status: 'in_progress',
  },
  {
    id: '3',
    companyName: 'Alpine Trades & Services',
    contactName: 'Jason Muller',
    persona: 'Executive Sponsor',
    overallScore: 47,
    grade: 'hot',
    currentDimension: 'D5',
    lastActive: '3 days ago',
    status: 'complete',
  },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const currentUser = useSessionStore((s) => s.currentUser)
  const clearSession = useSessionStore((s) => s.clearSession)
  const [sessions] = useState(MOCK_SESSIONS)

  const handleNewSession = () => {
    clearSession()
    navigate('/session-setup')
  }

  const inProgress = sessions.filter((s) => s.status === 'in_progress')
  const completed = sessions.filter((s) => s.status === 'complete')

  return (
    <div className="min-h-screen bg-slate-surface">
      {/* Header */}
      <header className="bg-white border-b border-slate-border px-8 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 bg-blue-primary rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <span className="font-display font-semibold text-lg text-ink">Blenko Discovery</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-ink-muted">
            {currentUser?.name || 'Sales Rep'}
          </span>
          <button
            onClick={handleNewSession}
            className="btn-primary text-sm"
          >
            + New Session
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-8 py-8">
        {/* Context line */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-display font-bold text-2xl text-ink">Dashboard</h1>
            <p className="text-ink-muted text-sm mt-1">
              {inProgress.length} active session{inProgress.length !== 1 ? 's' : ''} ·{' '}
              {completed.length} completed
            </p>
          </div>
        </div>

        {/* Active Sessions */}
        {inProgress.length > 0 && (
          <section className="mb-8">
            <h2 className="font-display font-semibold text-sm uppercase tracking-wider text-ink-muted mb-4">
              Active Sessions
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {inProgress.map((session) => (
                <SessionCard key={session.id} session={session} navigate={navigate} />
              ))}
            </div>
          </section>
        )}

        {/* Empty state */}
        {inProgress.length === 0 && (
          <div className="card p-12 text-center mb-8">
            <div className="w-12 h-12 bg-blue-light rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-blue-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h3 className="font-display font-semibold text-lg text-ink mb-2">No active sessions</h3>
            <p className="text-ink-muted text-sm mb-6">Start a new discovery session to begin qualifying a prospect.</p>
            <button onClick={handleNewSession} className="btn-primary">
              Start New Session
            </button>
          </div>
        )}

        {/* Completed Sessions */}
        {completed.length > 0 && (
          <section>
            <h2 className="font-display font-semibold text-sm uppercase tracking-wider text-ink-muted mb-4">
              Completed Sessions
            </h2>
            <div className="card overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-border bg-slate-subtle">
                    <th className="text-left px-5 py-3 font-medium text-ink-muted">Company</th>
                    <th className="text-left px-5 py-3 font-medium text-ink-muted">Contact</th>
                    <th className="text-left px-5 py-3 font-medium text-ink-muted">Score</th>
                    <th className="text-left px-5 py-3 font-medium text-ink-muted">Grade</th>
                    <th className="text-right px-5 py-3" />
                  </tr>
                </thead>
                <tbody>
                  {completed.map((session, i) => (
                    <tr key={session.id} className={i < completed.length - 1 ? 'border-b border-slate-border' : ''}>
                      <td className="px-5 py-4 font-medium text-ink">{session.companyName}</td>
                      <td className="px-5 py-4 text-ink-muted">{session.contactName}</td>
                      <td className="px-5 py-4 font-mono text-sm">{session.overallScore}/50</td>
                      <td className="px-5 py-4">
                        <GradeBadge grade={session.grade} />
                      </td>
                      <td className="px-5 py-4 text-right">
                        <button className="text-blue-primary text-sm hover:underline">View</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

function SessionCard({ session, navigate }) {
  const handleContinue = () => {
    navigate('/discovery')
  }

  const isStale = session.lastActive.includes('day') || session.lastActive.includes('week')

  return (
    <div className="card p-6 hover:shadow-elevated transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-display font-semibold text-base text-ink">{session.companyName}</h3>
          <p className="text-sm text-ink-muted mt-0.5">{session.contactName}</p>
        </div>
        <GradeBadge grade={session.grade} />
      </div>

      <div className="flex items-center gap-4 text-xs text-ink-muted mb-4">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-primary" />
          {session.currentDimension} in progress
        </span>
        <span>Persona: {session.persona}</span>
      </div>

      {/* Score bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-xs text-ink-muted">Overall Score</span>
          <span className="font-mono text-sm font-medium text-ink">{session.overallScore}<span className="text-ink-muted">/50</span></span>
        </div>
        <div className="h-1.5 bg-slate-subtle rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-primary rounded-full transition-all duration-500"
            style={{ width: `${(session.overallScore / 50) * 100}%` }}
          />
        </div>
      </div>

      {isStale && (
        <div className="text-xs text-amber-600 bg-amber-trigger-bg border border-amber-trigger-border rounded px-2.5 py-1.5 mb-3 flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Session untouched for {session.lastActive} — follow up?
        </div>
      )}

      <div className="flex gap-2">
        <button onClick={handleContinue} className="btn-primary text-sm flex-1 text-center">
          Continue Session
        </button>
        <button className="btn-secondary text-sm px-4">
          View
        </button>
      </div>
    </div>
  )
}

function GradeBadge({ grade }) {
  const labels = {
    unqualified: 'Unqualified',
    developing: 'Developing',
    qualified: 'Qualified',
    hot: '🔥 Hot',
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${GRADE_COLORS[grade]}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${GRADE_DOT[grade]}`} />
      {labels[grade]}
    </span>
  )
}
