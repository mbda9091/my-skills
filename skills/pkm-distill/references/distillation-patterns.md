# Distillation Patterns

Use the current target-vault Resource template. Do not impose a second frontmatter or heading schema from this skill.

For `create-resource`, prepare `title`, `source_type`, `summary`, `key_points`, `to_verify`, `raw_link`, `related_area`, and `related_project`. Relations may be empty strings; do not associate new notes with a completed Project by default.

- Summary: reusable takeaway in a few lines.
- Key Points: methods, criteria, and explicit decisions. A decision can be recorded here as `决策：…`; do not assume an unrecognized `decisions` payload field is persisted.
- To Verify: uncertain or changing external claims, with available sources.
- Related/Raw: traceable original record and actual Area/Project ownership.
- Actions: create executable tasks through the vault task wrapper in their owning Project, or Daily for unassigned same-day temporary work. Leave ordinary links in raw/Resource notes. If ownership is unclear, retain ordinary text in Actions/Notes pending triage.

A good Resource is useful without rereading the chat, distinguishes decisions from open questions, retains verification items, and has a knowledge-focused title. Validate decisions and action destinations after creation; the current QuickAdd template does not have dedicated Decisions/Actions placeholders.
