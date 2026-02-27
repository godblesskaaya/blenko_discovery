// src/components/DiscoveryFlow/NotesPanel.jsx
import React, { useState } from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { useAutoSave } from '../../hooks/useAutoSave'

const NOTE_TYPES = [
  { value: 'observation', label: 'Observation' },
  { value: 'quote', label: 'Direct Quote' },
  { value: 'objection', label: 'Objection' },
  { value: 'opportunity', label: 'Opportunity' },
  { value: 'risk', label: 'Risk' },
  { value: 'competitive_intel', label: 'Competitive Intel' },
  { value: 'other', label: 'Other' },
]

const NOTE_TYPE_COLORS = {
  observation: 'bg-blue-light text-blue-primary border-blue-mid',
  quote: 'bg-purple-50 text-purple-700 border-purple-200',
  objection: 'bg-red-warn-bg text-red-warn border-red-200',
  opportunity: 'bg-green-signal-bg text-green-signal border-green-200',
  risk: 'bg-amber-trigger-bg text-amber-700 border-amber-200',
  competitive_intel: 'bg-slate-subtle text-ink border-slate-border',
  other: 'bg-slate-subtle text-ink-muted border-slate-border',
}

export default function NotesPanel({ dimensionKey }) {
  const [noteContent, setNoteContent] = useState('')
  const [noteType, setNoteType] = useState('observation')
  const [isPinned, setIsPinned] = useState(false)
  const [savedNotes, setSavedNotes] = useState([])
  const { triggerAutoSave } = useAutoSave()

  const handleSaveNote = () => {
    if (!noteContent.trim()) return
    const note = {
      id: crypto.randomUUID(),
      content: noteContent.trim(),
      type: noteType,
      pinned: isPinned,
      createdAt: new Date().toISOString(),
    }
    setSavedNotes((prev) => [note, ...prev])
    triggerAutoSave({ note: { dimension: dimensionKey, ...note } })
    setNoteContent('')
    setIsPinned(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSaveNote()
    }
  }

  return (
    <div>
      {/* Note composer */}
      <div className="card p-4 mb-4">
        <div className="flex gap-2 mb-3 flex-wrap">
          {NOTE_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => setNoteType(t.value)}
              className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-all ${
                noteType === t.value
                  ? NOTE_TYPE_COLORS[t.value] || 'bg-blue-light text-blue-primary border-blue-mid'
                  : 'bg-white text-ink-muted border-slate-border hover:border-ink-muted'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <textarea
          className="form-input h-20 resize-none mb-3"
          value={noteContent}
          onChange={(e) => setNoteContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            noteType === 'quote'
              ? 'Capture their exact words...'
              : noteType === 'objection'
              ? 'What objection did they raise?'
              : 'Note your observation...'
          }
        />

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-xs text-ink-muted cursor-pointer">
            <input
              type="checkbox"
              checked={isPinned}
              onChange={(e) => setIsPinned(e.target.checked)}
              className="rounded"
            />
            Pin (appears at top of all Briefs)
          </label>
          <div className="flex items-center gap-2">
            <span className="text-xs text-ink-muted">⌘↵ to save</span>
            <button
              onClick={handleSaveNote}
              disabled={!noteContent.trim()}
              className="btn-primary text-xs px-3 py-1.5"
            >
              Save Note
            </button>
          </div>
        </div>
      </div>

      {/* Saved notes */}
      {savedNotes.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-ink-muted uppercase tracking-wider">
            Session Notes ({savedNotes.length})
          </h4>
          {savedNotes.map((note) => {
            const typeColor = NOTE_TYPE_COLORS[note.type] || NOTE_TYPE_COLORS.other
            return (
              <div
                key={note.id}
                className={`border rounded-lg p-3 ${typeColor}`}
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    {note.pinned && <span className="text-xs">📌</span>}
                    <span className="text-xs font-semibold uppercase tracking-wide opacity-70">
                      {NOTE_TYPES.find((t) => t.value === note.type)?.label}
                    </span>
                  </div>
                  <span className="text-xs opacity-50">
                    {new Date(note.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="text-sm leading-relaxed">{note.content}</p>
              </div>
            )
          })}
        </div>
      )}

      {savedNotes.length === 0 && (
        <p className="text-xs text-ink-muted text-center py-4">
          No notes yet — capture key observations, quotes, and objections as you go.
        </p>
      )}
    </div>
  )
}
