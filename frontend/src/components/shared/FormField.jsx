// src/components/shared/FormField.jsx
import React from 'react'

export function FormField({ label, required, error, children, hint }) {
  return (
    <div>
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="text-red-warn ml-0.5">*</span>}
        </label>
      )}
      {children}
      {hint && !error && <p className="text-xs text-ink-muted mt-1">{hint}</p>}
      {error && <p className="text-xs text-red-warn mt-1">{error}</p>}
    </div>
  )
}
