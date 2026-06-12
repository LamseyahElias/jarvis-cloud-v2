---
name: cloud-hosting
description: "Deploy apps to cloud platforms (Railway, Vercel, Render, etc.) — CLI setup, authentication, project linking, deployment commands"
category: devops
---

# Cloud Hosting

Setup and deployment for cloud hosting platforms.

## Railway

### Install (WSL)

Railway CLI is a **standalone binary**, not an npm package.

```bash
# 1. Download the Linux binary from GitHub releases
curl -L -o /tmp/railway.tar.gz \
  "https://github.com/railwayapp/cli/releases/download/v5.12.0/railway-v5.12.0-x86_64-unknown-linux-gnu.tar.gz"

# 2. Extract and install to ~/.local/bin
cd /tmp && tar xzf railway.tar.gz
mkdir -p ~/.local/bin
cp railway ~/.local/bin/railway
chmod +x ~/.local/bin/railway
rm -f /tmp/railway.tar.gz /tmp/railway

# 3. Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Authenticate

```bash
railway login            # Opens OAuth in browser. Use PTY terminal mode.
railway whoami           # Verify: "Logged in as <email>"
```

### Common Commands

```bash
railway list                           # List all projects
railway list --json                    # List as JSON (includes deletedAt field)
railway link --project <name>          # Link cwd to a project (non-interactive, use PTY)
railway status                         # Show linked project info
railway status --json                  # Full JSON with deployments, services, domains
railway up                             # Upload cwd + deploy linked service
railway up --json                      # Same with JSON output
railway deploy                         # Alias
railway redeploy                       # Rebuild+redeploy latest (needs --yes in non-interactive)
railway run <command>                  # Run command with project env vars
railway delete --project <name> --yes  # Delete a project (non-interactive)
railway variable list --json           # List env vars with masked values
railway deployment list --json         # List all deployments with status
railway service list --json            # List services in linked environment
railway service source connect         # Connect a service to GitHub repo
railway service logs --json            # Get service logs
railway logs                           # Get deployment/logs for linked service
```

### Project Management

```bash
# Check project deletion status (deletedAt != null = deletion queued)
railway list --json | jq '.[] | {name: .name, deleted: .deletedAt}'

# Unlink current directory (must delete .railway/ manually if not interactive)
rm -rf .railway/

# Init a new project
railway init --name <name>
# NOTE: --name arg may still prompt for workspace selection in non-interactive mode.
# The project IS created even if the command times out waiting for input.
```

### Environment Variables

```bash
# List all variables (values masked)
railway variable list --json

# Set a variable
railway variable set KEY=value

# Remove a variable
railway variable remove KEY
```

#### Cross-Service URLs (Auto-Injected)

Railway automatically creates env vars for inter-service communication:

```
RAILWAY_SERVICE_<NAME>_URL    → https://<service>.up.railway.app
RAILWAY_PUBLIC_DOMAIN          → <current-service>.up.railway.app
RAILWAY_PRIVATE_DOMAIN         → <current-service>.railway.internal
RAILWAY_STATIC_URL             → <current-service>.up.railway.app
```

These are **automatically available** — no manual config needed. Services can discover each other by name. Useful in monorepos where the API server needs to know the Telegram bot URL, etc.

```bash
# Read a cross-service URL from within a Railway container
echo $RAILWAY_SERVICE_TELEGRAM_BOT_URL
echo $RAILWAY_SERVICE_API_SERVER_URL
```

### Domains

```bash
# Generate a Railway-provided domain for a service
railway domain --service <name>                 # returns domain URL
railway domain --service <name> --json          # returns {"domain": "https://..."}

# List existing domains for linked project
railway domain list

# Add a custom domain
railway domain <custom-domain.com>
```

Domains follow the pattern `https://<service>-<environment>-<hash>.up.railway.app`.

### Service Logs (Runtime vs Build)

