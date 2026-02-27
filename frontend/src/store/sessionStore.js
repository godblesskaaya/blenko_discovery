// src/store/sessionStore.js
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import {
  SIGNALS,
  DIMENSIONS_ORDER,
  getQualificationGrade,
  getDimensionTier,
  FRAMEWORK_VERSION,
} from '../utils/framework'

// Build initial dimension state from framework signals
function buildInitialDimension(dimensionKey) {
  const signals = SIGNALS[dimensionKey] || []
  const signalScores = {}
  signals.forEach((s) => { signalScores[s.id] = 0 })

  const maxScores = {
    competitive_awareness: 10,
    brand_gap: 12,
    is_maturity: 14,
    cost_of_status_quo: 14,
  }

  return {
    signals: signalScores,
    achievedScore: 0,
    maxScore: maxScores[dimensionKey] || 10,
    tier: null,
    tierLabel: '',
    systemTrigger: null,
    notes: '',
    probesUsed: [],
    reframesDeployed: [],
    isComplete: false,
    completedAt: null,
  }
}

function buildInitialDimensions() {
  const dims = {}
  DIMENSIONS_ORDER.forEach((key) => {
    dims[key] = buildInitialDimension(key)
  })
  return dims
}

const initialState = {
  // Auth
  authToken: null,
  currentUser: null,

  // Session
  sessionId: null,
  interactionId: null,
  prospectId: null,
  sessionStatus: 'not_started', // not_started | layer_zero | persona | discovery | complete
  currentDimension: 'competitive_awareness',
  saveStatus: 'idle', // idle | saving | saved | error

  // Layer Zero — Prospect
  prospect: {
    companyName: '',
    contactName: '',
    contactRole: '',
    contactEmail: '',
    contactPhone: '',
    businessType: null,
    sizeTier: null,
    growthStage: null,
    geographicScope: null,
    vendorStatus: null,
    growthAmbition: null,
  },

  // Layer Zero — Business Profile
  businessProfile: {
    triggerEvent: '',
    triggerCategory: null,
    currentVendors: '',
    competitiveContext: '',
    additionalContext: '',
  },

  // Dimensions
  dimensions: buildInitialDimensions(),

  // Overall
  overallScore: 0,
  maxPossibleScore: 50,
  qualificationGrade: 'unqualified',
  crossSellPotential: 'low',

  // Pain & solution flags
  painFlags: [],
  solutionFlags: [],
}

