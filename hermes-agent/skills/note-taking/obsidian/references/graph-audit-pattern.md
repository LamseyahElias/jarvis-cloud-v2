# Graph Audit Pattern — Orphan/Dead-End Analysis

## execute_code Script Skeleton

Use this inside `execute_code` to scan an entire vault and identify disconnected notes:

```python
import re
from hermes_tools import read_file, search_files

vault = "/mnt/e/New folder (2)/Son"  # resolve from memory or env

# 1. Get all .md files
result = search_files("*.md", target="files", path=vault)
files = result.get("files", [])

# 2. Read each file, extract wikilinks
file_links = {}
for filepath in files:
    rel = filepath.replace(vault + "/", "")
    r = read_file(filepath)
    content = r.get("content", "")
    links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
    file_links[rel] = [l.strip() for l in links]

# 3. Build note-name → file mapping
note_names = {}
for f in file_links:
    name = f.split("/")[-1].replace(".md", "")
    note_names[name] = f

# 4. Build incoming/outgoing maps
incoming = {name: [] for name in note_names}
outgoing = {}
for f, links in file_links.items():
    src = f.split("/")[-1].replace(".md", "")
    outgoing[src] = links
    for link in links:
        if link in incoming:
            incoming[link].append(src)

# 5. Report
orphans = [n for n in note_names if not incoming[n]]
dead_ends = [n for n in note_names if not outgoing.get(n, [])]
print(f"Orphans ({len(orphans)}): {orphans}")
print(f"Dead-ends ({len(dead_ends)}): {dead_ends}")
```

## Fixing Patterns

### Orphan (no incoming links)
Find the natural parent and add a wikilink FROM parent TO orphan:
- Convert `**filename.md**` → `[[filename|Display Name]]`
- Or add to a "See also" footer in the parent

### Dead-end (no outgoing links)
Append a footer:
```markdown
---

*See also: [[JARVIS Dashboard]] · [[Parent Note]] · [[Related Note]]*
```

### Canvas Mind Map — Adding File Nodes
```json
{"id": "unique-id", "type": "file", "file": "Business/Belditalk.md", "x": 820, "y": 700, "width": 220, "height": 50, "color": "2"}
```
Edge to connect:
```json
{"id": "edge-id", "fromNode": "parent-node-id", "toNode": "unique-id", "fromSide": "right", "toSide": "left"}
```

Canvas `type: "file"` nodes are clickable in Obsidian — they open the linked note. Use `type: "text"` only for conceptual headers.

## Color codes in canvas
- `"1"` = red
- `"2"` = green
- `"3"` = yellow  
- `"4"` = blue
- `"5"` = purple
- `"6"` = cyan/teal
