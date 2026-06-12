# Codex on WSL — Windows Execution Patterns

## The Problem

Codex CLI is typically installed via Windows npm (`C:\Users\<user>\AppData\Roaming\npm\codex`).
Running it from WSL fails with: `Missing optional dependency @openai/codex-linux-x64`.
Installing the Linux version via WSL npm consistently hangs or times out.

## Solution: Run via cmd.exe

Codex must be invoked through the Windows side. Two patterns:

### Pattern 1: Direct cmd.exe (simple prompts, no quotes)
```
cmd.exe /c "cd /d C:\path\to\repo && codex exec --sandbox workspace-write \"simple prompt\""
```

### Pattern 2: Bat wrapper (complex prompts, recommended)
Write a `.bat` file to avoid quote-escaping hell:
```bat
@echo off
cd /d "E:\path\to\repo"
codex exec --sandbox danger-full-access "Your complex prompt with 'quotes' and special chars"
```
Invoke from WSL:
```
terminal(command='cmd.exe /c "C:\\Users\\USER\\run_codex.bat"', pty=true, timeout=120)
```

## Windows Sandbox Bug (v0.133.0)

The default sandbox mode (`workspace-write`) fails on Windows with:
```
ERROR codex_core::exec: exec error: windows sandbox: spawn setup refresh
```
Every shell command Codex tries to run fails before PowerShell starts.

**Fix:** Use `--sandbox danger-full-access`. This bypasses the sandbox entirely.
The old `--full-auto` flag (now deprecated) maps to `workspace-write` which has the same bug.

## Non-Git Directories

Codex refuses to run outside a git repo. For non-code directories (Obsidian vaults, docs repos):
```bash
cd "/path/to/directory"
git init
git add -A
git commit -m "init"
```
Then point Codex at it. Codex will be able to read all committed files and write new ones.

## Version Notes (v0.133.0)

- Default model: gpt-5.5
- `--full-auto` deprecated → use `--sandbox workspace-write`
- `--yolo` removed → use `--sandbox danger-full-access`
- Sandbox modes: `read-only`, `workspace-write`, `danger-full-access`
