// src/api/client.js
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Request interceptor: attach auth token ──────────────────────────────────
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('blenko_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ─── Response interceptor: token refresh ─────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('blenko_refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refresh,
          })
          localStorage.setItem('blenko_access_token', data.access_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return apiClient(original)
        } catch {
          localStorage.removeItem('blenko_access_token')
          localStorage.removeItem('blenko_refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  login: (email, password) =>
    apiClient.post('/auth/login', { username: email, password }),
  refresh: (refreshToken) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  logout: () =>
    apiClient.post('/auth/logout'),
}

// ─── Sessions ─────────────────────────────────────────────────────────────────
export const sessionAPI = {
  create: (prospectData, profileData) =>
    apiClient.post('/sessions/create', {
      prospect_data: prospectData,
      profile_data: profileData,
    }),

  get: (sessionId) =>
    apiClient.get(`/sessions/${sessionId}`),

  list: () =>
    apiClient.get('/sessions'),

  autoSave: (sessionId, updates) =>
    apiClient.patch(`/sessions/${sessionId}/autosave`, updates),

  complete: (sessionId) =>
    apiClient.post(`/sessions/${sessionId}/complete`),

  abandon: (sessionId) =>
    apiClient.post(`/sessions/${sessionId}/abandon`),
}

// ─── Scoring ──────────────────────────────────────────────────────────────────
export const scoringAPI = {
  updateSignal: (interactionId, dimension, signalName, score) =>
    apiClient.post('/scoring/signal', {
      interaction_id: interactionId,
      dimension,
      signal_name: signalName,
      score,
      framework_version: '1.0.0',
    }),

  getDimensionScore: (interactionId, dimension) =>
    apiClient.get(`/scoring/dimension/${interactionId}/${dimension}`),

  getOverallScore: (interactionId) =>
    apiClient.get(`/scoring/overall/${interactionId}`),

  completeDimension: (interactionId, dimension, notes, probesUsed, reframesDeployed) =>
    apiClient.post('/scoring/dimension/complete', {
      interaction_id: interactionId,
      dimension,
      notes,
      probes_used: probesUsed,
      reframes_deployed: reframesDeployed,
    }),
}

// ─── Summaries ────────────────────────────────────────────────────────────────
export const summaryAPI = {
  generate: (interactionId) =>
    apiClient.post(`/summaries/generate/${interactionId}`),

  get: (interactionId) =>
    apiClient.get(`/summaries/${interactionId}`),

  pushToErp: (summaryId) =>
    apiClient.post(`/summaries/${summaryId}/push-erp`),

  exportPdf: (summaryId) =>
    apiClient.get(`/summaries/${summaryId}/pdf`, { responseType: 'blob' }),
}

export default apiClient
