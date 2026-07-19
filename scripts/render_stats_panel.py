"""Stats panel SVG: languages + live GitHub stats in one terminal card.

Replaces cyber-langs.svg and the external github-readme-stats card so every
surface on the profile shares the same visual system.
"""

from palette import (
    BG, BORDER, TRACK, CYAN, GREEN, GREEN_SOFT, TEXT, MUTED, DIM, WARN, MONO,
    GLOW_FILTERS, titlebar,
)

BAR_W = 440


def _lang_bars(langs):
    out = []
    y = 96
    for idx, lang in enumerate(langs):
        width = round((lang["percent"] / 100) * BAR_W, 1)
        dot = lang["color"] or CYAN
        begin = round(0.15 + idx * 0.14, 2)
        dur = round(1.2 + idx * 0.2, 2)
        out.append(f'''  <g transform="translate(70, {y})">
    <circle cx="4" cy="-4" r="3.5" fill="{dot}"/>
    <text x="16" y="0" font-family="{MONO}" font-size="11" fill="{TEXT}" opacity="0.92">{lang["name"]}</text>
    <text x="{BAR_W}" y="0" text-anchor="end" font-family="{MONO}" font-size="11" fill="{CYAN}" opacity="0.9">{lang["percent"]:.1f}%</text>
    <rect x="0" y="8" width="{BAR_W}" height="5" rx="2.5" fill="{TRACK}"/>
    <rect x="0" y="8" width="{width}" height="5" rx="2.5" fill="url(#barFill)" filter="url(#glowSoft)">
      <animate attributeName="width" from="0" to="{width}" dur="{dur}s" begin="{begin}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.16, 1, 0.3, 1"/>
    </rect>
    <rect x="0" y="8" width="44" height="5" rx="2.5" fill="url(#barShimmer)" opacity="0.3">
      <animate attributeName="x" values="0;{BAR_W - 44};0" dur="{round(5.0 + idx * 0.5, 1)}s" begin="{begin}s" repeatCount="indefinite"/>
    </rect>
  </g>''')
        y += 34
    return "\n".join(out)


def _stat_block(x, y, value, label, accent, begin):
    return f'''  <g transform="translate({x}, {y})" opacity="0">
    <animate attributeName="opacity" values="0;1" dur="0.5s" begin="{begin}s" fill="freeze"/>
    <text x="0" y="0" font-family="{MONO}" font-size="10" fill="{MUTED}" letter-spacing="1.5">{label}</text>
    <text x="0" y="34" font-family="{MONO}" font-size="28" fill="{accent}" filter="url(#glow)">{value}</text>
  </g>'''


def generate_stats_panel(langs, streak_info, profile, data_ok):
    """profile: dict with stars, repos, followers, since. data_ok: real data?"""
    W, H = 1200, 280

    stats = [
        (f'{streak_info["total"]:,}', "COMMITS · 1Y", CYAN),
        (f'{streak_info["current"]}d', "CURRENT STREAK", GREEN_SOFT),
        (f'{streak_info["longest"]}d', "LONGEST STREAK", GREEN_SOFT),
        (f'★ {profile["stars"]}', "STARS EARNED", CYAN),
    ]
    blocks = []
    positions = [(700, 106), (960, 106), (700, 186), (960, 186)]
    for i, ((val, label, accent), (x, y)) in enumerate(zip(stats, positions)):
        blocks.append(_stat_block(x, y, val, label, accent, round(0.4 + i * 0.18, 2)))
    blocks_svg = "\n".join(blocks)

    if data_ok:
        source_mark = "  <!-- data: REAL_API -->"
    else:
        source_mark = (
            f'  <text x="{W - 24}" y="58" text-anchor="end" font-family="{MONO}" '
            f'font-size="10" fill="{WARN}" opacity="0.9">⚠ SIMULATED DATA</text>'
        )

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="barFill" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{GREEN_SOFT}"/>
      <stop offset="100%" stop-color="{CYAN}"/>
    </linearGradient>
    <linearGradient id="barShimmer" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
{GLOW_FILTERS}
  </defs>

  <rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
{titlebar(W, "stats --live")}
{source_mark}

  <text x="70" y="62" font-family="{MONO}" font-size="12" fill="{GREEN}" opacity="0.9">$ <tspan fill="{TEXT}">git shortlog --languages</tspan></text>
{_lang_bars(langs)}

  <line x1="620" y1="52" x2="620" y2="{H - 40}" stroke="{BORDER}" stroke-width="1"/>

  <text x="700" y="62" font-family="{MONO}" font-size="12" fill="{GREEN}" opacity="0.9">$ <tspan fill="{TEXT}">./uptime --github</tspan></text>
{blocks_svg}

  <line x1="20" y1="{H - 26}" x2="{W - 20}" y2="{H - 26}" stroke="{BORDER}" stroke-width="1"/>
  <text x="30" y="{H - 10}" font-family="{MONO}" font-size="10" fill="{MUTED}">repos: {profile["repos"]} · followers: {profile["followers"]} · shipping since {profile["since"]}</text>
  <circle cx="{W - 76}" cy="{H - 14}" r="3.5" fill="{GREEN_SOFT}" filter="url(#glow)">
    <animate attributeName="opacity" values="1;0.35;1" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <text x="{W - 66}" y="{H - 10}" font-family="{MONO}" font-size="10" fill="{GREEN_SOFT}" opacity="0.8">LIVE</text>
</svg>'''

    with open("dist/stats-panel.svg", "w") as f:
        f.write(svg)
