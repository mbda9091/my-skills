---
name: pkm-operator
description: Main entrypoint for the user's Obsidian/PKM workflow. Use when the user explicitly invokes $pkm-operator or asks Codex to capture, triage, distill, link, or review knowledge in the PKM vault according to the user's PARA and AI-conversation workflow. This skill routes the goal to explicit leaf skills and coordinates end-to-end validation.
---

# PKM Operator

## Target vault

`PKM_VALUT_DIR` is required and is the sole filesystem target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace or a fixed home-directory path.

Resolve note paths, templates, and the vault's `AGENTS.md` from this directory. Keep vault-relative paths inside the resolved root, including through symlinks. Follow `$PKM_VALUT_DIR/AGENTS.md` for vault operations. Skill-local `references/` and bundled `scripts/` resolve from this skill's installed directory, independently of the target vault and current working directory.

The QuickAdd wrapper is `$PKM_VALUT_DIR/scripts/pkm_quickadd.py`. Run it with `--vault-root "$PKM_VALUT_DIR"` in the configured vault directory. For Obsidian-backed actions, verify that the wrapper's `--vault` identifier points to the same vault before writing; pass the matching identifier when its default does not match.

## Role

Act as the PKM workflow router, not as a monolithic writer. Understand the user's goal, select the smallest necessary workflow stage, explicitly load the matching leaf skill, and coordinate validation.

The vault workflow is:

```text
capture -> triage -> distill -> link -> review
```

## Routing

Read `references/routing-table.md` before choosing a leaf skill unless the user already named one.

Use these leaf skills. The separate `$pkm-todo` is manual-only: do not invoke it implicitly. Workflow actions may call the vault task wrapper directly when authorized by the user and the vault rules.

| Goal | Leaf skill |
| --- | --- |
| Save raw input, AI chat, webpage excerpt, or fleeting idea | `$pkm-capture` |
| Decide whether content belongs in Daily, Project, Area, Resource, Inbox, or Archive | `$pkm-triage` |
| Extract reusable knowledge, decisions, actions, or verification items | `$pkm-distill` |
| Add backlinks, Daily links, MOC entries, or related project/resource references | `$pkm-link` |
| Review inbox, stale projects, unprocessed AI conversations, or weakly linked notes | `$pkm-review` |

After selecting a leaf, read that leaf skill's `SKILL.md` from the sibling skill directory, for example `../pkm-capture/SKILL.md`. Do not execute a leaf workflow from memory.

## End-To-End AI Conversation Flow

Use this as the first complete vertical slice:

1. `$pkm-capture`: Save the raw conversation into `00_inbox/AI Conversations/YYYY-MM-DD-title.md`.
2. `$pkm-distill`: Create or propose a `03 Resources/` note containing durable knowledge, decisions, actions, and items to verify.
3. Route explicit actions to the owning Project via `add-task`; use Daily Tasks only for unassigned same-day temporary work. Unresolved ownership stays as ordinary text under Actions until triaged.
4. `$pkm-link`: Link both raw and resource records, log progress in Daily Notes/Links, and update `MOCs/AI 对话沉淀.md` when appropriate.
5. Validate by reading the changed files and checking that raw context, distilled knowledge, and action links are all traceable.

## PKM QuickAdd Wrapper

For the vault selected by `PKM_VALUT_DIR`, prefer the vault-local QuickAdd wrapper:

