# Obsidian Vault Goal Sync — Implementation

## Vault Location
WSL: `/mnt/e/New folder (2)/Son`
Windows: `E:\New folder (2)\Son`

## Sync Logic (from helpers.py)

```python
def sync_obsidian_goals():
    """Walk vault, find checklist items, import as goals."""
    imported = 0
    vault = Path("/mnt/e/New folder (2)/Son")
    if not vault.exists():
        return imported
    
    existing = {g["text"] for g in get_goals()}
    
    for md_file in vault.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("- [ ]") or line.startswith("- [x]"):
                done = line.startswith("- [x]")
                item = line[5:].strip().lstrip("] ").strip()
                if item and item not in existing and len(item) > 3:
                    goals.append({
                        "id": len(goals) + 1,
                        "text": item,
                        "category": md_file.parent.name.lower() or "general",
                        "status": "completed" if done else "pending",
                        "progress": 100 if done else 0,
                        "source": f"obsidian:{md_file.name}",
                        "created": now_str(),
                        "updated": now_str(),
                    })
                    existing.add(item)
                    imported += 1
    return imported
```

## Key Details
- Category derived from parent folder name (lowercased)
- Dedup by exact text match against existing goals
- Minimum 3 chars to skip noise
- Source tagged as `obsidian:<filename>` for traceability
- First sync imported 404 goals from Elias's vault
- Supports both `- [ ]` (pending) and `- [x]` (completed)
