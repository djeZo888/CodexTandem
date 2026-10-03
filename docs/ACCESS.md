# Access and credential boundaries

Use separate credentials for SSH login, Codex model access, and GitHub repository access. Keep secret values in protected local storage or a credential manager. A private local profile may record where a credential is stored; it should not contain the credential itself.

## GitHub fine-grained PAT permissions

Choose **Only select repositories** and select the project repositories that need access. Set an expiration appropriate to the work. The table below is a practical starting point for this operating method; add permissions only when an assigned task requires them. GitHub documents [repository selection and fine-grained permissions](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

| Repository permission | Orchestrator / root token | Worker token | Purpose |
| --- | --- | --- | --- |
| Contents | Read and write | Read and write | Fetch code and push owned work branches |
| Metadata | Read | Read | Repository metadata |
| Pull requests | Read and write | No access | Orchestrator opens and maintains PRs |
| Actions | Read | No access | Orchestrator inspects CI results and logs |
| Workflows | Write only if managing CI files | No access | Change workflow definitions when assigned |
| Issues | Write only if issue work is required | No access | Track or update issues when assigned |
| Administration | No access | No access | Routine work does not manage repository policy |
| Secrets | No access | No access | Routine work does not manage repository secrets |
| Other repository, organization, account permissions | No access | No access | Grant only for a separately required action |

With this table, workers return a branch, patch, or Git bundle and receipt. The orchestrator handles PR creation and integration. Workers can also work without a GitHub write credential by returning a patch or bundle over the verified SSH path.

## Contents write also permits merging

**A worker PAT with Contents write is not a branch-only credential.** GitHub's [merge pull request endpoint](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request) accepts Contents write. Removing Pull requests write does not by itself prevent merges.

Protect the default branch with repository rules or branch protection, required review, and the intended human merge gate. Ensure the actor used by the worker credential has no bypass path for those rules. A separately authorized maintainer configures this policy; routine root and worker tokens do not need Administration permission.

Two PATs from the same account are useful for different scopes and revocation, but they do not create separate GitHub identities or a reliable enforced root/worker role boundary. PAT permissions are bounded by their owner, as described in [GitHub's token documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). Use distinct identities or an appropriately configured GitHub App when enforced role separation is required.

## Shared worker token

A single worker token can be reused across trusted workers if the user chooses that tradeoff. It has the same repository and permission scope on every host. Revoking it affects all workers, and GitHub attribution remains the token owner's account; it does not identify which physical worker acted. Separate tokens per worker improve revocation and local auditing, while still sharing account attribution if created by one account.

Keep the root token only on the orchestrator. Store worker credentials independently on each worker through the chosen protected mechanism. Never place a PAT in a clone URL, a shell history entry, a task brief, or a public receipt.

## SSH and Codex

SSH grants access to an ordinary account on a particular host. Use dedicated per-worker keys, verified host fingerprints, `StrictHostKeyChecking yes`, `IdentitiesOnly yes`, and `ForwardAgent no`. Preserve existing authorized keys.

Codex authentication enables model access; it does not grant GitHub permissions. Authenticate each host through an approved method. Treat saved authentication state as secret and keep it outside public repositories. Do not copy authentication state into public CI or log its contents.

The normal worker run uses a workspace write sandbox and respects applicable approval rules. Do not add a sandbox or approval bypass because SSH is unattended. If a task requires more access, make the necessary action concrete and obtain the authorization required by the current project and environment.

## Local access profile

Keep an inventory outside Git with host aliases, ordinary accounts, verified identity status, workspace roots, selected repositories, credential storage locations, expiration dates, and permitted test targets. Record authorization by scope and action. A retired project's approval does not authorize a new project's live-system changes.
