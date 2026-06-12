---
name: railway-deployment
title: Railway Deployment
description: Deploying multi-service cloud applications to Railway.app — CLI setup, monorepo strategy, databases, env vars, and common pitfalls.
---

# Railway Deployment Guide

## CLI Installation (Linux/WSL)

**WARNING: The npm package `railway` is the TypeScript SDK, NOT the CLI.**
**The correct package is `@railway/cli`.**

**WSL pitfall:** npm global installs from Windows npm (under `/mnt/c/`) often install shims (`.cmd`, `.ps1`) that don't work from Linux. The `railway` shell script at `/mnt/c/Users/USER/AppData/Roaming/npm/railway` may fail with exit code 1 silently.

```bash
# Option A — npm install (may hang/timeout in WSL)
npm install -g @railway/cli

# Option B — use the GraphQL API directly (see below) when CLI is broken
```

## Authentication

```bash
railway login    # Opens browser for OAuth device flow
railway whoami   # Verify login
```

When logged in, the session token is stored at `~/.railway/config.json` under `user.accessToken`. Use this for direct API calls.

## Project Lifecycle

### CLI Commands (when working)
```bash
# Create project
railway init --name <project-name>

# Link directory to project
railway link -p <project-name> -e production --service <service-name>

# List services
railway service list

# View logs
railway logs --service <service-name>

# Redeploy
railway up --json
```

### Adding Services (via CLI)
```bash
# From GitHub repo
railway add --service <name> --repo owner/repo --branch main

# From Docker image (e.g. PostgreSQL)
railway add --image postgres:16 --service postgres-db
```

### Adding Services (via GraphQL API — when CLI is broken)

Use the token from `~/.railway/config.json` to hit `https://backboard.railway.com/graphql/v2`.

**Get your auth token:**
```bash
TOKEN="$(cat ~/.railway/config.json | python3 -c 'import sys,json; print(json.load(sys.stdin)["user"]["accessToken"])')"
```

**Full service lifecycle:**

```bash
# ── 1. Create service ──
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceCreate(input: { name: \"<service-name>\", projectId: \"<project-id>\", environmentId: \"<env-id>\" }) { id name } }"}'

# ── 2. Connect GitHub repo source ──
# Run AFTER serviceCreate. Without this, the service has no code source.
# Uses owner/repo format (no full URL).
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceConnect(id: \"<service-id>\", input: { repo: \"owner/repo\", branch: \"main\" }) { id name } }"}'

# ── 3. Set rootDirectory (mandatory for monorepos) ──
# Get the ServiceInstance ID first:
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ service(id: \"<service-id>\") { serviceInstances { edges { node { id rootDirectory builder } } } } }"}'
# Then set rootDirectory (path relative to repo root):
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceInstanceUpdate(serviceId: \"<service-id>\", input: { rootDirectory: \"/subdir-name\" }) }"}'

# ── 4. Set environment variables ──
# Set BEFORE deploying so the first deploy picks them up.
# The response is just {"data":{"variableUpsert":true}} — no echo of the value.
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { variableUpsert(input: { environmentId: \"<env-id>\", projectId: \"<project-id>\", serviceId: \"<service-id>\", name: \"MY_VAR\", value: \"my-value\" }) }"}'

# ── 5. Set cron schedule (for cron workers) ──
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceInstanceUpdate(serviceId: \"<service-id>\", input: { cronSchedule: \"0 10 * * *\" }) }"}'

# ── 6. Create a public domain ──
# Railway auto-assigns domains, but if none was created, do it explicitly.
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceDomainCreate(input: { serviceId: \"<service-id>\", environmentId: \"<env-id>\" }) { id domain } }"}'
# Returns e.g. {"data":{"serviceDomainCreate":{"id":"...","domain":"myservice-production-xxxx.up.railway.app"}}}

# ── 7. Trigger deployment ──
# Returns deployment ID as a plain string (no object with subfields).
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceInstanceDeployV2(serviceId: \"<service-id>\", environmentId: \"<env-id>\") }"}'

# ── 8. Check deployment status ──
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ deployment(id: \"<deployment-id>\") { id status } }"}'
# Status values: BUILDING, SUCCESS, FAILED, CRASHED, REMOVED

# ── 9. Delete service ──
# Returns {"data":{"serviceDelete":true}} — no subfields.
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceDelete(id: \"<service-id>\") }"}'

# ── 10. List all deployments for a service ──
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ deployments(input: {serviceId: \"<service-id>\"}) { edges { node { id status createdAt } } } }"}'
```

