# React Dashboard Blueprint — config.json Shape

The vanilla React dashboard is driven entirely by `config.json`. Here's the full schema:

```json
{
  "userName": "Elias",
  "fullName": "Elias Lamseyah",
  "location": "Morocco",
  "timezone": "Africa/Casablanca",
  "hermesApi": "http://127.0.0.1:8080",

  "identity": {
    "soul": "...",
    "user": "...",
    "purpose": "...",
    "reasoning": "...",
    "values": ["Protect capital", "Be profitable", ...]
  },

  "trading": {
    "instrument": "XAUUSD",
    "broker": "IC Markets",
    "platform": "MT5",
    "account": "#52887972",
    "leverage": "1:500",
    "mode": "demo"
  },

  "goals": [
    { "icon": "📈", "name": "...", "pct": 35, "category": "trading",
      "milestones": [{ "label": "...", "done": true }] }
  ],

  "targets": [
    { "name": "Morning Brief", "done": false, "progress": 0, "label": "Not started" }
  ],

  "upgrades": [
    { "icon": "🧠", "name": "...", "desc": "...", "priority": "High", "date": "..." }
  ],

  "agents": [
    { "name": "Hermes", "role": "Brain", "status": "active", "color": "#3b82f6", "icon": "🔵" }
  ],

  "tools": [
    { "name": "terminal", "agent": "hermes", "desc": "Execute shell commands", "status": "active" }
  ],

  "skills": [
    { "name": "trading-analysis", "agent": "hermes", "desc": "...", "status": "active" }
  ],

  "knowledge": [],
  "chatHermes": [],
  "chatClaude": []
}
```

## Component API

All components receive `{ config }` as props. Pages are global functions loaded via script tags.

| Component | Props | What |
|-----------|-------|------|
| Sidebar | currentPage, setCurrentPage, config | Left nav with 8 items |
| Header | currentPage, config | Page title + live clock |
| StatsCards | config | 5 metric cards from config data |
| Goals | config | Goal progress bars + milestones |
| Targets | config | Daily target checklist |
| Analysis | config | 4-card grid with trading stats |
| Upgrades | config | Timeline of upgrades |
| ObsidianVault | config | Vault info card |

## Location

Dashboard lives at `~/agentic-os/` (WSL home). Served via `python3 -m http.server 3000`.
Windows access: http://localhost:3000
