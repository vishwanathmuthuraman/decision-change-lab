# 07 — Delivery case, risks, and decisions

Status: proposed management plan. No interviews, pilot commitments, operational savings, or implemented controls are claimed. Use actual dates and evidence as work proceeds.

## Delivery case and sequence

Objective: deliver an independently reproducible local workflow and a fair evaluation of revalidation strategies. Intended user value is faster identification of decisions needing attention while preserving valid work; this remains a hypothesis until measured in an appropriate setting.

Deliver the deterministic vertical slice first: fixture -> approval -> source change -> selection -> hold/case -> guarded dispatch -> trace. Then expand cases and metrics, add the bounded agent path, freeze the test protocol, and write the report. Keep the UI optional. A sequential 10–14 week engineering window is a planning estimate; the work packages total 184–250 focused hours before contingency. Research review and waiting for feedback can extend elapsed time.

Decision gates: G1 scope after WP-01; G2 atomic control after WP-06; G3 reproducible demo after WP-08; G4 protocol/budget freeze after WP-11; G5 release after WP-14. If a gate fails, record the reason and revise downstream dates. Do not reduce held-out integrity to meet a date. Public implementation status changes only when there is a working artifact.

## Responsibilities and working cadence

The implementer owns code, evidence integrity, and traceable claims. A domain reviewer checks scenario realism; a reproduction reviewer checks installation and stated outputs. A reviewer’s involvement is a target until accepted. A writing assistant may format reviewed public content but cannot invent results, grant data rights, or approve technical findings.

Weekly review: update task status and actual hours; show one inspectable artifact; review new failure evidence; resolve one highest-impact uncertainty; and record scope changes. Use `not_started`, `in_progress`, `blocked`, `in_review`, or `done` in the tracker. A blocked task needs a reason and next action. “Done” requires its stated acceptance evidence.

## Cost assumptions, not spending authorization

The deterministic study requires no paid model calls. Local runtime, storage, electricity, and reviewer time still have costs; measure runtime and report hardware. Optional hosting is unnecessary for the local release.

For the agent study, estimate token cost from an actual development pilot:

`estimated_model_cost = 120 × (mean_input_tokens_per_generation_sample × input_price_per_million + mean_output_tokens_per_generation_sample × output_price_per_million) / 1,000,000`

Add tool/API charges, development runs, failed calls, and a separately stated retry allowance. The 120 samples are cached and replayed in 480 strategy episodes without further model calls. A sample can contain multiple bounded calls; aggregate their tokens before estimating. For illustration only, a measured US$0.02–0.10 per generation sample would imply US$2.40–12.00 for 120 samples before these additions. Local replay work is measured separately. This is arithmetic, not a vendor quote or forecast. Record price date, caching assumptions, currencies, and billed-versus-estimated totals. A US$50 development planning cap can be used as a stop-and-review threshold, but it is not authorization to spend. Set a real permitted budget before paid calls and stop before exceeding it.

Budget 20–30% engineering contingency for state/time bugs and analysis fixes. Treat reviewer and discovery hours separately from implementation so a low API bill does not hide human effort. Defer the agent study if its gate cannot be funded; label the delivered scope accurately.

## Risk register

| ID | Failure -> consequence | Proposed control and test | Residual risk / launch decision |
|---|---|---|---|
| K-01 | Missing dependency -> early review missed | Compare supplied vs corrupted/extracted edges; common dispatch guard; T-05/T-13. | Completed work can remain unidentified; disclose, measure, and avoid broad prevention claims. |
| K-02 | Unobserved correction -> decision uses obsolete knowledge | Effective/observed times; T-02; separate retrospective scoring. | No system can use an unavailable observation; describe detection limits. |
| K-03 | Check/use race -> invalid local mutation | Single SQLite transaction and conditional write; T-07. | Remote transaction not covered; prohibit live execution in v1. |
| K-04 | Retry -> duplicate order/case | Stable idempotency identity, uniqueness constraints; T-08/T-09. | Caller changing keys can defeat deduplication; document contract. |
| K-05 | Full blocking appears safe -> unusable workflow | Valid-action completion and false escalation metrics; T-12. | Synthetic workload may not reflect reviewer tolerance; no productivity claim. |
| K-06 | Test leakage -> optimistic results | Group partitioning, sealed hashes, evaluator separation; T-11. | Solo authors know generator assumptions; disclose and seek independent cases. |
| K-07 | Incorrect grader -> false finding | Manual truth audit, hand-calculated metrics, consistent rescoring. | Reviewer disagreement remains possible; publish ambiguity and deviations. |
| K-08 | Model invents fields -> wrong proposal | Strict schema, reference validation, restricted tools; T-13. | Schema-valid false content still exists; require policy/review path. |
| K-09 | Scope expansion -> unfinished core | Gated build plan and optional UI/integration. | Estimates may change; reduce extras, not truthfulness. |
| K-10 | Public artifact leaks unrelated data -> confidentiality breach | Synthetic-only allowlist and content/history review; R-09. | Ignore rules do not sanitize tracked files; inspect before release. |
| K-11 | Source article mistaken for evidence of demand -> unsupported claim | Finding/inference table and actual discovery records. | Buyer usefulness remains unresolved until observed. |
| K-12 | Ambiguous licensing -> unusable release | Select code/docs/data licenses and review dependencies before release. | Blueprint is not an existing license grant. |

No operational probabilities are assigned before measurement. Severity prioritization should use a stated consequence and scope, rather than invented loss numbers.

## Initial decision log

| ID | Proposed decision | Rationale | Revisit trigger |
|---|---|---|---|
| D-01 | Local Python/SQLite simulator | Inspectable atomic boundary and simple reproduction. | An authorized integration requires a different boundary. |
| D-02 | One amendment workflow and one currency | Makes truth and failure interpretation tractable. | Core study complete and a second workflow has a distinct question. |
| D-03 | Four strategies share the final guard | Isolates selection/timing instead of granting the new strategy better protection. | A separately specified guard ablation is approved and funded. |
| D-04 | Three schedules, one assigned schedule per agent case; 120 cached proposals replayed four ways | Preserves 2,400 control and 480 paired agent-input episodes; isolates revalidation with matched proposal errors. | Development pilot shows coverage is inadequate; amend before freeze. |
| D-05 | Report negative results | Scientific value depends on valid evidence, not a winning product narrative. | Never revise merely because an outcome is inconvenient. |
| D-06 | No license chosen yet | Ownership and reuse terms need an explicit decision. | Before an openly licensed release. |

For every later decision record date, alternatives, evidence, owner, chosen tradeoff, and next review condition. The retrospective should compare original estimates to actual delivery, describe discarded features, and identify which claims remain unproven.
