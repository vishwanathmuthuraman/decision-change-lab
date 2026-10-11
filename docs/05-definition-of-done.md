# 05 — Definition of done and demonstration

**Every gate is currently unachieved.** This document specifies future acceptance, not test results. “Documentation prepared” is the present repository status. An implementation release is accepted only from linked evidence, not a checked box without an artifact.

## Requirement-to-test traceability

Test names below are planned identifiers; files do not exist yet.

| Requirement | Planned test IDs / location | Required evidence |
|---|---|---|
| FR-01 | T-01 `test_fixture_validation` | Valid input accepted; malformed amount/time/reference and conflicting identity rejected. |
| FR-02 | T-02 `test_fact_history` | Future facts excluded; backdated correction preserves prior knowledge; out-of-order history correct. |
| FR-03 | T-03 `test_approvals` | Immutable revisions and dependency-origin labels persist across restart. |
| FR-04 | T-04 `test_approvals` | Payload/authority/policy mutations cannot reuse stale authority; permitted benign proof documented. |
| FR-05 | T-05 `test_strategies` | Four selectors share identical evaluator, guard, population, and allowed response. |
| FR-06 | T-06 `test_strategies` | Pending hold and completed investigation differ; no automatic reversal. |
| FR-07 | T-07 `test_dispatch_races` | Both write orderings, conditional conflict, and rollback tested with independent connections. |
| FR-08 | T-08 `test_dispatch` | Duplicate request executes once; changed-key-content conflicts; event redelivery is harmless. |
| FR-09 | T-09 `test_replay` | Trace has causal order, reasons, references, and deduplicated cases. |
| FR-10 | T-10 `test_replay` | Repeated normalized replay digest matches without wall-clock sleeps. |
| FR-11 | T-11 `test_oracle` | Truth, future observations, split/template labels, descriptive IDs/paths, and fault hints cannot be read through initial or tool-response interfaces. |
| FR-12 | T-12 `test_metrics` | Hand-checked metrics, zero denominators, highest shared lineage clusters, failures, and 120-to-480 sample/episode counts reconcile. |
| FR-13 | T-13 `test_agent_boundary` | Invalid output, absent evidence, tool restriction, step/cost cutoff, provider failure, and immutable cache replay across all four strategies tested. |
| FR-14 | T-14 fresh-install record | Another clean environment runs locked install and offline demo. |
| FR-15 | T-15 `test_export` | Reviewer report references evidence and contains no secret or hidden-label leakage. |

## Five-minute demo script

Use the original example in `examples/`, not the held-out test set. The script is a future acceptance sequence.

1. **0:00–0:45 — State the problem.** Show two suppliers and three approved amendment records. Decision A and C reference supplier A; decision B references supplier B. Explain that all names and records are synthetic.
2. **0:45–1:30 — Show the approval basis.** Open decision A’s source versions, amendment, reviewer authority, and policy. Show decision C already committed before the hold became effective, with an open obligation.
3. **1:30–2:15 — Observe a delayed fact.** Ingest supplier A’s hold, effective 08:10 and observed 08:12. Explain that the system could not use this observation before 08:12.
4. **2:15–3:15 — Show consequences.** Selective revalidation holds pending A, leaves committed C committed and opens one investigation, and avoids escalating B. Dispatch A is rejected by the common guard; B commits.
5. **3:15–4:00 — Retry and inspect.** Retry B with the same idempotency key and show the same receipt and no second mutation. Show C’s case evidence and permitted reviewer disposition.
6. **4:00–5:00 — Compare and limit.** Show actual baseline output once implemented. Explain that early detection/work can differ even when all strategies block A at dispatch. Display missing-dependency and notification-loss failures, and the local-only atomicity boundary.

Never replace a failed step with pre-recorded output labeled live. A recording must name its code version and show whether it uses the deterministic fixture or agent mode.

## Release acceptance targets

| Gate | Target, not achieved | Evidence needed |
|---|---|---|
| R-01 Core correctness | All consequential transition, race, retry, knowledge-time, and leakage tests pass. | CI/run log at release commit; failures resolved or release blocked. |
| R-02 Demonstration | Example matches the specified assertions and runs offline with no credentials. | Fresh-run manifest and reviewed report. |
| R-03 Fair comparison | All four strategies use the same guard, evidence, policy, and response population. | Contract tests and frozen configuration diff. |
| R-04 Dataset integrity | 50 development and 200 held-out cases with required strata; no template-group leakage. | Dataset audit, hashes, review record. |
| R-05 Control evidence | 2,400 expected episodes accounted for, including failures, with paired analysis. | Run/status table, metrics, cluster count, report. |
| R-06 Agent evidence | 120 generated proposal samples and 480 paired replay episodes accounted for after the agent gate; separate extraction/error/cost analysis. | Subset/schedule manifest, versioned prompts, immutable proposal IDs/digests, four-way input-equality checks, sample/episode status tables. |
| R-07 Honest claims | Every numerical statement traces to actual output and identifies uncertainty/limits. | Claim-to-artifact review and technical report. |
| R-08 Reproduction | Locked install and offline demo reproduced in another clean environment. | Environment, commands, outputs, deviations, reviewer date. |
| R-09 Public release hygiene | Ownership/license choices recorded; public files reviewed; generated sensitive artifacts excluded. | Publication checklist and approved artifact list. |

R-01–05 and R-07–09 can support a **control-study release** explicitly labeled as such if agent work is incomplete. The planned full release additionally requires R-06. Do not call the agent study done merely because a mocked adapter test passes. A selective strategy need not outperform every baseline to ship an honest technical report. A failed control invariant does block a release advertised as implementing that invariant.

## Reviewer sign-off record to create later

Record reviewer role, date, commit/dataset versions, gates inspected, defects, dispositions, and remaining limitations. Record scope of review precisely: reviewing an example is not reproducing an entire benchmark. Do not invent reviewer names, consent, or independent validation. Track unresolved defects as issues with severity and a specific next action.