### Token Expiry & Refresh

Railway OAuth tokens expire after 1 hour. The token is stored at `~/.railway/config.json` under `user.accessToken`. When the API starts returning `{"errors":[{"message":"Not Authorized",...}]}` for ALL queries (not just specific ones), the token has expired.

**Refresh flow:**

```bash
# Read refresh token + client_id from config
REFRESH_TOKEN=$(python3 -c "import json; d=json.load(open('/home/user35909000/.railway/config.json')); print(d['user']['refreshToken'])")
CLIENT_ID=$(python3 -c "import json; d=json.load(open('/home/user35909000/.railway/config.json')); print(d.get('projectConfig',{}).get('clientId','rlwy_oaci_onEklvmksh1hRUiCo7E2zX12'))")

# CRITICAL: Must use application/x-www-form-urlencoded, NOT application/json
curl -s -X POST "https://backboard.railway.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=$REFRESH_TOKEN&client_id=$CLIENT_ID"

# → Returns {"access_token":"...","refresh_token":"...","expires_in":3600}
```

**Save the new token:**
```bash
# The old token is dead after refresh. Update config.json immediately.
# The new access_token goes into config.json's `user.accessToken`.
# The new refresh_token goes into `user.refreshToken`.
# Compute new expiry: current time + expires_in (3600s)
```

**Pitfalls:**
- The refresh endpoint ONLY accepts `application/x-www-form-urlencoded` — JSON POSTs will fail with `"invalid_request"`
- After refresh, the OLD token is immediately invalidated. Save the new token before making further API calls.
- The client_id is likely `rlwy_oaci_onEklvmksh1hRUiCo7E2zX12` (from the OAuth device flow). If `config.json` doesn't store it, hardcode this value.
- Tokens expire at `tokenExpiresAt` (Unix timestamp in `config.json`). Proactively refresh before expiry to avoid disruption.

**GraphQL API gotchas:**
- `serviceInstanceUpdate` returns `Boolean!` (no subfields) — the mutation itself is the result
- `serviceInstanceDeployV2` returns `String!` (the deployment ID) — also no subfields
- `variableUpsert` returns `Boolean!` — true means it worked
- `serviceConnect` returns `Service!` — you MUST add subfields `{ id name }` after the mutation call
- `serviceDelete` returns `Boolean!` — no subfields
- Builder enum values: `HEROKU`, `NIXPACKS`, `PAKETO`, `RAILPACK` — there is NO `DOCKERFILE` option. Railway auto-detects Dockerfiles when they exist in the build context (rootDirectory); no need to set builder explicitly.
- Service instance creation is implicit: after `serviceConnect` + git push, Railway auto-creates a ServiceInstance. You can check with `service { serviceInstances { edges { node { id } } } }`.

## Monorepo Deployment — The rootDirectory Pattern

**CRITICAL: When services are linked to a monorepo (single GitHub repo), Railway builds from the repo root by default. This causes Railpack to scan the monorepo root and fail to find the right entry point.**

**The fix: Set `rootDirectory` on each ServiceInstance via the GraphQL API.**

```bash
TOKEN="$(cat ~/.railway/config.json | python3 -c 'import sys,json; print(json.load(sys.stdin)[\"user\"][\"accessToken\"])')"

# First, find the ServiceInstance ID for your service
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"{ service(id: \\\"<service-id>\\\") { serviceInstances { edges { node { id rootDirectory builder } } } } }\"}"

# Then set rootDirectory (takes path relative to repo root, e.g. /telegram-bot)
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { serviceInstanceUpdate(serviceId: \\\"<service-id>\\\", input: { rootDirectory: \\\"/subdir-name\\\" }) }\"}"
```

After setting rootDirectory, push to GitHub to trigger a new deployment. Railway will build from the subdirectory and find the `railway.json` / `Dockerfile` there.

**Alternative: Standalone deploy directories** (used previously as a workaround):
```
/tmp/my-service-deploy/
├── Dockerfile
├── main.py
├── requirements.txt
├── railway.json
├── static/
└── .railway/config.json        # linked via `railway link`
```

