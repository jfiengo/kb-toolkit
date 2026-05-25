# One-time vault backfill

This is a **one-time** backfill of an existing Obsidian vault that pre-dates kb-toolkit. Read `CLAUDE.md` in the vault root for the hard rules (never delete, atomicity, link liberally, preserve tags, cite sources, flag contradictions, MOC hubs). Apply them here.

## Source folders to read (treat as raw material)

- `Ad Hoc/`
- `Austin Apartments/`
- `Austin Move/`
- `Daily Notes/`
- `Interview Prep/`
- `Jeep Tires/`
- `Projects/`

## Folders to ignore

- `Templates/` and `templater/` — plugin scaffolding, not knowledge.
- `inbox/`, `raw/`, `archive/` — empty or reserved for future use.
- `wiki/` — your output destination.
- `.obsidian/`, `.git/` — toolchain.

## What to do

For each source file:

1. Identify the durable, atomic concepts worth lifting into `wiki/`. Daily notes tend to be ephemeral — be selective; not every entry deserves a wiki page.
2. Create wiki pages following CLAUDE.md rules:
   - One concept per page, slug-cased filename in `wiki/`.
   - Search `wiki/` before creating; extend rather than duplicate.
   - Liberal `[[wikilinks]]` between related pages.
   - Preserve any tags from the source.
3. Cite the source at the bottom of each wiki page as a wikilink, e.g. `Source: [[Daily Notes/2025-04-28]]` or `Sources: [[Projects/ReplyGenius/Testing]], [[Projects/ReplyGenius/Front End]]`.
4. **Do not modify, move, rename, or delete** the source files. The existing top-level folder organization is the user's, not yours to manage.
5. Flag contradictions across sources with Obsidian callouts (`> [!warning] Contradiction`).
6. Create or update MOC (Map of Content) hub notes in `wiki/` for emergent themes — likely candidates: Austin Move MOC, Projects MOC, Interview Prep MOC, Jeep MOC. Link child wiki pages from the relevant MOC.

## Output

Print a short summary at the end:

- Files read (count by folder)
- Wiki pages created (list paths)
- MOC hubs created or updated (list)
- Contradictions flagged (if any, with location)
- Anything skipped and why
