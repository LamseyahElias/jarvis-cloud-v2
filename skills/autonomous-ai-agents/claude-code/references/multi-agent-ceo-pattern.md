# Multi-Agent CEO Pattern: Hermes + Claude Code + Codex

## When to Use
Hermes acts as CEO/orchestrator, deploying Claude Code and Codex as parallel workers for large builds (websites, startup packages, major refactors). Each agent gets a well-scoped task while Hermes manages project state, verification, and vault sync.

## The Pattern

### 1. Scaffold the Project
```
mkdir -p project/{public/images,src,scripts}
git init && git checkout -b main
```
Copy assets (logos, reference docs) into the project.

### 2. Write CLAUDE.md — The Spec
This is the critical step. CLAUDE.md is the project brief that Claude Code reads automatically. Include:
- **What this is** — one paragraph
- **Tech stack** — what to use and what NOT to use
- **Design direction** — colors, fonts, inspiration, feel
- **Brand assets** — paths to logos, images
- **Detailed section specs** — every page/section with content, layout, behavior
- **Integration specs** — exact form action URLs, checkout link placeholders, script tags
- **Key requirements** — responsive, SEO, accessibility
- **DO NOT list** — explicit anti-patterns to avoid

The more specific the CLAUDE.md, the fewer turns Claude Code needs. For Belditalk, a 13KB CLAUDE.md with exact Mailchimp form URLs and Lemon Squeezy script tags produced a 3047-line site with all integrations wired on the first pass.

### 3. Commit and Deploy Claude Code
```
git add -A && git commit -m "Initial scaffold"
claude -p "Read CLAUDE.md carefully. Build the ENTIRE [thing] as described. Follow every specification exactly." \
  --allowedTools "Read,Write,Edit,Bash" --max-turns 30
```
Key flags:
- `--allowedTools "Read,Write,Edit,Bash"` — full file access, no dangerous perms dialog
- `--max-turns 30` — enough for a full website build
- NOT `--dangerously-skip-permissions` — `allowedTools` is safer and skips the dialog

### 4. Deploy Codex in Parallel (via bat wrapper on WSL)
Write a `.bat` file for complex prompts (avoids cmd.exe quote escaping):
```bat
@echo off
cd /d "C:\path\to\project"
codex exec --sandbox danger-full-access "Your detailed prompt here"
```
Invoke: `cmd.exe /c "C:\Users\USER\run_codex.bat"` with pty=true

Codex is good for: documentation, ops files, templates, business content.
Claude Code is good for: websites, apps, complex code, multi-file builds.

### 5. Verify and Commit
```
# Check files exist and have content
wc -l project/public/index.html
# Launch and test
python3 -m http.server 3001 --directory project/public
# Commit
git add -A && git commit -m "Full build complete"
```

### 6. Integration Verification Pattern
After any build that includes third-party integrations, run a batch check:
```python
# via execute_code
checks = {
    "Mailchimp form": "list-manage.com",
    "Lemon Squeezy script": "lemon.js",
    "Checkout links": "lemonsqueezy.com/checkout/buy",
    "Pricing section": 'id="pricing"',
    # etc.
}
for name, pattern in checks.items():
    r = search_files(pattern=pattern, path="public/index.html")
    count = len(r.get("matches", []))
    print(f"{'✅' if count > 0 else '❌'} {name}: {count} matches")
```
This is faster and more reliable than grepping one-by-one.

### 7. Deploy
```
vercel deploy --prod --yes --token=$VERCEL_TOKEN
# Verify live
curl -s -o /dev/null -w "HTTP %{http_code}, %{size_download} bytes" https://project.vercel.app/
```

### 8. Sync to Obsidian Vault
Copy deliverables or summaries to the vault. Update the relevant vault note with build status, file locations, and next steps.

## Example: Belditalk.com Full Build (May 2026)

**Claude Code built:** Full 3,047-line website (12 sections, Moroccan zellige design, responsive, SEO, Mailchimp forms, Lemon Squeezy checkout overlay)
**Codex built:** 5 business ops docs (social calendar, email sequences, Discord structure, launch checklist, SEO keywords — 1,026 lines total)
**Hermes managed:** Asset audit, CLAUDE.md spec (13KB), agent deployment, 12 course modules, API integrations (Meta, Lemon Squeezy, Mailchimp), Vercel deployment, vault sync

**Total build time:** ~20 minutes for a fully deployed, checkout-ready academy website.

## Pitfalls

1. **Don't use `--dangerously-skip-permissions` for print mode** — use `--allowedTools` instead. It's safer and doesn't trigger the interactive permissions dialog that can hang.
2. **Codex on WSL needs cmd.exe** — Windows npm install, Linux binary missing. Always use bat wrapper.
3. **Codex sandbox broken on Windows** — use `--sandbox danger-full-access` if you hit `windows sandbox: spawn setup refresh`.
4. **CLAUDE.md specificity matters** — vague specs = bad output + wasted turns. Write exact section content, exact color codes, exact feature list. Include exact third-party URLs (form actions, checkout links, script tags).
5. **Commit before deploying agents** — both agents work better when the git history is clean and they can see what files exist.
6. **Verify output** — agent self-reports ("I built everything!") are not proof. Check file sizes, run the server, inspect the HTML.
7. **Large builds exceed terminal timeout.** A full website build (3000+ lines) can take 10+ minutes. Set `timeout=600` and expect it may still time out. When it does, check the output file anyway — Claude Code may have finished writing even though the Hermes terminal timed out. Verify with `wc -l` and `grep` for key integrations before re-running.
8. **Use execute_code for integration checks.** After a build, run a batch of grep checks via execute_code to verify all integrations landed (Mailchimp form URLs, payment scripts, section IDs, etc.) rather than checking one by one.
9. **Include content references in CLAUDE.md.** If you have course modules or content files the site should reference (e.g., curriculum details), tell Claude Code to "Read the content/ modules for curriculum details" in the prompt. It will pull real content instead of inventing placeholder text.