```bash
(
  [[ "${PKM_VALUT_DIR:?Set PKM_VALUT_DIR}" = /* && -d "$PKM_VALUT_DIR" ]] || { echo "PKM_VALUT_DIR must be an existing absolute directory" >&2; exit 1; }
  cd -- "$PKM_VALUT_DIR" || exit
  python3 scripts/pkm_quickadd.py capture-ai --vault-root "$PKM_VALUT_DIR" --payload-json '{"title":"topic","date":"YYYY-MM-DD","context":"Conversation context","prompt":"User request","raw_answer":"Raw answer"}' || exit
  python3 scripts/pkm_quickadd.py create-resource --vault-root "$PKM_VALUT_DIR" --payload-json '{"title":"resource","source_type":"ai","summary":"Durable takeaway","key_points":"Reusable method; 决策：保留明确判断","to_verify":"","raw_link":"[[00_inbox/AI Conversations/YYYY-MM-DD-topic]]","related_area":"","related_project":""}' || exit
  python3 scripts/pkm_quickadd.py append-daily --vault-root "$PKM_VALUT_DIR" --payload-json '{"date":"YYYY-MM-DD","section":"Notes","content":"- 今日推进 [[01 Projects/project]]","create_if_missing":"true","allow_duplicate":"false"}'
)
```

Run these commands in `$PKM_VALUT_DIR`. For QuickAdd actions, pass the target root explicitly and keep the configured choice ids, `quickadd:check` / `quickadd:run` order, and target-path detection. For `append-daily`, the wrapper edits local Markdown directly. The operator and leaf skills should generate structured payloads and call the wrapper; do not put large `vars=...` JSON directly in the shell command.

Configured wrapper actions:

| Action | Use |
| --- | --- |
| `capture-ai` | QuickAdd capture (`b0f3c0d6-89a5-4d86-bb7b-9f8f2f61c101`) |
| `create-resource` | QuickAdd resource (`f50ab515-88cb-4878-9d0c-449278ef94b2`) |
| `append-daily` | Local log, idea, or link append |
| `append-moc-link` | Local MOC section append |
| `append-project-resource` | Local Project resource append |
| `add-task` | New structured Daily or Project task |
| `set-task-status` | Complete, cancel, or reopen an existing task |
| `update-task` | Edit, move, or backfill a task with reason/history |
| `check-tasks` | Read-only structural task audit |

Prefer `--payload-json` for short payloads; use `--payload -` or a UTF-8 file for long content. MOC, Project, and Daily writes use the wrapper, including when Obsidian CLI is unavailable: these local actions do not require Obsidian. See `references/workflow.md` for task ownership and status/content boundaries.

Payload for `capture-ai`:

```json
{
  "title": "topic",
  "date": "YYYY-MM-DD",
  "context": "why this conversation happened",
  "prompt": "core user request",
  "raw_answer": "raw or lightly compressed answer"
}
```

Payload for `create-resource`:

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

Payload for `append-daily`:

```json
{
  "date": "YYYY-MM-DD",
  "section": "Notes",
  "content": "- Short daily note.",
  "create_if_missing": "true",
  "allow_duplicate": "false"
}
```

Daily records progress and links under `Notes` or `Links`. Only unassigned same-day temporary tasks belong under `Tasks`; project tasks belong in the project `Next Actions`. Use `add-task` with structured text and optional due date; the wrapper generates `➕ YYYY-MM-DD` in Asia/Shanghai. The compatibility `append-daily` Tasks entry also adds creation dates, but must not be used for status or content edits.

Markdown values may contain lists and multiline text. When preparing JSON by hand, encode newlines as JSON newlines (`\n`), not as literal backslash-n text.

For capture/resource creation only, use the current vault templates and local Markdown fallback when the wrapper, Obsidian CLI, or QuickAdd choice is unavailable, or the user explicitly requests direct creation. Do not extend this exception to task operations or MOC/Project/Daily appends: use their local wrapper actions. If the required local action is unavailable, report the error rather than hand-editing around task/date/history rules.

## Operating Rules

- Before PKM vault writes, read `$PKM_VALUT_DIR/AGENTS.md`; use `references/workflow.md` only as skill-local routing context.
- Ask for clarification only when routing is genuinely ambiguous and a wrong write would be costly.
- Preserve user-authored content. Never overwrite notes unless explicitly requested.
- For facts that may change over time, require verification before turning them into durable knowledge.
- For each run, state the selected route before making file edits.
- For multi-stage work, validate each stage before moving to the next.

## Validation

Use `references/validation-plan.md` for independent leaf validation and whole-flow validation.
