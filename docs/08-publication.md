# 08 — Public release and maintenance runbook

This repository is prepared for authorized public GitHub sharing as a documentation blueprint. Public availability of these documents is not an application release: implementation, hosting, model calls and measured evaluation remain uncompleted. License selection is pending; no code, documentation or data license grant is supplied. The runbook describes future release requirements; it is not permission to publish unrelated material.

## Before any public repository release

1. Confirm which artifacts are being released and their ownership. Use only original synthetic fixtures or explicitly permitted public inputs. Do not add operational exports, access tokens, raw model logs, private correspondence, or screenshots containing unrelated tabs or identities.
2. Select licenses for code, documentation, and synthetic data, checking compatibility with dependencies and any future borrowed material. Add the actual license files only after that decision. “License pending” must not be presented as an open-source license.
3. Inspect the entire tracked-file list and history. Ignore rules prevent some new files being added; they do not remove previously tracked content or rewrite history. Review JSON, notebooks, logs, archives, screenshots, and metadata as well as text.
4. Keep a public allowlist: source code once implemented, reviewed synthetic fixtures, schemas, locked environment, tests, protocol, curated aggregate results, necessary synthetic failure traces, and documentation. Keep generated working artifacts outside this allowlist.
5. Check every claim against status: proposed design, implemented feature, measured result, reproduced result, and independently reviewed result mean different things. Replace future commands with tested commands only after they work.

## Implementation release procedure — FUTURE

- Complete the applicable gates in [definition of done](05-definition-of-done.md).
- Reproduce installation and offline demo in a clean environment; record exact commands, versions, and output digests.
- Run consequential tests, lint, and package build at the intended release revision. Record limitations and known defects in release notes.
- Freeze and review the artifact manifest. Generated `reports/` remains ignored; copy only reviewed publication artifacts into a deliberate tracked location such as `docs/results/`, with run IDs and provenance.
- Inspect repository status and diff before staging. Stage explicit reviewed paths rather than indiscriminately adding the workspace. Review history before the first public push.
- Create a versioned release only when publication is authorized. Record actual date, commit, dataset/protocol versions, reproduction instructions, and limitations. Never backdate activity or attach results to a version that did not produce them.
- Verify the published README, links, downloadable files, and quick start from the public view. If a hosted demo is later added, bind it to synthetic data and a separate deployment threat model.

## What the technical report should contain

Problem and scope; source-to-design rationale; related work; dataset generation and partitions; exact baseline differences; common final guard; oracle/dependency conditions; schedules; model and tool configuration; preregistered or merely frozen status; separate accounting for 120 generation samples and 480 paired replay episodes; immutable proposal matching; the conditional-on-generation estimand; error/work/completion results with uncertainty; representative failures; cost; limitations; protocol deviations; and reproduction instructions.

A technical report is not automatically a peer-reviewed paper. A preprint must be labeled as a preprint. Submission is not acceptance, and acceptance status must match the actual venue and version. Select a research venue only after a current related-work review and external feedback support a complete contribution; check its current anonymity and prior-publication rules before public posting. No venue deadline or acceptance is assumed here.

A future archive or DOI should identify the exact release and license. It is an identifier, not a quality certification. Keep old reports accessible with correction notices when an analysis changes; do not silently replace unfavorable numbers. A material grader correction gets a versioned erratum and consistent rescoring of all affected strategies.

## A truthful public description today

“Decision Change Lab is a proposed local research system for studying how workflows should respond when source facts change after approval. The documentation defines a synthetic purchase-order scenario, four revalidation strategies, a common execution check, and a planned evaluation. Implementation and experimental results are pending.”

Once implemented, replace that text with the specific completed features and actual measured evidence. Do not call this production-ready, compliant, loss-preventing, novel, adopted, independently validated, or commercially proven without appropriate evidence.

## Maintenance and incident procedure — FUTURE

For a reported bug: collect a minimal synthetic reproduction; record affected versions; classify whether it changes safety, measurement, or documentation; fix the underlying behavior; run relevant regression checks; rescore affected results when needed; and publish a scoped correction. If an artifact accidentally contains sensitive information, stop distributing it, remove public access where possible, rotate any exposed credentials, and follow an appropriate incident process. Deletion cannot guarantee copies were not retained.

For dependency updates: create a separate change, run the core tests and demo, record output differences, and avoid reusing old benchmark results as if newly reproduced. For new benchmark versions: preserve old identifiers and document changed cases, rules, and scoring. For external contributions: require an ownership statement and synthetic reproduction, and review both technical behavior and data provenance.
