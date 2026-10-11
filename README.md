# Decision Change Lab

![Decision Change Lab — Reliable decisions when the facts change.](docs/assets/overview.svg)

[![Documentation integrity](https://github.com/vishwanathmuthuraman/decision-change-lab/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/vishwanathmuthuraman/decision-change-lab/actions/workflows/docs.yml)

**Which approved decisions should be checked again when their supporting facts change?**

Trace source versions to dependent decisions, identify affected work, and compare revalidation strategies under a shared final execution check.

**Stage: research specification.** This repository contains design work and synthetic examples. Application implementation and performance evaluation are pending; there is no working product or measured result yet.

[Explore the example](#a-concrete-example) · [Architecture](docs/02-architecture.md) · [Evaluation protocol](docs/04-evaluation.md) · [Engineering standards](ENGINEERING.md)

## A concrete example

A purchase-order amendment is approved. Before execution, a supplier is placed on hold. The approval still exists, but the evidence that justified it has changed.

[Supplier-hold input](examples/supplier-hold.json) · [Expected behavior](examples/supplier-hold.expected.json) · [Fixture guide](examples/README.md)

The expected outcomes describe the intended behavior. They are not output from an executed application.

## How the proposed system works

```mermaid
flowchart LR
    A[Versioned evidence] --> B[Decision dependencies]
    B --> C[Changed facts]
    C --> D[Revalidation queue]
    D --> E[Final execution guard]
    E --> F[Allow or block with evidence]
```

The engineering question is the tradeoff between rechecking everything and selectively rechecking decisions without relaxing the common final guard.

## What you can inspect today

| Artifact | What it establishes |
|---|---|
| Requirements and architecture | The proposed problem, boundaries and consequential design decisions. |
| Original synthetic scenarios and schemas | Concrete inputs and explicit expected behavior. |
| Evaluation protocol and release criteria | How implementation and claims should be assessed. |
| Source rationale | Which public evidence motivated the design and which conclusions remain hypotheses. |
| Documentation checks | Whether the supplied JSON, relative links and original SVG assets are structurally valid. |

One original synthetic scenario, input/output schemas, requirements, architecture and a comparative evaluation protocol.

## Technical choices

Python + SQLite for a reproducible event simulator and transactional state rules. A model adapter is optional; it cannot authorize execution.

Python, Go, Rust, SQL, TypeScript and Rails each have appropriate uses. This project follows [documented selection rules](ENGINEERING.md): add a runtime or framework only when requirements, profiling and maintainability justify it.

## What the evaluation must show

Compare four revalidation strategies using the same execution guard. Report unsafe actions, unnecessary review, completed work and limitations when dependencies are missing. Separate deterministic control experiments from optional model-generated proposals.

The [evaluation protocol](docs/04-evaluation.md) defines the comparison and limitations. No benchmark score, customer impact, novelty claim or independent endorsement is asserted.

## Read the design

| Start with | Then inspect |
|---|---|
| [Problem and requirements](docs/01-product-requirements.md) | [Architecture and boundaries](docs/02-architecture.md) |
| [Public implementation milestones](docs/03-build-plan.md) | [Evaluation protocol](docs/04-evaluation.md) |
| [Definition of done](docs/05-definition-of-done.md) | [Sources and design rationale](docs/06-sources-and-design-rationale.md) |
| [Technical limitations](docs/07-delivery-and-risk.md) | [Publication boundaries](docs/08-publication.md) |

## Check this documentation

From a clone of this repository with Python 3.12 or later:

```sh
python scripts/check_public_docs.py
```

This checks documentation only. Application installation and demo commands will be added when implemented and verified. The repository's **Documentation integrity** workflow runs the same check on pushes and pull requests.

## Research roadmap

- [x] Define the problem, contracts and illustrative synthetic scenarios.
- [x] Document evaluation methods and consequential failure cases.
- [ ] Implement and test a reproducible offline baseline.
- [ ] Complete held-out comparisons and publish actual results, including failures.
- [ ] Seek independent reproduction and review.

## Scope and contribution

See [contribution guidance](CONTRIBUTING.md) for useful review questions. Reports should include a minimal synthetic example and the relevant requirement or evaluation rule. Never submit customer records, credentials or private operational information.

This is a curated research repository. Internal delivery schedules and commercial planning are maintained separately. Public technical methods are deliberately inspectable; public availability does not imply production readiness.

Maintained by [Vishwanath Muthuraman](https://github.com/vishwanathmuthuraman). Source material is cited; citations do not imply endorsement. License selection is pending, and no code, documentation or data license grant is supplied.
