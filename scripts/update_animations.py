import os
import requests
import json
import random
import traceback
import re
from datetime import datetime, timedelta

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "skillparty")
REPO = os.environ.get("GITHUB_REPOSITORY", f"{USER}/{USER}")
REQUEST_TIMEOUT = 12
CONTRIB_CACHE_URL = f"https://raw.githubusercontent.com/{REPO}/output/contrib-cache.json"

HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
HTML_HEADERS = {
    "User-Agent": "skillparty-profile-assets/1.0",
    "Accept": "text/html",
}
REAL_SOURCES = {"REAL_API", "REAL_HTML", "REAL_CACHE"}

def is_real_data(source):
    return source in REAL_SOURCES

def fetch_contributions():
    """Returns (grid, streak_info) where streak_info = {current, longest, total}"""
    if GITHUB_TOKEN:
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
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            print("Contributions data response:")
            print(json.dumps(data, indent=2)[:500] + "...")
            errors = data.get("errors")
            if not errors:
                grid, streak_info, days = process_github_contribs(data)
                if grid and days:
                    write_contrib_cache(days, "REAL_API")
                    return grid, streak_info, "REAL_API"
            if errors:
                print("GraphQL Error:", errors)
        else:
            print("Failed to fetch data:", response.status_code, response.text)
    else:
        print("No GITHUB_TOKEN provided, falling back to HTML/cache.")

    html_days = fetch_contributions_html()
    if html_days:
        grid = build_grid_from_days(html_days)
        streak_info = calculate_streaks_from_days(html_days)
        write_contrib_cache(html_days, "REAL_HTML")
        return grid, streak_info, "REAL_HTML"

    cache_days = read_contrib_cache()
    if cache_days:
        grid = build_grid_from_days(cache_days)
        streak_info = calculate_streaks_from_days(cache_days)
        return grid, streak_info, "REAL_CACHE"

    grid, streak_info = simulate_contributions()
    return grid, streak_info, "SIMULATED"

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

def normalize_days(days):
    if not days:
        return []
    day_map = {}
    for d in days:
        day_map[d["date"]] = int(d["count"])
    return [{"date": date, "count": day_map[date]} for date in sorted(day_map.keys())]

def calculate_streaks_from_days(days):
    """Calculate current streak, longest streak, and total contributions from day list."""
    ordered = normalize_days(days)
    total = sum(d["count"] for d in ordered)

    current_streak = 0
    longest_streak = 0
    streak = 0

    for d in ordered:
        if d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    for d in reversed(ordered):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    return {"current": current_streak, "longest": longest_streak, "total": total}

def map_count_to_level(count):
    if count == 0:
        return 0
    if count <= 3:
        return 1
    if count <= 8:
        return 2
    if count <= 14:
        return 3
    return 4

def build_grid_from_days(days):
    ordered = normalize_days(days)
    if not ordered:
        return []

    levels = [map_count_to_level(d["count"]) for d in ordered]
    needed = 42 * 7
    levels = levels[-needed:]
    if len(levels) < needed:
        levels = [0] * (needed - len(levels)) + levels

    grid = []
    for i in range(42):
        start = i * 7
        grid.append(levels[start:start + 7])
    return grid

def process_github_contribs(data):
    try:
        calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        weeks = calendar["weeks"]
        days = []
        for w in weeks:
            for d in w["contributionDays"]:
                days.append({"count": d["contributionCount"], "date": d["date"]})

        days = normalize_days(days)
        if not days:
            return None, None, []

        streak_info = calculate_streaks_from_days(days)
        grid = build_grid_from_days(days)
        return grid, streak_info, days
    except Exception as e:
        print(f"Error parsing contributions: {e}")
        traceback.print_exc()
        return None, None, []

