from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class S3StoredObject:
    content_hash: str
    storage_uri: str
    size: int
    key: str


class S3ContentAddressedStore:
    """S3-compatible immutable content-addressed artifact store."""

    def __init__(self, *, client, bucket: str, prefix: str = "objects") -> None:
        if not bucket.strip():
            raise ValueError("bucket is required")
        self.client = client
        self.bucket = bucket
        self.prefix = prefix.strip("/")

    def key_for(self, content_hash: str) -> str:
        leaf = f"{content_hash[:2]}/{content_hash[2:]}"
        return f"{self.prefix}/{leaf}" if self.prefix else leaf

    def put_bytes(self, content: bytes) -> S3StoredObject:
        digest = hashlib.sha256(content).hexdigest()
        key = self.key_for(digest)
        existing = self._try_get(key)
        if existing is None:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                Metadata={"sha256": digest},
                ContentType="application/octet-stream",
            )
        elif existing != content:
            raise RuntimeError("content hash collision or corrupted S3 object")
        return S3StoredObject(digest, f"s3://{self.bucket}/{key}", len(content), key)

    def get_bytes(self, content_hash: str) -> bytes:
        key = self.key_for(content_hash)
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body = response["Body"].read()
        actual = hashlib.sha256(body).hexdigest()
        if actual != content_hash:
            raise RuntimeError("artifact content hash mismatch")
        return body

    def delete_hash(self, content_hash: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=self.key_for(content_hash))

    def _try_get(self, key: str) -> bytes | None:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            response = getattr(exc, "response", {}) or {}
            code = str(response.get("Error", {}).get("Code", ""))
            if code in {"NoSuchKey", "404", "NotFound"}:
                return None
            raise
        return response["Body"].read()