Railway has two log streams:
- **Deploy logs** (`railway logs` / `railway deployment list`) — shows build output and healthcheck attempts
- **Service logs** (`railway service logs --service <name> --json`) — shows **application runtime output** (Python print, errors, tracebacks)

When a deployment shows SUCCESS but healthcheck fails, check service logs for runtime errors:

```bash
railway service logs --service <name> --json | grep -i "error\|traceback\|exception"
```

## Vercel

<!-- Vercel setup and deploy instructions live here when added -->

## Monorepo Deployment (Multiple Services in One Railway Project)

Railway does NOT natively support monorepo subdirectory routing via Railpack. Two reliable approaches:

### Approach A: Standalone Directory + Dockerfile (RECOMMENDED)

Each service deploys from its own standalone directory with its own Dockerfile.

```bash
# 1. Create standalone deploy directories per service
mkdir -p /tmp/api-deploy /tmp/tg-deploy /tmp/bd-deploy

# 2. Copy service-specific files to each deploy dir
cp -r project/api-server/main.py project/api-server/static/ \
  project/api-server/requirements.txt /tmp/api-deploy/
cp project/telegram-bot/bot.py project/telegram-bot/requirements.txt /tmp/tg-deploy/

# 3. Add a Dockerfile to each deploy dir
# api-deploy/Dockerfile:
: '
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY static/ static/
EXPOSE $PORT
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
'

# 4. Add railway.json (DOCKERFILE builder) to each deploy dir
: '{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "DOCKERFILE", "dockerfilePath": "Dockerfile" },
  "deploy": { "restartPolicyType": "ON_FAILURE", "restartPolicyMaxRetries": 10 }
}'

# 5. Add .railway/config.json pointing to the specific service
mkdir -p /tmp/api-deploy/.railway
echo "{\"project\":\"<project-id>\",\"environment\":\"<env-id>\",\"service\":\"<service-id>\"}" \
  > /tmp/api-deploy/.railway/config.json

# 6. Deploy from each standalone directory
cd /tmp/api-deploy && railway up
cd /tmp/tg-deploy  && railway up
```

### Approach B: GitHub Integration (requires rootDirectory via API for monorepos)

```bash
# Create services linked to GitHub repo
railway add --service api-server --repo owner/repo --branch main
railway add --service telegram-bot --repo owner/repo --branch main

# Deploy via GitHub push
git push origin main

# CRITICAL: For monorepos, set rootDirectory on each service's ServiceInstance
# via the GraphQL API. Without this, Railway builds from the repo root.
# See the railway-deployment skill for the full API workflow.
```

**Limitation:** Railway CLI has no `--rootDirectory` parameter. Must use the GraphQL API directly to set `rootDirectory` via `serviceInstanceUpdate` mutation. See `railway-deployment` skill for exact API calls.

### Linking Mechanics

Railway stores link info in `~/.railway/config.json` (global config) indexed by filesystem path:

```json
{
  "projects": {
    "/tmp/api-deploy": {
      "projectPath": "/tmp/api-deploy",
      "name": "jarvis-cloud",
      "project": "<project-uuid>",
      "environment": "<env-uuid>",
      "environmentName": "production",
      "service": "<service-uuid>"
    }
  }
}
```

- Each linked directory gets its own entry keyed by absolute path
- `railway link` creates this automatically
- `railway up` checks the cwd's path in this config

### Dockerfile Patterns for Railway

#### API Server (FastAPI)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY static/ static/
EXPOSE $PORT
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

#### Background Worker (Telegram Bot)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .
CMD ["python", "bot.py"]
```

#### Cron Worker
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY worker.py .
CMD ["python", "worker.py"]
```

**Key rules:**
- Use JSON-format `CMD` (`["cmd", "arg1"]`) not shell-format — Docker warns about OS signal handling with shell format
- `--no-cache-dir` keeps image size down
- `$PORT` is provided automatically by Railway (NOT port 8000)
- Always use `$PORT` in CMD, never hardcode ports
- Railway provides `RAILWAY_SERVICE_<NAME>_URL` env vars for cross-service discovery

