---
name: codex
description: "Delegate coding to OpenAI Codex CLI (features, PRs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing

Requires the codex CLI and a git repository.

## Authentication

Codex needs either OAuth login or an API key:

### Option A: API Key (recommended — works from any device)
1. Generate a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Pipe it in:
   ```bash
   printenv OPENAI_API_KEY | codex login --with-api-key
   ```
3. Or set `OPENAI_API_KEY` in `~/.hermes/.env`

### Option B: Device Auth (OAuth flow)
```bash
codex login --device-auth
```
Shows a URL + code to visit on any device. **Known issue:** This can hang when invoked via `powershell.exe` from WSL with no output. If it hangs (empty output after 15s), kill it and use the API key method instead.

### Option C: Hermes-Managed Auth
`model.provider: openai-codex` uses Hermes-managed Codex OAuth from `~/.hermes/auth.json` after `hermes auth add openai-codex`.

### Checking auth status
```bash
codex login status
```

### User-side key generation (from phone)
The user can generate an OpenAI API key on their phone by visiting https://platform.openai.com/api-keys, clicking "Create new secret key", and sending the key to the agent to pipe into `codex login --with-api-key`.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI auth configured: either `OPENAI_API_KEY` or Codex OAuth credentials
  from the Codex CLI login flow
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

For Hermes itself, `model.provider: openai-codex` uses Hermes-managed Codex
OAuth from `~/.hermes/auth.json` after `hermes auth add openai-codex`. For the
standalone Codex CLI, a valid CLI OAuth session may live under
`~/.codex/auth.json`; do not treat a missing `OPENAI_API_KEY` alone as proof
that Codex auth is missing.

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --sandbox workspace-write 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--sandbox workspace-write` | Auto-approves file changes in workspace (default for `exec`) |
| `--sandbox danger-full-access` | No sandbox, no approvals (fastest, most dangerous) |
| `--sandbox read-only` | Can only read, no writes |

> **Deprecated flags (v0.133+):** `--full-auto` is replaced by `--sandbox workspace-write`. `--yolo` is replaced by `--sandbox danger-full-access`. Old flags may still work but emit warnings.

## WSL + Windows Execution

On WSL, Codex is typically installed via **Windows npm** (`/mnt/c/.../npm/codex`) and must be invoked through `cmd.exe` when working on Windows-side paths. The WSL Linux npm install often hangs or fails due to missing `@openai/codex-linux-x64`.

**The bat-wrapper pattern** — required when the prompt contains quotes or special characters that cmd.exe mangles:

```bat
@echo off
cd /d "E:\path\to\repo"
codex exec --sandbox danger-full-access "Your prompt here with quotes"
```

Then invoke from WSL:
```
terminal(command='cmd.exe /c "C:\\Users\\USER\\run_codex.bat"', pty=true, timeout=120)
```

### Windows Sandbox Bug

The default `--sandbox workspace-write` mode can fail on Windows with:
```
ERROR codex_core::exec: exec error: windows sandbox: spawn setup refresh
```
**Workaround:** Use `--sandbox danger-full-access` instead. This bypasses the sandbox entirely but allows Codex to actually execute commands.

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex exec --sandbox danger-full-access 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex exec --sandbox danger-full-access 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch. For non-code directories (e.g. Obsidian vaults), `git init && git add -A && git commit -m "init"` first.
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--sandbox workspace-write` for building** — auto-approves changes within the sandbox (replaces old `--full-auto`)
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work
8. **On WSL, use cmd.exe wrapper** — Codex installed on Windows npm won't run natively in WSL. Use a `.bat` file or `cmd.exe /c` to invoke it.
9. **Windows sandbox broken** — if you hit `windows sandbox: spawn setup refresh`, switch to `--sandbox danger-full-access`

## Support Files

- `references/wsl-windows-patterns.md` — detailed WSL→Windows execution patterns, sandbox bug details, non-git directory setup
