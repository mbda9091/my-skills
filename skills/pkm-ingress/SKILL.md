---
name: pkm-ingress
description: Controlled external entry point for the user's PKM vault. Use when external systems, bots, browser tools, another agent, or the user explicitly ask to submit outside content into the vault without reading AGENTS.md or performing PARA triage. Creates External Drops only.
---

# PKM Ingress

## Target vault

`PKM_VALUT_DIR` is required and is the sole target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace, the skill repository, or a fixed home-directory path.

Resolve all note paths, templates, and vault-local scripts from this directory. Reject vault-relative paths that escape the resolved root, including through symlinks. Run vault-local wrappers with this directory as their working directory; if a wrapper accepts `--vault-root`, pass the same directory. A wrapper that selects another vault must be corrected before use. Skill-local `references/` and `scripts/` remain relative to this skill, not the vault.

The environment is caller configuration, not an External Drop payload field. This skill still does not read the target vault's `AGENTS.md` or perform internal triage.

## Role

Accept external content through the smallest contract and create an External Drop. Do not summarize, triage, classify, link, create Resources, add Tasks, or read the vault `AGENTS.md`.

External Ingress is the boundary before the vault workflow:

```text
external caller -> $pkm-ingress -> scripts/pkm_ops.py create-external-drop -> External Drop
```

The output is always a pending note under `00_inbox/External Drops/`.

## Contract

Required fields:

- `source_app`: single-line external entry identifier, such as `feishu-bot`, `qq-bot`, `browser-extension`, `cli`, or `another-agent`.
- `content`: raw external content.

Optional fields:

- `source_ref`: external locator, such as a URL, message id, thread id, or external file id.
- `source_created_at`: timestamp from the source system.
- `external_id`: source-system idempotency key. Reusing the same `source_app + external_id` returns the existing drop.
- `title_hint`: weak human title hint.
- `intent_hint`: one of `capture`, `distill`, `task`, `unknown`.
- `content_format`: one of `plain_text`, `markdown`.
- `attachments`: list of external attachment references. Do not pass local absolute paths.

Unknown fields are invalid. External callers must not pass PARA placement, Dashboard fields, MOC targets, or Tasks plugin syntax.

## Workflow

1. Build the smallest payload from the external request.
2. Run in the configured target vault:

```bash
(
  [[ "${PKM_VALUT_DIR:?Set PKM_VALUT_DIR}" = /* && -d "$PKM_VALUT_DIR" ]] || { echo "PKM_VALUT_DIR must be an existing absolute directory" >&2; exit 1; }
  cd -- "$PKM_VALUT_DIR" || exit
  python3 scripts/pkm_ops.py create-external-drop --payload-json '{"source_app":"cli","content":"raw text","intent_hint":"unknown"}'
)
```

3. Read the returned `target_path` if validation is needed.
4. Return only the drop path, wiki link, duplicate flag, and pending status to the caller.

## Guardrails

- Do not read `AGENTS.md`; External Ingress should not import the vault's internal workflow into the external context.
- Do not convert `intent_hint: task` into a checkbox. Task ownership is decided during internal ingest.
- Do not copy or localize attachments in this skill. Preserve external references only.
- Do not call `ingest-drop`. Use `$pkm-ingest` or `$pkm-operator` after the drop exists.
