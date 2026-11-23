---
name: pkm-distill
description: Leaf skill for turning raw PKM captures into durable knowledge. Use only when explicitly invoked by $pkm-distill or selected by $pkm-operator. Extracts summaries, methods, judgment criteria, decisions, actions, verification items, and Resource notes from AI conversations or other raw notes.
---

# PKM Distill

## Target vault

`PKM_VALUT_DIR` is required and is the sole target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace, the skill repository, or a fixed home-directory path.

Resolve all note paths, templates, and vault-local scripts from this directory. Reject vault-relative paths that escape the resolved root, including through symlinks. Run vault-local wrappers with this directory as their working directory; if a wrapper accepts `--vault-root`, pass the same directory. A wrapper that selects another vault must be corrected before use. Skill-local `references/` and `scripts/` remain relative to this skill, not the vault.

Follow the target vault's `AGENTS.md` for internal vault operations. Keep each run bound to the same resolved directory.

## Role

Convert raw material into reusable knowledge. Preserve traceability to the raw source, but do not dump transcripts into Resource notes.

## Workflow

1. Read the raw note or user-provided content.
2. Identify the reusable unit:
   - method
   - checklist
   - framework
   - decision record
   - implementation plan
   - reference summary
3. Extract:
   - Summary
   - Key Points
   - Decisions
   - Actions
   - To Verify
   - Related Project/Area/Raw links
4. If writing a Resource note, prefer `scripts/pkm_ops.py create-resource`.
5. If writing directly, use `03 Resources/` unless triage indicates Project or Area.
6. Route link updates to `$pkm-link`.

## Resource Shape

Use `references/distillation-patterns.md` for output patterns. Prefer dense, reusable notes over long summaries.

## PKM Ops Wrapper

Generate Markdown-ready values and write them to a payload JSON file:

```json
{
  "title": "durable resource title",
  "source_type": "ai",
  "summary": "- Durable takeaway.",
  "key_points": "- Reusable point.",
  "to_verify": "- Unstable claim to verify, or leave blank.",
  "raw_link": "[[00_inbox/AI Conversations/YYYY-MM-DD-title]]",
  "related_area": "[[02 Areas/related area]]",
  "related_project": "[[01 Projects/related project]]"
}
```

Resolve `related_area` and `related_project` from the actual note ownership. Use an empty string when either relation does not apply; never default new resources to a completed project.

Then call the wrapper in the configured target vault:

```bash
(
  [[ "${PKM_VALUT_DIR:?Set PKM_VALUT_DIR}" = /* && -d "$PKM_VALUT_DIR" ]] || { echo "PKM_VALUT_DIR must be an existing absolute directory" >&2; exit 1; }
  cd -- "$PKM_VALUT_DIR" || exit
  python3 scripts/pkm_ops.py create-resource --payload-json '{"title":"durable resource title","source_type":"ai","summary":"- ...","key_points":"- ...","raw_link":"[[00_inbox/AI Conversations/YYYY-MM-DD-title]]"}'
)
```

Use `scripts/pkm_quickadd.py` only as an explicit legacy/manual fallback when the user asks for QuickAdd behavior.

## External Facts

If the source contains facts that may change, keep them under `To Verify` until verified. Do not convert unstable claims into durable knowledge without sources.
