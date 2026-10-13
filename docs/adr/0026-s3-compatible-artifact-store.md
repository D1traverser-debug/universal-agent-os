# ADR-026 — S3-Compatible Content-Addressed Artifact Store

Status: ACCEPTED
Date: 2026-10-14

## Decision

Production artifacts require an object-store adapter rather than relying on the development filesystem. The adapter remains content-addressed: SHA-256 determines object identity, writes are immutable/idempotent for identical content, and reads re-hash bytes before returning them.

The implementation targets the S3 protocol instead of a specific vendor. MinIO is used only as an integration-test implementation of that protocol. Passing a MinIO roundtrip is evidence that the adapter performs real network/object-store operations; it is not evidence that the eventual production bucket, permissions, lifecycle rules, region, visibility or delivery path are correct.

The S3 dependency remains inside the optional `live` integration extra. Local-only users and pure control-plane tests do not need boto3.
