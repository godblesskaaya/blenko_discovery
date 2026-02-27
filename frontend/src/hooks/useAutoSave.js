// src/hooks/useAutoSave.js
import { useRef, useCallback } from 'react'
import toast from 'react-hot-toast'
import { sessionAPI } from '../api/client'
import { useSessionStore } from '../store/sessionStore'

/**
 * useAutoSave
 * Debounces saves to the backend. Every field change calls triggerAutoSave()
 * with the partial update payload. Fires after `delay` ms of inactivity.
 *
 * Also updates the global saveStatus so the TopBar can show the indicator.
 */
export function useAutoSave(delay = 800) {
  const sessionId = useSessionStore((s) => s.sessionId)
  const setSaveStatus = useSessionStore((s) => s.setSaveStatus)
  const timerRef = useRef(null)

  const triggerAutoSave = useCallback(
    (updates) => {
      if (!sessionId) return

      setSaveStatus('saving')

      if (timerRef.current) clearTimeout(timerRef.current)

      timerRef.current = setTimeout(async () => {
        try {
          await sessionAPI.autoSave(sessionId, updates)
          setSaveStatus('saved')
          // Reset to idle after 2s
          setTimeout(() => setSaveStatus('idle'), 2000)
        } catch (err) {
          setSaveStatus('error')
          toast.error('Auto-save failed — data is stored locally')
          console.error('[AutoSave]', err)
        }
      }, delay)
    },
    [sessionId, setSaveStatus, delay]
  )

  return { triggerAutoSave }
}
