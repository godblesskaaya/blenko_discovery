// src/pages/Login.jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { authAPI } from '../api/client'
import { useSessionStore } from '../store/sessionStore'
import { Button } from '../components/shared/Button'

export default function Login() {
  const navigate = useNavigate()
  const setAuth = useSessionStore((s) => s.setAuth)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    if (!email || !password) return
    setLoading(true)
    try {
      const { data } = await authAPI.login(email, password)
      localStorage.setItem('blenko_access_token', data.access_token)
      localStorage.setItem('blenko_refresh_token', data.refresh_token)
      setAuth(data.access_token, data.user)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  // DEV: allow bypass without backend
  const devBypass = () => {
    setAuth('dev-token', { name: 'Dev Rep', role: 'rep' })
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-3 mb-2">
            <div className="w-8 h-8 bg-blue-primary rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h1 className="font-display font-bold text-2xl text-white">Blenko Discovery</h1>
          </div>
          <p className="text-ink-muted text-sm">Sales Intelligence System</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-elevated p-8">
          <h2 className="font-display font-semibold text-xl text-ink mb-6">Sign in</h2>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="form-label">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="form-input"
                placeholder="you@blenko.com"
                required
              />
            </div>
            <div>
              <label className="form-label">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder="••••••••"
                required
              />
            </div>
            <Button type="submit" fullWidth loading={loading} className="mt-2">
              Sign in
            </Button>
          </form>

          {/* Dev bypass — remove in production */}
          <div className="mt-6 pt-5 border-t border-slate-border">
            <p className="text-center text-xs text-ink-muted mb-3">Development mode</p>
            <button
              onClick={devBypass}
              className="w-full text-sm text-ink-muted border border-slate-border rounded-lg py-2 hover:bg-slate-subtle transition-all"
            >
              Continue without login (dev)
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
