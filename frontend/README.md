# Blenko Discovery System — Frontend

Sprint 1 implementation. React 18 + Zustand + Tailwind CSS + Vite.

## Quick Start

```bash
npm install
npm run dev
# App runs at http://localhost:3000
```

## Dev Mode (No Backend)

The app runs fully without a backend in Sprint 1:

1. Navigate to `http://localhost:3000`
2. Click **"Continue without login (dev)"** on the login page
3. Click **"+ New Session"** on the dashboard
4. Complete the Layer Zero form and click **"Begin Discovery Session →"**
   - If the backend is not running, the app will show a warning and proceed in offline mode
5. Use the Discovery Flow screen — all signal scoring, score calculations, and dimension navigation work locally

## Architecture

```
src/
├── utils/framework.js          # ALL framework content (questions, signals, probes, reframes)
│                               # Future: fetched from backend by framework_version
├── store/sessionStore.js       # Zustand store — full session state
├── api/client.js               # Axios client — all backend endpoints
├── hooks/
│   ├── useAutoSave.js          # Debounced auto-save on every field change
│   └── useScoring.js          # Signal scoring with optimistic updates + backend sync
├── components/
│   ├── shared/
│   │   ├── Button.jsx
│   │   ├── RadioGroup.jsx
│   │   └── FormField.jsx
│   └── DiscoveryFlow/
│       ├── DimensionShell.jsx  # Persistent tab structure (same layout for all 4 dimensions)
│       ├── ScoreTracker.jsx    # Right sidebar — real-time score display
│       ├── SignalScoring.jsx   # Signal 0/1/2 panel — always visible
│       ├── SystemTrigger.jsx   # Amber alert on tier threshold
│       ├── OpeningQuestion.jsx # Tab: opening question + notes
│       ├── ProbesPanel.jsx     # Tab: probe cards with Mark Used
│       ├── ReframesPanel.jsx   # Tab: reframe statements
│       └── NotesPanel.jsx      # Tab: free-form notes with type + pin
└── pages/
    ├── Login.jsx
    ├── Dashboard.jsx           # Session cards + completed table
    ├── SessionSetup.jsx        # Layer Zero form (full)
    └── DiscoveryFlow.jsx       # Main discovery screen with top bar + dimension nav
```

## Key Design Decisions

### Performance
- **Optimistic updates**: Signal scoring updates local Zustand state immediately (~16ms), then syncs with backend asynchronously. The 100ms requirement is met even without backend.
- **Debounced auto-save**: Field changes trigger auto-save after 800ms of inactivity. No save button.
- **Session persistence**: Full Zustand state is persisted to localStorage — page refresh never loses data.

### Framework Content
- All questions, probes, signals, reframes, and triggers are in `src/utils/framework.js`
- Every piece of content carries a `FRAMEWORK_VERSION = '1.0.0'` reference
- Structured so backend can serve this content in future sprints — just swap `import` for API call

### Scoring
- Local calculation in `useScoring.js` for instant feedback
- Backend sync is non-blocking — failures are logged but don't block the UI
- `getDimensionTier()` and `getQualificationGrade()` utilities handle all tier logic

### Offline Mode
- When backend is unavailable, session creation falls through to a local ID
- All scoring, dimension navigation, and note-taking work locally
- Auto-save shows error toast but data is safe in localStorage

## Environment Variables

```env
VITE_API_URL=/api           # Backend API base URL (proxied via Vite dev server)
```

## Sprint 2 Additions (Planned)
- Persona Detection module + PersonaCard component
- Backend-driven framework content (replaces framework.js)
- Dimension 2, 3, 4 content auto-loaded from DB
- Multi-stakeholder handling

## Sprint 3 Additions (Planned)
- Qualification Summary generation
- PDF export
- Full Dashboard with real session data from API