## Dockerfile Patterns Per Service Type

### Web API (FastAPI/Uvicorn)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY static/ static/
EXPOSE $PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
```
- Needs `healthcheckPath: "/api/health"` in railway.json
- Must bind to `0.0.0.0`, not `127.0.0.1`

### Background Worker (long-polling loop)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .
EXPOSE $PORT
CMD python bot.py
```
Bot must include a health HTTP server (threaded) on `$PORT` to satisfy Railway's port-binding check:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading, os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
    def log_message(self, *a): pass

PORT = int(os.environ.get("PORT", 8080))
threading.Thread(target=HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever, daemon=True).start()
```

### Cron Worker (scheduled execution)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY script.py .
CMD python script.py   # script runs once and exits
```
- Set `cronSchedule: "0 10 * * *"` in railway.json deploy config
- Container starts, runs script, exits. Railway restarts it per schedule.
- No healthcheck needed (it finishes before Railway can check)

## Full Hermes Agent Deployment

Deploying the full Hermes AI agent to Railway requires careful Docker + config setup. This is NOT a simple Python bot — it's the full `hermes-agent` PyPI package with skills, memory, gateway, and Telegram platform.

### Architecture

```
Railway Container: hermes-agent
├── hermes-agent 0.14.0 (pip installed)
├── 84 builtin skills (auto-initialized at startup)
├── entrypoint.sh (generates config from env vars)
├── config.template.yaml (with {{PORT}} substitution)
└── skills/ directory (bundled in image at build time)
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pin to match local version for compatibility
RUN pip install --no-cache-dir hermes-agent==0.14.0

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY config.template.yaml /app/config.template.yaml

EXPOSE $PORT

ENTRYPOINT ["/app/entrypoint.sh"]
```

### entrypoint.sh Pattern

The entrypoint script must:
1. Generate `.env` from Railway environment variables
2. Generate `config.yaml` from a template (substituting `{{PORT}}`)
3. Set `HERMES_HOME` to a writable directory
4. Start `hermes gateway run --accept-hooks`

```bash
#!/bin/bash
set -e

HERMES_HOME="${HERMES_HOME:-/app/.hermes}"
export HERMES_HOME
mkdir -p "$HERMES_HOME/skills" "$HERMES_HOME/data" "$HERMES_HOME/cache" "$HERMES_HOME/logs"

# Generate .env from Railway env vars
cat > "$HERMES_HOME/.env" << EOENV
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_HOME_CHANNEL="${TELEGRAM_HOME_CHANNEL:-7044443781}"
EOENV

# Generate config.yaml from template (substitute {{PORT}})
PORT="${PORT:-8080}"
sed "s/{{PORT}}/$PORT/g" /app/config.template.yaml > "$HERMES_HOME/config.yaml"

exec hermes gateway run --accept-hooks
```

### config.template.yaml Pattern

The template uses `{{PORT}}` as a placeholder that the entrypoint substitutes:

```yaml
gateway:
  platforms:
    api_server:
      enabled: true
      host: 0.0.0.0    # Must be 0.0.0.0 for Railway
      port: {{PORT}}   # Substituted by entrypoint
    telegram:
      enabled: false   # Initially disabled to avoid token conflicts
```

**Strategy to avoid Telegram token conflicts** (local vs cloud Hermes using same bot token):
1. **Phase 1 — API-only**: Deploy with `telegram.enabled: false`. Test via Railway internal API.
2. **Phase 2 — Switch Telegram**: Stop local Hermes gateway. Set `telegram.enabled: true` in config. Redeploy.
3. Since only ONE instance of the bot is running at a time (cloud after local stops), getUpdates polling works without conflict.
4. Alternative: Use Telegram **webhook** mode instead of polling. Set webhook URL to the Railway domain. This is cleaner but requires the webhook endpoint to be implemented.

### Required Railway Env Vars

| Var | Required | Purpose |
|---|---|---|
| `DEEPSEEK_API_KEY` | ✅ | Primary model provider |
| `TELEGRAM_BOT_TOKEN` | ✅ (Phase 2) | Telegram platform |
| `TELEGRAM_HOME_CHANNEL` | ✅ | User's Telegram chat ID |

