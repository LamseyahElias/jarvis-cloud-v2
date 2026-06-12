# Agentic OS — Boot & Operations Reference

Elias's personal agentic operating system at `/mnt/c/Users/USER/agentic-os/`.
Combines Hermes (scheduler/crons) + Claude Code (reasoning) + MT5 bridge (trading) + Obsidian (memory).

## Boot Sequence

### Step 1: Start Hermes API server (localhost)
```
terminal(background=true, command="hermes gateway run")
# Verify:
curl -s http://127.0.0.1:8080/health
# Expect: {"status": "ok", "platform": "hermes-agent"}
```

### Step 2: Boot Agentic OS via Claude Code
```
terminal(background=true, notify_on_complete=true,
  command='cd /mnt/c/Users/USER/agentic-os && claude -p "Boot sequence. Read CLAUDE.md, SOUL.md, AGENTS.md, GOALS.md, and memory/session.md. Then run the morning brief skill: check today\'s date, summarize priorities, check trading status, check business pipeline status. Write the brief to memory/session.md appending a new entry. Be concise and actionable." --dangerously-skip-permissions')
```

### CRITICAL: Do NOT attempt interactive mode from Hermes
Claude Code's interactive TUI requires a real terminal emulator. From Hermes:
- `pty=true` alone → fails with "Input must be provided either through stdin or as a prompt argument when using --print"
- `background=true` + `pty=true` → process runs but produces no capturable output
- `script -q -c "claude" /dev/null` → same failure as pty=true
- **Only `-p` (print mode) works.** No exceptions. Don't waste tokens retrying.

For interactive Claude Code sessions, the user must open their own terminal:
```
cd C:\Users\USER\agentic-os
claude
```

### Why --dangerously-skip-permissions
When the boot prompt involves file operations (reading SOUL.md, writing session.md, etc.), Claude Code in `-p` mode will hang waiting for permission approvals unless `--dangerously-skip-permissions` is used. Always include it for Agentic OS boot commands that read/write project files.

### Running as background with notification
Use `background=true` + `notify_on_complete=true` since boot can take 30-60 seconds. This lets JARVIS continue working while the Agentic OS boots, then report the result when it arrives.

## File Structure
```
agentic-os/
├── CLAUDE.md          ← Claude Code reads this on boot (entry point)
├── SOUL.md            ← Agent personality, identity, rules
├── AGENTS.md          ← Governance: hard limits, approvals, coordination
├── GOALS.md           ← Current targets and priorities
├── .agents/skills/    ← Claude Code skills (trading, morning-brief, daily-note, vault-cleanup, infinity-mirror)
└── memory/
    ├── session.md     ← Current runtime state
    ├── trade-log.md   ← All trades
    └── lessons.md     ← Hard lessons encoded
```

## Running Skills
```
claude -p "morning brief" --dangerously-skip-permissions --max-turns 10
claude -p "resume trading" --dangerously-skip-permissions --max-turns 15
```
Always include `--dangerously-skip-permissions` when skills need to read/write files.

## Key Facts
- Claude Code v2.1.148 installed at /mnt/c/Users/USER/AppData/Roaming/npm/claude
- Agentic OS CLAUDE.md also references an OpenClaw/Cleo agent system at ~/.openclaw/ (legacy)
- Trading crons are managed by Hermes, NOT by Claude Code directly
- The system reads SOUL.md for identity, AGENTS.md for governance limits (daily loss cap $15, max trade loss $5, no overnight positions without approval)
- Saturday/Sunday: markets closed, trading status will always be "paused/off"
