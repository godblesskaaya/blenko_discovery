// src/components/DiscoveryFlow/ReframesPanel.jsx
import React from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { useAutoSave } from '../../hooks/useAutoSave'
import { REFRAMES } from '../../utils/framework'

export default function ReframesPanel({ dimensionKey }) {
  const dimensionData = useSessionStore((s) => s.dimensions[dimensionKey])
  const markReframeDeployed = useSessionStore((s) => s.markReframeDeployed)
  const { triggerAutoSave } = useAutoSave()

  const reframes = REFRAMES[dimensionKey] || []
  const deployed = dimensionData?.reframesDeployed || []

  const handleToggle = (reframeId) => {
    markReframeDeployed(dimensionKey, reframeId)
    triggerAutoSave({ reframes_deployed: { [dimensionKey]: reframeId } })
  }

  if (reframes.length === 0) {
    return (
      <div className="text-sm text-ink-muted text-center py-8">
        No reframes defined for this dimension.
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-ink-muted leading-relaxed">
        Use these reframes when the prospect pushes back or shows low awareness. Mark as deployed when you use one.
      </p>

      {reframes.map((reframe) => {
        const isDeployed = deployed.includes(reframe.id)

        return (
          <div
            key={reframe.id}
            className={`border rounded-xl p-4 transition-all ${
              isDeployed
                ? 'border-blue-mid bg-blue-light'
                : 'border-slate-border bg-white'
            }`}
          >
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-1">
                  Trigger: {reframe.label}
                </div>
              </div>
              <button
                onClick={() => handleToggle(reframe.id)}
                className={`text-xs px-2.5 py-1 rounded-full font-medium flex-shrink-0 transition-all border ${
                  isDeployed
                    ? 'bg-blue-primary text-white border-blue-primary'
                    : 'bg-white text-ink-muted border-slate-border hover:border-blue-primary hover:text-blue-primary'
                }`}
              >
                {isDeployed ? '✓ Deployed' : 'Mark Deployed'}
              </button>
            </div>

            <blockquote className={`text-sm leading-relaxed italic ${isDeployed ? 'text-blue-hover' : 'text-ink'}`}>
              "{reframe.text}"
            </blockquote>
          </div>
        )
      })}
    </div>
  )
}
