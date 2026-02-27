import os
import requests
import json
import random
import traceback
from datetime import datetime, timedelta

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "skillparty")

HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def fetch_contributions():
    """Returns (grid, streak_info) where streak_info = {current, longest, total}"""
    if not GITHUB_TOKEN:
        print("No GITHUB_TOKEN provided, falling back to simulated data.")
        return simulate_contributions()

    query = """
    query($user: String!) {
      user(login: $user) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"user": USER}},
        headers=HEADERS
    )
    
    if response.status_code == 200:
        data = response.json()
        print("Contributions data response:")
        print(json.dumps(data, indent=2)[:500] + "...")
        if "errors" in data:
            print("GraphQL Error:", data["errors"])
            return simulate_contributions()
        return process_github_contribs(data)
    else:
        print("Failed to fetch data:", response.status_code, response.text)
        return simulate_contributions()

def simulate_contributions():
    # 42 weeks x 7 days
    grid = []
    levels = [0, 1, 2, 3, 4]
    for c in range(42):
        col = []
        activity = c / 41
        for r in range(7):
            rv = random.random()
            if rv < 0.82 - activity * 0.62:
                col.append(0)
            else:
                lv = random.random()
                w = lv ** max(0.3, 1.5 - activity * 1.2)
                if w < 0.3: col.append(1)
                elif w < 0.55: col.append(2)
                elif w < 0.78: col.append(3)
                else: col.append(4)
        grid.append(col)
    return grid, {"current": random.randint(3, 15), "longest": random.randint(20, 60), "total": random.randint(400, 1200)}

def calculate_streaks(weeks_data):
    """Calculate current streak, longest streak, and total contributions from raw weeks data."""
    all_days = []
    for w in weeks_data:
        for d in w["contributionDays"]:
            all_days.append({"count": d["contributionCount"], "date": d["date"]})
    
    total = sum(d["count"] for d in all_days)
    
    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    streak = 0
    
    for d in all_days:
        if d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0
    
    # Current streak: count backwards from today
    for d in reversed(all_days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break
    
    return {"current": current_streak, "longest": longest_streak, "total": total}

def process_github_contribs(data):
    try:
        calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        weeks = calendar["weeks"]
        
        streak_info = calculate_streaks(weeks)
        
        days = []
        for w in weeks:
            for d in w["contributionDays"]:
                count = d["contributionCount"]
                if count == 0: val = 0
                elif count <= 3: val = 1
                elif count <= 8: val = 2
                elif count <= 14: val = 3
                else: val = 4
                days.append(val)
                
        # We need exactly 294 days (42 cols x 7 rows)
        needed = 42 * 7
        days = days[-needed:]
        
        # Pad if not enough
        if len(days) < needed:
            days = [0]*(needed - len(days)) + days
            
        grid = []
        for i in range(42):
            start = i * 7
            grid.append(days[start:start+7])
        return grid, streak_info
    except Exception as e:
        print(f"Error parsing contributions: {e}")
        traceback.print_exc()
        return simulate_contributions()

def generate_black_hole_svg(grid, streak_info):
    COLS, ROWS = 42, 7
    BLOCK, CELL = 14, 24
    GRID_X, GRID_Y = 100, 72
    W, H = 1200, 340
    BH_Y = 151
    DUR = 20
    
    COLORS = ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"]

    def col_delay(c):
        cx = GRID_X + c * CELL + BLOCK / 2
        return round((cx + 50) / 65, 1)

    grid_lines = []
    total_contribs = 0
    for c in range(COLS):
        delay = col_delay(c)
        for r in range(ROWS):
            val = grid[c][r]
            if val > 0: total_contribs += 1
            
            cx = GRID_X + c * CELL + BLOCK // 2
            cy = GRID_Y + r * CELL + BLOCK // 2
            color = COLORS[val]

            grid_lines.append(f'    <g transform="translate({cx},{cy})">')
            grid_lines.append(f'      <rect x="-7" y="-7" width="14" height="14" rx="3" fill="{color}">')
            grid_lines.append(
                f'        <animateTransform attributeName="transform" type="scale"'
                f' values="1;1.3;0;0;0.3;1;1"'
                f' keyTimes="0;0.03;0.09;0.48;0.56;0.64;1"'
                f' dur="{DUR}s" begin="{delay}s" repeatCount="indefinite"/>'
            )
            grid_lines.append(
                f'        <animate attributeName="opacity"'
                f' values="1;1;0;0;0.3;1;1"'
                f' keyTimes="0;0.03;0.09;0.48;0.56;0.64;1"'
                f' dur="{DUR}s" begin="{delay}s" repeatCount="indefinite"/>'
            )
            grid_lines.append(f'      </rect>')
            grid_lines.append(f'    </g>')
            
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
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

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

  <!-- Matrix rain -->
  <g font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11" filter="url(#glow)">
{rain_svg}
  </g>

  <!-- Terminal header -->
  <g filter="url(#glitch)">
    <text x="24" y="28" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11" fill="#00FF41" opacity="0.8" filter="url(#glow)">
      root@{USER}:~$ ./scan_contributions --mode=singularity --live
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
  <g>
    <animateTransform attributeName="transform" type="translate"
      values="-50 {BH_Y};1250 {BH_Y}" dur="{DUR}s" repeatCount="indefinite"/>
    <circle r="90" fill="url(#bhGlow)" opacity="0.5" filter="url(#glowHeavy)">
      <animate attributeName="r" values="80;95;80" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.4;0.6;0.4" dur="3s" repeatCount="indefinite"/>
    </circle>
    <ellipse rx="55" ry="14" fill="none" stroke="url(#accretion1)" stroke-width="4" opacity="0.7" filter="url(#glowStrong)">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="3.5s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse rx="40" ry="10" fill="none" stroke="url(#accretion2)" stroke-width="2.5" opacity="0.6" filter="url(#glow)">
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="2.2s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse rx="28" ry="7" fill="none" stroke="#00FFFF" stroke-width="1.5" opacity="0.5" filter="url(#glow)">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="1.5s" repeatCount="indefinite"/>
    </ellipse>
    <circle r="20" fill="none" stroke="#9333EA" stroke-width="1.5" filter="url(#glowStrong)">
      <animate attributeName="r" values="18;23;18" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle r="16" fill="url(#bhCore)"/>
    <circle r="6" fill="#000000"/>
    <circle r="3" fill="#000000">
      <animate attributeName="r" values="3;4;3" dur="1s" repeatCount="indefinite"/>
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
    {USER.upper()} // CONTRIBUTION MATRIX
  </text>
</svg>'''
    
    with open("dist/contribution-matrix.svg", "w") as f:
        f.write(svg)

def fetch_languages():
    if not GITHUB_TOKEN: return simulate_languages()
    query = """
    query($user: String!) {
      user(login: $user) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
          nodes {
            name
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  color
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"user": USER}},
        headers=HEADERS
    )
    if response.status_code == 200:
        data = response.json()
        print("Languages data response:")
        print(json.dumps(data, indent=2)[:500] + "...")
        if "errors" in data:
            print("GraphQL Error (langs):", data["errors"])
            return simulate_languages()
        
        try:
            lang_stats = {}
            repos = data["data"]["user"]["repositories"]["nodes"]
            for repo in repos:
                for edge in repo["languages"]["edges"]:
                    name = edge["node"]["name"]
                    color = edge["node"]["color"]
                    size = edge["size"]
                    if name not in lang_stats:
                        lang_stats[name] = {"color": color, "size": 0}
                    lang_stats[name]["size"] += size
                    
            # Sort by size and take top 5
            sorted_langs = sorted(lang_stats.items(), key=lambda x: x[1]["size"], reverse=True)[:5]
            total_size = sum(x[1]["size"] for x in sorted_langs)
            
            results = []
            for lang_name, lang_data in sorted_langs:
                percent = (lang_data["size"] / total_size) * 100
                results.append({"name": lang_name, "color": lang_data["color"], "percent": percent})
                
            # Get last active repo
            last_repo = repos[0]["name"] if repos else "unknown"
            return results, last_repo
        except Exception as e:
            print(f"Error parsing languages: {e}")
            traceback.print_exc()
            return simulate_languages()
    else:
        print("Failed to fetch languages:", response.status_code, response.text)
    return simulate_languages()

