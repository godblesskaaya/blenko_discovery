// src/components/DiscoveryFlow/OpeningQuestion.jsx
import React from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { useAutoSave } from '../../hooks/useAutoSave'
import { DIMENSION_META } from '../../utils/framework'

export default function OpeningQuestion({ dimensionKey }) {
  const meta = DIMENSION_META[dimensionKey]
  const dimensionData = useSessionStore((s) => s.dimensions[dimensionKey])
  const updateDimensionNotes = useSessionStore((s) => s.updateDimensionNotes)
  const { triggerAutoSave } = useAutoSave()

  const handleNotesChange = (value) => {
    updateDimensionNotes(dimensionKey, value)
    triggerAutoSave({ dimension_notes: { [dimensionKey]: value } })
  }

  if (!meta) return null

  return (
    <div className="space-y-5">
      {/* Opening Question */}
      <div className="relative">
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-primary rounded-full" />
        <div className="pl-5">
          <div className="text-xs font-semibold uppercase tracking-wider text-blue-primary mb-2">
            Opening Question
          </div>
          <p className="text-lg leading-relaxed text-ink font-medium">
            "{meta.openingQuestion}"
          </p>
        </div>
      </div>

      {/* Positioning Moment */}
      <div className="bg-slate-subtle border border-slate-border rounded-xl p-4">
        <div className="flex items-start gap-3">
          <span className="text-base flex-shrink-0">🎯</span>
          <div>
            <div className="text-xs font-semibold text-ink-muted uppercase tracking-wider mb-1.5">
              Positioning Moment
            </div>
            <p className="text-sm text-ink-muted leading-relaxed">
              {meta.positioningMoment}
            </p>
          </div>
        </div>
      </div>

      {/* Rep Notes */}
      <div>
        <label className="form-label">Rep Notes — key points from response</label>
        <textarea
          className="form-input h-28 resize-none"
          value={dimensionData?.notes || ''}
          onChange={(e) => handleNotesChange(e.target.value)}
          placeholder="Note the prospect's language, any specific signals you hear, emotional cues..."
        />
      </div>
    </div>
  )
}
