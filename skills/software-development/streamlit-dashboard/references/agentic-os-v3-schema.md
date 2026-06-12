# Agentic OS v3 — Schema Reference

## Agents (seeded on first run)

| id       | name            | role (short)                  | tools                                           | default_room    | color   | icon |
|----------|-----------------|-------------------------------|------------------------------------------------|-----------------|---------|------|
| ceo      | CEO Hermes      | Orchestrator                  | Hermes CLI, Obsidian, Memory, Cron             | ceo_office      | #00ff88 | 👔   |
| trading  | Trading Agent   | XAUUSD Scalper                | RPyC/MT5, yfinance, ta, pandas                 | trading_room    | #ff6b35 | 📈   |
| research | Research Agent  | Intel & Analysis              | web_search, arXiv, Polymarket                  | research_room   | #00b4d8 | 🔬   |
| coding   | Coding Agent    | Full-Stack Dev                | Claude Code, Codex, GitHub, Node.js, React     | dev_room        | #e040fb | 💻   |
| content  | Content Agent   | Creative & Marketing          | ElevenLabs TTS, Canva API, TikTok API          | content_studio  | #ffd60a | 🎨   |
| finance  | Finance Agent   | Money & Metrics               | Notion (ntn CLI), spreadsheets, trade logs     | finance_room    | #4caf50 | 💰   |
| memory   | Memory Agent    | Knowledge Ops                 | Obsidian, Hermes Memory, session_search        | research_room   | #ab47bc | 🧠   |
| security | Security Agent  | Guard & Monitor               | terminal, cron, process monitor                | hallway         | #ef5350 | 🛡️   |

## Default Goals (seeded on first run)

| id | title                                            | initial % |
|----|--------------------------------------------------|-----------|
| g1 | Launch Belditalk.com — content, social, email, Discord | 35    |
| g2 | Trading Account $54 → $200 (20-pip challenge)    | 15        |
| g3 | Full Agent Autonomy — all agents self-operating   | 10        |
| g4 | Infinity Mirror Maroc — product line & website    | 5         |
| g5 | Agentic OS — real agent integration (not simulation) | 20     |

## Rooms (Canvas coordinates)

| id              | label          | x   | y   | w   | h   | border_color |
|-----------------|----------------|-----|-----|-----|-----|-------------|
| ceo_office      | CEO Command    | 30  | 30  | 240 | 170 | #00ff88     |
| trading_room    | Trading Floor  | 300 | 30  | 250 | 170 | #ff6b35     |
| research_room   | Research Lab   | 580 | 30  | 220 | 170 | #00b4d8     |
| dev_room        | Dev Workshop   | 30  | 260 | 240 | 170 | #e040fb     |
| content_studio  | Content Studio | 300 | 260 | 250 | 170 | #ffd60a     |
| finance_room    | Finance Ops    | 580 | 260 | 220 | 170 | #4caf50     |
| hallway         | (central)      | 30  | 210 | 770 | 40  | #2a3a4e     |
| meeting_room    | Meeting Room   | 580 | 440 | 220 | 50  | #ab47bc     |

## SQLite Tables

```sql
agents: id, name, role, room, status, current_task, progress, last_action, avatar_color, sprite_char, created_at, updated_at
tasks:  id, title, description, assigned_agent, target_room, status, progress, priority, created_at, started_at, completed_at
logs:   id, agent_id, task_id, message, level, timestamp
goals:  id, title, progress, status, created_at
```

## Furniture Types Available
desk_large, desk_row, monitor, screen_wall, bookshelf, plant, whiteboard, server_rack, camera, easel, safe, filing_cabinet, table_round

## Agent Sprite Features
- 14px tall pixel character with body/head/hair/arms/legs
- Bobbing animation when working (sin wave)
- Eye blinking (periodic)
- Arm swing when working
- Name label above head (first name only)
- Status indicator dot (green=idle, amber=working)
- Progress bar below feet when working
- Smooth walking via lerp (1.5px/frame toward target)

## API Integrations Available
- **ElevenLabs:** TTS for content (env: ELEVENLABS_API_KEY) — ready
- **Canva:** Design automation (env: CANVA_CLIENT_ID, CANVA_CLIENT_SECRET) — needs OAuth
- **TikTok:** Content publishing (env: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET) — needs OAuth
- **Notion:** ntn CLI v0.14.1 installed — needs `ntn login`
