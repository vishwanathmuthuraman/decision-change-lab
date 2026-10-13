<p align="center"><img src="docs/assets/brand/logo.svg" width="88" height="88" alt="DecisionLatch logo"></p>

# DecisionLatch — Decision revalidation research

<p align="center"><img src="docs/assets/brand/banner.svg" width="100%" alt="DecisionLatch: Keep decisions connected to changing evidence. Versioned facts, Dependency tracing, Review evidence. Offline research components."></p>

[![Implementation checks](https://github.com/vishwanathmuthuraman/decision-change-lab/actions/workflows/implementation.yml/badge.svg?branch=main)](https://github.com/vishwanathmuthuraman/decision-change-lab/actions/workflows/implementation.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square)](pyproject.toml)
[![Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-68b89b?style=flat-square)](LICENSE)
[![Documentation integrity](https://github.com/vishwanathmuthuraman/decision-change-lab/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/vishwanathmuthuraman/decision-change-lab/actions/workflows/docs.yml)

[Quick start](#run-the-initial-implementation) · [Implemented scope](docs/IMPLEMENTATION.md) · [Architecture](docs/02-architecture.md) · [Evaluation](docs/04-evaluation.md) · [Contribute](CONTRIBUTING.md)

---

**Which approved decisions should be checked again when their supporting facts change?**

Trace source versions to dependent decisions, identify affected work, and compare revalidation strategies under a shared final execution check.

**Stage: initial offline implementation.** Runnable Python components, synthetic demos and behavioral tests are available. The complete workflow, predictive/model evaluation and production product remain pending.

This is the public research project previously called **Decision Change Lab**. The repository URL, Python package and CLI commands remain unchanged.

## Run the initial implementation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from this repository. The runtime is pinned to Python 3.12.13; dependencies are pinned in `uv.lock`.

```sh
uv sync --locked
uv run --locked dcl inspect examples/supplier-hold.json
uv run --locked pytest
```

The CLI prints JSON. `validate` checks the same input contract; invalid or unsupported input returns exit code 2 with a JSON error on stderr. Successful inspection returns exit code 0.

**Initial verification:** 17 behavioral/CLI tests, Ruff checks, and an installed wheel executed outside the checkout. The [original verification record](reports/initial-implementation/verification.json) and [captured demo output](reports/initial-implementation/demo-1.json) retain the evidence for that first slice.

**Current component checks:** 35 source tests and the same 35 tests against an installed wheel pass. Approval bindings now preserve grant-time evidence versions and both validity bounds, reject changed evidence, and expose read-only mappings. See [implemented behavior and remaining work](docs/IMPLEMENTATION.md). This is a trusted offline fixture component: the digests check consistency, and the helper does not authenticate approvals or authorize dispatch. Durable issuance, revocation and the final execution guard remain pending.

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
| [Initial implementation](docs/IMPLEMENTATION.md) | Runnable component code, boundary tests and captured synthetic output. |
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

This checks documentation only. Behavioral tests run separately in the **Implementation checks** workflow. The repository's **Documentation integrity** workflow runs the same check on pushes and pull requests.

## Research roadmap

- [x] Define the problem, contracts and illustrative synthetic scenarios.
- [x] Document evaluation methods and consequential failure cases.
- [x] Implement and test the initial offline components documented above.
- [ ] Complete the full offline workflow and baseline required by the release criteria.
- [ ] Complete held-out comparisons and publish actual results, including failures.
- [ ] Seek independent reproduction and review.

## Scope and contribution

See [contribution guidance](CONTRIBUTING.md) for useful review questions. Reports should include a minimal synthetic example and the relevant requirement or evaluation rule. Never submit customer records, credentials or private operational information.

This is a curated research repository. Internal delivery schedules and commercial planning are maintained separately. Public technical methods are deliberately inspectable; public availability does not imply production readiness.

Maintained by [Vishwanath Muthuraman](https://github.com/vishwanathmuthuraman). Source material is cited; citations do not imply endorsement. Original code, documentation and synthetic fixtures are licensed under Apache-2.0; see LICENSE and NOTICE. Third-party material retains its own terms.

## License

Original repository material is licensed under [Apache-2.0](LICENSE). See [licensing and attribution](docs/09-licensing.md) for scope, third-party material and distribution requirements.
