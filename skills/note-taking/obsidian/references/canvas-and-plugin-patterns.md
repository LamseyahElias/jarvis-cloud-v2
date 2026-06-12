# Obsidian Canvas Format & Plugin Configuration

## Canvas File Format (.canvas)

Obsidian renders `.canvas` files as a visual node-and-edge graph. The file is JSON:

```json
{
  "nodes": [
    {
      "id": "unique-string",
      "type": "text",
      "text": "**Markdown** content here",
      "x": 0, "y": 0,
      "width": 250, "height": 60,
      "color": "4"
    }
  ],
  "edges": [
    {
      "id": "edge-unique-string",
      "fromNode": "node-id-1",
      "toNode": "node-id-2",
      "fromSide": "right",
      "toSide": "left"
    }
  ]
}
```

### Node properties
- `id`: unique string per node
- `type`: `"text"` (inline markdown), `"file"` (embed a vault note), `"link"` (embed URL), `"group"` (visual container)
- `text`: markdown content (for type=text)
- `file`: vault path like `"Trading/Playbook.md"` (for type=file)
- `x`, `y`: canvas coordinates (0,0 = center; negative values go left/up)
- `width`, `height`: pixel dimensions
- `color`: `"1"` red, `"2"` orange, `"3"` yellow, `"4"` green, `"5"` cyan, `"6"` purple

### Edge properties
- `fromSide` / `toSide`: `"top"`, `"bottom"`, `"left"`, `"right"`

### Layout tips for mind maps
- Center node at (0, 0) with larger dimensions (400×100)
- Branch nodes radiate outward: right-side branches use positive x, left-side use negative x
- Vertical spread: 200-300px between nodes vertically, 400-500px between branch levels horizontally
- A 6-branch mind map with ~20 nodes per branch = ~130 nodes, ~33KB file

## Plugin Installation (headless, no GUI)

Community plugins live in `.obsidian/plugins/<plugin-id>/`. Each needs:
- `main.js` (required) — the plugin code
- `manifest.json` (required) — plugin metadata
- `styles.css` (optional) — plugin styles
- `data.json` (optional) — plugin configuration

### Download from GitHub releases

```bash
VAULT="/path/to/vault"
PLUGIN_ID="dataview"
REPO="blacksmithgu/obsidian-dataview"

mkdir -p "$VAULT/.obsidian/plugins/$PLUGIN_ID"
curl -sL "https://github.com/$REPO/releases/latest/download/main.js" \
  -o "$VAULT/.obsidian/plugins/$PLUGIN_ID/main.js"
curl -sL "https://github.com/$REPO/releases/latest/download/manifest.json" \
  -o "$VAULT/.obsidian/plugins/$PLUGIN_ID/manifest.json"
curl -sL "https://github.com/$REPO/releases/latest/download/styles.css" \
  -o "$VAULT/.obsidian/plugins/$PLUGIN_ID/styles.css" 2>/dev/null
```

### Enable plugins

Write `.obsidian/community-plugins.json` with an array of plugin IDs:
```json
["dataview", "templater-obsidian", "obsidian-kanban", "calendar"]
```

**Important:** Plugins are installed but disabled until the user toggles them ON in Settings → Community Plugins. The `community-plugins.json` registers them; the user still needs to enable each one.

### Common plugin configs (data.json)

**Homepage** (obsidian-homepage) — auto-open a note on startup:
```json
{
  "version": 3,
  "defaultNote": "JARVIS Dashboard",
  "openMode": "Replace all open notes",
  "openOnStartup": true,
  "refreshDataview": true
}
```

**Dataview** — enable JS queries and inline fields:
```json
{
  "enableDataviewJs": true,
  "enableInlineDataviewJs": true,
  "refreshEnabled": true,
  "refreshInterval": 2500,
  "allowHtml": true,
  "prettyRenderInlineFields": true,
  "prettyRenderInlineFieldsInLivePreview": true
}
```

### Recommended plugin set for a JARVIS-style vault

| Plugin ID | Repo | Purpose |
|-----------|------|---------|
| dataview | blacksmithgu/obsidian-dataview | Query engine |
| templater-obsidian | SilentVoid13/Templater | Templates |
| obsidian-kanban | mgmeyers/obsidian-kanban | Kanban boards |
| obsidian-mind-map | lynchjames/obsidian-mind-map | Mind maps |
| obsidian-excalidraw-plugin | zsviczian/obsidian-excalidraw-plugin | Diagrams |
| obsidian-git | Vinzent03/obsidian-git | Git backup |
| calendar | liamcain/obsidian-calendar-plugin | Calendar |
| table-editor-obsidian | tgrosinger/advanced-tables-obsidian | Tables |
| obsidian-style-settings | mgmeyers/obsidian-style-settings | Themes |
| quickadd | chhoumann/quickadd | Quick capture |
| obsidian-homepage | mirnovov/obsidian-homepage | Auto-open |
| obsidian-checklist-plugin | delashum/obsidian-checklist-plugin | Checklists |

### Pitfall: obsidian-daily-notes-interface-plugin
This is a developer library (liamcain), NOT a user-facing plugin. It has no GitHub releases. Skip it — the core Daily Notes feature works without it.
