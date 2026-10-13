# Legacy -> Clean-Slate Migration Plan

## Principle
Do not “refactor the old repository into the new one”. Build the new kernel from frozen requirements and selectively import durable business truth.

## What can migrate
- user-confirmed requirements;
- active task identities and checkpoints that remain meaningful;
- canonical business knowledge with provenance;
- approved artifacts/assets;
- domain-specific workflows/methodologies that are still required;
- incident/history evidence useful for regression scenarios.

## What does not migrate by default
- old prompt prose whose semantics are now represented structurally;
- duplicate policies;
- brittle exact-text tests;
- current control-plane implementation merely because it exists;
- stale caches;
- abandoned experimental branches;
- workaround files with no frozen-requirement mapping.

## Import method
1. legacy importer reads old objects read-only;
2. maps into new schemas;
3. tags all imported records with source repo/ref/hash and `legacy_import`;
4. validation reports unmapped/ambiguous fields;
5. no ambiguous object becomes canonical automatically;
6. source repository remains read-only historical evidence during transition.

## Cutover
- run new system in shadow mode on representative tasks;
- compare requirement coverage, outputs, recovery and evidence;
- migrate domains one by one;
- do not enable autonomous maintenance until core task/assurance behavior is stable;
- after final cutover, old repository becomes archive/reference, not a parallel authority.
