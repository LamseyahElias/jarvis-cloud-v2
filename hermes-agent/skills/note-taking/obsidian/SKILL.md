---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Hermes inside Obsidian (WSL)

Template launcher `.bat` file: `templates/hermes-launcher.bat` — deploy to `C:\Users\<username>\hermes.bat` and point the Obsidian terminal plugin profile at it.

## Installing plugins from the agent

Obsidian community plugins can be installed without the GUI by writing files directly into `.obsidian/plugins/<plugin-id>/`:

1. **Get release assets** from GitHub:
   ```bash
   curl -sL "https://api.github.com/repos/<owner>/<repo>/releases/latest" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(a['browser_download_url']) for a in d.get('assets',[])]"
   ```
2. **Download** `main.js`, `manifest.json`, and `styles.css` (if present) into `.obsidian/plugins/<plugin-id>/`. **CRITICAL:** After downloading, read `manifest.json` and verify the folder name matches the `id` field. Many repos use a different name than the manifest ID (e.g. `obsidian-homepage` repo → `homepage` ID). Rename the folder if they don't match — Obsidian will show "404 Not Found" otherwise.
3. **Enable the plugin** by adding its ID to `.obsidian/community-plugins.json`:
   ```json
   {"community-plugins": ["terminal", "dataview", "templater-obsidian"]}
   ```
4. **Write plugin config** (optional) to `.obsidian/plugins/<plugin-id>/data.json`.
5. **Restricted mode** must be off. If setting up a fresh vault, also write `.obsidian/app.json` and `.obsidian/appearance.json` so the vault opens configured.

### Terminal plugin (polyipseity/obsidian-terminal)

Plugin ID: `terminal`. Gives an embedded terminal inside Obsidian — useful for running Hermes directly in the vault.

