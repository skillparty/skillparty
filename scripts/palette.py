"""Shared visual system for all profile SVGs — one terminal, one palette."""

# Base surfaces
BG = "#0A0E14"          # card background
BG_TITLEBAR = "#0D1420"  # terminal title bar
BORDER = "#1F2A3A"       # card border
TRACK = "#1B2838"        # progress bar track

# Accents (disciplined: cyan primary, matrix green secondary, purple sparse)
CYAN = "#00FFFF"
GREEN = "#00FF41"
GREEN_SOFT = "#39D353"   # GitHub contribution green
PURPLE = "#A855F7"
TEXT = "#E6EDF3"         # primary text
MUTED = "#64748B"        # secondary text
DIM = "#475569"          # tertiary text
WARN = "#F97316"         # simulated-data warning only

MONO = "ui-monospace,SFMono-Regular,Menlo,monospace"

GLOW_FILTERS = '''    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowSoft">
      <feGaussianBlur stdDeviation="0.8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>'''


def titlebar(width, title):
    """Terminal window chrome: traffic lights + centered session title."""
    return f'''  <path d="M0 12 Q0 0 12 0 H{width - 12} Q{width} 0 {width} 12 V32 H0 Z" fill="{BG_TITLEBAR}"/>
  <circle cx="22" cy="16" r="5" fill="#FF5F56" opacity="0.75"/>
  <circle cx="42" cy="16" r="5" fill="#FFBD2E" opacity="0.75"/>
  <circle cx="62" cy="16" r="5" fill="#27C93F" opacity="0.75"/>
  <text x="{width // 2}" y="20" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{title}</text>'''
