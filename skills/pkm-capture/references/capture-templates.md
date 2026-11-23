# Capture Templates

Read the target vault’s current templates before creation. Do not freeze a copy of the vault schema in this skill.

- AI primary and local fallback: `Templates/QuickAdd-PKM-AI-Conversation.md`.
- Interactive/manual AI template: `Templates/AI-Conversation.md`; resolve Templater syntax rather than saving literal template commands.
- Daily: `Templates/Diary.md`, through the vault-local wrapper.
- Generic inbox material: preserve raw content, source, and context; do not invent task placeholders when no inbox template exists.

The bundled `capture_note.py` renders the current QuickAdd AI template locally, including Shanghai timestamps and multiline context/prompt/raw answer. It fails on unsupported template tokens rather than silently dropping content. The user’s input is data: template-looking text inside an input is preserved literally.

Preserve explicit decisions and verification candidates in the raw record. A captured actionable item must have one owning checkbox only: Project Next Actions first; Daily Tasks only for unassigned same-day temporary work. Unresolved actions remain ordinary text until triaged. Use `add-task` for actual task creation, not the capture helper.