Optional: `ELEVENLABS_API_KEY`, business API keys, etc.

### Builtin vs Custom Skills

- **84 builtin skills** come bundled with the `hermes-agent` pip package — available automatically
- **5 local skills** (trading-analysis, business-operations, cloud-hosting, railway-deployment, streamlit-dashboard) are custom and must be re-added post-deployment
- Custom skills can be installed after deployment: `hermes skills install <name>` from within the container

### Railway Service Setup

```bash
# 1. Create service (no source yet)
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation { serviceCreate(input: { name: \"hermes-agent\", projectId: \"<project>\", environmentId: \"<env>\" }) { id name } }"}'

# 2. Connect GitHub repo
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation { serviceConnect(id: \"<service>\", input: { repo: \"owner/repo\", branch: \"main\" }) { id name } }"}'

# 3. Set rootDirectory
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation { serviceInstanceUpdate(serviceId: \"<service>\", input: { rootDirectory: \"/hermes-agent\" }) }"}'

# 4. Set env vars (per variableUpsert)
# 5. Create domain
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation { serviceDomainCreate(input: { serviceId: \"<service>\", environmentId: \"<env>\" }) { id domain } }"}'

# 6. Trigger deploy
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation { serviceInstanceDeployV2(serviceId: \"<service>\", environmentId: \"<env>\") }"}'
```

### Security: Token Handling

**NEVER expose token values in chat output.** When setting env vars or debugging:
- Use masked output: `"DEEPSEEK_API_KEY set ✅"` instead of echoing the value
- When reading tokens from files, strip them: `grep TOKEN .env | cut -d'=' -f2 | sed 's/./.../6'` to show only prefix
- If you must verify a token exists, check non-empty: `[ -n "$TOKEN" ] && echo "set" || echo "missing"`
- Railway's GraphQL API response for `variableUpsert` returns `{"data":{"variableUpsert":true}}` — no value echo. This is by design; respect it.
- The `config.yaml` references tokens in templates as `"${VAR_NAME:-}"` default-to-empty — avoid hardcoding defaults.

## Production Migration Protocol

Before switching any production traffic (e.g. Telegram from local → cloud), a **Pre-Flight Checklist** must pass. This is NOT optional — it protects against silent failures after the cutover.

### Phase 1: Staging Deployment (External Integration Disabled)

Deploy the service WITHOUT its primary external integration so it can be tested in isolation.

```yaml
# config.template.yaml — Phase 1
gateway:
  platforms:
    telegram:
      enabled: false  # External integration disabled
```

### Phase 2: Pre-Flight Checklist (ALL 5 Must Pass)

Run these tests in order. Do NOT proceed if any test fails — diagnose and fix first.

| # | Test | What to Verify | How |
|---|---|---|---|
| 1 | **Health endpoint** | Service responds 2xx on public URL | `curl -sS https://\<domain\>/api/health` — check status, uptime, agent count |
| 2 | **Memory persistence** | Agent can write + read memory across calls | Send a conversation, store a fact, start new session, verify fact is recalled |
| 3 | **Database read/write** | PostgreSQL (or SQLite) accepts writes + returns data | Create a record (task, log, note), query it, verify content matches |
| 4 | **Agent-to-agent communication** | Internal service mesh works | Cloud Hermes calls api-server or vice versa, verify response from Railway internal network |
| 5 | **Stability** | No crashes, leaks, degradation over time | Monitor for 30 minutes. Check: no restarts, error logs clean, memory stable, responses consistent |

**Failure diagnosis protocol:**
If ANY test fails:
1. Check deployment status (`BUILDING` / `SUCCESS` / `FAILED` / `CRASHED`)
2. Get APP logs (not build logs) — look for Python tracebacks
3. Identify the EXACT failing step + error message
4. Identify root cause (missing file, wrong path, env var, dependency)
5. Fix → push → redeploy → re-run from step 1
6. Do NOT skip tests or proceed with failures

### Phase 3: Cutover

Only after ALL 5 tests pass:
1. Update config to enable external integration (e.g. `telegram.enabled: true`)
2. Push to GitHub → trigger redeploy
3. Stop local service (kill PID, remove @reboot cron)
4. Verify external integration works end-to-end via actual usage
5. Monitor for 15 minutes after cutover — ready to rollback at first sign of trouble

