# 01 — Product requirements

Status: proposed requirements, not implemented. Read [architecture](02-architecture.md) next.

## Problem, user, and end state

A procurement operations reviewer approves an amendment using the information available at that moment. Later, a supplier is suspended, a price is corrected, or approval authority changes. A historical approval can remain authentic while its justification becomes stale. A generic event log does not by itself determine which decisions need attention.

The primary user is the reviewer responsible for purchase-order amendments. An automation owner configures rules and investigates failures. A researcher needs reproducible comparisons. These are proposed users; interviews and adoption have not been established.

The end state is a local demonstration where one changed supplier affects a pending amendment and a previously committed, still-open order, while an unrelated amendment can proceed. A reviewer sees the change, supporting records, applicable rule, affected decisions, and available next step. The same histories can be replayed through four strategies and scored without exposing the answer key to those strategies.

## User stories

| ID | Story | Observable acceptance |
|---|---|---|
| US-01 | As a reviewer, I need to know which facts an approval relied on. | Every approved revision has record IDs, source versions, policy version, and an approval binding. |
| US-02 | As a reviewer, I need relevant changes separated from unrelated changes. | A supplier-A hold targets dependent decisions; supplier-B decisions remain eligible if their own checks pass. |
| US-03 | As an automation owner, I need a stale amendment stopped at dispatch. | The shared final guard rejects a known-invalid amendment inside the local transaction. |
| US-04 | As a reviewer, I need completed work investigated without silent reversal. | A committed order keeps its committed status and receives an investigation case. |
| US-05 | As a researcher, I need fair comparisons and observable failures. | Identical scenario/schedule inputs reach each strategy, and all failed or timed-out runs remain in the report. |

## Functional requirements

| ID | Required behavior | Acceptance evidence planned |
|---|---|---|
| FR-01 | Validate versioned synthetic scenario input; reject malformed times, amounts, references, and duplicate conflicting IDs. | Schema plus semantic validation tests. |
| FR-02 | Preserve append-only source versions with effective time and observed time; provide a knowledge-cutoff query. | Delayed, corrected, and out-of-order fact tests. |
| FR-03 | Store immutable decision revisions and recorded dependencies, identifying supplied-oracle versus extracted dependencies. | Revision and dependency integrity tests. |
| FR-04 | Bind approval to decision revision, normalized payload, policy version, source-version digest, actor, and expiry. | Mutation, revocation, and stale-proof tests. |
| FR-05 | Implement cached, fixed-expiry, full, and selective revalidation using one policy evaluator and the same decision population. | Strategy selection contract tests and fairness manifest. |
| FR-06 | Revalidate pending work and open investigations for affected committed work using the same escalation rules for every strategy. | Pending/completed transition tests. |
| FR-07 | Enforce an atomic local final check and simulated commit; failed checks cannot write an executed order amendment. | Two-connection race, rollback, and conditional-write tests. |
| FR-08 | Deduplicate event delivery and execution requests; reject same idempotency key with changed content. | Duplicate, conflict, and retry tests. |
| FR-09 | Record ordered audit events, reasons, state changes, source references, and investigation ownership. | Replay equality and trace completeness tests. |
| FR-10 | Replay virtual-clock schedules deterministically with injected faults and no wall-clock sleeps. | Repeat replay produces the same normalized digest. |
| FR-11 | Isolate truth labels and future observations from system-visible inputs. | Redaction and future-knowledge access tests. |
| FR-12 | Produce separate control/agent results with denominators, failure cases, clustered uncertainty, and costs. | Count reconciliation, identical cached proposals across strategies, and hand-checked metric tests. |
| FR-13 | Add an optional provider-neutral agent adapter with validated structured output and bounded calls. | Mocked adapter, invalid-output, budget-stop, and restricted-tool tests. |
| FR-14 | Run the core demo without network access or credentials and provide an independent fresh-install reproduction. | Offline demo and clean-environment record. |
| FR-15 | Export a reviewer-readable case report without raw prompts, secrets, or hidden labels in system traces. | Export content review and schema test. |

## Proposed business rules for version 1

Use one simulated currency, USD, represented as integer cents, and integer units. An amendment contains an order ID, supplier ID, quantity, unit price, and requested delivery date. It must satisfy all of the following at dispatch: supplier active; positive bounded quantity; unit price and total within the current contract/policy limits; current authorized approval for the exact revision; and an open order eligible for amendment. Derive totals deterministically, never from model arithmetic.

A changed value does not necessarily require escalation. Revalidation can establish that a change was benign; it records work but leaves a valid approval usable under the frozen policy. If the decision remains substantively valid but its bound source versions change, issue a new machine revalidation proof referencing the original human approval and current versions. This is allowed only when the frozen policy explicitly permits it; a substantive amendment or authority change requires a new human approval. Never silently rebind an approval across a material change.

For this benchmark, an open committed order linked to a newly suspended supplier requires an investigation, even if it was valid when committed. This is a synthetic workflow rule, not an assertion about procurement law or universal practice. A completed investigation records a reviewer disposition; it does not undo the original order.

## Nonfunctional requirements and non-goals

- Reproducibility: pin dependencies and runtime, record the code revision and configuration, and separate virtual time from measured runtime.
- Inspectability: explain a hold with a rule and source references, rather than a model’s unsupported narrative.
- Bounded execution: configurable per-run step, duration, and optional model-spend limits; distinguish error from a business rejection.
- Recovery: a crashed transaction leaves no partial execution. Database rebuild from fixture plus durable audit input is testable.
- Local isolation: no live credentials, remote execution endpoint, public upload, multi-tenant authorization, distributed transaction, real payment, or production ERP connector in v1.
- Research integrity: no promise that selective revalidation wins, that synthetic cases represent all incidents, or that the design is novel.

An optional UI visualizes existing state. It must not become a prerequisite for evaluating the system. Production authentication, high availability, distributed event delivery, and customer-data integration require a separate scope and threat model.