def parse_contributions_html(html):
    matches = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-count="(\d+)"', html)
    if not matches:
        reversed_matches = re.findall(r'data-count="(\d+)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html)
        matches = [(date, count) for count, date in reversed_matches]

    if not matches:
        return []

    days = []
    for date, count in matches:
        days.append({"date": date, "count": int(count)})
    return normalize_days(days)

def fetch_contributions_html():
    try:
        url = f"https://github.com/users/{USER}/contributions"
        response = requests.get(url, headers=HTML_HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            print("HTML contributions fetch failed:", response.status_code)
            return []
        days = parse_contributions_html(response.text)
        if not days:
            print("HTML contributions parse returned no days")
        return days
    except Exception as e:
        print(f"HTML contributions error: {e}")
        traceback.print_exc()
        return []

def read_contrib_cache():
    local_path = "dist/contrib-cache.json"
    if os.path.exists(local_path):
        try:
            with open(local_path, "r") as f:
                payload = json.load(f)
            days = payload.get("days", [])
            return normalize_days(days)
        except Exception as e:
            print(f"Local cache read error: {e}")

    try:
        response = requests.get(CONTRIB_CACHE_URL, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            print("Cache fetch failed:", response.status_code)
            return []
        payload = response.json()
        days = payload.get("days", [])
        return normalize_days(days)
    except Exception as e:
        print(f"Remote cache error: {e}")
        return []

def write_contrib_cache(days, source):
    os.makedirs("dist", exist_ok=True)
    payload = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "days": normalize_days(days),
    }
    with open("dist/contrib-cache.json", "w") as f:
        json.dump(payload, f, indent=2)

from render_hero import generate_hero_svg
from render_stats_panel import generate_stats_panel
from render_black_hole import generate_black_hole_svg


def fetch_languages():
    if not GITHUB_TOKEN:
        langs, last_repo = simulate_languages()
        return langs, last_repo, "SIMULATED", 0, 0
    query = """
    query($user: String!) {
      user(login: $user) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
          nodes {
            name
            stargazerCount
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
      headers=HEADERS,
      timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 200:
        data = response.json()
        print("Languages data response:")
        print(json.dumps(data, indent=2)[:500] + "...")
        if "errors" in data:
            print("GraphQL Error (langs):", data["errors"])
            langs, last_repo = simulate_languages()
            return langs, last_repo, "SIMULATED", 0
        
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
            stars = sum(r.get("stargazerCount", 0) for r in repos)
            return results, last_repo, "REAL_API", stars
        except Exception as e:
            print(f"Error parsing languages: {e}")
            traceback.print_exc()
            langs, last_repo = simulate_languages()
            return langs, last_repo, "SIMULATED", 0
    else:
        print("Failed to fetch languages:", response.status_code, response.text)
        langs, last_repo = simulate_languages()
        return langs, last_repo, "SIMULATED", 0

def simulate_languages():
    return [
        {"name": "TypeScript", "color": "#3178C6", "percent": 45.0},
        {"name": "JavaScript", "color": "#F7DF1E", "percent": 25.0},
        {"name": "Python", "color": "#3572A5", "percent": 15.0},
        {"name": "Dart", "color": "#00B4AB", "percent": 10.0},
        {"name": "HTML", "color": "#E34C26", "percent": 5.0},
    ], "skillparty/skillparty"


def fetch_profile_stats(stars):
    """Public profile numbers for the stats panel (REST, cheap)."""
    profile = {"stars": stars, "repos": 0, "followers": 0, "since": "?"}
    try:
        r = requests.get(f"https://api.github.com/users/{USER}", headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            u = r.json()
            profile["repos"] = u.get("public_repos", 0)
            profile["followers"] = u.get("followers", 0)
            profile["since"] = (u.get("created_at") or "?")[:4]
    except Exception as e:
        print(f"Profile stats fetch failed: {e}")
    return profile


os.makedirs("dist", exist_ok=True)
print(f"User: {USER}")
print(f"Token present: {bool(GITHUB_TOKEN)}")
if GITHUB_TOKEN:
    test_r = requests.get("https://api.github.com/user", headers=HEADERS, timeout=REQUEST_TIMEOUT)
    print(f"Auth test: {test_r.status_code}")

data_source = {"contributions": "unknown", "languages": "unknown"}

try:
    print("Generating Hero SVG...")
    generate_hero_svg(USER)

    print("Fetching contributions...")
    grid, streak_info, contributions_source = fetch_contributions()
    data_source["contributions"] = contributions_source
    print(f"Streak info: {streak_info}")
    print(f"Contributions source: {contributions_source}")
    print("Generating Black Hole Matrix SVG...")
    generate_black_hole_svg(grid, streak_info, USER, is_real_data(contributions_source))

    print("Fetching Languages...")
    langs, last_repo, languages_source, stars = fetch_languages()
    data_source["languages"] = languages_source
    print(f"Languages source: {languages_source}")
    print(f"Languages: {[l['name'] for l in langs]}")

    print("Fetching profile stats...")
    profile = fetch_profile_stats(stars)
    print(f"Profile: {profile}")

    print("Generating Stats Panel SVG...")
    all_real = is_real_data(contributions_source) and is_real_data(languages_source)
    generate_stats_panel(langs, streak_info, profile, all_real)

    print("\n=== SUMMARY ===")
    print(f"Contributions: {data_source['contributions']}")
    print(f"Languages: {data_source['languages']}")
    print("Done! Artifacts saved to dist/")
except Exception as e:
    print(f"FATAL ERROR: {e}")
    traceback.print_exc()
    raise
