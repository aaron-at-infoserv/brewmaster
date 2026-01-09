---
description: Review the current branch against the Brewmaster house rules
---

Review the diff between this branch and `main`.

For every finding give: file, line, severity (blocker / should-fix / nit), and why
it matters. If there are no findings, say so in one line.

Check specifically:

- Does it satisfy the acceptance criteria on the linked issue? Quote the criterion.
- Is there a test that would fail if this change were reverted? If not, that is a
  blocker.
- Money must be handled exactly. Floats are a blocker anywhere near a balance.
- Any behaviour change not covered by a test.
- Anything that destroys or rewrites historical records rather than adding to them.
- Any loop whose exit condition depends on values that could be equal.

Do not comment on formatting - ruff owns that. Do not praise the change.
Do not suggest improvements that are out of scope for the linked issue.