### Healthcheck Debugging

```bash
# 1. Check deployment status
railway deployment list --json

# 2. Get APP logs (not build logs) — look for Python tracebacks
railway service logs --service <name> --json | grep -i "error\\|traceback\\|exception"

# 3. Common causes:
#    - Wrong static file path in Docker:
#      Local (file in subdir):     Path(__file__).parent.parent / "static"
#      Docker (file at /app/):     Path(__file__).parent / "static"
#    - Missing dependency (check requirements.txt)
#    - Port binding (must use $PORT, Railway does not use port 8000)
#    - Relative import paths break in Docker (files moved from app/ to root)
#    - Shell-format CMD causes SIGTERM issues: use JSON format ["python", "bot.py"]

# 4. Redeploy after fix:
railway redeploy   # needs --yes or PTY mode
```

### GraphQL API

Railway exposes GraphQL at `https://backboard.railway.app/graphql/v2`.

```bash
TOKEN=$(python3 -c "
import json
from pathlib import Path
d = json.load(open(Path.home() / '.railway' / 'config.json'))
print(d['user']['accessToken'])
")

# Query project details
curl -s https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ project(id: \"<id>\") { id name environments { edges { node { id name serviceInstances { edges { node { id serviceName latestDeployment { id status } } } } } } } }"}'
```

### User Workflow Preferences (Elias)

- **Fast action, no explanations.** Deploy first, report results. Don't narrate the plan before executing — just do it.
- **Clean-slate approach.** Delete broken state and rebuild properly rather than patching broken code.
- **Short confirmations.** "YES PROCEED" / "SON" style. Don't ask permission for obvious next steps.
- **Transparency on failure.** Say what broke and what fixed it — not why it wasn't your fault. No excuses.
- **No repeating yourself.** Don't say the same thing over and over. Say it once, act, move on.
- **Questions that need answers:** When you need the user to do something (browser auth, provide a token), give a CLEAR single instruction. Don't ask open-ended. Say "Open this URL: <link>" or "Paste your token here:" 
- **Scoping:** Before building, tell the user WHAT you'll build and ASK if the scope is right. Don't skip planning entirely, but keep it to 2-3 lines max.

## Pitfalls

- **Wrong npm package:** `npm install -g railway` installs the TypeScript SDK, not the CLI. The correct package is `@railway/cli` but its postinstall downloads a binary and may time out. Always use the direct GitHub release.
- **Windows npm is useless in WSL:** Railway installed via Windows npm (`AppData/Roaming/npm/railway.cmd`) is a batch file — WSL can't run it. Install a native Linux binary inside WSL.
- **OAuth needs a browser:** `railway login` opens a URL but can't complete without browser interaction. Always use PTY mode so the redirect URI localhost server can function.
- **npm global install fails:** `EACCES` on `/usr/local/lib/node_modules/` is standard in WSL. Fix: `npm config set prefix ~/.npm-global` or install binaries manually to `~/.local/bin/`.
- **No project linked:** `railway status` fails with "No linked project" unless you `railway link` first. This is per-directory.
- **Deletion is asynchronous:** `railway delete --yes` returns immediately but the project is only marked as deleted. It still shows in `railway list` until Railway purges it. Check `railway list --json | jq '.[].deletedAt'` to confirm deletion was accepted (non-null = queued).
- **Cannot create duplicate project names:** While a deleted project still exists (even marked deleted), you cannot create a new project with the same name. Use a fresh name.
- **`railway unlink` has no `--yes` flag:** Cannot unlink non-interactively. Delete `.railway/` manually: `rm -rf .railway/`.
- **Linking a new project needs fresh directory:** `railway link` can't be run from a directory that was already linked to a different project without unlinking first. Use `rm -rf .railway/` or a fresh temp directory.
- **Env var values are masked in CLI output:** `railway variable list --json` shows partial values with `***`. To read current values, use `railway run -- echo \$VAR_NAME`.
