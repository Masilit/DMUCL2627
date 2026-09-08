# -*- coding: utf-8 -*-
"""Fetch the live UCL 2026/27 league-phase table from football-data.org and
write it to standings.json in the shape the tracker web app expects.

Run by GitHub Actions on a schedule. Reads the API key from the environment
variable FOOTBALL_DATA_TOKEN (set as a GitHub Actions secret).

If any team name from the API cannot be matched to one of our 36 canonical
names, the script exits non-zero WITHOUT overwriting standings.json — so a bad
run never corrupts the table; the previous good file stays in place. The log
lists the unmatched names so a mapping can be added below.
"""
import os, sys, json, unicodedata, datetime, urllib.request, urllib.error

SEASON = os.environ.get("CL_SEASON", "2026")          # 2026 => 2026/27 season
COMP = "CL"                                            # UEFA Champions League
API = "https://api.football-data.org/v4/competitions/%s/standings?season=%s" % (COMP, SEASON)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "standings.json")

# Canonical names — MUST match the names used in the predictions / the app.
CANON = [
 "Paris Saint-Germain","Bayern München","Real Madrid","Liverpool","Inter Milan",
 "Manchester City","Arsenal","Barcelona","Atlético de Madrid","Borussia Dortmund",
 "Roma","Sporting CP","Aston Villa","Porto","Manchester United","Club Brugge",
 "Real Betis","PSV Eindhoven","Feyenoord","Lille","Napoli","RB Leipzig","Villarreal",
 "Shakhtar Donetsk","Galatasaray","Fenerbahçe","Bodø/Glimt","Viking","Slavia Praha",
 "VfB Stuttgart","AEK Athens","LASK","Como","Lens","Sabah","Slovan Bratislava",
]

# Explicit variants seen from football-data.org (left) -> canonical (right).
VARIANTS = {
 "paris saint germain fc":"Paris Saint-Germain", "paris saint-germain fc":"Paris Saint-Germain",
 "fc bayern munchen":"Bayern München", "fc bayern munich":"Bayern München", "bayern munchen":"Bayern München",
 "real madrid cf":"Real Madrid",
 "liverpool fc":"Liverpool",
 "fc internazionale milano":"Inter Milan", "inter":"Inter Milan", "internazionale":"Inter Milan",
 "manchester city fc":"Manchester City",
 "arsenal fc":"Arsenal",
 "fc barcelona":"Barcelona",
 "club atletico de madrid":"Atlético de Madrid", "atletico madrid":"Atlético de Madrid",
 "borussia dortmund":"Borussia Dortmund",
 "as roma":"Roma",
 "sporting clube de portugal":"Sporting CP", "sporting cp":"Sporting CP", "sporting lisbon":"Sporting CP",
 "aston villa fc":"Aston Villa",
 "fc porto":"Porto",
 "manchester united fc":"Manchester United",
 "club brugge kv":"Club Brugge", "club brugge":"Club Brugge",
 "real betis balompie":"Real Betis", "real betis":"Real Betis",
 "psv":"PSV Eindhoven", "psv eindhoven":"PSV Eindhoven",
 "feyenoord rotterdam":"Feyenoord", "feyenoord":"Feyenoord",
 "losc lille":"Lille", "lille osc":"Lille", "lille":"Lille",
 "ssc napoli":"Napoli", "napoli":"Napoli",
 "rb leipzig":"RB Leipzig", "rasenballsport leipzig":"RB Leipzig",
 "villarreal cf":"Villarreal",
 "fc shakhtar donetsk":"Shakhtar Donetsk", "shakhtar donetsk":"Shakhtar Donetsk",
 "galatasaray sk":"Galatasaray", "galatasaray":"Galatasaray",
 "fenerbahce sk":"Fenerbahçe", "fenerbahce":"Fenerbahçe",
 "fk bodo glimt":"Bodø/Glimt", "bodo glimt":"Bodø/Glimt",
 "viking fk":"Viking", "viking":"Viking",
 "sk slavia praha":"Slavia Praha", "slavia praha":"Slavia Praha", "slavia prague":"Slavia Praha",
 "vfb stuttgart":"VfB Stuttgart",
 "aek athens fc":"AEK Athens", "aek athens":"AEK Athens",
 "lask":"LASK", "lask linz":"LASK",
 "como 1907":"Como", "como":"Como",
 "rc lens":"Lens", "lens":"Lens",
 "sabah fk":"Sabah", "sabah fa":"Sabah", "sabah":"Sabah",
 "sk slovan bratislava":"Slovan Bratislava", "slovan bratislava":"Slovan Bratislava",
}

