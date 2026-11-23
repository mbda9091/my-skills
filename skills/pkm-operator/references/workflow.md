# PKM Workflow

The vault uses PARA plus an AI-conversation intake workflow.

`PKM_VALUT_DIR` selects the target vault and must name an existing absolute directory. All vault paths below are relative to its resolved root. Internal operations follow `$PKM_VALUT_DIR/AGENTS.md`. QuickAdd uses the wrapper in that vault with an explicit `--vault-root "$PKM_VALUT_DIR"`; its Obsidian vault identifier must resolve to the same library.

Core stages:

```text
Capture -> Triage -> Distill -> Link -> Review
```

Default directories:

| Directory | Purpose |
| --- | --- |
| `Daily/` | Daily tasks, notes, ideas, and links |
| `00_inbox/` | Unprocessed captures |
| `00_inbox/AI Conversations/` | Raw AI conversation records |
| `01 Projects/` | Active efforts with outcomes and next actions |
| `02 Areas/` | Ongoing responsibilities and standards |
| `03 Resources/` | Reusable knowledge, methods, summaries, templates, and references |
| `04 Archive/` | Completed or inactive material |
| `MOCs/` | Curated maps and index notes |

PARA routing rule:

1. Needs near-term action: `Daily/` or `01 Projects/`.
2. Ongoing responsibility: `02 Areas/`.
3. Reusable later: `03 Resources/`.
4. Unprocessed but potentially useful: `00_inbox/`.
5. Completed, inactive, or no longer useful: `04 Archive/` or deletion if the user asks.

AI-conversation rule:

```text
raw conversation -> 00_inbox/AI Conversations/
durable knowledge -> 03 Resources/
actions -> Daily/ or 01 Projects/
index -> MOCs/AI 对话沉淀.md
```
