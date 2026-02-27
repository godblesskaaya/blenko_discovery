// src/components/DiscoveryFlow/ScoreTracker.jsx
import React from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { DIMENSION_META, DIMENSIONS_ORDER } from '../../utils/framework'

const GRADE_STYLES = {
  unqualified: { bg: 'bg-gray-50', text: 'text-gray-600', border: 'border-gray-200', bar: 'bg-gray-400' },
  developing: { bg: 'bg-amber-trigger-bg', text: 'text-amber-700', border: 'border-amber-200', bar: 'bg-amber-trigger' },
  qualified: { bg: 'bg-green-signal-bg', text: 'text-green-signal', border: 'border-green-200', bar: 'bg-green-signal' },
  hot: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', bar: 'bg-purple-600' },
}

const GRADE_LABELS = {
  unqualified: 'Unqualified',
  developing: 'Developing',
  qualified: 'Qualified',
  hot: '🔥 Hot',
}

const TIER_COLORS = {
  low: 'text-red-warn',
  emerging: 'text-amber-600',
  high: 'text-green-signal',
}

export default function ScoreTracker() {
  const dimensions = useSessionStore((s) => s.dimensions)
  const overallScore = useSessionStore((s) => s.overallScore)
  const qualificationGrade = useSessionStore((s) => s.qualificationGrade)
  const currentDimension = useSessionStore((s) => s.currentDimension)
  const MAX_SCORE = 50

  const gradeStyle = GRADE_STYLES[qualificationGrade] || GRADE_STYLES.unqualified
  const scorePercent = (overallScore / MAX_SCORE) * 100

  return (
    <aside className="w-72 bg-white border-l border-slate-border flex flex-col overflow-y-auto scrollbar-thin flex-shrink-0">
      <div className="p-5 border-b border-slate-border">
        <h3 className="font-display font-semibold text-sm text-ink-muted uppercase tracking-wider mb-4">
          Score Tracker
        </h3>

        {/* Overall Score */}
        <div className="mb-4">
          <div className="flex items-end justify-between mb-2">
            <span className="text-sm text-ink-muted">Overall</span>
            <span className="font-mono font-semibold text-2xl text-ink leading-none">
              {overallScore}
              <span className="text-sm text-ink-muted font-normal">/{MAX_SCORE}</span>
            </span>
          </div>
          <div className="h-2 bg-slate-subtle rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-primary rounded-full transition-all duration-300 ease-out"
              style={{ width: `${scorePercent}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-ink-muted mt-1">
            <span>0</span>
            <span>25</span>
            <span>50</span>
          </div>
        </div>

        {/* Grade */}
        <div className={`rounded-lg px-3.5 py-3 border ${gradeStyle.bg} ${gradeStyle.border}`}>
          <div className="text-xs text-ink-muted mb-1">Qualification Grade</div>
          <div className={`font-display font-bold text-base ${gradeStyle.text}`}>
            {GRADE_LABELS[qualificationGrade]}
          </div>
        </div>
      </div>

      {/* Dimension breakdown */}
      <div className="p-5 space-y-3">
        <h4 className="font-display font-semibold text-xs text-ink-muted uppercase tracking-wider">
          Dimensions
        </h4>
        {DIMENSIONS_ORDER.map((key) => {
          const meta = DIMENSION_META[key]
          const dim = dimensions[key]
          const pct = dim ? (dim.achievedScore / dim.maxScore) * 100 : 0
          const isActive = key === currentDimension
          const isComplete = dim?.isComplete

          return (
            <div
              key={key}
              className={`rounded-lg p-3 border transition-all duration-150 ${
                isActive
                  ? 'border-blue-mid bg-blue-light'
                  : isComplete
                  ? 'border-slate-border bg-slate-subtle'
                  : 'border-slate-border bg-white'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className={`text-xs font-medium ${isActive ? 'text-blue-primary' : 'text-ink-muted'}`}>
                  {meta?.shortLabel}: {meta?.label}
                </span>
                <span className="font-mono text-xs font-semibold text-ink">
                  {dim?.achievedScore ?? 0}/{dim?.maxScore ?? '-'}
                </span>
              </div>

              <div className="h-1 bg-slate-subtle rounded-full overflow-hidden mb-1.5">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${
                    isActive ? 'bg-blue-primary' : 'bg-blue-mid'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>

              {dim?.tierLabel && (
                <div className={`text-xs ${TIER_COLORS[dim.tier] || 'text-ink-muted'}`}>
                  {dim.tierLabel}
                </div>
              )}

              {dim?.probesUsed?.length > 0 && (
                <div className="text-xs text-ink-muted mt-0.5">
                  {dim.probesUsed.length} probe{dim.probesUsed.length !== 1 ? 's' : ''} used
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Flags count */}
      <div className="p-5 pt-0">
        <div className="rounded-lg border border-slate-border p-3 bg-slate-subtle">
          <div className="text-xs text-ink-muted mb-1">Session Totals</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="font-mono font-semibold text-ink">
                {Object.values(dimensions).reduce((n, d) => n + (d.probesUsed?.length ?? 0), 0)}
              </span>
              <span className="text-ink-muted"> probes used</span>
            </div>
            <div>
              <span className="font-mono font-semibold text-ink">
                {Object.values(dimensions).filter((d) => d.isComplete).length}
              </span>
              <span className="text-ink-muted"> dims complete</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
