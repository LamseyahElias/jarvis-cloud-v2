# Known Plugin Folder ↔ Manifest ID Mismatches

When installing Obsidian community plugins headlessly (downloading from GitHub releases),
the folder name under `.obsidian/plugins/` MUST match the `id` field in `manifest.json`.

Many GitHub repos use a name that differs from their manifest ID. This causes Obsidian
to show "404 Not Found" in the community plugins list.

## Known Mismatches (verified 2026-05-22)

| GitHub Repo / Common Folder Name | Manifest `id` | Fix |
|----------------------------------|----------------|-----|
| `obsidian-homepage` (mirnovov) | `homepage` | Rename folder to `homepage/` |
| `obsidian-calendar-plugin` (liamcain) | `calendar-beta` | Rename folder to `calendar-beta/` |
| `advanced-tables-obsidian` (tgrosinger) | `table-editor-obsidian` | Matches if you use the repo name |

## Verification Script

Run from the vault root to check all installed plugins:

```bash
for d in .obsidian/plugins/*/; do
  folder="${d%/}"; folder="${folder##*/}"
  id=$(python3 -c "import json; print(json.load(open('${d}manifest.json'))['id'])" 2>/dev/null)
  if [ "$folder" = "$id" ]; then
    echo "✅ $folder"
  else
    echo "❌ MISMATCH: folder=$folder → manifest_id=$id (rename folder to $id)"
  fi
done
```

## Correct Install Flow

1. `mkdir -p .obsidian/plugins/TEMP_NAME/`
2. Download `main.js`, `manifest.json`, `styles.css` into it
3. Read the `id` from `manifest.json`
4. If folder name ≠ id, `mv .obsidian/plugins/TEMP_NAME .obsidian/plugins/CORRECT_ID`
5. Add the manifest `id` (not repo name) to `community-plugins.json`

## Recommended Plugin Set (with correct IDs)

Tested working set for a JARVIS-style vault:

```json
[
  "dataview",
  "templater-obsidian",
  "obsidian-kanban",
  "obsidian-mind-map",
  "obsidian-excalidraw-plugin",
  "obsidian-git",
  "calendar-beta",
  "table-editor-obsidian",
  "obsidian-style-settings",
  "quickadd",
  "homepage",
  "obsidian-checklist-plugin"
]
```