def simulate_languages():
    return [
        {"name": "TypeScript", "color": "#3178C6", "percent": 45.0},
        {"name": "JavaScript", "color": "#F7DF1E", "percent": 25.0},
        {"name": "Python", "color": "#3572A5", "percent": 15.0},
        {"name": "Dart", "color": "#00B4AB", "percent": 10.0},
        {"name": "HTML", "color": "#E34C26", "percent": 5.0},
    ], "skillparty/skillparty"

def generate_cyber_langs(langs, last_repo):
    W, H = 500, 200
    
    # Render bars
    bars_svg = ""
    y_offset = 60
    for l in langs:
        width = int((l["percent"] / 100) * 300)
        color = l["color"] or "#00FFFF"
        bars_svg += f'''
        <g transform="translate(40, {y_offset})">
            <text x="0" y="0" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{color}" opacity="0.9" filter="url(#glow)">{l['name'].upper()}</text>
            <text x="390" y="0" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{color}" opacity="0.9">{l['percent']:.1f}%</text>
            <rect x="0" y="8" width="400" height="4" fill="#1b2838" rx="2"/>
            <rect x="0" y="8" width="{width}" height="4" fill="{color}" rx="2" filter="url(#glow)">
               <animate attributeName="width" from="0" to="{width}" dur="1.5s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.1, 0.8, 0.3, 1"/>
            </rect>
        </g>
        '''
        y_offset += 25
        
    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{W}" height="{H}" rx="8" fill="#0A0A0A" stroke="#1B2838" stroke-width="1"/>
  
  <text x="40" y="30" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#00FFFF" opacity="0.8" filter="url(#glow)">
    sys.status.langs // NEURAL LINK ACTIVE
  </text>
  
  <g>
    {bars_svg}
  </g>
  
  <rect x="40" y="{H-25}" width="8" height="8" fill="#FF003C" filter="url(#glow)">
    <animate attributeName="opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite"/>
  </rect>
  <text x="55" y="{H-17}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="#FF003C" opacity="0.8">
    NOW OPERATING: {last_repo}
  </text>