export const useSessionStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // ─── Auth ─────────────────────────────────────────────────────────────
      setAuth: (token, user) => set({ authToken: token, currentUser: user }),
      clearAuth: () => set({ authToken: null, currentUser: null }),

      // ─── Session lifecycle ────────────────────────────────────────────────
      setSessionId: (id) => set({ sessionId: id }),
      setInteractionId: (id) => set({ interactionId: id }),
      setProspectId: (id) => set({ prospectId: id }),
      setSessionStatus: (status) => set({ sessionStatus: status }),
      setSaveStatus: (status) => set({ saveStatus: status }),

      setCurrentDimension: (dim) => set({ currentDimension: dim }),

      // ─── Layer Zero ───────────────────────────────────────────────────────
      updateProspect: (field, value) =>
        set((state) => ({
          prospect: { ...state.prospect, [field]: value },
        })),

      updateBusinessProfile: (field, value) =>
        set((state) => ({
          businessProfile: { ...state.businessProfile, [field]: value },
        })),

      // ─── Signal scoring ───────────────────────────────────────────────────
      updateSignalScore: (dimensionKey, signalId, score) =>
        set((state) => {
          const dimension = state.dimensions[dimensionKey]
          const updatedSignals = { ...dimension.signals, [signalId]: score }

          // Recalculate dimension total
          const achievedScore = Object.values(updatedSignals).reduce((sum, s) => sum + s, 0)

          // Determine tier
          const tier = getDimensionTier(dimensionKey, achievedScore)

          // Recalculate overall score
          const updatedDimension = {
            ...dimension,
            signals: updatedSignals,
            achievedScore,
            tier: tier?.key || null,
            tierLabel: tier?.label || '',
          }

          const updatedDimensions = {
            ...state.dimensions,
            [dimensionKey]: updatedDimension,
          }

          const overallScore = Object.values(updatedDimensions).reduce(
            (sum, d) => sum + d.achievedScore,
            0
          )
          const qualificationGrade = getQualificationGrade(overallScore)

          return {
            dimensions: updatedDimensions,
            overallScore,
            qualificationGrade,
          }
        }),

      // Called when backend confirms score (authoritative)
      updateDimensionFromBackend: (dimensionKey, scoreData) =>
        set((state) => ({
          dimensions: {
            ...state.dimensions,
            [dimensionKey]: {
              ...state.dimensions[dimensionKey],
              achievedScore: scoreData.achieved_score ?? state.dimensions[dimensionKey].achievedScore,
              tier: scoreData.tier ?? state.dimensions[dimensionKey].tier,
              tierLabel: scoreData.tier_label ?? state.dimensions[dimensionKey].tierLabel,
              systemTrigger: scoreData.system_trigger ?? state.dimensions[dimensionKey].systemTrigger,
            },
          },
          overallScore: scoreData.overall_score ?? state.overallScore,
          qualificationGrade: scoreData.qualification_grade ?? state.qualificationGrade,
        })),

      // Show system trigger for a dimension
      setSystemTrigger: (dimensionKey, trigger) =>
        set((state) => ({
          dimensions: {
            ...state.dimensions,
            [dimensionKey]: {
              ...state.dimensions[dimensionKey],
              systemTrigger: trigger,
            },
          },
        })),

      dismissSystemTrigger: (dimensionKey) =>
        set((state) => ({
          dimensions: {
            ...state.dimensions,
            [dimensionKey]: {
              ...state.dimensions[dimensionKey],
              systemTrigger: null,
            },
          },
        })),

      // ─── Probes & Reframes ────────────────────────────────────────────────
      markProbeUsed: (dimensionKey, probeId) =>
        set((state) => {
          const current = state.dimensions[dimensionKey].probesUsed
          if (current.includes(probeId)) {
            return {
              dimensions: {
                ...state.dimensions,
                [dimensionKey]: {
                  ...state.dimensions[dimensionKey],
                  probesUsed: current.filter((id) => id !== probeId),
                },
              },
            }
          }
          return {
            dimensions: {
              ...state.dimensions,
              [dimensionKey]: {
                ...state.dimensions[dimensionKey],
                probesUsed: [...current, probeId],
              },
            },
          }
        }),

      markReframeDeployed: (dimensionKey, reframeId) =>
        set((state) => {
          const current = state.dimensions[dimensionKey].reframesDeployed
          if (current.includes(reframeId)) {
            return {
              dimensions: {
                ...state.dimensions,
                [dimensionKey]: {
                  ...state.dimensions[dimensionKey],
                  reframesDeployed: current.filter((id) => id !== reframeId),
                },
              },
            }
          }
          return {
            dimensions: {
              ...state.dimensions,
              [dimensionKey]: {
                ...state.dimensions[dimensionKey],
                reframesDeployed: [...current, reframeId],
              },
            },
          }
        }),

      // ─── Notes ────────────────────────────────────────────────────────────
      updateDimensionNotes: (dimensionKey, notes) =>
        set((state) => ({
          dimensions: {
            ...state.dimensions,
            [dimensionKey]: {
              ...state.dimensions[dimensionKey],
              notes,
            },
          },
        })),

      // ─── Complete dimension ────────────────────────────────────────────────
      completeDimension: (dimensionKey) =>
        set((state) => ({
          dimensions: {
            ...state.dimensions,
            [dimensionKey]: {
              ...state.dimensions[dimensionKey],
              isComplete: true,
              completedAt: new Date().toISOString(),
            },
          },
        })),

      // ─── Pain & Solution flags ────────────────────────────────────────────
      addPainFlag: (flag) =>
        set((state) => ({ painFlags: [...state.painFlags, { ...flag, id: crypto.randomUUID() }] })),

      addSolutionFlag: (flag) =>
        set((state) => ({ solutionFlags: [...state.solutionFlags, { ...flag, id: crypto.randomUUID() }] })),

      // ─── Session clear ────────────────────────────────────────────────────
      clearSession: () =>
        set({
          sessionId: null,
          interactionId: null,
          prospectId: null,
          sessionStatus: 'not_started',
          currentDimension: 'competitive_awareness',
          saveStatus: 'idle',
          prospect: initialState.prospect,
          businessProfile: initialState.businessProfile,
          dimensions: buildInitialDimensions(),
          overallScore: 0,
          qualificationGrade: 'unqualified',
          painFlags: [],
          solutionFlags: [],
        }),
    }),
    {
      name: 'blenko-session-v1',
      storage: createJSONStorage(() => localStorage),
      // Persist everything — session must survive page refresh mid-call
    }
  )
)
