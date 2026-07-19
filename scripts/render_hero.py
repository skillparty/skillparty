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


BOOT_LINES = [
    ("[  OK  ]", "mounting /dev/creativity"),
    ("[  OK  ]", "starting flutter.service"),
    ("[  OK  ]", "npm run dev --turbo"),
    ("[ BOOT ]", "initializing skillparty..."),
]


def _boot_sequence(left):
    """Fast boot log that flashes before the logo, then fades out."""
    out = []
    for i, (tag, msg) in enumerate(BOOT_LINES):
        y = 78 + i * 18
        delay = round(0.1 + i * 0.22, 2)
        out.append(
            f'    <text x="{left}" y="{y}" font-family="{MONO}" font-size="12" opacity="0">'
            f'<tspan fill="{GREEN}">{tag}</tspan><tspan fill="{MUTED}"> {msg}</tspan>'
            f'<animate attributeName="opacity" values="0;0.9" dur="0.06s" begin="{delay}s" fill="freeze"/>'
            f"</text>"
        )
    return (
        f'  <g>\n' + "\n".join(out) + "\n"
        f'    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.82;1" dur="1.7s" begin="0s" fill="freeze"/>\n'
        f"  </g>"
    )


def _matrix_rain(width, height):
    """Faint katakana rain behind the logo — echoes the singularity section."""
    chars = "01スキルパーティコード"
    cols = [(60, 5.2), (150, 4.1), (240, 6.0), (960, 4.6), (1050, 5.5), (1140, 4.3)]
    out = []
    for i, (x, dur) in enumerate(cols):
        ch = chars[i % len(chars)]
        op = round(0.05 + (i % 3) * 0.03, 2)
        out.append(
            f'    <text x="{x}" font-family="{MONO}" font-size="12" fill="{GREEN}" opacity="{op}">{ch}'
            f'<animate attributeName="y" values="30;{height - 30}" dur="{dur}s" repeatCount="indefinite"/>'
            f"</text>"
        )
    return "\n".join(out)


def generate_hero_svg(user):
    W, H = 1200, 300
    rows = _ascii_rows("SKILLPARTY")

    ascii_lines = []
    ascii_y = 68
    line_h = 17
    for idx, row in enumerate(rows):
        y = ascii_y + idx * line_h
        delay = round(1.7 + idx * 0.12, 2)
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
    cmd1, t1 = _typed_tspans("whoami", 2.9)
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
    <pattern id="crt" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1.5" fill="#000000" opacity="0.14"/>
    </pattern>
    <filter id="rgbGlitch">
      <feOffset in="SourceGraphic" dx="0" dy="0" result="r">
        <animate attributeName="dx" values="0;0;3;-2;1;0;0" keyTimes="0;0.9;0.92;0.94;0.96;0.98;1" dur="7s" repeatCount="indefinite"/>
      </feOffset>
      <feOffset in="SourceGraphic" dx="0" dy="0" result="b">
        <animate attributeName="dx" values="0;0;-3;2;-1;0;0" keyTimes="0;0.9;0.92;0.94;0.96;0.98;1" dur="7s" repeatCount="indefinite"/>
      </feOffset>
      <feColorMatrix in="r" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="red"/>
      <feColorMatrix in="b" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="blue"/>
      <feBlend in="red" in2="blue" mode="screen" result="split"/>
      <feBlend in="SourceGraphic" in2="split" mode="screen"/>
    </filter>
{GLOW_FILTERS}
  </defs>

  <rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
{titlebar(W, f"alejandro@{user}: ~/profile — bash")}

  <!-- matrix rain, behind everything -->
  <g filter="url(#glowSoft)">
{_matrix_rain(W, H)}
  </g>

  <!-- boot sequence, flashes then fades -->
{_boot_sequence(300)}

  <!-- ASCII name with periodic RGB-split glitch -->
  <g filter="url(#rgbGlitch)">
{ascii_svg}
  </g>

  <!-- typed session -->
  <text x="{LEFT}" y="192" font-family="{MONO}" font-size="13" fill="{GREEN}" opacity="0">$ <tspan fill="{TEXT}">{cmd1}</tspan><animate attributeName="opacity" values="0;0.9" dur="0.05s" begin="2.85s" fill="freeze"/></text>
  <text x="{LEFT}" y="214" font-family="{MONO}" font-size="13" fill="{TEXT}" opacity="0.92">{out1}</text>
  <text x="{LEFT}" y="238" font-family="{MONO}" font-size="13" fill="{GREEN}" opacity="0">$ <tspan fill="{TEXT}">{cmd2}</tspan><animate attributeName="opacity" values="0;0.9" dur="0.05s" begin="{t2 + 0.3}s" fill="freeze"/></text>
  <text x="{LEFT}" y="260" font-family="{MONO}" font-size="13" fill="{CYAN}" opacity="0.9" filter="url(#glowSoft)">{out2}</text>

  <!-- blinking cursor after last output -->
  <rect x="{LEFT + 468}" y="249" width="8" height="14" fill="{CYAN}" opacity="0">
    <animate attributeName="opacity" values="0;0.85;0.85;0;0" dur="1.1s" begin="{t4}s" repeatCount="indefinite"/>
  </rect>

  <!-- scanline sweep -->
  <rect x="1" y="34" width="{W - 2}" height="3" fill="url(#heroScan)" opacity="0.35">
    <animate attributeName="y" values="34;{H - 6};34" dur="9s" repeatCount="indefinite"/>
  </rect>

  <!-- CRT texture over the whole tube -->
  <rect x="1" y="33" width="{W - 2}" height="{H - 34}" fill="url(#crt)" opacity="0.5"/>

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
