# Hermes Agent Docker Deployment to Railway

## Background

The full Hermes AI agent (`hermes-agent` PyPI package v0.14.0) was deployed to Railway as part of the JARVIS Cloud migration. Unlike simple web APIs or Telegram bots, the Hermes agent requires:

- The full `hermes-agent` Python package with all dependencies
- Config generation from Railway environment variables
- Skills directory (builtin skills auto-initialized at first run)
- Gateway with both API server and Telegram platforms
- No token conflicts with locally-running Hermes instances

## Key Files

### `hermes-agent/Dockerfile`

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir hermes-agent==0.14.0
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY config.template.yaml /app/config.template.yaml
EXPOSE $PORT
ENTRYPOINT ["/app/entrypoint.sh"]
```

Key decisions:
- `python:3.11-slim` matches the local venv (Python 3.11.15)
- `apt-get install git` is needed because `hermes setup` may check for git
- No `--break-system-packages` needed inside Docker (no PEP 668 restrictions)
- `ENTRYPOINT` not `CMD` so the shell script can set env vars before exec

### `hermes-agent/entrypoint.sh`

Responsibilities in order:
1. Set `HERMES_HOME` (defaults to `/app/.hermes` if not set by Railway)
2. Create directory structure: `skills/`, `data/`, `cache/`, `logs/`
3. Generate `.env` from Railway env vars using a heredoc (all vars default to empty string)
4. Substitute `{{PORT}}` in config template → write to `$HERMES_HOME/config.yaml`
5. Warn if required vars are missing (DEEPSEEK_API_KEY, TELEGRAM_BOT_TOKEN)
6. `exec hermes gateway run --accept-hooks`

The `--accept-hooks` flag is critical for non-interactive mode — without it, the gateway may hang waiting for TTY approval on first-run security hooks.

### `hermes-agent/config.template.yaml`

Uses `{{PORT}}` as a placeholder. The YAML linter will flag this as invalid — that's expected. The entrypoint script does `sed "s/{{PORT}}/$PORT/g"` before Hermes reads the file.

Key config differences from local:
- `gateway.platforms.api_server.host: 0.0.0.0` (not `127.0.0.1`)
- `gateway.platforms.api_server.port: {{PORT}}` (not `8765`)
- `gateway.platforms.telegram.enabled: false` initially (token conflict avoidance)
- `terminal.auto_source_bashrc: false` (no .bashrc in Docker container)
- No `plugin` entries (obsidian-context-bridge not available)

## Railway Service IDs

During this session:
- `hermes-agent` service ID: `3d6b0c1d-b4ff-4a72-af6e-9120631e4ad7`
- ServiceInstance ID: `b6b275f2-8b52-4edc-9144-30e30601bae9`
- Domain: to be assigned after deployment succeeds
- rootDirectory: `/hermes-agent`

## Env Vars Set on Railway Service

| Name | Value (masked) |
|---|---|
| `DEEPSEEK_API_KEY` | `sk-58c8...78` |
| `TELEGRAM_BOT_TOKEN` | `861051...Ie0Y` |
| `TELEGRAM_HOME_CHANNEL` | `7044443781` |

## Token Conflict Avoidance Strategy

**Problem:** Local Hermes (running on WSL) and cloud Hermes (deploying to Railway) use the same Telegram bot token `8610511473:AAEx_MVq6mO3Fe_2Msf7NfOZgzIiI0Ie0Y` (@lamseyahbot). Both using `getUpdates` long-polling causes message loss — Telegram delivers each update to whichever poller picks it up first.

**Solution — Phased Rollout:**
1. Deploy cloud Hermes with `telegram.enabled: false` — only API server runs
2. Test cloud Hermes via API calls (conversations, agents, memory, DB)
3. Once verified working: stop local Hermes gateway (`kill` PID, remove `@reboot` cron)
4. Enable `telegram.enabled: true` in config template → push to GitHub → redeploy
5. Only ONE instance is polling at any time → no conflict

**Alternative (Webhook):** Set Telegram webhook via `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<railway-domain>/webhook`. This makes Telegram push updates directly to Railway. Disables local `getUpdates` automatically. Cleaner but requires webhook endpoint implementation in the cloud bot.

## Testing the Cloud Hermes (API-only Phase)

Once deployed (Phase 1), test via:
```bash
# Hermes gateway API (on Railway, accessible via public domain)
curl -s https://<hermes-agent-domain>/api/health

# Or from another Railway service (internal networking):
curl -s http://<hermes-agent-service>.railway.internal:8080/api/health
```

The Hermes gateway API server exposes endpoints for messaging and status. The cloud api-server service can proxy requests to the cloud Hermes for agent-to-agent communication.

## Local vs Cloud Skills

| Source | Count | Available on Cloud? |
|---|---|---|
| Builtin (bundled with pip) | 84 | ✅ Auto-initialized |
| Local (custom: trading, business) | 5 | ❌ Must re-add post-deploy |

Custom skills to re-add post-deployment:
- `business-operations` (business launch workflows)
- `trading-analysis` (XAUUSD analysis — limited use since MT5 is local)
- `cloud-hosting` (this skill — meta!)
- `railway-deployment` (this skill — meta!)
- `streamlit-dashboard` (dashboard building)

## Common Docker Pitfalls

1. **`pip install hermes-agent` fails on slim images** — missing build dependencies for some packages. Use `python:3.11-slim` (not `3.13-slim`) and install `git` for setup checks.
2. **Gateway hangs at startup** — missing `--accept-hooks` flag. The gateway waits for TTY approval of security hooks.
3. **Config file not found** — `$HERMES_HOME` not set or template substitution failed. Check entrypoint logs.
4. **Skills not loading** — builtin skills are created on first `hermes gateway run`. If they don't appear, run `hermes skills list` to verify. Custom skills must be explicitly installed.
5. **Port binding conflicts** — Hermes API server and Railway's PORT must match. Set `gateway.platforms.api_server.port: {{PORT}}` in template.
6. **Telegram token conflict** — both local and cloud polling same bot. Use phased rollout (see above).
