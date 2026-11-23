---
name: pkm-triage
description: Leaf skill for deciding where PKM material belongs by PARA action distance. Use only when explicitly invoked by $pkm-triage or selected by $pkm-operator. Classifies content into Daily, 00_inbox, 01 Projects, 02 Areas, 03 Resources, 04 Archive, or deletion candidates with rationale and next action.
---

# PKM Triage

## Role

Decide where a note or idea belongs. Produce a destination, rationale, and next action. Do not rewrite the content unless the user asks.

## Decision Tree

1. Does it require action today or this week?
   - Yes: `Daily/` if small, `01 Projects/` if it has an outcome and multiple steps.
2. Does it have a clear outcome, deadline, or finish condition?
   - Yes: `01 Projects/`.
3. Is it an ongoing responsibility, standard, habit, or maintained domain?
   - Yes: `02 Areas/`.
4. Is it reusable knowledge, a method, reference, template, or judgment framework?
   - Yes: `03 Resources/`.
5. Is it unprocessed but may be useful?
   - Yes: `00_inbox/`.
6. Is it completed, inactive, obsolete, or no longer useful?
   - Yes: `04 Archive/` or deletion candidate.

## Output Format

```markdown
## Triage Result
- Destination:
- Rationale:
- Confidence: high|medium|low
- Next Action:
- Links to update:
```

Use `references/para-rules.md` for edge cases.
