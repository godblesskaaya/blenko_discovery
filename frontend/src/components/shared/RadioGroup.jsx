// src/components/shared/RadioGroup.jsx
import React from 'react'

/**
 * RadioGroup
 * Used throughout Layer Zero for Business Type, Size Tier, etc.
 * Renders as button-style radio options.
 */
export function RadioGroup({ label, options, value, onChange, required = false, error, columns = 'auto' }) {
  const gridClass =
    columns === 'auto'
      ? 'flex flex-wrap gap-2'
      : `grid gap-2 grid-cols-${columns}`

  return (
    <div>
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="text-red-warn ml-0.5">*</span>}
        </label>
      )}
      <div className={gridClass}>
        {options.map((opt) => {
          const optValue = typeof opt === 'string' ? opt : opt.value
          const optLabel = typeof opt === 'string' ? opt : opt.label
          const optDesc = typeof opt === 'object' ? opt.description : null
          const isActive = value === optValue

          return (
            <button
              key={optValue}
              type="button"
              onClick={() => onChange(optValue)}
              className={`radio-option ${isActive ? 'radio-option-active' : 'radio-option-inactive'}`}
            >
              {isActive && (
                <span className="w-2 h-2 rounded-full bg-blue-primary flex-shrink-0" />
              )}
              <span>
                <span className="block">{optLabel}</span>
                {optDesc && (
                  <span className="block text-xs font-normal opacity-70 mt-0.5">{optDesc}</span>
                )}
              </span>
            </button>
          )
        })}
      </div>
      {error && <p className="text-red-warn text-xs mt-1.5">{error}</p>}
    </div>
  )
}
