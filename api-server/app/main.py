#!/usr/bin/env python3
"""JARVIS Cloud — FastAPI backend with SQLite state (ported from Agentic OS)."""

import json, time, uuid, sqlite3, os, threading
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Data directory — Railway provides /data or we use a local /data/
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "agentic_os.db"

# Also ensure app-level data dir exists (for local dev)
Path(__file__).parent.parent.joinpath("data").mkdir(exist_ok=True)

app = FastAPI(title="JARVIS Cloud — Agentic OS", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── Database ────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        room TEXT NOT NULL DEFAULT 'hallway',
        status TEXT NOT NULL DEFAULT 'idle',
        current_task TEXT DEFAULT '',
        progress INTEGER DEFAULT 0,
        last_action TEXT DEFAULT '',
        avatar_color TEXT DEFAULT '#00ff88',
        sprite_char TEXT DEFAULT '🤖',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        assigned_agent TEXT REFERENCES agents(id),
        target_room TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        progress INTEGER DEFAULT 0,
        priority TEXT DEFAULT 'normal',
        created_at TEXT DEFAULT (datetime('now')),
        started_at TEXT,
        completed_at TEXT
    );
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        task_id TEXT,
        message TEXT NOT NULL,
        level TEXT DEFAULT 'info',
        timestamp TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    # Seed default agents if empty
    if conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0] == 0:
        agents = [
            ("ceo",       "CEO Hermes",      "Orchestrator · Delegates tasks, monitors all agents, makes strategic decisions · Tools: Hermes CLI, Obsidian, Memory, Cron",  "ceo_office",   "#00ff88", "👔"),
            ("trading",   "Trading Agent",   "XAUUSD Scalper · MT5 bridge, auto-scalper, position manager, market analysis · Tools: RPyC/MT5, yfinance, ta, pandas", "trading_room", "#ff6b35", "📈"),
            ("research",  "Research Agent",   "Intel & Analysis · Web research, arXiv, competitor analysis, market data · Tools: web_search, arxiv, Polymarket, NotebookLM (manual)",  "research_room","#00b4d8", "🔬"),
            ("coding",    "Coding Agent",     "Full-Stack Dev · Builds websites, APIs, dashboards, scripts · Tools: Claude Code, Codex, GitHub, Node.js, Python, React",      "dev_room",     "#e040fb", "💻"),
            ("content",   "Content Agent",    "Creative & Marketing · Social media, video scripts, Darija lessons, designs · Tools: ElevenLabs TTS, Canva API, TikTok API","content_studio","#ffd60a","🎨"),
            ("finance",   "Finance Agent",    "Money & Metrics · Revenue tracking, P&L, invoicing, budget forecasts · Tools: Notion (ntn CLI), spreadsheets, trade logs","finance_room", "#4caf50", "💰"),
            ("memory",    "Memory Agent",     "Knowledge Ops · Obsidian vault, skill management, session history, context · Tools: Obsidian, Hermes Memory, session_search","research_room","#ab47bc","🧠"),
            ("security",  "Security Agent",   "Guard & Monitor · API key rotation, system health, cron watchdog, backups · Tools: terminal, cron, process monitor",     "hallway",      "#ef5350", "🛡️"),
        ]
        for a in agents:
            conn.execute(
                "INSERT INTO agents (id, name, role, room, avatar_color, sprite_char) VALUES (?,?,?,?,?,?)", a
            )
        # Seed default goals
        goals = [
            ("g1", "Launch Belditalk.com — content, social, email, Discord", 35),
            ("g2", "Trading Account $54 → $200 (20-pip challenge)", 15),
            ("g3", "Full Agent Autonomy — all agents self-operating", 10),
            ("g4", "Infinity Mirror Maroc — product line & website", 5),
            ("g5", "Agentic OS — real agent integration (not simulation)", 20),
        ]
        for g in goals:
            conn.execute("INSERT INTO goals (id, title, progress) VALUES (?,?,?)", g)
        conn.commit()
        _log(conn, "ceo", None, "JARVIS Cloud v3 initialized. All agents reporting for duty.", "system")
    conn.close()

