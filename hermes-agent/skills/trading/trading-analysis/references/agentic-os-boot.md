# Agentic OS — Reference (updated 2026-05-23)

The Agentic OS dashboard was rebuilt as a vanilla React app (no Streamlit).
Full architecture is in the **streamlit-dashboard** skill (which now covers both approaches).

## Current Location
- **Dashboard:** `~/agentic-os/` (WSL home, NOT C:\Users\USER\ anymore)
- **Launch:** `python3 -m http.server 3000` or `bash ~/agentic-os/launch.sh`
- **URL:** http://localhost:3000
- **Data:** `config.json` (single file, all data)
- **Stack:** React 18 (CDN) + Babel + vanilla CSS

## Identity Clarification (still relevant to trading)
- **JARVIS is a nickname for Hermes Agent** — not a separate system.
- Elias prefers "Hermes" as the name.
- Claude Code and Hermes Agent are separate tools — don't conflate them.
