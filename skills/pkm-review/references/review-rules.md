# Review Rules

Review by workflow bottleneck:

- Inbox files with no clear destination need `$pkm-triage`.
- AI conversations with unextracted methods or decisions need `$pkm-distill`. Already extracted but unassociated notes may need linking; inspect the actual content.
- Resource notes with empty Related sections need `$pkm-link`.
- Projects without next actions need project review.
- Old inbox items with no reusable value are archive or delete candidates.

Exclude Welcome.md, Untitled.md, Resource Untitled*.md, test/ and sync/agent/backup metadata before reading notes. The helper scans ai/inbox only. A To Verify heading by itself is not an outstanding claim; known processed statuses or a Resource association should not automatically return to the distill queue. A Resource association does not prove its target exists: check target validity when reviewing links.

For AI conversation review, prioritize:

1. Conversations that produced decisions.
2. Conversations that produced reusable methods.
3. Conversations that created actions.
4. Conversations with facts needing verification.