</svg>'''
    with open("dist/cyber-langs.svg", "w") as f:
        f.write(svg)

def generate_header_svg():
    """Generate a cyberpunk typing-effect header SVG."""
    W, H = 900, 120
    
    lines = [
        f"Jose Alejandro Rollano",
        "Freelance Software Developer",
        "Bolivia // Next.js · Flutter · Python · Cloud",
    ]
    
    # Build typing animation for each line
    typing_elements = []
    for i, line in enumerate(lines):
        y = 38 + i * 28
        delay = i * 2.0
        total_dur = len(line) * 0.06
        
        if i == 0:
            font_size = 22
            color = "#00FFFF"
            opacity = 0.95
        elif i == 1:
            font_size = 14
            color = "#00FF41"
            opacity = 0.8
        else:
            font_size = 11
            color = "#7C3AED"
            opacity = 0.7
        
        # Each character appears one by one
        char_elements = []
        for j, ch in enumerate(line):
            char_delay = round(delay + j * 0.06, 2)
            escaped = ch.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if ch == ' ':
                escaped = '&#160;'
            char_elements.append(
                f'<tspan opacity="0">'
                f'{escaped}'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.05s" begin="{char_delay}s" fill="freeze"/>'
                f'</tspan>'
            )
        
        char_svg = ''.join(char_elements)
        
        # Blinking cursor after the line
        cursor_x_approx = 60 + len(line) * (font_size * 0.6)
        cursor_appear = round(delay + len(line) * 0.06, 2)
        cursor_disappear = round(delay + len(line) * 0.06 + 1.5, 2) if i < len(lines) - 1 else None
        
        typing_elements.append(
            f'  <text x="60" y="{y}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="{font_size}" fill="{color}" opacity="{opacity}" filter="url(#glow)">'
            f'{char_svg}'
            f'</text>'
        )
        
        # Cursor
        if i == len(lines) - 1:
            typing_elements.append(
                f'  <rect x="{min(cursor_x_approx, W - 60)}" y="{y - font_size + 4}" width="{font_size * 0.55}" height="{font_size}" fill="{color}" opacity="0">'
                f'    <animate attributeName="opacity" values="0;0;0.8;0.8;0;0.8;0.8;0" '
                f'keyTimes="0;{cursor_appear/10};{cursor_appear/10 + 0.01};{(cursor_appear + 0.5)/10};{(cursor_appear + 0.5)/10 + 0.01};{(cursor_appear + 1)/10};{(cursor_appear + 1)/10 + 0.01};1" '
                f'dur="10s" fill="freeze"/>'
                f'  </rect>'
            )
    
    typing_svg = '\n'.join(typing_elements)
    
    # Scanline horizontal
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glitch">
      <feOffset in="SourceGraphic" dx="2" dy="0" result="r">
        <animate attributeName="dx" values="0;3;-2;0;1;-1;0" dur="0.3s" begin="6s" repeatCount="3"/>
      </feOffset>
      <feOffset in="SourceGraphic" dx="-2" dy="0" result="b">
        <animate attributeName="dx" values="0;-3;2;0;-1;1;0" dur="0.3s" begin="6s" repeatCount="3"/>
      </feOffset>
      <feColorMatrix in="r" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="red"/>
      <feColorMatrix in="b" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="blue"/>
      <feBlend in="red" in2="blue" mode="screen" result="glitched"/>
      <feBlend in="SourceGraphic" in2="glitched" mode="normal"/>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" rx="10" fill="#0A0A0A" stroke="#1B2838" stroke-width="1"/>

  <!-- Terminal prompt -->
  <text x="20" y="17" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9" fill="#00FF41" opacity="0.4">
    root@{USER}:~$ cat /etc/identity.conf
  </text>

  <!-- Typing content -->
  <g filter="url(#glitch)">
{typing_svg}
  </g>

  <!-- Bottom status bar -->
  <line x1="20" y1="{H - 18}" x2="{W - 20}" y2="{H - 18}" stroke="#00FFFF" stroke-width="0.5" opacity="0.2"/>
  <circle cx="30" cy="{H - 9}" r="3" fill="#00FF41" filter="url(#glow)">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>
  </circle>
  <text x="40" y="{H - 5}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="8" fill="#475569" opacity="0.6">
    SESSION ACTIVE // {timestamp} // github.com/{USER}
  </text>
</svg>'''
    
    with open("dist/header-typing.svg", "w") as f:
        f.write(svg)

os.makedirs("dist", exist_ok=True)
print(f"User: {USER}")
print(f"Token present: {bool(GITHUB_TOKEN)}")

try:
    print("Generating Header SVG...")
    generate_header_svg()

    print("Fetching contributions...")
    grid, streak_info = fetch_contributions()
    print(f"Streak info: {streak_info}")
    print("Generating Matrix SVG...")
    generate_black_hole_svg(grid, streak_info)

    print("Fetching Languages...")
    langs, last_repo = fetch_languages()
    print("Generating Cyber Langs SVG...")
    generate_cyber_langs(langs, last_repo)

    print("Done! Artifacts saved to dist/")
except Exception as e:
    print(f"FATAL ERROR: {e}")
    traceback.print_exc()
    raise
