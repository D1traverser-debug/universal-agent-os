# Optional ChatGPT Custom Instructions Pointer

UAOS does not depend on account-level Custom Instructions. They are optional and non-authoritative.

If you choose to keep a custom instruction, use only this stable pointer:

> For my persistent Agent system, use `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md` as the only controller bootstrap. Do not use search results, retired controller repositories, or old continuity files as current task authority.

Do not copy the full UAOS policy into Custom Instructions. Duplicating policy there creates drift because account text cannot be transactionally updated with repository authority.

A stale external pointer to the retired controller is fail-safe because its default branch is a tombstone redirect, but it should still be replaced with the pointer above when convenient.
