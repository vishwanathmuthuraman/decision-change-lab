# 03 — Public milestones

The repository currently contains a design and synthetic example. All application and experiment milestones below are pending; a milestone is complete only when its evidence is available.

| Milestone | Intended result | Evidence required |
|---|---|---|
| M1 — Validated contracts | Reject malformed identities, amounts and times; preserve versioned facts and knowledge cutoffs. | Contract and history tests; a reproducible environment. |
| M2 — Guarded replay | Replay the supplier-hold example with immutable approvals, separate pending/completed consequences and idempotent local dispatch. | Actual trace, race/retry tests and normalized replay digests. |
| M3 — Comparable strategies | Compare cached, fixed-expiry, full and selective revalidation using the same policy, evidence and final guard. | Strategy contract tests and reviewed comparison configuration. |
| M4 — Deterministic study | Freeze the dataset and evaluation protocol, then account for every control episode. | Split audit, immutable manifests, complete results and limitations. |
| M5 — Optional agent-input study | Evaluate validated model proposals separately from deterministic replay. | Proposal provenance, four-way replay equality, error/cost accounting and explicit incomplete status if deferred. |
| M6 — Reproducible release | Publish a reviewed artifact that another environment can reproduce. | Clean-install record, demo, measured report and release review. |

Read the [requirements](01-product-requirements.md), [architecture](02-architecture.md), [evaluation protocol](04-evaluation.md) and [definition of done](05-definition-of-done.md) for the public behavioral contract. M4 must precede a control-study claim; M5 additionally precedes an agent-study claim. A useful negative result remains publishable when all runs and limitations are reported.

The intended interface is a local command-line runner with an optional read-only report interface. No application installation or execution command is available today. A future quick start must use commands tested against the released implementation.

Milestone updates should link the relevant source revision, verification artifact and unresolved limitations. Planned sample sizes and expected fixture outcomes must not be presented as observed results.
