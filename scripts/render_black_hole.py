"""Black hole contribution matrix SVG — the signature piece, moved verbatim
from update_animations.py with only the debug footer cleaned up."""

import random
from datetime import datetime

from palette import WARN


def generate_black_hole_svg(grid, streak_info, user, is_real=True):
    COLS, ROWS = 42, 7
    BLOCK, CELL = 14, 24
    GRID_X, GRID_Y = 100, 72
    W, H = 1200, 340
    BH_Y = 151
    BH_X = 620
    DUR = 20
    
    COLORS = ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"]

    # Calculate max distance from ANY cell to the BH for normalization
    corners = [
        (GRID_X + BLOCK // 2, GRID_Y + BLOCK // 2),
        (GRID_X + (COLS - 1) * CELL + BLOCK // 2, GRID_Y + BLOCK // 2),
        (GRID_X + BLOCK // 2, GRID_Y + (ROWS - 1) * CELL + BLOCK // 2),
        (GRID_X + (COLS - 1) * CELL + BLOCK // 2, GRID_Y + (ROWS - 1) * CELL + BLOCK // 2),
    ]
    max_dist = max(((BH_X - cx) ** 2 + (BH_Y - cy) ** 2) ** 0.5 for cx, cy in corners)

    def absorb_timing(cx, cy):
        dist = ((BH_X - cx) ** 2 + (BH_Y - cy) ** 2) ** 0.5
        normalized = min(1.0, dist / max_dist)
        start_t = round(0.08 + normalized * 0.55, 3)
        impact_t = round(min(0.92, start_t + 0.12), 3)
        return start_t, impact_t

    fx_random = random.Random(20260302)
    grid_lines = []
    absorb_end_t = 0.72
    for c in range(COLS):
      for r in range(ROWS):
        val = grid[c][r]
        x0 = GRID_X + c * CELL
        y0 = GRID_Y + r * CELL
        cx = x0 + BLOCK // 2
        cy = y0 + BLOCK // 2
        color = COLORS[val]

        start_t, impact_t = absorb_timing(cx, cy)
        lens_t = round(max(0.0, start_t - 0.035), 3)

        # Target position: center of BH minus half the shrunk size
        target_x = BH_X - 1
        target_y = BH_Y - 1
        shrunk = 2  # final size before disappearing

        if val == 0:
          grid_lines.append(f'    <rect x="{x0}" y="{y0}" width="{BLOCK}" height="{BLOCK}" rx="3" fill="{color}" opacity="0.28"/>')
          continue

        absorb_end_t = max(absorb_end_t, impact_t)

        # Use simple attribute animations (no additive transforms)
        grid_lines.append(f'    <rect x="{x0}" y="{y0}" width="{BLOCK}" height="{BLOCK}" rx="3" fill="{color}">')

        # Spiral infall: curved path toward the singularity (perpendicular
        # control point bends every trajectory in the same swirl direction).
        tx = target_x - x0
        ty = target_y - y0
        dist_c = max(1.0, (tx * tx + ty * ty) ** 0.5)
        swirl = min(90.0, dist_c * 0.32)
        qx = round(tx / 2 - (ty / dist_c) * swirl, 1)
        qy = round(ty / 2 + (tx / dist_c) * swirl, 1)
        grid_lines.append(
          f'      <animateMotion path="M0,0 Q{qx},{qy} {tx},{ty}"'
          f' keyPoints="0;0;1;1" keyTimes="0;{start_t};{impact_t};1"'
          f' calcMode="linear" dur="{DUR}s" begin="0s" repeatCount="indefinite"/>'
        )
        grid_lines.append(
          f'      <animate attributeName="width"'
          f' values="{BLOCK};{BLOCK};{shrunk};{shrunk}"'
          f' keyTimes="0;{start_t};{impact_t};1"'
          f' dur="{DUR}s" begin="0s" repeatCount="indefinite"/>'
        )
        grid_lines.append(
          f'      <animate attributeName="height"'
          f' values="{BLOCK};{BLOCK};{shrunk};{shrunk}"'
          f' keyTimes="0;{start_t};{impact_t};1"'
          f' dur="{DUR}s" begin="0s" repeatCount="indefinite"/>'
        )
        grid_lines.append(
          f'      <animate attributeName="opacity"'
          f' values="1;1;0.6;0"'
          f' keyTimes="0;{start_t};{round(start_t + (impact_t - start_t) * 0.7, 3)};{impact_t}"'
          f' dur="{DUR}s" begin="0s" repeatCount="indefinite"/>'
        )
        grid_lines.append(
          f'      <animate attributeName="fill"'
          f' values="{color};{color};#A855F7;#7C3AED"'
          f' keyTimes="0;{lens_t};{start_t};{impact_t}"'
          f' dur="{DUR}s" begin="0s" repeatCount="indefinite"/>'
        )

        grid_lines.append(f'    </rect>')

        # Particles trailing toward BH
        for p in range(1):
          p_offset_x = cx + fx_random.randint(-5, 5)
          p_offset_y = cy + fx_random.randint(-5, 5)
          particle_delay = round(start_t * DUR + p * 0.18, 2)
          p_color = "#A855F7" if p == 0 else "#00FFFF"
          p_size = 1.6 if p == 0 else 1.2
          grid_lines.append(
            f'    <circle cx="{p_offset_x}" cy="{p_offset_y}" r="{p_size}" fill="{p_color}" opacity="0">'
            f'      <animate attributeName="opacity" values="0;0.55;0.35;0" keyTimes="0;0.1;0.7;1"'
            f' dur="1.2s" begin="{particle_delay}s" repeatCount="indefinite"/>'
            f'      <animate attributeName="cx" values="{p_offset_x};{BH_X}" dur="1.5s"'
            f' begin="{particle_delay}s" repeatCount="indefinite"/>'
            f'      <animate attributeName="cy" values="{p_offset_y};{BH_Y}" dur="1.5s"'
            f' begin="{particle_delay}s" repeatCount="indefinite"/>'
            f'      <animate attributeName="r" values="{p_size};0.5;0" keyTimes="0;0.7;1"'
            f' dur="1.5s" begin="{particle_delay}s" repeatCount="indefinite"/>'
            f'    </circle>'
          )

    grid_svg = "\\n".join(grid_lines)

    # Matrix rain columns
    rain_chars = list("01スキルパーティマトリクスコード")
    rain_lines = []
    rain_cols = [
        (30, 4.2), (90, 3.6), (180, 5.1), (320, 3.3),
        (460, 4.7), (600, 3.8), (750, 4.4), (900, 3.5),
        (1020, 5.0), (1100, 3.9), (1160, 4.5),
    ]
    for i, (x, dur) in enumerate(rain_cols):
        ch1 = rain_chars[i % len(rain_chars)]
        ch2 = rain_chars[(i + 5) % len(rain_chars)]
        op1 = round(0.3 + (i % 4) * 0.1, 1)
        rain_lines.append(
            f'    <text x="{x}" fill="#00FF41" opacity="{op1}">'
            f'<tspan>{ch1}</tspan>'
            f'<animate attributeName="y" values="-20;360" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{op1};0.05" dur="{dur}s" repeatCount="indefinite"/>'
            f'</text>'
        )
        rain_lines.append(
            f'    <text x="{x}" fill="#00FF41" opacity="{round(op1*0.4,2)}">'
            f'<tspan>{ch2}</tspan>'
            f'<animate attributeName="y" values="-60;320" dur="{dur}s" repeatCount="indefinite"/>'
            f'</text>'
        )
    rain_svg = "\\n".join(rain_lines)

    # Tron background grid
    bg_lines = []
    for x in range(0, W + 1, 50):
        bg_lines.append(f'    <line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
    for y in range(0, H + 1, 50):
        bg_lines.append(f'    <line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    bg_grid_svg = "\\n".join(bg_lines)

    stars_lines = []
    for i in range(40):
      sx = fx_random.randint(8, W - 8)
      sy = fx_random.randint(8, H - 8)
      sr = round(fx_random.uniform(0.5, 1.3), 2)
      sop = round(fx_random.uniform(0.12, 0.36), 2)
      sdur = round(fx_random.uniform(3.8, 8.8), 1)
      sbegin = round(fx_random.uniform(0.0, 3.5), 2)
      stars_lines.append(
        f'    <circle cx="{sx}" cy="{sy}" r="{sr}" fill="#7DD3FC" opacity="{sop}" filter="url(#starGlow)">'
        f'<animate attributeName="opacity" values="{sop};{round(min(0.55, sop + 0.16), 2)};{sop}" dur="{sdur}s" begin="{sbegin}s" repeatCount="indefinite"/>'
        f'</circle>'
      )
    stars_svg = "\\n".join(stars_lines)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    absorb_end_t = round(min(0.95, absorb_end_t), 3)

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @media (prefers-color-scheme: light) {{
        .bg-color {{ fill: #0d1117; }} /* Enforcing dark theme for this SVG specifically */
      }}
    </style>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowStrong">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowHeavy">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="starGlow">
      <feGaussianBlur stdDeviation="1.1" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glitch">
      <feOffset in="SourceGraphic" dx="2" dy="0" result="r">
        <animate attributeName="dx" values="0;3;-2;0;1;-1;0" dur="0.3s" begin="4s" repeatCount="3"/>
      </feOffset>
      <feOffset in="SourceGraphic" dx="-2" dy="0" result="b">
        <animate attributeName="dx" values="0;-3;2;0;-1;1;0" dur="0.3s" begin="4s" repeatCount="3"/>
      </feOffset>
      <feColorMatrix in="r" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="red"/>
      <feColorMatrix in="b" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="blue"/>
      <feBlend in="red" in2="blue" mode="screen" result="glitched"/>
      <feBlend in="SourceGraphic" in2="glitched" mode="normal"/>
    </filter>
    <radialGradient id="bhGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#7C3AED" stop-opacity="0.6"/>
      <stop offset="40%" stop-color="#6D28D9" stop-opacity="0.3"/>
      <stop offset="70%" stop-color="#4C1D95" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#4C1D95" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="bhCore" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#000000"/>
      <stop offset="60%" stop-color="#030303"/>
      <stop offset="100%" stop-color="#0A0A0A"/>
    </radialGradient>
    <linearGradient id="accretion1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7C3AED"/>
      <stop offset="25%" stop-color="#00FFFF"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.9"/>
      <stop offset="75%" stop-color="#00FFFF"/>
      <stop offset="100%" stop-color="#7C3AED"/>
    </linearGradient>
    <linearGradient id="accretion2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00FFFF" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#A78BFA" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#00FFFF" stop-opacity="0.8"/>
    </linearGradient>
    <linearGradient id="jetUp" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="#E8FFFF" stop-opacity="0.9"/>
      <stop offset="35%" stop-color="#00FFFF" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="jetDown" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#E8FFFF" stop-opacity="0.9"/>
      <stop offset="35%" stop-color="#00FFFF" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="scanLine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#00FF41" stop-opacity="0"/>
      <stop offset="40%" stop-color="#00FF41" stop-opacity="0.12"/>
      <stop offset="50%" stop-color="#00FF41" stop-opacity="0.4"/>
      <stop offset="60%" stop-color="#00FF41" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#00FF41" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect width="{W}" height="{H}" rx="12" fill="#0A0A0A" class="bg-color"/>

  <!-- Tron background grid -->
  <g opacity="0.04" stroke="#00FF41" stroke-width="0.5">
{bg_grid_svg}
  </g>

  <g>
{stars_svg}
  </g>

  <!-- Matrix rain -->
  <g font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11" filter="url(#glow)">
{rain_svg}
  </g>

  <!-- Terminal header -->
  <g filter="url(#glitch)">
    <text x="24" y="28" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11" fill="#00FF41" opacity="0.8" filter="url(#glow)">
      root@{user}:~$ ./scan_contributions --mode=singularity --live
    </text>
    <text x="24" y="44" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10" fill="#00FF41" opacity="0.5">
      [SINGULARITY] ████████████████████ GRAVITATIONAL LOCK
      <animate attributeName="opacity" values="0;0;0.3;0.5;0.5" keyTimes="0;0.1;0.2;0.3;1" dur="8s" repeatCount="indefinite"/>
    </text>
  </g>

  <g stroke="#00FFFF" stroke-width="1.5" opacity="0.4" filter="url(#glow)">
    <polyline points="100,70 98,70 98,74" fill="none"/>
    <polyline points="1100,70 1102,70 1102,74" fill="none"/>
    <polyline points="98,232 98,236 100,236" fill="none"/>
    <polyline points="1102,232 1102,236 1100,236" fill="none"/>
    <animate attributeName="opacity" values="0.25;0.6;0.25" dur="3s" repeatCount="indefinite"/>
  </g>

  <!-- CONTRIBUTIONS -->
  <g>
{grid_svg}
  </g>

  <rect x="{GRID_X}" y="{GRID_Y}" width="2" height="170" fill="url(#scanLine)" opacity="0.4" filter="url(#glow)">
    <animateTransform attributeName="transform" type="translate" values="0 0;1000 0;0 0" dur="7s" repeatCount="indefinite"/>
  </rect>

  <!-- BLACK HOLE -->
  <g transform="translate({BH_X},{BH_Y})">
    <!-- Seed square (initial form, fades as BH takes over) -->
    <rect x="-7" y="-7" width="14" height="14" rx="2" fill="#1a0030" stroke="#7C3AED" stroke-width="0.6" opacity="0.9">
      <animate attributeName="opacity" values="0.9;0.15;0" keyTimes="0;0.15;{absorb_end_t}" dur="{DUR}s" repeatCount="indefinite"/>
    </rect>
    
    <!-- Gravitational distortion waves -->
    <circle r="7" fill="none" stroke="#7C3AED" stroke-width="0.8" opacity="0" filter="url(#glowStrong)">
      <animate attributeName="r" values="7;80;140" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.22;0.04" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>
    <circle r="5" fill="none" stroke="#00FFFF" stroke-width="0.5" opacity="0" filter="url(#glow)">
      <animate attributeName="r" values="5;60;110" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.15;0.03" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>
    
    <!-- Glow aura (grows as BH absorbs) -->
    <circle r="7" fill="url(#bhGlow)" opacity="0" filter="url(#glowHeavy)">
      <animate attributeName="r" values="7;55;100" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.1;0.4;0.5" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>
    
    <g transform="rotate(-10)">
    <!-- Accretion disk 1 -->
    <ellipse rx="5" ry="1.5" fill="none" stroke="url(#accretion1)" stroke-width="3" opacity="0" filter="url(#glowStrong)">
      <animate attributeName="rx" values="5;38;68" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="ry" values="1.5;10;18" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.6;0.7" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="5.2s" repeatCount="indefinite"/>
    </ellipse>
    <!-- Accretion disk 2 -->
    <ellipse rx="4" ry="1.2" fill="none" stroke="url(#accretion2)" stroke-width="2" opacity="0" filter="url(#glow)">
      <animate attributeName="rx" values="4;28;50" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="ry" values="1.2;7;13" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.5;0.55" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="4.8s" repeatCount="indefinite"/>
    </ellipse>
    <!-- Accretion disk 3 -->
    <ellipse rx="3" ry="1" fill="none" stroke="#00FFFF" stroke-width="1.2" opacity="0" filter="url(#glow)">
      <animate attributeName="rx" values="3;20;36" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="ry" values="1;5;9" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.45;0.5" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4.1s" repeatCount="indefinite"/>
    </ellipse>
    
    <!-- Polar jets: fire once the hole is feeding at full rate -->
    <g transform="rotate(-18)">
      <rect x="-1.5" y="-8" width="3" height="0" fill="url(#jetUp)" opacity="0" filter="url(#glowStrong)">
        <animate attributeName="height" values="0;6;95" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
        <animate attributeName="y" values="-8;-14;-103" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;0.15;0.7" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      </rect>
      <rect x="-1.5" y="8" width="3" height="0" fill="url(#jetDown)" opacity="0" filter="url(#glowStrong)">
        <animate attributeName="height" values="0;6;95" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
        <animate attributeName="y" values="8;8;8" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;0.15;0.7" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      </rect>
    </g>

    </g>

    <!-- Event horizon ring -->
    <circle r="5" fill="none" stroke="#9333EA" stroke-width="1.5" opacity="0" filter="url(#glowStrong)">
      <animate attributeName="r" values="5;18;40" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.75;0.85" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>

    <!-- Photon ring: thin bright circle just outside the horizon -->
    <circle r="5.5" fill="none" stroke="#E8FFFF" stroke-width="1" opacity="0" filter="url(#glowStrong)">
      <animate attributeName="r" values="5.5;16;35" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.55;0.9" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
      <animate attributeName="stroke-width" values="1;1.2;1.6" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>
    
    <!-- BH core (dark center, grows as it feeds) -->
    <circle r="4" fill="url(#bhCore)">
      <animate attributeName="r" values="4;14;32" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>
    <circle r="2" fill="#000000">
      <animate attributeName="r" values="2;8;22" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>
    <circle r="0.8" fill="#000000">
      <animate attributeName="r" values="0.8;3;10" keyTimes="0;{absorb_end_t};1" dur="{DUR}s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- Streak HUD -->
  <g filter="url(#glow)">
    <text x="100" y="255" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9" fill="#7C3AED" opacity="0.7">
      STREAK: {streak_info["current"]}d
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="2s" repeatCount="indefinite"/>
    </text>
    <text x="230" y="255" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9" fill="#9333EA" opacity="0.6">
      LONGEST: {streak_info["longest"]}d
    </text>
    <text x="380" y="255" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9" fill="#00FFFF" opacity="0.6">
      TOTAL: {streak_info["total"]}
    </text>
  </g>

  <!-- Bottom HUD -->
  <g filter="url(#glitch)">
    <text x="100" y="275" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10" fill="#00FF41" opacity="0.7" filter="url(#glow)">
      [SINGULARITY ACTIVE] [absorption: 100%] [regeneration: ENABLED]
    </text>
    <text x="720" y="275" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10" fill="#00FFFF" opacity="0.5" filter="url(#glow)">
      UPTD: {timestamp}
    </text>
  </g>

{('  <!-- data: REAL -->' if is_real else f'''  <g filter="url(#glow)">
    <text x="24" y="318" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10" fill="{WARN}" opacity="0.85">
      SIMULATED DATA — set GH_PAT
      <animate attributeName="opacity" values="0.6;0.82;0.6" dur="3.4s" repeatCount="indefinite"/>
    </text>
  </g>''')}

  <g transform="translate(1100,20)">
    <circle cx="0" cy="0" r="4" fill="#00FF41" filter="url(#glow)">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <text x="10" y="4" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10" fill="#00FF41" opacity="0.6">LIVE</text>
  </g>

  <line x1="100" y1="285" x2="1100" y2="285" stroke="#00FFFF" stroke-width="0.8" opacity="0.25" filter="url(#glow)">
    <animate attributeName="opacity" values="0.15;0.4;0.15" dur="4s" repeatCount="indefinite"/>
  </line>

  <text x="600" y="318" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11" fill="#3B5249" letter-spacing="4" opacity="0.6">
    {user.upper()} // CONTRIBUTION MATRIX
  </text>
</svg>'''
    
    with open("dist/contribution-matrix.svg", "w") as f:
        f.write(svg)
