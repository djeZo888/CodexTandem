# Setup

Use this checklist to qualify each host once, then recheck the facts that can drift before a task. Keep your actual addresses, fingerprints, credential locations, and project paths in a private local profile outside this repository.

## 1. Record a small host inventory

| Field | Orchestrator | Each worker |
| --- | --- | --- |
| Host role | Plans, dispatches, reviews, integrates | Implements and tests owned tasks |
| Connection | Local ordinary user | Verified SSH alias and ordinary user |
| Platform | OS and architecture | OS and architecture; native toolchain support |
| Workspace | Integration checkout | Isolated checkout or worktree for each task |
| Tools | Git, SSH, project tools, Codex CLI | Same tools needed by assigned work |
| Authentication | Codex auth; GitHub root access | Codex auth; limited GitHub worker access if needed |
| Capacity | Review and integration budget | CPU, memory, storage, concurrent session limit |

For an ARM Linux worker, confirm the project dependencies support its architecture before assigning native builds. An x86 or GPU test target can remain a separate, explicitly controlled integration target.

## 2. Establish dedicated SSH access

Use one dedicated key for each worker. Generate it on the orchestrator, keep the private key there, and install only its public key on the intended account. Preserve existing `authorized_keys` entries and access. Use normal account permissions; do not make `sudo` part of the default workflow.

```sshconfig
# Private ~/.ssh/config example; replace every placeholder locally.
Host worker-one
    HostName <worker-hostname>
    User <ordinary-worker-account>
    IdentityFile ~/.ssh/id_ed25519_worker_one
    IdentitiesOnly yes
    ForwardAgent no
    StrictHostKeyChecking yes
```

Verify the host-key fingerprint through a trusted, independent path before adding the host to `known_hosts`. A key gathered with `ssh-keyscan` is a candidate key; gathering it does not establish trust. If the identity changes, investigate it before replacing the trusted entry.

Use `ssh -G worker-one` to inspect effective configuration. Confirm the intended account, identity file, strict host checking, and disabled agent forwarding. A read-only SSH check should report the expected hostname, OS, architecture, working directory, and installed tool versions. Keep private host details out of public task reports.

## 3. Authenticate the CLI on each host

Authenticate Codex using an approved account or provider on each host. Do not put authentication files, API keys, GitHub PATs, or private SSH keys in the repository, briefs, logs, screenshots, or command-line examples. GitHub authentication, Codex authentication, and SSH authentication are separate credentials with separate purposes.

Read-only CLI checks:

```sh
codex --version
codex exec --help
codex login status
git --version
```

These checks do not prove a paid model call or workspace edit works. Once authorized, qualify the host with one bounded real task: read a small fixture, make an isolated reversible edit, run its check, return the diff, and verify session closure. Keep that acceptance separate from tool installation and login checks.

## 4. Preserve the requested model

Record the user's exact model and reasoning selection in the task. Resolve its executable model identifier from the installed CLI's supported model listing, selection interface, or local model metadata. Confirm that the requested reasoning setting is supported by that model on that host. Do not invent an identifier from a display name or silently substitute a newer model.

If the exact selection is unavailable, report that constraint and leave the task undispatched until the user chooses an alternative. Model availability and CLI configuration can differ across hosts. Repeat this check after a CLI or provider change.

## 5. Isolate the task workspace

Use a separate clone or worktree per task, rooted at the approved base commit. A worktree shares its repository's Git storage, so serialize operations that touch shared Git state. A separate clone is useful when independent Git operations or long-lived tasks make that simpler.

Keep the orchestrator's integration checkout separate from worker checkouts. Workers must not edit the same checkout or push to the default branch. If one task needs a change to another owner's file, return that need to the orchestrator and adjust ownership before either edits it.

Recommended local layout, adapted to each platform:

```text
<worker-storage>/
  projects/<project>/<task>/       # task checkout
  artifacts/<project>/<task>/      # submitted patch/bundle and receipt
  logs/<project>/<task>/           # original stdout/stderr and test logs
  builds/<project>/<task>/         # isolated build outputs
  cache/                          # approved shared download cache
```

The usual `workspace-write` run permits model-generated writes in the task checkout. Keep test/build outputs there when possible. If a task needs an external task-owned build, environment, or artifact directory, grant only that directory with `--add-dir <task-owned-path>` after checking local CLI help. The launcher can capture logs outside the checkout; that does not grant the agent permission to write other external paths. Prepare shared caches through their assigned owner instead of broadly exposing the worker's storage root.

Do not migrate active Codex or SQLite state as part of routine project setup. Any storage move needs a separate plan that stops all state writers, preserves rollback, and verifies integrity and restart.

## 6. Preflight before each dispatch

- The trusted host identity and expected ordinary account still match.
- The chosen checkout is clean, isolated, and at the recorded base commit.
- The exact model and reasoning setting are available; CLI help matches the planned flags.
- Required dependencies are ready, or the task can make useful progress without them.
- File ownership, shared resources, acceptance checks, and the user-selected timebox are explicit.
- Log and artifact paths are writable without exposing credentials.
- Any previous owner of this workspace or shared resource is closed and verified absent.

Keep this preflight short and proportional. It is a host and task readiness check, not a new management framework.
