// src/pages/SessionSetup.jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useSessionStore } from '../store/sessionStore'
import { sessionAPI } from '../api/client'
import { RadioGroup } from '../components/shared/RadioGroup'
import { FormField } from '../components/shared/FormField'
import { Button } from '../components/shared/Button'
import {
  BUSINESS_TYPES,
  SIZE_TIERS,
  GROWTH_STAGES,
  GEOGRAPHIC_SCOPES,
  VENDOR_STATUSES,
  GROWTH_AMBITIONS,
  TRIGGER_CATEGORIES,
} from '../utils/framework'

export default function SessionSetup() {
  const navigate = useNavigate()
  const {
    prospect,
    businessProfile,
    updateProspect,
    updateBusinessProfile,
    setSessionId,
    setInteractionId,
    setProspectId,
    setSessionStatus,
  } = useSessionStore()

  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const validate = () => {
    const e = {}
    if (!prospect.contactName?.trim()) e.contactName = 'Contact name is required'
    if (!prospect.companyName?.trim()) e.companyName = 'Company name is required'
    if (!prospect.businessType) e.businessType = 'Select a business type'
    if (!prospect.sizeTier) e.sizeTier = 'Select a size tier'
    if (!prospect.growthStage) e.growthStage = 'Select a growth stage'
    if (!prospect.geographicScope) e.geographicScope = 'Select geographic scope'
    if (!prospect.vendorStatus) e.vendorStatus = 'Select vendor status'
    if (!prospect.growthAmbition) e.growthAmbition = 'Select growth ambition'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async () => {
    if (!validate()) {
      toast.error('Please complete all required fields')
      return
    }

    setLoading(true)
    try {
      const { data } = await sessionAPI.create(prospect, businessProfile)
      setSessionId(data.session_id)
      setInteractionId(data.interaction_id)
      setProspectId(data.prospect_id)
      setSessionStatus('discovery')
      navigate('/discovery')
    } catch (err) {
      // In dev mode without backend: proceed anyway
      if (err.code === 'ERR_NETWORK' || err.response?.status === 404) {
        toast('Running in offline mode — proceeding without backend', { icon: '⚠️' })
        setSessionId(`local-${Date.now()}`)
        setSessionStatus('discovery')
        navigate('/discovery')
      } else {
        toast.error('Failed to create session: ' + (err.response?.data?.message || err.message))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-surface">
      {/* Header */}
      <header className="bg-white border-b border-slate-border px-8 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-ink-muted hover:text-ink transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="text-ink-muted text-sm">/</span>
          <span className="font-display font-semibold text-ink">New Discovery Session</span>
        </div>
        <div className="text-sm text-ink-muted">Layer Zero — Business Profile</div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10">
        {/* Section header */}
        <div className="mb-8">
          <h1 className="font-display font-bold text-2xl text-ink">Business Profile</h1>
          <p className="text-ink-muted mt-2 text-sm leading-relaxed">
            Capture context before any scoring begins. This profile calibrates the discovery flow for this specific prospect.
          </p>
        </div>

        {/* ── Contact Info ──────────────────────────────────────────────── */}
        <Section title="Contact Information">
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Company Name" required error={errors.companyName}>
              <input
                className="form-input"
                value={prospect.companyName}
                onChange={(e) => { updateProspect('companyName', e.target.value); clearError('companyName') }}
                placeholder="Hartwell Constructions"
              />
            </FormField>
            <FormField label="Contact Name" required error={errors.contactName}>
              <input
                className="form-input"
                value={prospect.contactName}
                onChange={(e) => { updateProspect('contactName', e.target.value); clearError('contactName') }}
                placeholder="Mike Hartwell"
              />
            </FormField>
            <FormField label="Role / Title">
              <input
                className="form-input"
                value={prospect.contactRole}
                onChange={(e) => updateProspect('contactRole', e.target.value)}
                placeholder="Managing Director"
              />
            </FormField>
            <FormField label="Email">
              <input
                type="email"
                className="form-input"
                value={prospect.contactEmail}
                onChange={(e) => updateProspect('contactEmail', e.target.value)}
                placeholder="mike@hartwell.com.au"
              />
            </FormField>
            <FormField label="Phone">
              <input
                type="tel"
                className="form-input"
                value={prospect.contactPhone}
                onChange={(e) => updateProspect('contactPhone', e.target.value)}
                placeholder="+61 4xx xxx xxx"
              />
            </FormField>
          </div>
        </Section>

        {/* ── Business Profile ──────────────────────────────────────────── */}
        <Section title="Business Profile">
          <div className="space-y-6">
            <RadioGroup
              label="Business Type"
              required
              options={BUSINESS_TYPES}
              value={prospect.businessType}
              onChange={(v) => { updateProspect('businessType', v); clearError('businessType') }}
              error={errors.businessType}
            />
            <RadioGroup
              label="Size Tier"
              required
              options={SIZE_TIERS}
              value={prospect.sizeTier}
              onChange={(v) => { updateProspect('sizeTier', v); clearError('sizeTier') }}
              error={errors.sizeTier}
            />
            <RadioGroup
              label="Growth Stage"
              required
              options={GROWTH_STAGES}
              value={prospect.growthStage}
              onChange={(v) => { updateProspect('growthStage', v); clearError('growthStage') }}
              error={errors.growthStage}
            />
            <RadioGroup
              label="Geographic Scope"
              required
              options={GEOGRAPHIC_SCOPES}
              value={prospect.geographicScope}
              onChange={(v) => { updateProspect('geographicScope', v); clearError('geographicScope') }}
              error={errors.geographicScope}
            />
            <RadioGroup
              label="Current Vendor Status"
              required
              options={VENDOR_STATUSES}
              value={prospect.vendorStatus}
              onChange={(v) => { updateProspect('vendorStatus', v); clearError('vendorStatus') }}
              error={errors.vendorStatus}
            />
            <RadioGroup
              label="Growth Ambition"
              required
              options={GROWTH_AMBITIONS}
              value={prospect.growthAmbition}
              onChange={(v) => { updateProspect('growthAmbition', v); clearError('growthAmbition') }}
              error={errors.growthAmbition}
            />
          </div>
        </Section>

        {/* ── Trigger Event ─────────────────────────────────────────────── */}
        <Section title="What Triggered This Conversation?">
          <p className="text-sm text-ink-muted mb-4">
            The most direct path to urgency. What brought them to this conversation?
          </p>
          <FormField label="In Their Own Words">
            <textarea
              className="form-input h-24 resize-none"
              value={businessProfile.triggerEvent}
              onChange={(e) => updateBusinessProfile('triggerEvent', e.target.value)}
              placeholder="e.g. We just won a contract with a national retailer and our current branding doesn't reflect where we're going..."
            />
          </FormField>
          <div className="mt-4">
            <RadioGroup
              label="Trigger Category"
              options={TRIGGER_CATEGORIES}
              value={businessProfile.triggerCategory}
              onChange={(v) => updateBusinessProfile('triggerCategory', v)}
            />
          </div>
        </Section>

        {/* ── CTA ───────────────────────────────────────────────────────── */}
        <div className="mt-8 flex items-center justify-between">
          <p className="text-sm text-ink-muted">
            <span className="text-red-warn">*</span> Required fields
          </p>
          <Button onClick={handleSubmit} loading={loading} size="lg">
            Begin Discovery Session →
          </Button>
        </div>
      </main>
    </div>
  )

  function clearError(field) {
    if (errors[field]) setErrors((e) => { const ne = { ...e }; delete ne[field]; return ne })
  }
}

function Section({ title, children }) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-5">
        <h2 className="font-display font-semibold text-base text-ink">{title}</h2>
        <div className="flex-1 h-px bg-slate-border" />
      </div>
      {children}
    </div>
  )
}
