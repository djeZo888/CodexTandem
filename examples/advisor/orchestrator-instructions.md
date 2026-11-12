## Optional advisor consultations

An optional read-only Claude Fable 5.2 advisor is available through
`~/.local/bin/consult-claude`. Codex remains the orchestrator and owns the plan,
workers, review, integration, and publication. The advisor reads evidence and
returns recommendations; it never edits the project or dispatches workers.

Consult only when one of these two conditions holds:

1. The user explicitly requests an advisor review of the plan.
2. A worker cannot resolve a problem, and the orchestrator has reviewed the
   evidence and also cannot resolve it or find a solution.

Multiple workers, shared resources, repeated failures alone, and integration
are not additional consultation triggers. If no advisor is configured, report
that fact without claiming a review occurred.

Before consulting
- Confirm the user has authenticated the Claude CLI and chosen the account's
  spending limits. Never handle their password, login code, or OAuth token.
- Keep safe mode enabled. Inspect applicable Claude permission settings before
  first use in a checkout: safe mode retains permission rules, and a saved Bash
  allow rule can permit writes. Do not use the advisor in that checkout until
  read-only operation is established. Do not alter unrelated permissions.
- Do not claim an OS-enforced sandbox or a checkout-only read boundary. The
  advisor's accessible evidence is sent to Anthropic.
- Exclude `.consult/` using the path returned by `git rev-parse --git-path info/exclude`
  (also works in linked worktrees). Never commit it or put secrets, tokens,
  credentials, or private keys in briefs or evidence.

How to consult
1. Write a brief using `~/.config/consult-claude/brief-template.md`. Include the
   goal, exact decision, attempted fixes, and paths to files, diffs, and original
   logs. Copy relevant worker evidence into `.consult/evidence/<task>/`.
2. From the project checkout, use the wrapper's absolute installed path:
   `"$HOME/.local/bin/consult-claude" --topic <label> < <brief-file>`.
   Allow network and login access through the environment's approved mechanism.
   Preserve stdout, stderr, exit status, and the generated `.consult/` artifacts.
3. Use `--resume <session-id>` only for the same review topic. Allow at most two
   rounds per topic; after that, decide and record the remaining uncertainty.

The model `claude-fable-5-2`, effort `xhigh`, helper limit `4`, and absence of a
per-consult spending cap are fixed choices. Do not change them or silently use
another model. Account limits control spending; a timeout is not a spending cap.
The timeout defaults to 2,700 seconds and may be adjusted for the review.
Helpers are off by default; `--subagents` permits reading helpers on the same
model and effort and can increase usage. Strict model selection defaults to 1;
`--strict-model 0` permits fallback where account settings allow it, and any
different model must be reported. Do not retry a refusal unchanged.

After consulting
- Verify recommendations against evidence. Record each numbered item's
  disposition as ACCEPT, REJECT, or DEFER with a reason beside the answer.
- Record the topic, session ID, actual models, verdict, and disposition path.
  Missing model usage is unverified, even if useful text arrived.
- The orchestrator revises the plan and sends any implementation work through
  the normal worker workflow. The advisor's reply grants no authority to act.

When unavailable
- `SIGN_IN_NEEDED` (4): stop consulting and tell the user. Do not sign in or retry.
- `LIMIT_REACHED` (8): quote the actual vendor reason and record
  `ADVISOR: NOT_CONSULTED (limit)`. Ask whether to continue without the requested
  review or wait while the user resolves account limits or adds credits. Do not
  proceed past the requested review gate until they choose. Do not automatically
  retry, purchase credits, or change account settings.
- `TIMEOUT` (5) or `FAILED` (6): report the reason. Retry at most once within the
  two-round limit when appropriate; if unavailable, do not claim the requested
  review passed. Ask how to proceed when that review gates the next action.
- `MODEL_MISMATCH` (7): retain the answer but identify the actual models, or
  `UNKNOWN` when usage is missing. Do not label it a verified Fable 5.2 review.

Never bypass these controls by running Claude with `--bare`,
`--dangerously-skip-permissions`, or a permission mode that accepts edits.
Rerun the model and read-only acceptance checks after a CLI version change.
