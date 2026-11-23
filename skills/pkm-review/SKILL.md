---
name: pkm-review
description: Leaf skill for reviewing PKM inboxes, unprocessed AI conversations, stale projects, and weakly linked notes. Use only when explicitly invoked by $pkm-review or selected by $pkm-operator. Produces concrete recommendations and does not mutate files unless explicitly asked.
---

# PKM Review

## Role

Review the vault and recommend next actions. Default to reporting, not editing.

## Workflow

1. Determine review scope:
   - AI conversation inbox
   - general inbox
   - projects
   - resources
   - whole vault
2. Use `scripts/review_inbox.py` for inbox and AI conversation reviews.
3. Group findings by recommended action:
   - distill
   - triage
   - link
   - archive
   - delete candidate
4. Provide concrete file paths and reasons.
5. Only edit files after the user approves the proposed changes.

## Output

```markdown
## Review Result

### Distill
- file: reason

### Triage
- file: reason

### Link
- file: reason

### Archive
- file: reason

### Delete Candidates
- file: reason
```
