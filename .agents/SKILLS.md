# Skills Index

Canonical project skills live under `.agents/skills/`. Each skill is a portable
instruction package with a `SKILL.md` file using Agent Skills frontmatter.

## Available Skills

- `guidelines`: mandatory coding discipline for writing, reviewing,
  and refactoring changes without overengineering or broad unrelated edits.
- `capture-evidence-bundle`: collect screenshots, page snapshot text, URL, and
  available artifact metadata for browser task evidence.
- `scrape-with-pagination`: extract repeated page content across paginated or
  infinite-scroll listings.
- `safe-login`: perform a standard email/password login without exposing
  credentials in logs or artifacts.

## Maintenance Rules

- Skill folder name must match the `name` frontmatter field.
- Update this index whenever a skill is added, renamed, or removed.
- Keep each `SKILL.md` focused. Move detailed references into `references/`
  only when needed.
- Do not store credentials, cookies, or captured private data in skill assets.
