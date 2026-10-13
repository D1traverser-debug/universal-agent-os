from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StoredObject:
    content_hash: str
    storage_uri: str
    size: int


class LocalContentAddressedStore:
    """Development artifact store with immutable content-addressed objects."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def put_bytes(self, content: bytes) -> StoredObject:
        digest = hashlib.sha256(content).hexdigest()
        path = self.root / digest[:2] / digest[2:]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(content)
        elif path.read_bytes() != content:
            raise RuntimeError("content hash collision or corrupted object")
        return StoredObject(digest, path.as_uri(), len(content))

    def get_bytes(self, content_hash: str) -> bytes:
        path = self.root / content_hash[:2] / content_hash[2:]
        content = path.read_bytes()
        actual = hashlib.sha256(content).hexdigest()
        if actual != content_hash:
            raise RuntimeError("artifact content hash mismatch")
        return content
