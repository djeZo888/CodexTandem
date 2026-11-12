# Optional advisor reference files

These files support the optional workflow in [Advisor](../../docs/ADVISOR.md).
They do not install Claude Code, authenticate an account, or start a model call.

- `consult-claude`: POSIX shell wrapper; requires `jq` and Claude Code.
- `advisor-role.md`: read-only review role for a generic Codex orchestrator.
- `brief-template.md`: evidence-oriented consultation brief.
- `orchestrator-instructions.md`: optional global-instruction snippet with the
  two consultation triggers and user-controlled handling of unavailable reviews.
- `smoke-test.py`: offline wrapper checks using a fake Claude executable; requires
  Python 3 and `jq`, with no account or network use.

After reviewing the files, install them under your own user account:

```sh
# Run from the repository root. Review existing files before replacing them.
mkdir -p "$HOME/.local/bin" "$HOME/.config/consult-claude"
install -m 755 examples/advisor/consult-claude "$HOME/.local/bin/consult-claude"
install -m 644 examples/advisor/advisor-role.md "$HOME/.config/consult-claude/advisor-role.md"
install -m 644 examples/advisor/brief-template.md "$HOME/.config/consult-claude/brief-template.md"
```

Merge the instruction snippet into your global Codex instructions; preserve
existing instructions and use `AGENTS.override.md` if it takes precedence.
Follow the main advisor guide for authentication and live acceptance checks.

Run the offline checks from the repository root:

```sh
python3 examples/advisor/smoke-test.py
```

The tests create and remove a temporary fixture directory beside the script.
They check argument/environment wiring and simulated result handling. They do
not prove model access, account billing behavior, or live permission enforcement.

The reference wrapper keeps the configured model, effort, defaults, and account
spending policy. Unlike the original setup example, missing `modelUsage` returns
`MODEL_MISMATCH` (exit 7), and the fixed model must match exactly rather than as a
substring; neither missing identity nor a similar model name counts as success.

Read-only operation depends on Claude permissions as well as the role. Safe mode
does not erase saved permission rules, so preapproved Bash commands can still
write. Check each checkout's applicable settings. The wrapper itself writes logs;
it is not an OS filesystem sandbox or proof of a checkout-only read boundary.
`--strict-model 0` leaves fallback to the account's existing settings. Give
concurrent calls distinct topics, keep `.consult/` out of Git, and never put
credentials in briefs or logs.
