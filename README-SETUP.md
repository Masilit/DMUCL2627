# UCL Points Tracker — setup (GitHub Actions + GitHub Pages)

This folder is a ready-to-deploy website. GitHub hosts the page **and** auto-refreshes
the live standings for you. You share one link; your friends just open it.

## What's in here
```
index.html                     the web app (what visitors see)
standings.json                 the actual table (auto-updated by the robot)
scripts/fetch_standings.py     pulls the live table from the football API
.github/workflows/update-standings.yml   the scheduled "robot" that runs the script
template.html, build_tracker.py, ...     source used to regenerate index.html (not needed to run)
```

## One-time setup (~10 minutes)

### 1. Get a free API key
- Go to **https://www.football-data.org/client/register** and register (free).
- They email you an **API token** (a long string). Copy it.

### 2. Put this folder on GitHub
- Create a new **public** repository (public = free unlimited automation + free Pages).
- Upload everything in this `tracker` folder to the repo root (so `index.html` is at the top level).

### 3. Add your key as a secret (this is how it stays hidden)
- Repo → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `FOOTBALL_DATA_TOKEN`  ·  Value: *(paste your token)*  → Save.
- The key lives only here. It is never in the web page and never visible to visitors.

### 4. Turn on the website (GitHub Pages)
- Repo → **Settings → Pages** → *Build and deployment* → Source: **Deploy from a branch**
- Branch: **main**, folder: **/ (root)** → Save.
- After a minute your link appears: `https://<your-username>.github.io/<repo-name>/`

### 5. Pull real data once (optional but nice)
- Repo → **Actions** tab → **Update UCL standings** → **Run workflow**.
- This fetches the current table immediately instead of waiting for the next scheduled run.

That's it. **Share the Pages link** from step 4 with the WhatsApp group.

## How updating works (two separate clocks)

**The robot (GitHub Actions)** — defined in `.github/workflows/update-standings.yml`:
- Runs on a schedule: currently **once an hour**. GitHub may delay a scheduled run by a
  few minutes; that's fine. You can also hit **Run workflow** any time for an instant refresh.
- Each run calls the API, rewrites `standings.json`, and **only commits if something changed**
  (no pointless updates).
- To refresh more often on match nights, open the workflow file and add another schedule line,
  e.g. `- cron: '*/15 18-23 * * 2,3'` (every 15 min, Tue & Wed evenings UTC).

**The API (football-data.org)**:
- The table only changes when matches are played. The CL league phase is **8 matchdays** spread
  across Sep 2026 – Jan 2027 (games on Tue/Wed nights), so the real standings actually change
  only a handful of times all season. Hourly polling is far more than enough.
- Free tier allows 10 requests/minute; we use one per run.

**The web page**:
- On load, and whenever a visitor taps **Refresh**, it re-reads `standings.json` (cache-busted),
  so everyone sees the latest committed table. Note GitHub Pages' CDN can cache a file for up to
  ~10 minutes, so a brand-new update may take a few minutes to reach everyone.
- The **"Last updated"** shown on the page is the timestamp inside `standings.json`.

## If a run fails with "team name could not be matched"
The football API occasionally spells a club differently than expected. The failed run does **not**
overwrite the good file — it just logs the unmatched name. Send me that name (from the Actions log)
and I'll add it to `VARIANTS` in `scripts/fetch_standings.py`, or add it yourself.

## Editing predictions later
Predictions are baked into `index.html`. To change them, edit `../Prediction/prediction.txt`,
re-run `../Prediction/parse_predictions.py`, then `python build_tracker.py`, and re-upload `index.html`.

## Prefer no API at all?
You can skip steps 1 & 3 and just edit `standings.json` by hand after each matchday (keep the same
shape: `rank, team, played, points, gd`). The page works identically. Team names in `standings.json`
must match the canonical names (see `scripts/fetch_standings.py` → `CANON`).
