# Linking Rules

Use Obsidian wiki links for local notes:

```markdown
[[03 Resources/Note Title]]
[[Note Title]]
```

Prefer path links when titles may collide. Prefer title-only links when the note is stable and unique.

Daily links:

- Append under `## Links` for references.
- Daily Tasks is only for unassigned same-day temporary actions. Project tasks stay in Next Actions. Use the task wrapper; backlinks are ordinary text or links.
- Append under `## Notes` for short logs.

MOC links:

- Only add entries that are worth revisiting.
- Do not add every raw inbox item to an MOC.
- Use `append-moc-link` and deduplicate within the target section through the wrapper. Links elsewhere do not replace index entries.

Project resource links use `append-project-resource`. Daily logs/links use `append-daily`. Raw and Related associations in AI/Resource notes can be edited minimally; never use the link helper for generic file writes.
