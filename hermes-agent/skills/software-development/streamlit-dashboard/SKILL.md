---
name: streamlit-dashboard
description: "Build local web dashboards for Elias. PRIMARY: FastAPI + React + Canvas pixel-art office (Agentic OS v3). FALLBACK: Streamlit (Python, heavier)."
version: 3.0.0
tags: [dashboard, ui, agentic-os, react, streamlit, localhost]
---

# Local Dashboard — Build Pattern

## When to Use
- User asks for a dashboard, admin panel, or monitoring UI
- Building the Agentic OS dashboard or similar multi-page app
- Any localhost web app with dark theme, live data, agent integration

## CRITICAL: User Preference
Elias tried Streamlit and rejected it — "IT'S STILL MESSED UP", pages conflicted, Streamlit multipage routing caused ghost pages, CSS overrides were fragile. **Default to vanilla HTML/JS/React** (Approach A). Only use Streamlit if explicitly requested.

## Approach A — FastAPI + React Single-Page (PRIMARY, Agentic OS v3)

Python FastAPI backend with SQLite state, single-file React frontend with embedded Canvas engine. This is the current Agentic OS architecture.

### Architecture
```
~/agentic-os/
├── server.py           ← FastAPI backend, SQLite state, REST API, simulation tick
├── data/
│   └── agentic_os.db   ← SQLite (agents, tasks, logs, goals tables)
├── static/
│   └── index.html      ← ALL frontend: CSS + Canvas office + React UI in one file
└── launch.sh           ← pip install deps, start uvicorn on port 3000
```

### Key Rules
1. **SQLite = single source of truth.** All agent state, tasks, logs, goals stored in DB. API exposes CRUD. No config.json needed.
2. **Single HTML file.** CSS (`<style>`), Canvas office engine, and React UI all embedded in `static/index.html`. No build step, no separate JS files to manage.
3. **FastAPI serves everything.** `StaticFiles` mount for `/static`, root `/` returns `index.html`, `/api/*` for data endpoints.
4. **Simulation thread.** Background thread auto-progresses active tasks (3s ticks, +3-12% per tick) — gives visual feedback even without real agents.
5. **React 18 + Babel from CDN.** `type="text/babel"` in script tags for JSX. No npm/node required.
6. **Pixel-art Canvas office.** Custom 2D Canvas engine draws rooms, furniture, agent sprites with smooth walking animation. NOT Phaser or PixiJS — pure Canvas API for zero deps.

### Backend API Shape
```
GET  /api/agents          → list all agents
GET  /api/agents/:id      → single agent
PATCH /api/agents/:id     → update room/status/progress
POST /api/tasks           → assign task (moves agent to target room)
PATCH /api/tasks/:id      → update progress/status
GET  /api/tasks           → list tasks
GET  /api/logs?limit=N    → recent logs
GET  /api/goals           → goals with progress
POST /api/goals           → create goal
GET  /api/health          → system status summary
```

### Agent-Task Flow
1. POST `/api/tasks` with `assigned_agent` and `title`
2. Backend auto-maps agent to target room, sets agent status=working
3. Frontend Canvas shows agent sprite walking to room (smooth lerp)
4. Simulation thread (or real agent) bumps progress via PATCH
5. At progress=100, agent returns to hallway, status=idle

### Pixel Office Canvas Engine
- 7 rooms defined with x/y/w/h, border colors, labels
- Furniture drawn per-room: desks, monitors (animated screen glow), bookshelves, server racks, cameras, easels, whiteboards, plants, safes
- Agent sprites: body + head + hair + arms + legs, bobbing animation when working, eye blinking, arm swing, name label, progress bar
- Smooth agent movement via lerp toward target position (1.5px/frame)
- Ambient floating particles for atmosphere
- CRT scanline overlay via CSS

### Updating Agent/Goal Definitions
Agent and goal data is seeded into SQLite on first run (when table is empty). To apply changes to agent roles, tools, or goals in `server.py`:
1. Kill the server
2. Delete the DB: `rm -f ~/agentic-os/data/agentic_os.db`
3. Restart — fresh seed runs with updated definitions
This is a destructive reset. Active tasks and logs are lost. For non-destructive updates, PATCH agents via the API.

### Launch
```bash
bash ~/agentic-os/launch.sh
# → http://localhost:3000
# Deps: pip install fastapi uvicorn aiofiles python-multipart
```

## Approach A-legacy — Vanilla React (static, no backend)

For simpler dashboards without agent state management. Loads React + Babel from CDN. Uses `config.json` as data source with `python3 -m http.server`.

### Key Rules
1. **config.json = single source of truth.** Hermes modifies this one file.
2. **Components are global functions.** Loaded via script tags in order. No import/export.
3. **python3 -m http.server** for serving. No npm, no node, no build step.