### Phase 4: Rollback Readiness

Always have a rollback plan ready before cutover:
- Keep the old deployment's config or branch available for quick restore
- Know the kill command for the new service: `railway service delete --service \<name\> --yes`
- Have the local service ready to restart if cloud fails
- Document the exact rollback procedure in the deployment PR

## Docker Build Failure Diagnosis

When Railway build reports FAILED, follow this structured diagnosis before attempting fixes. **Do NOT guess or retry blindly.**

### Step 1: Get Build Status

```bash
# Via Railway API
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ deployments(input: {serviceId: \"<service-id>\"}) { edges { node { id status } } } }"}'
```

Status values: `BUILDING`, `SUCCESS`, `FAILED`, `CRASHED`, `REMOVED`.

### Step 2: Get Build Logs

```bash
# Via API (buildLogs field contains the Docker build output)
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ deployment(id: \"<deployment-id>\") { id status buildLogs } }"}'

# App logs (runtime output after container starts)
railway service logs --service <name> --json
```

### Step 3: Classify the Failure

| Failure Pattern | Look For in Build Logs | Likely Root Cause |
|---|---|---|
| **Missing package** | `pip install` error, `ModuleNotFoundError`, `E: Package not found` | requirements.txt typo, missing system dep in Dockerfile |
| **Missing file** | `COPY failed: file not found`, `No such file or directory`, `cannot stat` | Wrong rootDirectory, file not in build context, Dockerfile path typo |
| **Invalid Dockerfile** | `Dockerfile parse error`, `Unknown instruction`, `failed to solve with frontend` | Syntax error, invalid instruction, wrong base image name |
| **Requirements install failure** | `pip install` non-zero exit, dependency conflict, wheel build fails | Version conflict, platform mismatch, missing build tools (gcc, libpq-dev) |
| **Build context problem** | `Context must be a directory`, `file not found in build context` | rootDirectory doesn't exist in repo, Railway service not linked properly |
| **rootDirectory problem** | Railpack scans root, shows monorepo listing; `The app contents that Railpack analyzed contains:` lists all subdirs | rootDirectory NOT set on ServiceInstance via `serviceInstanceUpdate` mutation |
| **Permission problem** | `Permission denied`, `EACCES`, `cannot access` | File permissions in git, COPY tries to access protected path, chmod missing |
| **Architecture mismatch** | `Exec format error`, `cannot execute binary file` | Binary compiled for wrong arch (x86_64 binary on arm64 runner — rare on Railway) |

### Step 4: Locate the Failing Dockerfile Line

The build log usually annotates which RUN or COPY instruction failed. Cross-reference with the Dockerfile:
```bash
# Check the Dockerfile line that corresponds to the failing step
grep -n "RUN\|COPY\|FROM\|CMD" Dockerfile
```

### Step 5: Diagnose Root Cause

