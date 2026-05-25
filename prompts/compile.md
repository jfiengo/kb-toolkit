# Compile run

You are compiling an Obsidian knowledge base vault. Work inside the vault directory provided on the command line.

## Instructions

1. Read `CLAUDE.md` in the vault root. Follow every rule there; they override generic habits.
2. Process `inbox/` first:
   - For each note, identify concepts and promote content into `wiki/` (existing pages or new atomic pages).
   - Confirm each promoted concept is present in a wiki page **and linked** before touching the inbox note.
   - Apply `inbox_after_promotion` from `CLAUDE.md` only after that confirmation.
3. Process `raw/`:
   - Review new or changed sources since the last compile.
   - Extract durable knowledge into `wiki/`; cite every extraction as `[[raw/filename]]`.
   - Never delete raw sources.
4. Wiki hygiene:
   - Search `wiki/` before creating any page.
   - Preserve all user tags (`#tag` and frontmatter `tags:`).
   - Flag contradictions with callouts; do not silently overwrite.
   - Update MOC hub notes for affected topic areas.
5. Do not delete anything in `wiki/` or `raw/`.

## Output

When finished, print a short summary:

- Inbox notes processed (count and titles)
- Wiki pages created or updated (list)
- Raw sources incorporated (list)
- Contradictions flagged (if any)
- Inbox actions taken (archived / marked / deleted per policy)
