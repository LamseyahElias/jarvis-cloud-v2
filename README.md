# JARVIS Cloud — Agentic OS Monorepo

A 4-service monorepo for deploying **JARVIS** (Hermes AI agent) to Railway.

## Architecture

```
jarvis-cloud-v2/
├── api-server/          # FastAPI backend + Agentic OS dashboard (PORT)
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py      # All API routes ported from Agentic OS
│   ├── static/
│   │   └── index.html    # React dashboard (pixel-art office)
│   ├── requirements.txt
│   └── railway.json
├── telegram-bot/        # Telegram bot (TELEGRAM_TOKEN)
│   ├── bot.py
│   ├── requirements.txt
│   └── railway.json
├── belditalk-worker/    # Daily FB poster (FB_PAGE_TOKEN, cron 10AM)
│   ├── belditalk_post.py
│   ├── requirements.txt
│   └── railway.json
├── obsidian-vault/      # Git-synced knowledge base (empty stub)
│   └── README.md
├── .gitignore
└── README.md
```

## Services

| Service           | Description                          | Env Vars              | Schedule     |
|------------------|--------------------------------------|-----------------------|--------------|
| **api-server**   | FastAPI + SQLite + React dashboard   | `PORT`                | Always on    |
| **telegram-bot** | Telegram message relay               | `TELEGRAM_TOKEN`      | Always on    |
| **belditalk-worker** | Facebook daily post             | `FB_PAGE_TOKEN`       | Daily 10 AM  |
| **obsidian-vault** | Knowledge base (stub)             | —                     | Manual sync  |

## API Routes (api-server)

All routes are ported exactly from the local Agentic OS:

| Route              | Method | Description                |
|--------------------|--------|----------------------------|
| `/`                | GET    | Serves React dashboard     |
| `/api/health`      | GET    | System health check        |
| `/api/agents`      | GET    | List all agents            |
| `/api/agents/:id`  | GET    | Get single agent           |
| `/api/agents/:id`  | PATCH  | Update agent state         |
| `/api/tasks`       | GET    | List all tasks             |
| `/api/tasks`       | POST   | Create new task            |
| `/api/tasks/:id`   | PATCH  | Update task progress/status|
| `/api/tasks/:id`   | DELETE | Delete task                |
| `/api/logs`        | GET    | Get system logs            |
| `/api/goals`       | GET    | List strategic goals       |
| `/api/goals`       | POST   | Create new goal            |
| `/api/chat`        | POST   | Chat with Hermes           |

## Deployment (Railway)

Each service deploys separately within the same Railway project:

```bash
# Each is a service pointed at its subdirectory
railway login
cd api-server && railway up
cd ../telegram-bot && railway up
cd ../belditalk-worker && railway up
```

## Local Development

```bash
# API server
cd api-server
pip install -r requirements.txt
python -m app.main

# Telegram bot
cd telegram-bot
TELEGRAM_TOKEN=xxx python bot.py

# BeldiTalk poster
cd belditalk-worker
FB_PAGE_TOKEN=xxx python belditalk_post.py
```

## Tech Stack

- **Backend**: Python 3.13, FastAPI, SQLite (SQLAlchemy-ready)
- **Frontend**: React 18 (CDN), Babel standalone, Canvas 2D
- **Infra**: Railway (RAILPACK build, health checks, cron)
