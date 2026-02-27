// src/hooks/useScoring.js
import { useCallback } from 'react'
import { scoringAPI } from '../api/client'
import { useSessionStore } from '../store/sessionStore'
import { getDimensionTier, SCORE_TRIGGERS } from '../utils/framework'

/**
 * useScoring
 * Manages signal scoring with optimistic local updates + backend sync.
 * Handles the <100ms requirement by updating local state immediately,
 * then syncing with backend.
 */
export function useScoring(dimensionKey) {
  const interactionId = useSessionStore((s) => s.interactionId)
  const updateSignalScore = useSessionStore((s) => s.updateSignalScore)
  const updateDimensionFromBackend = useSessionStore((s) => s.updateDimensionFromBackend)
  const setSystemTrigger = useSessionStore((s) => s.setSystemTrigger)
  const dimensionData = useSessionStore((s) => s.dimensions[dimensionKey])

  const scoreSignal = useCallback(
    async (signalId, score) => {
      // 1. Optimistic local update — fires within a render cycle (~16ms)
      updateSignalScore(dimensionKey, signalId, score)

      // 2. Compute new score locally to decide if trigger should show
      const signals = { ...dimensionData.signals, [signalId]: score }
      const newScore = Object.values(signals).reduce((sum, s) => sum + s, 0)
      const tier = getDimensionTier(dimensionKey, newScore)

      if (tier) {
        const triggers = SCORE_TRIGGERS[dimensionKey]
        const triggerData = triggers?.[tier.key]
        if (triggerData && newScore > 0) {
          setSystemTrigger(dimensionKey, triggerData)
        }
      }

      // 3. Sync with backend (non-blocking)
      if (!interactionId) return // No session yet — local-only mode

      try {
        const { data } = await scoringAPI.updateSignal(
          interactionId,
          dimensionKey,
          signalId,
          score
        )
        if (data?.dimension_total) {
          updateDimensionFromBackend(dimensionKey, data.dimension_total)
        }
      } catch (err) {
        // Non-fatal — local state is authoritative
        console.warn('[Scoring] Backend sync failed:', err.message)
      }
    },
    [interactionId, dimensionKey, dimensionData, updateSignalScore, updateDimensionFromBackend, setSystemTrigger]
  )

  return { scoreSignal }
}
