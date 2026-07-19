"""Hero SVG: one terminal window — ASCII name, typed identity, live status bar.

Replaces the old ascii-art.svg + header-typing.svg pair.
"""

from datetime import datetime

from palette import (
    BG, BORDER, CYAN, GREEN, GREEN_SOFT, PURPLE, TEXT, MUTED, DIM, MONO,
    GLOW_FILTERS, titlebar,
)

# ANSI-Shadow figlet letters, 6 rows each. Assembled programmatically so the
# rows stay perfectly aligned (77 chars total).
_LETTERS = {
    "S": ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"],
    "K": ["██╗  ██╗", "██║ ██╔╝", "█████╔╝ ", "██╔═██╗ ", "██║  ██╗", "╚═╝  ╚═╝"],
    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    "L": ["██╗     ", "██║     ", "██║     ", "██║     ", "███████╗", "╚══════╝"],
    "P": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔═══╝ ", "██║     ", "╚═╝     "],
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
    "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
    "Y": ["██╗   ██╗", "╚██╗ ██╔╝", " ╚████╔╝ ", "  ╚██╔╝  ", "   ██║   ", "   ╚═╝   "],
}


def _ascii_rows(word):
    return ["".join(_LETTERS[ch][row] for ch in word) for row in range(6)]


def _typed_tspans(line, begin, per_char=0.045):
    """Character-by-character reveal, terminal-typing style."""
    out = []
    for j, ch in enumerate(line):
        delay = round(begin + j * per_char, 3)
        escaped = ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if ch == " ":
            escaped = "&#160;"
        out.append(
            f'<tspan opacity="0">{escaped}'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.04s" begin="{delay}s" fill="freeze"/>'
            f"</tspan>"
        )
    end = round(begin + len(line) * per_char, 3)
    return "".join(out), end


def generate_hero_svg(user):
    W, H = 1200, 300
    rows = _ascii_rows("SKILLPARTY")

    ascii_lines = []
    ascii_y = 68
    line_h = 17
    for idx, row in enumerate(rows):
        y = ascii_y + idx * line_h
        delay = round(0.12 + idx * 0.12, 2)
        ascii_lines.append(
            f'  <text x="600" y="{y}" text-anchor="middle" xml:space="preserve" '
            f'font-family="{MONO}" font-size="13" fill="url(#nameGradient)" '
            f'opacity="0" filter="url(#glowSoft)">{row}'
            f'<animate attributeName="opacity" values="0;0.95" dur="0.35s" begin="{delay}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0.95;0.78;0.95" dur="7s" begin="{delay + 1}s" repeatCount="indefinite"/>'
            f"</text>"
        )
    ascii_svg = "\n".join(ascii_lines)

    # Terminal session under the name
    LEFT = 300
    cmd1, t1 = _typed_tspans("whoami", 1.3)
    out1, t2 = _typed_tspans("Jose Alejandro Rollano — Freelance Software Developer", t1 + 0.25)
    cmd2, t3 = _typed_tspans("cat ~/stack.txt", t2 + 0.35)
    out2, t4 = _typed_tspans("Next.js · React · TypeScript · Flutter · Python · Firebase", t3 + 0.25)

    timestamp = datetime.now().strftime("%Y-%m-%d")

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="nameGradient" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{GREEN}"/>
      <stop offset="50%" stop-color="{CYAN}"/>
      <stop offset="100%" stop-color="{PURPLE}"/>
    </linearGradient>
    <linearGradient id="heroScan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{CYAN}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>
{GLOW_FILTERS}
  </defs>

  <rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
{titlebar(W, f"alejandro@{user}: ~/profile — bash")}

{ascii_svg}

  <!-- typed session -->
  <text x="{LEFT}" y="192" font-family="{MONO}" font-size="13" fill="{GREEN}" opacity="0.9">$ <tspan fill="{TEXT}">{cmd1}</tspan></text>
  <text x="{LEFT}" y="214" font-family="{MONO}" font-size="13" fill="{TEXT}" opacity="0.92">{out1}</text>
  <text x="{LEFT}" y="238" font-family="{MONO}" font-size="13" fill="{GREEN}" opacity="0.9">$ <tspan fill="{TEXT}">{cmd2}</tspan></text>
  <text x="{LEFT}" y="260" font-family="{MONO}" font-size="13" fill="{CYAN}" opacity="0.9" filter="url(#glowSoft)">{out2}</text>

  <!-- blinking cursor after last output -->
  <rect x="{LEFT + 468}" y="249" width="8" height="14" fill="{CYAN}" opacity="0">
    <animate attributeName="opacity" values="0;0.85;0.85;0;0" dur="1.1s" begin="{t4}s" repeatCount="indefinite"/>
  </rect>

  <!-- scanline sweep -->
  <rect x="1" y="34" width="{W - 2}" height="3" fill="url(#heroScan)" opacity="0.35">
    <animate attributeName="y" values="34;{H - 6};34" dur="9s" repeatCount="indefinite"/>
  </rect>

  <!-- status bar -->
  <line x1="20" y1="{H - 22}" x2="{W - 20}" y2="{H - 22}" stroke="{BORDER}" stroke-width="1"/>
  <circle cx="30" cy="{H - 11}" r="3.5" fill="{GREEN_SOFT}" filter="url(#glow)">
    <animate attributeName="opacity" values="1;0.35;1" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <text x="42" y="{H - 7}" font-family="{MONO}" font-size="10" fill="{MUTED}">ONLINE // Cochabamba, Bolivia (UTC-4)</text>
  <text x="{W - 20}" y="{H - 7}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{DIM}">{timestamp} // github.com/{user}</text>
</svg>'''

    with open("dist/hero.svg", "w") as f:
        f.write(svg)
