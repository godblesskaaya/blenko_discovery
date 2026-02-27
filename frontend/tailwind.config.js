/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Bricolage Grotesque"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"DM Mono"', 'monospace'],
      },
      colors: {
        ink: {
          DEFAULT: '#0F1729',
          soft: '#1E2D4A',
          muted: '#3D5170',
        },
        slate: {
          surface: '#FAFAF9',
          border: '#E5E4E0',
          subtle: '#F2F1EE',
        },
        blue: {
          primary: '#1D4ED8',
          hover: '#1E40AF',
          light: '#EFF6FF',
          mid: '#BFDBFE',
        },
        amber: {
          trigger: '#F59E0B',
          'trigger-bg': '#FFFBEB',
          'trigger-border': '#FCD34D',
        },
        green: {
          signal: '#059669',
          'signal-bg': '#ECFDF5',
        },
        red: {
          warn: '#DC2626',
          'warn-bg': '#FEF2F2',
        },
        grade: {
          unqualified: '#6B7280',
          developing: '#D97706',
          qualified: '#059669',
          hot: '#7C3AED',
        },
      },
      boxShadow: {
        card: '0 1px 3px rgba(15,23,41,0.08), 0 1px 2px rgba(15,23,41,0.04)',
        elevated: '0 4px 12px rgba(15,23,41,0.10), 0 2px 4px rgba(15,23,41,0.06)',
        trigger: '0 0 0 3px rgba(245,158,11,0.25)',
      },
    },
  },
  plugins: [],
}