- GitHub: `polyipseity/obsidian-terminal`
- Config (`data.json`): set `executable` to `wsl.exe` with `args: "-d Ubuntu"` on Windows, or the shell path on Linux/macOS.
- Hotkey: bind `terminal:open-terminal` to Ctrl+` via `.obsidian/hotkeys.json`.

## Launching Obsidian from WSL

## Bulk Vault Build Workflow

When building or restructuring an entire vault (new vault, major expansion):

1. **Scan first** — `search_files(target="files", pattern="*.md")` + check `.obsidian/plugins/` and `.obsidian/community-plugins.json` to understand current state
2. **Install plugins** — download from GitHub releases into `.obsidian/plugins/<id>/`, update `community-plugins.json`
3. **Configure plugins** — write `data.json` for each plugin that needs config (homepage, dataview especially)
4. **Configure app** — write `.obsidian/app.json` (attachments folder, line numbers, etc.) and `.obsidian/appearance.json`
5. **Create folder structure** — `mkdir -p` all content folders
6. **Write notes** — use `write_file` for each note with YAML frontmatter, [[wikilinks]], and consistent tags
7. **Create dashboard/MOC** — a central hub note linking every other note, configured as homepage
8. **Create visual map** — `.canvas` file for mind map view (see `references/canvas-and-plugin-patterns.md`)
9. **Clean up** — delete empty/default files (Welcome.md, Untitled.md, etc.)

All notes should have: YAML frontmatter (tags, date), [[wikilinks]] cross-referencing related notes, link back to the dashboard.

## Launching Obsidian from WSL

On WSL, Obsidian lives on the Windows side. Common install path:
```
/mnt/c/Users/<username>/AppData/Local/Programs/Obsidian/Obsidian.exe
```

Launch with:
```bash
cmd.exe /c start "" "C:\Users\<username>\AppData\Local\Programs\Obsidian\Obsidian.exe"
```

To open a specific vault, use the Obsidian URI protocol (though the user may need to select the vault on first open):
```bash
cmd.exe /c start "" "obsidian://open?path=C:\Users\<username>\Documents\Obsidian Vault"
```

## Fresh vault bootstrap

When creating a vault from scratch, set up these `.obsidian` files:

| File | Purpose |
|------|---------|
| `community-plugins.json` | List of enabled plugin IDs |
| `app.json` | Core settings (new file location, attachment folder, link update behavior) |
| `appearance.json` | Editor settings (line numbers, live preview, fold, spellcheck) |
| `hotkeys.json` | Custom keybindings |
| `workspace.json` | Sidebar and pane layout |

Create the folder structure first (`mkdir -p`), then write notes with `[[wikilinks]]` cross-referencing each other. Obsidian resolves wikilinks by note title, so `[[My Note]]` finds `any/path/My Note.md` automatically.

## Ingesting External Folders

When the user provides a folder path to import into the vault (e.g. business docs, project files):

1. **Copy the folder** into the vault under the appropriate section (e.g. `Business/<folder-name>/`)
2. **Extract text from PDFs** — use `pdftotext` (from `poppler-utils`) since pymupdf/fitz may not be installed:
   ```bash
   pdftotext '/path/to/file.pdf' -    # outputs to stdout
   ```
   If `pdftotext` is missing: `sudo apt-get install -y poppler-utils`
3. **Read and study** all documents to understand the content
4. **Create a summary note** (`.md`) in the vault with:
   - YAML frontmatter (tags, date, aliases)
   - Structured summary of all documents
   - Key data points, financials, timelines
   - [[wikilinks]] to related vault notes
   - Agent assessment / analysis section
   - Link back to [[dashboard/hub note]]
5. **Update the dashboard** to link the new note
6. **Git commit** if vault is git-tracked

This pattern works for business plans, project docs, research papers, or any document collection the user wants to bring into the vault knowledge graph.

## Git-Tracking the Vault

If delegating vault work to Codex or Claude Code, the vault must be a git repo. Initialize with:
```bash
cd "/path/to/vault" && git init && git add -A && git commit -m "Initial vault commit"
```
Commit after each batch of changes to maintain history and enable agent delegation.

## Support Files

- `references/canvas-and-plugin-patterns.md` — Obsidian canvas JSON format (mind maps), headless plugin installation from GitHub releases, plugin data.json configs, recommended plugin set
- `references/plugin-id-mismatches.md` — Known cases where GitHub repo names differ from manifest IDs (causes 404 errors), verification script, correct install flow
- `references/graph-audit-pattern.md` — execute_code script skeleton for orphan/dead-end analysis, wikilink regex, fixing patterns for orphans/dead-ends/canvas nodes

## Multi-Agent Vault Access

When multiple AI agents (Codex, Claude Code) need to work with the vault:

1. **Initialize as git repo** — Codex requires a git repository. Run `git init && git add -A && git commit -m "init"` in the vault root.
2. **Write agent guide files** — Create a `JARVIS/CODEX.md` (or similar) that explains the vault structure, active projects, conventions, and rules to the external agent. This saves tokens and prevents the agent from misunderstanding the vault's purpose.
3. **Guide file contents:** vault folder tree, current projects/goals, how the agent should behave (preserve frontmatter, use wikilinks, don't modify SOUL.md), and links to key notes.
4. **After agent writes:** commit changes, verify note quality (frontmatter, wikilinks, formatting), and update the dashboard MOC with links to new notes.

## Vault Link Health Check (Orphan Wiring)

When the user says notes are "not connected" or asks to "link everything," run a full orphan analysis:

1. **Scan all .md files** with `search_files(target="files", pattern="*.md")`
2. **Read every file via `execute_code`** using `read_file()` in a loop — extract `[[wikilinks]]` with regex `r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'`
3. **Build incoming/outgoing link maps** — note name = filename without `.md`
4. **Identify orphans** (no incoming links) and **dead-ends** (no outgoing links)
5. **Fix orphans** by adding wikilinks FROM parent/hub notes. Convert plain-text references (`**filename.md**`) to `[[filename|Display Name]]`
6. **Fix dead-ends** by appending a `*See also: [[Hub]] · [[Related]]*` footer
7. **Update the `.canvas` mind map** if one exists — add `type: "file"` nodes for missing notes + connecting edges
8. **Git commit** with a summary of changes

