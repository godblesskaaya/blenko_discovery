// src/components/DiscoveryFlow/ProbesPanel.jsx
import React, { useState } from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { useAutoSave } from '../../hooks/useAutoSave'
import { PROBES } from '../../utils/framework'

export default function ProbesPanel({ dimensionKey }) {
  const dimensionData = useSessionStore((s) => s.dimensions[dimensionKey])
  const markProbeUsed = useSessionStore((s) => s.markProbeUsed)
  const { triggerAutoSave } = useAutoSave()
  const [expanded, setExpanded] = useState(null)

  const probes = PROBES[dimensionKey] || []
  const usedProbes = dimensionData?.probesUsed || []

  const handleToggleUsed = (probeId) => {
    markProbeUsed(dimensionKey, probeId)
    triggerAutoSave({ probes_used: { [dimensionKey]: probeId } })
  }

  const usedCount = usedProbes.length
  const totalCount = probes.length

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-ink-muted">
          {usedCount}/{totalCount} used
        </span>
        <div className="flex gap-1">
          {probes.map((p) => (
            <div
              key={p.id}
              className={`w-2 h-2 rounded-full ${usedProbes.includes(p.id) ? 'bg-green-signal' : 'bg-slate-border'}`}
              title={p.label}
            />
          ))}
        </div>
      </div>

      <div className="space-y-2">
        {probes.map((probe) => {
          const isUsed = usedProbes.includes(probe.id)
          const isOpen = expanded === probe.id

          return (
            <div
              key={probe.id}
              className={`border rounded-xl transition-all duration-150 overflow-hidden ${
                isUsed
                  ? 'border-green-signal bg-green-signal-bg'
                  : 'border-slate-border bg-white hover:border-blue-mid'
              }`}
            >
              {/* Header */}
              <div className="flex items-center px-4 py-3 cursor-pointer" onClick={() => setExpanded(isOpen ? null : probe.id)}>
                <div className="flex-1 min-w-0">
                  <div className={`text-sm font-semibold ${isUsed ? 'text-green-signal' : 'text-blue-primary'}`}>
                    {probe.label}
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-3 flex-shrink-0">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleToggleUsed(probe.id) }}
                    className={`text-xs px-2.5 py-1 rounded-full font-medium transition-all border ${
                      isUsed
                        ? 'bg-green-signal text-white border-green-signal'
                        : 'bg-white text-ink-muted border-slate-border hover:border-green-signal hover:text-green-signal'
                    }`}
                  >
                    {isUsed ? '✓ Used' : 'Mark Used'}
                  </button>

                  <svg
                    className={`w-4 h-4 text-ink-muted transition-transform duration-150 ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* Expanded probe text */}
              {isOpen && (
                <div className="px-4 pb-4 pt-1 border-t border-slate-border/50">
                  <p className={`text-sm leading-relaxed ${isUsed ? 'text-green-800' : 'text-ink'}`}>
                    "{probe.text}"
                  </p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
