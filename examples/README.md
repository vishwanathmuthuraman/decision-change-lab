# Synthetic worked example

`suppliers`, `orders`, decision IDs, reviewer ID, amounts, and dates were created for this project. They do not describe actual organizations or transactions. This example is educational and is **not part of the planned held-out set**.

Read [supplier-hold.json](supplier-hold.json) with [the scenario schema](../schemas/scenario.schema.json). It specifies source events and three approved decisions at 08:00 UTC. Decision C is dispatched at 08:05 while supplier A is active. A supplier hold becomes effective at 08:10, but is observed and delivered only at 08:12. Pending A requires a hold; committed C requires an investigation because its order remains open. Decision B uses another supplier and remains valid.

The expected result in [supplier-hold.expected.json](supplier-hold.expected.json) is a **manually specified acceptance oracle for the selective strategy in the canonical schedule**, not a recorded run. Do not feed it into the system under test. Schema validation checks structure; semantic validation must also check references, time order, version history, actor authority, totals, and expected consequences.

Initial decisions contain an `approval_seed` instead of a precomputed cryptographic hash. The future loader must derive the approval binding from the normalized amendment, policy, actor, and initial fact versions, then record the actual digest. This avoids pretending a fabricated digest was produced by an implementation. `valid_until` is later than the fixture horizon; the shared final guard still detects a material source change before expiry.

The policy and contract fields are intentionally small. Add detailed approval/contract-change fixtures during development rather than claiming this one example covers every planned family. Action order is explicit through `sequence`; timestamp equality alone must not determine causality. Initial source versions must be loaded before seeding approvals.

The event schema also permits optional `effective_until` and `supersedes_source_version` fields for later correction fixtures. Their interval and supersession validity requires semantic checks. Policy and actor records are seeded as versioned configuration before approvals; later changes use the same event envelope.