Key patterns for linking:
- Ops files → link back to parent project note + Operations Hub + Dashboard
- Trade logs → link to Trading Journal + Playbook + Risk Management
- Session logs → link from Logs.md
- System status files → cross-link each other
- SOUL/identity files → link to Dashboard + Agent Config + Capabilities

## Pitfalls

1. **Vault path may contain spaces.** Always quote paths in terminal commands. File tools handle this natively.
2. **`.obsidian` directory is hidden.** Use `search_files` with the full `.obsidian` path to inspect plugin state.
3. **Plugin changes require Obsidian restart** (or at minimum a vault reload) to take effect. Writing files into `.obsidian/plugins/` does not hot-load them.
4. **On WSL, the vault lives on the Windows filesystem** (`/mnt/c/...` or other mounted drives like `/mnt/e/`). File operations work but are slower than native Linux paths due to the 9P filesystem bridge.

5. **Vault path discovery on WSL.** The authoritative source is `obsidian.json` on the Windows side: `cat /mnt/c/Users/<username>/AppData/Roaming/obsidian/obsidian.json`. It contains a `vaults` object mapping IDs to `{path, ts, open}`. Windows paths use `\\` — convert to `/mnt/<drive>/...` for WSL access.

6. **Delegating vault work to Codex/Claude Code.** Both agents require a git repository. If the vault isn't already git-tracked, run `git init && git add -A && git commit -m "init"` before delegating. For Codex on WSL specifically, invoke via `cmd.exe /c` with a `.bat` wrapper pointing at the Windows path (e.g. `E:\New folder (2)\Son`), and use `--sandbox danger-full-access` because the default sandbox is broken on Windows.

7. **Terminal plugin + Hermes on Windows/WSL.** The Obsidian terminal plugin runs executables from the Windows side. To launch Hermes (which lives in WSL), create a `.bat` launcher:
   ```bat
   @echo off
   title JARVIS (Hermes Agent)
   :loop
   C:\Windows\System32\wsl.exe -d Ubuntu -- bash -lc "cd ~ && hermes"
   echo [Session ended. Restarting...]
   timeout /t 3 /nobreak >nul
   goto loop
   ```
   Point the terminal plugin profile to this `.bat` file with `useWin32Conhost: true`. The restart loop prevents the terminal from going blank if hermes exits.

8. **Terminal plugin profile config.** Set `executable` to the `.bat` path and `args: []` (empty). Setting `wsl.exe` directly as executable with hermes in args often fails with "command not found" because WSL non-login shells don't load PATH from `.bashrc`/`.profile`.

9. **Plugin folder name MUST match manifest.json `id` field.** This is the #1 cause of "404 Not Found" errors after headless plugin installs. Many plugins have a GitHub repo name that differs from their manifest ID (e.g. repo `obsidian-homepage` → manifest `id: "homepage"`, repo `obsidian-calendar-plugin` → manifest `id: "calendar-beta"`). After downloading, always read `manifest.json` and rename the folder to match the `id` field. Quick verification:
   ```bash
   for d in .obsidian/plugins/*/; do
     folder="${d%/}"; folder="${folder##*/}"
     id=$(python3 -c "import json; print(json.load(open('${d}manifest.json'))['id'])")
     [ "$folder" != "$id" ] && echo "MISMATCH: folder=$folder manifest_id=$id"
   done
   ```
   Also update `community-plugins.json` to use the manifest IDs, not the folder names you initially chose.

10. **community-plugins.json uses manifest IDs, not folder names.** The array entries must match the `id` field from each plugin's `manifest.json`. Using the GitHub repo name or a custom folder name will cause Obsidian to not recognize the plugin.
