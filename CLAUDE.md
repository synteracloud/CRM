# Pakistan CRM — Claude Instructions

## MANDATORY: Read the full seed before building any page

Before building any app/ page, use the Read tool on the seed file and read it completely.
Do NOT rely on PowerShell line-count scripts alone — they show numbers, not structure.

**Why this rule exists:** AI section pages (src/ai/*.html) have a completely different body
structure — their own `<aside class="ai-menubar-tabs">` and `<header class="app-header ai-app-header">`
baked into the HTML, no crm-shell.js. This was only discovered after pages were built wrong
and the user caught it in the browser.

**What to verify in every seed before building:**
1. Does it have `<aside class="app-menubar-tabs">` (standard CRM shell) or its own aside?
2. Does it have a standard `<header class="app-header">` or its own, or none?
3. Does its script stack include crm-shell.js? If not, do NOT add it.
4. Are there inter-page links (e.g. `ai/xxx.html`, `forms/xxx.html`) that need rewriting to `app/xxx.html`?
5. Are there extra CSS libs in `<head>` not in the standard stack?

**Rule: if the seed does not have the standard CRM aside/header, copy the full seed verbatim
and only rewrite internal folder paths (e.g. ai/ → app/, forms/ → app/).**

---

## Current phase
**Library phase complete** (96 NexLink pages). Custom design phase is now active.
**Phase gate:** `D:\CRM\DESIGN-SPEC.md` — 75 custom pages, 13 archetypes (A–M), 8 build phases.
- App pages live in: `D:\CRM\frontend\src\app\`
- Dev server: `npm run serve` from `D:\CRM\frontend`, port 3001
- Screen artefacts (QC records): `D:\CRM\SCREEN-ARTEFACTS.md`

## Path translation rule
All internal seed links must be rewritten:
- `href="index.html"` → `href="app/dashboard.html"`
- `href="<folder>/xxx.html"` → `href="app/xxx.html"` (for any subfolder)
- `href="profile.html"` → `href="app/profile.html"` (bare filenames in self-contained pages)
