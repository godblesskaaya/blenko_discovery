// src/pages/DiscoveryFlow.jsx
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useSessionStore } from '../store/sessionStore'
import DimensionShell from '../components/DiscoveryFlow/DimensionShell'
import ScoreTracker from '../components/DiscoveryFlow/ScoreTracker'
import { DIMENSION_META, DIMENSIONS_ORDER } from '../utils/framework'

const SAVE_STATUS_CONFIG = {
  idle: { text: '', show: false },
  saving: { text: 'Saving...', color: 'text-ink-muted', dot: 'bg-amber-trigger animate-pulse' },
  saved: { text: 'Saved', color: 'text-green-signal', dot: 'bg-green-signal' },
  error: { text: 'Save failed', color: 'text-red-warn', dot: 'bg-red-warn' },
}

export default function DiscoveryFlow() {
  const navigate = useNavigate()
  const prospect = useSessionStore((s) => s.prospect)
  const currentDimension = useSessionStore((s) => s.currentDimension)
  const setCurrentDimension = useSessionStore((s) => s.setCurrentDimension)
  const dimensions = useSessionStore((s) => s.dimensions)
  const saveStatus = useSessionStore((s) => s.saveStatus)

  const saveConfig = SAVE_STATUS_CONFIG[saveStatus]
  const companyName = prospect.companyName || 'New Session'

  return (
    <div className="h-screen flex flex-col bg-slate-surface overflow-hidden">
      {/* ── Top Bar ─────────────────────────────────────────────────────── */}
      <header className="bg-white border-b border-slate-border px-6 py-3 flex items-center justify-between flex-shrink-0">
        {/* Left: App + Company */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-ink-muted hover:text-ink transition-colors"
          >
            <div className="w-6 h-6 bg-blue-primary rounded-md flex items-center justify-center">
              <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="font-display font-semibold text-sm">Blenko</span>
          </button>
          <span className="text-slate-border">/</span>
          <span className="font-display font-semibold text-sm text-ink truncate max-w-48">
            {companyName}
          </span>
          {prospect.contactName && (
            <>
              <span className="text-slate-border">/</span>
              <span className="text-sm text-ink-muted">{prospect.contactName}</span>
            </>
          )}
        </div>

        {/* Center: Dimension Progress */}
        <div className="flex items-center gap-1">
          {DIMENSIONS_ORDER.map((key, idx) => {
            const meta = DIMENSION_META[key]
            const isActive = key === currentDimension
            const isComplete = dimensions[key]?.isComplete
            const hasScores = Object.values(dimensions[key]?.signals || {}).some((s) => s > 0)

            return (
              <React.Fragment key={key}>
                <button
                  onClick={() => setCurrentDimension(key)}
                  title={meta?.label}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-primary text-white shadow-sm'
                      : isComplete
                      ? 'bg-green-signal-bg text-green-signal border border-green-200 hover:bg-green-100'
                      : hasScores
                      ? 'bg-amber-trigger-bg text-amber-700 border border-amber-200 hover:bg-amber-100'
                      : 'text-ink-muted hover:bg-slate-subtle border border-transparent'
                  }`}
                >
                  {isComplete ? (
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-white' : 'bg-current opacity-60'}`} />
                  )}
                  {meta?.shortLabel}
                </button>

                {idx < DIMENSIONS_ORDER.length - 1 && (
                  <div className="w-3 h-px bg-slate-border" />
                )}
              </React.Fragment>
            )
          })}
        </div>

        {/* Right: Save status */}
        <div className="flex items-center gap-3">
          {saveConfig.show !== false && saveStatus !== 'idle' && (
            <div className={`save-indicator ${saveConfig.color || 'text-ink-muted'}`}>
              <div className={`w-1.5 h-1.5 rounded-full ${saveConfig.dot}`} />
              {saveConfig.text}
            </div>
          )}
        </div>
      </header>

      {/* ── Main Area ───────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        {/* Content: Dimension Shell */}
        <div className="flex-1 flex flex-col overflow-hidden bg-white border-r border-slate-border">
          <DimensionShell dimensionKey={currentDimension} />
        </div>

        {/* Right: Score Tracker */}
        <ScoreTracker />
      </div>
    </div>
  )
}
