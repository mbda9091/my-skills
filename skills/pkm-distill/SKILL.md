---
name: pkm-distill
description: Leaf skill for turning raw PKM captures into durable knowledge. Use only when explicitly invoked by $pkm-distill or selected by $pkm-operator. Extracts summaries, methods, judgment criteria, decisions, actions, verification items, and Resource notes from AI conversations or other raw notes.
---

# PKM Distill

## Target vault

`PKM_VALUT_DIR` is required and is the sole filesystem target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace or a fixed home-directory path.

Resolve note paths, templates, and the vault's `AGENTS.md` from this directory. Keep vault-relative paths inside the resolved root, including through symlinks. Follow `$PKM_VALUT_DIR/AGENTS.md` for vault operations. Skill-local `references/` and bundled `scripts/` resolve from this skill's installed directory, independently of the target vault and current working directory.

The QuickAdd wrapper is `$PKM_VALUT_DIR/scripts/pkm_quickadd.py`. Run it with `--vault-root "$PKM_VALUT_DIR"` in the configured vault directory. For Obsidian-backed actions, verify that the wrapper's `--vault` identifier points to the same vault before writing; pass the matching identifier when its default does not match.

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
4. If writing a Resource note in the vault selected by `PKM_VALUT_DIR`, prefer the wrapper action `create-resource`.
5. If writing directly, use `03 Resources/` unless triage indicates Project or Area.
6. Preserve decisions in `key_points` (for example, `决策：…`) or the Resource Notes section; the current QuickAdd payload has no separate decisions/actions fields, so do not assume extra keys are persisted.
7. Route actionable work to the owning Project `Next Actions` using `add-task`. Only unassigned same-day temporary work belongs in Daily Tasks. Keep unclear actions as ordinary text in Actions/Notes pending triage; do not copy task checkboxes into raw and Resource notes. Include ordinary links back to the owning Project/task.
8. Route link updates to `$pkm-link`, including the raw record’s Resource association. Validate that decisions, action ownership, and verification items survived creation.

## Resource Shape

Use `references/distillation-patterns.md` for output patterns. Prefer dense, reusable notes over long summaries.

## QuickAdd Wrapper

Generate Markdown-ready values. Prefer `--payload-json` for short payloads; use a UTF-8 JSON file or stdin for long content:

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
  python3 scripts/pkm_quickadd.py create-resource --vault-root "$PKM_VALUT_DIR" --payload-json '{"title":"resource","source_type":"ai","summary":"Durable takeaway","key_points":"Reusable method; 决策：保留明确判断","to_verify":"","raw_link":"[[00_inbox/AI Conversations/YYYY-MM-DD-topic]]","related_area":"","related_project":""}'
)
```

The wrapper uses choice id `f50ab515-88cb-4878-9d0c-449278ef94b2`, runs `quickadd:check` before `quickadd:run`, and returns the created target path. If check reports missing fields, provide explicit empty strings for intentionally blank optional values. Do not copy the full Resource template into the skill when the wrapper path is available.

For Resource creation only, render the target vault’s current Resource/QuickAdd template locally if the wrapper, Obsidian CLI, or QuickAdd choice is unavailable, or the user requests direct creation. Preserve source_type, related_project, related_area, and Raw. This does not permit hand-editing tasks or bypassing the local wrapper for Daily, MOC, or Project appends.

## External Facts

If the source contains facts that may change, keep them under `To Verify` until verified. Do not convert unstable claims into durable knowledge without sources.