def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # strip accents
    s = s.lower().replace("&", " and ").replace("/", " ")
    out = []
    for ch in s:
        out.append(ch if (ch.isalnum() or ch == " ") else " ")
    return " ".join("".join(out).split())

# Build a normalized lookup from canonical names + variants.
LOOKUP = {}
for c in CANON:
    LOOKUP[norm(c)] = c
for k, v in VARIANTS.items():
    LOOKUP[norm(k)] = v

def resolve(api_name):
    n = norm(api_name)
    if n in LOOKUP:
        return LOOKUP[n]
    # strip common club words then retry
    stop = {"fc","cf","sk","kv","fk","sc","as","ss","ssc","afc","cp","de","club",
            "balompie","rotterdam","eindhoven","donetsk","praha","linz","osc","losc","1907","fa"}
    n2 = " ".join(w for w in n.split() if w not in stop)
    if n2 in LOOKUP:
        return LOOKUP[n2]
    for key, val in LOOKUP.items():
        k2 = " ".join(w for w in key.split() if w not in stop)
        if k2 and (k2 == n2 or k2 in n2 or n2 in k2):
            return val
    return None

def main():
    token = os.environ.get("FOOTBALL_DATA_TOKEN", "").strip()
    if not token:
        print("ERROR: FOOTBALL_DATA_TOKEN is not set."); sys.exit(2)

    req = urllib.request.Request(API, headers={"X-Auth-Token": token})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print("ERROR: API returned HTTP %s — %s" % (e.code, e.read().decode("utf-8", "ignore")[:300]))
        sys.exit(3)
    except Exception as e:
        print("ERROR: request failed —", e); sys.exit(3)

    # Pick the TOTAL table with the most rows (the 36-team league-phase table).
    best = None
    for s in data.get("standings", []):
        if s.get("type") not in (None, "TOTAL"):
            continue
        table = s.get("table", [])
        if best is None or len(table) > len(best):
            best = table
    if not best:
        print("ERROR: no standings table in API response."); sys.exit(4)

    rows, unmatched = [], []
    for row in best:
        api_name = (row.get("team") or {}).get("name", "")
        canon = resolve(api_name)
        if not canon:
            unmatched.append(api_name); continue
        rows.append({
            "rank": row.get("position"),
            "team": canon,
            "played": row.get("playedGames", 0),
            "won": row.get("won", 0),
            "draw": row.get("draw", 0),
            "lost": row.get("lost", 0),
            "gf": row.get("goalsFor", 0),
            "ga": row.get("goalsAgainst", 0),
            "gd": row.get("goalDifference", 0),
            "points": row.get("points", 0),
        })

    if unmatched:
        print("ERROR: %d team name(s) could not be matched — NOT writing standings.json:" % len(unmatched))
        for u in unmatched:
            print("   -", repr(u), " (normalized:", repr(norm(u)) + ")")
        print("Add these to VARIANTS in scripts/fetch_standings.py.")
        sys.exit(5)

    rows.sort(key=lambda r: r["rank"] or 999)
    season = data.get("season", {}) or {}
    md = season.get("currentMatchday")
    out = {
        "season": "2026/27",
        "competition": "UEFA Champions League",
        "phase": "League phase",
        "matchday": md if md is not None else 0,
        "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": "football-data.org",
        "standings": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("OK: wrote %d teams to %s (matchday %s)" % (len(rows), OUT, out["matchday"]))

if __name__ == "__main__":
    main()
