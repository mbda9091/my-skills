---
name: pkm-link
description: Leaf skill for connecting PKM notes after capture or distillation. Use only when explicitly invoked by $pkm-link or selected by $pkm-operator. Updates Daily notes, MOCs, backlinks, Related sections, Raw links, and project/resource references while preserving existing content and avoiding duplicate links.
---

# PKM Link

## Role

Connect notes so work remains traceable. Add the smallest useful set of links; do not reorganize content beyond the requested connection.

## Workflow

1. Identify the source note, target note, and link purpose.
2. Read existing files before editing.
3. Use `scripts/pkm_ops.py append-daily` when appending to Daily notes.
4. Use `scripts/pkm_ops.py append-moc-link` for MOC links and `scripts/pkm_ops.py append-project-resource` for Project resource links.
5. Avoid duplicate entries.
6. Validate by reading the changed section.

## Common Links

- Raw AI capture -> Resource: add raw link in the Resource `Related` section.
- Resource -> Daily: append the resource link under `## Links` or `## Notes`.
- Resource -> MOC: append under the relevant index heading.
- Project -> Resource: add resource link under `## Resources`.

## Daily Script

```bash
python3 scripts/pkm_ops.py append-daily --payload-json '{"date":"YYYY-MM-DD","section":"Links","content":"- [[03 Resources/example]]"}'
```

Payload:

```json
{
  "date": "YYYY-MM-DD",
  "section": "Links",
  "content": "- [[03 Resources/example]]",
  "create_if_missing": "true",
  "allow_duplicate": "false"
}
```

Use `Links` for references, `Tasks` for dated actions, `Notes` for short logs, and `Ideas` for fleeting ideas. Entries under `Tasks` must follow the vault Tasks syntax.

## MOC and Project Scripts

```bash
python3 scripts/pkm_ops.py append-moc-link --payload-json '{"link":"[[03 Resources/example]]"}'
python3 scripts/pkm_ops.py append-project-resource --payload-json '{"project":"01 Projects/example.md","resource":"[[03 Resources/example]]"}'
```