## Approach B — Streamlit (FALLBACK only)

Only if user explicitly asks for Streamlit.

### Architecture
```
project/
├── app.py           ← set_page_config, load CSS, sidebar radio nav, route pages
├── config.py        ← ALL settings in one file
├── helpers.py       ← JSON CRUD, Obsidian sync, metric computation
├── pages/*.py       ← each exports render() function
├── data/*.json      ← state files
└── static/theme.css ← single CSS file
```

### Import Pattern (every page file)
```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from helpers import *
from config import *
```

### Routing (single app.py, NOT Streamlit multipage)
```python
selected = st.radio("Navigate", list(pages.keys()), label_visibility="collapsed")
if page_name == "Home":
    from pages.home import render
    render()
```

## Color Palette (v3 Cyberpunk Theme)

```css
--bg-dark: #0a0e17;
--bg-card: #111827;
--bg-card-hover: #1a2332;
--border: #1e293b;
--text: #e2e8f0;
--text-dim: #64748b;
--text-muted: #475569;
--accent: #00ff88;      /* primary green */
--accent2: #00b4d8;     /* info blue */
--accent3: #e040fb;     /* purple */
--danger: #ef4444;
--warning: #f59e0b;
--success: #22c55e;
--info: #3b82f6;
```
Fonts: `'Press Start 2P'` (pixel headings) + `'JetBrains Mono'` (body/code)
CRT scanline overlay: `repeating-linear-gradient(0deg, transparent 2px, rgba(0,0,0,0.03) 4px)`

## Standard Pages for Agentic OS

| Page | What | Key Features |
|------|------|-------------|
| Dashboard | Overview | Metric cards, progress bars, activity feed |
| Chat | Dual agent | Hermes API + Claude CLI, shared knowledge |
| Goals | Tracking | Obsidian sync, categories, progress per goal |
| Identity | SOUL/USER/PURPOSE/REASONING | Editable, core values list |
| Knowledge | Shared brain | Both agents feed in, searchable, source-tagged |
| Upgrades | Evolution | Timeline, version tracking |
| Tools | Inventory | Hermes + Claude tools/skills with status |
| Agents | Status | Agent cards with connection status |

## Obsidian Goal Sync

Walk vault dir recursively (`/mnt/e/New folder (2)/Son`), find `- [ ]`/`- [x]` lines, import with category = parent folder name. Dedup by text content.

## Delegate to Subagents

Dashboard pages are independent — perfect for delegate_task parallelism. Provide each subagent:
- CSS class names available
- Helper functions / config shape
- Color palette
- Whether using React.createElement or JSX

## Pitfalls

1. **Streamlit multipage conflict.** Old `dashboard/pages/` with numbered files creates ghost nav items. Kill the `dashboard/` folder before rebuilding. Delete `__pycache__` dirs.
2. **pkill -f streamlit** can take multiple rounds — zombie processes block port. Verify with `pgrep`.
3. **python vs python3.** WSL doesn't alias `python` — always use `python3`.
4. **Vault path variants.** When doing bulk path replacement, `patch()` tool misses single-backslash variants. Use `execute_code` with Python `str.replace()` + `open()`.
5. **Old Obsidian path.** The vault moved from `C:\Users\USER\Documents\Obsidian Vault` to `E:\New folder (2)\Son`. Always check memory for current path.
6. **Script load order matters.** In vanilla React, components must be loaded before pages that use them. App.js loads last.
7. **User hates markdown-rendered dashboards.** Must be interactive — charts, forms, navigation, progress bars. Not pre-rendered markdown.
8. **User wants BOTH agents.** Chat section must have separate Hermes + Claude channels, both feeding into one shared knowledge base.
9. **PEP 668 blocks pip install on Python 3.14.** System Python refuses `pip install` without a venv. Fix: `pip install --break-system-packages <pkg>`. Use `execute_code` with `subprocess.run(["pip", "install", "--break-system-packages", ...])` if terminal blocks the command (heuristic falsely detects it as a long-lived server).
10. **terminal heuristic false positives.** `pip install` and `uvicorn` commands can trigger "long-lived server" detection in the terminal tool. Workaround: use `execute_code` with `subprocess.run()` for pip installs, and `terminal(background=True)` for the actual server.

## Support Files

- `references/agentic-os-v3-schema.md` — Agent IDs, room layout coordinates, SQLite schema, furniture types, sprite features
- `references/css-class-reference.md` — CSS class inventory for the theme
- `references/obsidian-sync.md` — Obsidian vault goal sync details
- `references/react-dashboard-blueprint.md` — Full config.json shape and component API
