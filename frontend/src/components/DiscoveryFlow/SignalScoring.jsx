// src/components/DiscoveryFlow/SignalScoring.jsx
import React from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { useScoring } from '../../hooks/useScoring'
import { SIGNALS } from '../../utils/framework'

const SCORE_LABELS = { 0: 'Not Present', 1: 'Emerging', 2: 'Strong' }

const BUTTON_STYLES = {
  0: {
    inactive: 'border-slate-border text-ink-muted bg-white hover:border-blue-mid hover:bg-blue-light/30',
    active: 'border-slate-border bg-slate-subtle text-ink-muted',
  },
  1: {
    inactive: 'border-slate-border text-ink-muted bg-white hover:border-amber-trigger hover:bg-amber-trigger-bg',
    active: 'border-amber-trigger bg-amber-trigger-bg text-amber-700 font-semibold',
  },
  2: {
    inactive: 'border-slate-border text-ink-muted bg-white hover:border-green-signal hover:bg-green-signal-bg',
    active: 'border-green-signal bg-green-signal-bg text-green-signal font-semibold',
  },
}

export default function SignalScoring({ dimensionKey }) {
  const dimensionData = useSessionStore((s) => s.dimensions[dimensionKey])
  const { scoreSignal } = useScoring(dimensionKey)
  const signals = SIGNALS[dimensionKey] || []

  const totalScore = dimensionData?.achievedScore ?? 0
  const maxScore = dimensionData?.maxScore ?? signals.length * 2
  const pct = maxScore > 0 ? (totalScore / maxScore) * 100 : 0

  return (
    <div className="border-t border-slate-border bg-white pt-4 mt-4 flex-shrink-0">
      {/* Panel header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="font-display font-semibold text-sm text-ink">Signal Scoring</h3>
        <div className="flex items-center gap-3">
          <div className="h-1.5 w-24 bg-slate-subtle rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-primary rounded-full transition-all duration-300"
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className="font-mono text-sm font-semibold text-ink">
            {totalScore}<span className="text-ink-muted font-normal">/{maxScore}</span>
          </span>
        </div>
      </div>

      {/* Signal rows */}
      <div className="space-y-2">
        {signals.map((signal) => {
          const currentScore = dimensionData?.signals?.[signal.id] ?? 0

          return (
            <div
              key={signal.id}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg border border-slate-border bg-white hover:bg-slate-surface transition-colors duration-100"
            >
              {/* Signal info */}
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold text-ink truncate">{signal.label}</div>
                <div className="text-xs text-ink-muted leading-snug mt-0.5 line-clamp-1">{signal.description}</div>
              </div>

              {/* Score buttons 0/1/2 */}
              <div className="flex items-center gap-1.5 flex-shrink-0">
                {[0, 1, 2].map((score) => {
                  const isActive = currentScore === score
                  const styles = BUTTON_STYLES[score]

                  return (
                    <button
                      key={score}
                      title={`${score} — ${SCORE_LABELS[score]}`}
                      onClick={() => scoreSignal(signal.id, score)}
                      className={`signal-score-btn ${isActive ? styles.active : styles.inactive} border-2`}
                    >
                      {score}
                    </button>
                  )
                })}
              </div>

              {/* Current score indicator */}
              <div className="w-16 text-right flex-shrink-0">
                <span className={`text-xs font-medium ${
                  currentScore === 2 ? 'text-green-signal' :
                  currentScore === 1 ? 'text-amber-600' :
                  'text-ink-muted'
                }`}>
                  {SCORE_LABELS[currentScore]}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-border px-1">
        <span className="text-xs text-ink-muted font-medium">Scale:</span>
        <div className="flex items-center gap-4 text-xs text-ink-muted">
          <span><span className="font-mono font-semibold text-ink">0</span> Not Present</span>
          <span><span className="font-mono font-semibold text-amber-600">1</span> Emerging</span>
          <span><span className="font-mono font-semibold text-green-signal">2</span> Strong</span>
        </div>
      </div>
    </div>
  )
}
