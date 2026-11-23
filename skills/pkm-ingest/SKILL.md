---
name: pkm-ingest
description: Internal PKM workflow for processing External Drops into formal vault notes. Use when the user asks to process, ingest, review, normalize, or convert files under 00_inbox/External Drops into AI Conversations, Resources, Daily notes, Project tasks, MOC links, rejections, or failed records.
---

# PKM Ingest

## Role

Process a valid External Drop inside the vault boundary. This is where `AGENTS.md`, PARA rules, Tasks syntax, Resource templates, Daily rules, and MOC linking apply.

The internal flow is:

```text
External Drop -> validate -> decide mode -> dry-run -> write formal outputs -> update drop outputs/status
```

## Workflow

1. Read the vault `AGENTS.md`.
2. Read the target External Drop.
3. Validate drop format:

```bash
python3 scripts/pkm_ops.py validate-drops
```

For one invalid file, reject by default. Only move it when the user explicitly asks:

```bash
python3 scripts/pkm_ops.py ingest-drop --file "00_inbox/External Drops/example.md" --move-invalid
```

4. Decide the ingest mode:
   - `ai-conversation`: external content should become a formal AI conversation raw note.
   - `resource`: content contains reusable knowledge, a method, checklist, decision, or reference summary.
   - `daily-note`: content is a short log or context note.
   - `task`: content is an actionable item with clear owner/date/target.
   - `reject`: content is duplicate, irrelevant, or should not enter the formal vault.
5. Run dry-run first:

```bash
python3 scripts/pkm_ops.py ingest-drop --file "00_inbox/External Drops/example.md" --payload-json '{"mode":"resource","title":"Title","source_type":"external","summary":"- ...","key_points":"- ..."}'
```

6. If the planned outputs are correct, run with `--write`.
7. Read back the External Drop and generated notes. Verify `status`, `outputs`, `Raw` links, wiki link paths, and Tasks syntax.

## Rules

- Use `--retry` for `failed` drops and `--force` only when intentionally reprocessing `processed` drops.
- Do not guess a Project. Link a Project only when the drop contains a clear wiki link or the user provides `--project`/payload project information.
- Do not turn unclear task-like content into a checkbox. Leave it as a note or recommendation until ownership and due date are clear.
- Put unstable facts, prices, legal/product/model claims, schedules, and news under `To Verify` unless verified.
- If creating an AI Resource, update `MOCs/AI 对话沉淀.md`; other Resources rely on dynamic Resource MOC tables unless explicitly requested.
