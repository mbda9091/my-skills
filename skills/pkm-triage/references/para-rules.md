# PARA Rules

Classify by action distance, not topic.

| Destination | Test |
| --- | --- |
| `Daily/` | Unassigned same-day temporary action, or dated log/link; project actions stay in Project |
| `00_inbox/` | Useful but not processed yet |
| `01 Projects/` | Has project ownership, outcome, finish condition, or continuing progress value; task size is irrelevant |
| `02 Areas/` | Ongoing responsibility or standard with no finish date |
| `03 Resources/` | Reusable reference or knowledge without immediate action |
| `04 Archive/` | Inactive, completed, obsolete, or retained for history |

Ambiguous cases:

- A resource used by a project remains in `03 Resources/`; link it from the project.
- A project that becomes a long-term responsibility should be summarized into `02 Areas/` before archiving the project.
- An AI answer with unverified external facts should stay in inbox or include `To Verify` until checked.
