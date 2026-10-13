# Initial implementation — 0.1.0

This is the first implemented offline slice. “Complete” below means the bounded component passed the recorded checks; it does not mean the proposed product or evaluation is complete.

## Completed component tasks

| Task | Work | Status | Delivered behavior |
|---|---|---|---|
| C01 | Validate scenario and source events | Complete for this slice | Strict schemas, time windows, references and integer money; reject conflicting source identities. |
| C02 | Persist versioned facts and inspect dependencies | Complete for this slice | Atomic SQLite ingestion, identical-delivery deduplication, restart persistence, as-of visibility and affected decision IDs. |
| C03 | Package, test and document the slice | Complete for this slice | Independent Python package, packaged existing schema resources, locked dependencies, CLI error behavior, behavioral tests, CI and captured demo evidence. |

Source: [core](../src/decision_change_lab/core.py), [contracts/utilities](../src/decision_change_lab/common.py), [CLI](../src/decision_change_lab/cli.py), [behavioral tests](../tests/test_core.py), [CLI tests](../tests/test_cli.py). Runtime selection is recorded in [ADR 0001](decisions/0001-offline-core.md).

## Initial verification (historical)

Verified on Python **3.12.13**, Darwin: **17 tests passed, zero failed**, Ruff lint/format checks passed. A wheel was built, installed with locked dependency hashes into a fresh environment and exercised from outside the checkout; its schema files loaded from the installed package. The CLI input/output hashes and implementation-file hashes are in the [verification record](../reports/initial-implementation/verification.json). That file identifies exact tested inputs; expected specifications were not copied into an execution report.

```sh
uv sync --locked
uv run --locked dcl inspect examples/supplier-hold.json
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
uv run --locked pytest
```

Observed demo: At the supplied horizon, the supplier hold produces review candidates DEC-A and DEC-C. DEC-B remains unaffected. The report explicitly records that dispatch is unimplemented.

[Captured output](../reports/initial-implementation/demo-1.json). Test use of authored expected files is restricted to development assertions; application code does not open them. These are component regressions, not independent held-out evaluation or performance measurements.

## M2 increment: immutable approval bindings (FR-04, first part)

[approval.py](../src/decision_change_lab/approval.py) creates a read-only in-memory binding, including a read-only source-version mapping. It captures the fixture decision revision, payload digest, actor, policy version, source versions and both bounds of the approval window.

Binding resolves the evidence available at the approval's `granted_at`, checks it against the recorded dependency and policy versions, and rejects binding later if those versions changed. Visible actor/policy facts take precedence over the fixture's baseline snapshot. An old approval seed cannot silently acquire newer evidence. A new trusted fixture approval must carry its new grant time and matching recorded versions; this helper does not issue or authenticate human approvals.

`verify_binding` checks consistency, revision, payload, source versions and the half-open validity window: `granted_at <= at < valid_until`. It reports `approval_not_yet_valid`, `approval_expired`, `binding_tampered`, `revision_mismatch`, `payload_mismatch` or `source_versions_changed`. Missing evidence still raises `ContractError`. An empty reason list is not permission to dispatch.

Five regression cases failed against the original draft: actor and policy rebinding, mutation at the top level and in nested source versions, and verification before the grant. After the fixes, **35 source tests passed**, including the earlier core/CLI tests. The same 35 tests also passed against a clean installed wheel from outside the checkout. Ruff lint/format and documentation integrity checks passed. Positive cases also cover new fixture approvals after authority changes, grant-time acceptance, policy-version mismatch and mutation of caller-owned inputs. These are synthetic component checks, not a held-out benchmark.

The unkeyed digests detect accidental inconsistency; anyone able to rewrite a record can recompute them. Read-only mappings prevent mutation through the returned Python interface, not hostile same-process code. Input fixtures are trusted grant-time records, not an authenticated issuance ledger. The helper does not prevent a caller from inventing a replacement scenario or approval ID.

Remaining limits: no durable approval/revision ledger, revocation, benign revalidation proofs, final execution guard, dispatch, idempotency receipts or replay. No serialization or restart guarantee is claimed for these local mapping views. FR-04 and M2 remain partial.

## Relationship to the full plan

M1 has initial contract/history evidence; M2 has partial approval-binding evidence. The rest of M2 and M3–M5 remain pending. M6 has packaging checks for the implemented components, not a complete research release.

The [build plan](03-build-plan.md), [requirements](01-product-requirements.md), [evaluation](04-evaluation.md) and [definition of done](05-definition-of-done.md) remain the release criteria. Planned acceptance registers describe the wider system; partial progress does not replace their full conditions. Documentation checks validate authored artifacts separately from application CI.

## Explicit limits

Approval execution, dispatch, correction/supersession semantics, revalidation strategies and the controlled study are unimplemented. The inspector reports dependency changes; it does not decide whether a proposed business action is safe.

All example records and observations are synthetic. No network integration or external business action exists in this slice. Financial and property results support human review. No customer impact, trained-model quality, production readiness or independent endorsement is established.

## Next implementation steps

1. Persist approval/revision records and add revocation plus a final execution guard against current policy, actor authority and fact versions; test restart and a fact change during dispatch.
2. Add a replay runner with pending/completed consequences and persisted idempotent local effects; demonstrate retry and restart behavior before comparing strategies.
3. Implement the four strategies behind one guard, then freeze scenarios and evaluation inputs before measuring outcomes.

For each step, add meaningful failure-case tests, capture actual output, preserve evidence/time/money boundaries, and update this record with the revision and unresolved limitations. Do not mark the full release complete from component test counts.
