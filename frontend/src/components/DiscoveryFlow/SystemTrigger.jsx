// src/components/DiscoveryFlow/SystemTrigger.jsx
import React, { useEffect, useRef } from 'react'
import { useSessionStore } from '../../store/sessionStore'

const TIER_STYLES = {
  low: {
    bg: 'bg-red-warn-bg',
    border: 'border-red-warn',
    icon: '⚠️',
    label: 'Attention Required',
    textColor: 'text-red-700',
    btnClass: 'bg-red-warn text-white hover:bg-red-700',
  },
  emerging: {
    bg: 'bg-amber-trigger-bg',
    border: 'border-amber-trigger',
    icon: '📊',
    label: 'System Trigger',
    textColor: 'text-amber-800',
    btnClass: 'bg-amber-trigger text-white hover:bg-amber-600',
  },
  high: {
    bg: 'bg-green-signal-bg',
    border: 'border-green-signal',
    icon: '✅',
    label: 'Strong Signal',
    textColor: 'text-green-800',
    btnClass: 'bg-green-signal text-white hover:bg-green-700',
  },
}

/**
 * SystemTrigger
 * Appears automatically when score crosses a tier threshold.
 * Must be visually unmissable — amber background, distinct typography.
 * Scroll-into-view on mount.
 */
export default function SystemTrigger({ dimensionKey }) {
  const dimensionData = useSessionStore((s) => s.dimensions[dimensionKey])
  const dismissSystemTrigger = useSessionStore((s) => s.dismissSystemTrigger)
  const ref = useRef(null)

  const trigger = dimensionData?.systemTrigger
  const tier = dimensionData?.tier
  const score = dimensionData?.achievedScore ?? 0
  const tierLabel = dimensionData?.tierLabel ?? ''

  useEffect(() => {
    if (trigger && ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [trigger])

  if (!trigger) return null

  const style = TIER_STYLES[tier] || TIER_STYLES.emerging

  return (
    <div
      ref={ref}
      className={`mt-4 rounded-xl border-2 ${style.bg} ${style.border} p-5 shadow-trigger`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl flex-shrink-0 mt-0.5">{style.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span className={`font-display font-bold text-base ${style.textColor}`}>
              {style.label}
            </span>
            <span className={`font-mono text-xs px-2 py-0.5 rounded-full border ${style.textColor} ${style.bg} ${style.border}`}>
              Score {score} — {tierLabel}
            </span>
          </div>
          <p className={`text-sm leading-relaxed ${style.textColor}`}>
            {trigger.instruction}
          </p>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="text-xs text-ink-muted italic">
          Acknowledge to continue. Scores can always be revised retroactively.
        </div>
        <button
          onClick={() => dismissSystemTrigger(dimensionKey)}
          className={`text-sm font-semibold px-4 py-2 rounded-lg transition-colors ${style.btnClass}`}
        >
          Acknowledge & Continue →
        </button>
      </div>
    </div>
  )
}