Ask these questions in order:
1. **Does the file referenced in the error actually exist in the repo at the expected path?** (Check git: `git ls-files <path>`)
2. **Is rootDirectory set on the Railway ServiceInstance?** (If missing, Railpack scans from monorepo root — this is the #1 cause of monorepo build failures)
3. **Does the Dockerfile instruction reference a file that exists in the build context?** (COPY paths are relative to rootDirectory)
4. **Is the pip package name correct?** (Typos in requirements.txt are extremely common)
5. **Does the base image tag exist for this architecture?** (e.g. `python:3.14-slim` may not exist on ARM)
6. **Are build-time dependencies installed?** (psycopg2 needs `gcc` + `libpq-dev`, many ML packages need `g++`, `cmake`)

### Step 6: Apply the Fix

Fix → `git push origin main` → Railway auto-deploys → verify status from Step 1.

**Never retry a deployment without evidence from the build logs.**

## Environment Variables

### Per-Service Railway-Auto-Injected Vars
- `PORT` — The port Railway expects the container to listen on
- `RAILWAY_SERVICE_NAME` — Name of the current service
- `RAILWAY_ENVIRONMENT_NAME` — Production/staging/etc.
- `RAILWAY_PUBLIC_DOMAIN` — The public URL (e.g. api-server-production-XXXX.up.railway.app)
- `RAILWAY_PRIVATE_DOMAIN` — Internal .railway.internal URL for cross-service communication
- `RAILWAY_SERVICE_<OTHER_SERVICE_NAME>_URL` — Auto-injected cross-service URLs in uppercase

### Manually Set Env Vars
Set these after service creation, then redeploy:
```bash
railway variables set KEY=value --service <service-name>
```

**Naming pitfall:** Ensure env var names in your code match what you set on Railway. Common mismatch: `TELEGRAM_TOKEN` in code vs `TELEGRAM_BOT_TOKEN` on Railway.

### PostgreSQL Database Linking
1. Add PostgreSQL service: `railway add --image postgres:16 --service postgres-db`
2. Railway auto-generates a `DATABASE_URL` on the postgres service
3. **CRITICAL: Copy `DATABASE_URL` as an env var on the api-server service** so the app can connect
4. The connection string is private (`.railway.internal`) — accessible only within Railway's network
5. In code: check for `DATABASE_URL` at startup → use PostgreSQL if set, SQLite fallback otherwise

## railway.json Schema

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/api/health",      // Web services only
    "cronSchedule": "0 10 * * *"           // Cron services only
  }
}
```

## Common Pitfalls

1. **CLI silent failure in WSL** — the `railway` npm shim exits with code 1 but no message. Fix: use GraphQL API directly or install `@railway/cli` properly.
2. **Static file paths in Docker** — `Path(__file__).parent` not `parent.parent`
3. **Healthcheck fails** — check `railway logs --json | grep -i error` for import/runtime errors; common cause: app listens on wrong host (use `0.0.0.0` not `127.0.0.1`)
4. **Env vars set after deploy** — must redeploy to pick up new vars (push to GitHub or trigger via API). Set env vars BEFORE the first deploy to avoid redeploy loops.
5. **Service created but no ServiceInstance** — `serviceCreate` does NOT auto-create a ServiceInstance when you omit `source.repo`. You must separately call `serviceConnect` to link the GitHub repo, THEN push to GitHub to trigger the first deployment which creates the instance. Check with `service { serviceInstances { edges { node { id } } } }`.
6. **railway.json not read** — when service is linked to monorepo root without `rootDirectory` set, Railway doesn't find subdirectory `railway.json` files. Always set `rootDirectory` per service via `serviceInstanceUpdate`.
7. **GitHub OAuth token stale** — in `~/.config/gh/hosts.yml`, tokens can expire. Re-auth with `gh auth login` if API returns 401.
8. **PostgreSQL DATABASE_URL not auto-linked** — must be manually copied as env var on consuming service; Railway does NOT auto-inject cross-service connection strings.
9. **All deployments FAILED** — check build logs via API: `deployment(id) { buildLogs }`. Common: wrong rootDirectory, missing Dockerfile, pip install failure, syntax error.
10. **Cron schedule not applying** — set `cronSchedule` via `serviceInstanceUpdate(serviceId, input: { cronSchedule: "..." })` mutation, matching Cron syntax. Railway's cron worker runs the container per schedule then stops it.
11. **serviceDomainCreate returns domain but URL 404s** — the domain is provisioned but the deployment may still be starting. Wait 30s and retry. If still 404, check deployment status (might be CRASHED/FAILED).
12. **Builder enum has no DOCKERFILE** — Railway auto-detects Dockerfiles in the build context. Don't try to set `builder: DOCKERFILE` — the API rejects it. Just put a Dockerfile in the rootDirectory and Railway uses it automatically with RAILPACK.
14. **OAuth token expires silently** — The `accessToken` in `~/.railway/config.json` expires after 1 hour (`tokenExpiresAt` field). All GraphQL API calls then return `"Not Authorized"` for ALL queries. Fix: refresh using the `refreshToken` with `grant_type=refresh_token` and `Content-Type: application/x-www-form-urlencoded`. Save the new tokens immediately since the old ones stop working.
15. **variableUpsert returns true but var not set** — verify you included `serviceId` (not just `projectId` + `environmentId`). Without `serviceId`, the var is project-wide. With `serviceId`, it's service-scoped.

## Verification
```bash
curl -s https://<url>/api/health
# Or via GraphQL API:
curl -s "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ deployments(input: {serviceId: \"<id>\"}) { edges { node { id status } } } }"}'
```