def _log(conn, agent_id, task_id, message, level="info"):
    conn.execute("INSERT INTO logs (agent_id, task_id, message, level) VALUES (?,?,?,?)",
                 (agent_id, task_id, message, level))
    conn.commit()

# ─── Models ──────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assigned_agent: str
    target_room: str = ""
    priority: str = "normal"

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None

class GoalCreate(BaseModel):
    title: str
    progress: int = 0

class ChatMessage(BaseModel):
    message: str
    model: str = "hermes"

class AgentUpdate(BaseModel):
    room: Optional[str] = None
    status: Optional[str] = None
    current_task: Optional[str] = None
    progress: Optional[int] = None
    last_action: Optional[str] = None

# ─── Routes ──────────────────────────────────────────────────────────

@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")

# --- Agents ---
@app.get("/api/agents")
async def list_agents():
    conn = get_db()
    rows = conn.execute("SELECT * FROM agents ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Agent not found")
    return dict(row)

@app.patch("/api/agents/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate):
    conn = get_db()
    agent = conn.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
    if not agent: raise HTTPException(404, "Agent not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        sets = ", ".join(f"{k}=?" for k in updates)
        vals = list(updates.values()) + [agent_id]
        conn.execute(f"UPDATE agents SET {sets}, updated_at=datetime('now') WHERE id=?", vals)
        conn.commit()
        if "room" in updates:
            _log(conn, agent_id, None, f"Moved to {updates['room']}")
        if "status" in updates:
            _log(conn, agent_id, None, f"Status → {updates['status']}")
    row = conn.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
    conn.close()
    return dict(row)

# --- Tasks ---
@app.get("/api/tasks")
async def list_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/tasks")
async def create_task(body: TaskCreate):
    conn = get_db()
    agent = conn.execute("SELECT * FROM agents WHERE id=?", (body.assigned_agent,)).fetchone()
    if not agent: raise HTTPException(400, f"Agent '{body.assigned_agent}' not found")

    # Determine target room from agent's default if not specified
    room_map = {
        "ceo": "ceo_office", "trading": "trading_room", "research": "research_room",
        "coding": "dev_room", "content": "content_studio", "finance": "finance_room",
        "memory": "research_room", "security": "hallway"
    }
    target = body.target_room or room_map.get(body.assigned_agent, "hallway")
    task_id = f"task-{uuid.uuid4().hex[:8]}"

    conn.execute(
        "INSERT INTO tasks (id, title, description, assigned_agent, target_room, priority, status, started_at) VALUES (?,?,?,?,?,?,?,datetime('now'))",
        (task_id, body.title, body.description, body.assigned_agent, target, body.priority, "active")
    )
    # Update agent state
    conn.execute(
        "UPDATE agents SET room=?, status='working', current_task=?, progress=0, last_action=?, updated_at=datetime('now') WHERE id=?",
        (target, body.title, f"Started: {body.title}", body.assigned_agent)
    )
    _log(conn, body.assigned_agent, task_id, f"📋 New task assigned: {body.title}", "task")
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict(row)

@app.patch("/api/tasks/{task_id}")
async def update_task(task_id: str, body: TaskUpdate):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task: raise HTTPException(404, "Task not found")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if "status" in updates and updates["status"] == "completed":
        updates["completed_at"] = datetime.utcnow().isoformat()
        updates["progress"] = 100
        # Move agent back to hallway and set idle
        conn.execute(
            "UPDATE agents SET room='hallway', status='idle', current_task='', progress=0, last_action=?, updated_at=datetime('now') WHERE id=?",
            (f"Completed: {task['title']}", task["assigned_agent"])
        )
        _log(conn, task["assigned_agent"], task_id, f"✅ Task completed: {task['title']}", "success")
    elif "progress" in updates:
        conn.execute(
            "UPDATE agents SET progress=?, last_action=?, updated_at=datetime('now') WHERE id=?",
            (updates["progress"], f"Progress: {updates['progress']}%", task["assigned_agent"])
        )

    if updates:
        sets = ", ".join(f"{k}=?" for k in updates)
        vals = list(updates.values()) + [task_id]
        conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", vals)
        conn.commit()

    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict(row)

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task: raise HTTPException(404)
    if task["status"] == "active":
        conn.execute(
            "UPDATE agents SET room='hallway', status='idle', current_task='', progress=0 WHERE id=?",
            (task["assigned_agent"],)
        )
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

# --- Logs ---
@app.get("/api/logs")
async def list_logs(limit: int = 50):
    conn = get_db()
    rows = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Goals ---
@app.get("/api/goals")
async def list_goals():
    conn = get_db()
    rows = conn.execute("SELECT * FROM goals ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/goals")
async def create_goal(body: GoalCreate):
    conn = get_db()
    gid = f"g-{uuid.uuid4().hex[:6]}"
    conn.execute("INSERT INTO goals (id, title, progress) VALUES (?,?,?)", (gid, body.title, body.progress))
    conn.commit()
    row = conn.execute("SELECT * FROM goals WHERE id=?", (gid,)).fetchone()
    conn.close()
    return dict(row)

# --- Chat ---
@app.post("/api/chat")
async def chat(body: ChatMessage):
    return {
        "reply": "Echo: " + body.message,
        "model": body.model,
        "timestamp": datetime.utcnow().isoformat()
    }

# --- System Health ---
@app.get("/api/health")
async def health():
    conn = get_db()
    agents = conn.execute("SELECT COUNT(*) as c FROM agents").fetchone()["c"]
    active_tasks = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE status='active'").fetchone()["c"]
    total_tasks = conn.execute("SELECT COUNT(*) as c FROM tasks").fetchone()["c"]
    completed = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE status='completed'").fetchone()["c"]
    conn.close()
    return {
        "status": "operational",
        "agents_online": agents,
        "active_tasks": active_tasks,
        "total_tasks": total_tasks,
        "completed_tasks": completed,
        "uptime": "99.9%",
        "timestamp": datetime.utcnow().isoformat()
    }

# --- Simulation: auto-progress active tasks ---
def _simulation_tick():
    """Every 3 seconds, nudge active tasks forward by 5-15%."""
    import random
    while True:
        time.sleep(3)
        try:
            conn = get_db()
            active = conn.execute("SELECT * FROM tasks WHERE status='active'").fetchall()
            for t in active:
                bump = random.randint(3, 12)
                new_prog = min(t["progress"] + bump, 100)
                if new_prog >= 100:
                    conn.execute("UPDATE tasks SET status='completed', progress=100, completed_at=datetime('now') WHERE id=?", (t["id"],))
                    conn.execute(
                        "UPDATE agents SET room='hallway', status='idle', current_task='', progress=0, last_action=? WHERE id=?",
                        (f"✅ Completed: {t['title']}", t["assigned_agent"])
                    )
                    _log(conn, t["assigned_agent"], t["id"], f"✅ Task completed: {t['title']}", "success")
                else:
                    conn.execute("UPDATE tasks SET progress=? WHERE id=?", (new_prog, t["id"]))
                    conn.execute(
                        "UPDATE agents SET progress=?, last_action=? WHERE id=?",
                        (new_prog, f"Working... {new_prog}%", t["assigned_agent"])
                    )
            conn.commit()
            conn.close()
        except Exception:
            pass

# Mount static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "static"), name="static")

@app.on_event("startup")
async def startup():
    init_db()
    t = threading.Thread(target=_simulation_tick, daemon=True)
    t.start()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
