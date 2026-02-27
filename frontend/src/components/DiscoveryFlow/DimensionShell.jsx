// src/components/DiscoveryFlow/DimensionShell.jsx
import React, { useState } from 'react'
import OpeningQuestion from './OpeningQuestion'
import ProbesPanel from './ProbesPanel'
import ReframesPanel from './ReframesPanel'
import NotesPanel from './NotesPanel'
import SignalScoring from './SignalScoring'
import SystemTrigger from './SystemTrigger'
import { DIMENSION_META } from '../../utils/framework'
import { useSessionStore } from '../../store/sessionStore'

const TABS = [
  { id: 'opening', label: 'Opening Question' },
  { id: 'probes', label: 'Probes' },
  { id: 'reframes', label: 'Reframes' },
  { id: 'notes', label: 'Notes' },
]

/**
 * DimensionShell
 * The persistent content wrapper used for ALL dimensions.
 * Structure never changes between dimensions — only content inside.
 * Keeps reps oriented so they never have to relearn the layout.
 */
export default function DimensionShell({ dimensionKey }) {
  const [activeTab, setActiveTab] = useState('opening')
  const meta = DIMENSION_META[dimensionKey]
  const dimensionData = useSessionStore((s) => s.dimensions[dimensionKey])
  const completeDimension = useSessionStore((s) => s.completeDimension)
  const setCurrentDimension = useSessionStore((s) => s.setCurrentDimension)
  const dimensions = useSessionStore((s) => s.dimensions)

  const DIMENSIONS_ORDER = ['competitive_awareness', 'brand_gap', 'is_maturity', 'cost_of_status_quo']
  const currentIndex = DIMENSIONS_ORDER.indexOf(dimensionKey)
  const nextDimension = DIMENSIONS_ORDER[currentIndex + 1] || null
  const hasSignals = Object.values(dimensionData?.signals || {}).some((s) => s > 0)

  const handleCompleteDimension = () => {
    completeDimension(dimensionKey)
    if (nextDimension) {
      setCurrentDimension(nextDimension)
    }
  }

  const probesUsedCount = dimensionData?.probesUsed?.length || 0

  return (
    <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
      {/* Dimension header */}
      <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-slate-border flex-shrink-0">
        <div>
          <div className="text-xs font-semibold text-ink-muted uppercase tracking-wider mb-1">
            {meta?.shortLabel}
          </div>
          <h2 className="font-display font-bold text-xl text-ink">{meta?.label}</h2>
        </div>
        <div className="flex items-center gap-2">
          {probesUsedCount > 0 && (
            <span className="text-xs text-ink-muted bg-slate-subtle border border-slate-border rounded-full px-2.5 py-1">
              {probesUsedCount} probe{probesUsedCount !== 1 ? 's' : ''} used
            </span>
          )}
          {dimensionData?.isComplete ? (
            <span className="text-xs font-medium text-green-signal bg-green-signal-bg border border-green-200 rounded-full px-2.5 py-1 flex items-center gap-1">
              ✓ Complete
            </span>
          ) : (
            <button
              onClick={handleCompleteDimension}
              disabled={!hasSignals}
              className="btn-primary text-sm disabled:opacity-40 disabled:cursor-not-allowed"
              title={!hasSignals ? 'Score at least one signal before completing' : ''}
            >
              {nextDimension ? `Complete & Move to ${DIMENSION_META[nextDimension]?.shortLabel} →` : 'Complete Dimension'}
            </button>
          )}
        </div>
      </div>

      {/* Tab navigation */}
      <div className="flex border-b border-slate-border px-6 flex-shrink-0 overflow-x-auto">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-btn ${activeTab === tab.id ? 'tab-btn-active' : 'tab-btn-inactive'}`}
          >
            {tab.label}
            {tab.id === 'probes' && probesUsedCount > 0 && (
              <span className="ml-1.5 bg-green-signal text-white text-xs rounded-full w-4 h-4 inline-flex items-center justify-center">
                {probesUsedCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content — scrollable */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-6 py-5">
        {activeTab === 'opening' && <OpeningQuestion dimensionKey={dimensionKey} />}
        {activeTab === 'probes' && <ProbesPanel dimensionKey={dimensionKey} />}
        {activeTab === 'reframes' && <ReframesPanel dimensionKey={dimensionKey} />}
        {activeTab === 'notes' && <NotesPanel dimensionKey={dimensionKey} />}
      </div>

      {/* Signal Scoring — always visible, pinned to bottom */}
      <div className="px-6 pb-5 flex-shrink-0">
        <SignalScoring dimensionKey={dimensionKey} />
        <SystemTrigger dimensionKey={dimensionKey} />
      </div>
    </div>
  )
}
