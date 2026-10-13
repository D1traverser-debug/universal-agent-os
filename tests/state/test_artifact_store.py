from pathlib import Path
from uaos.state import LocalContentAddressedStore


def test_content_addressed_store_deduplicates_and_verifies(tmp_path: Path):
    store = LocalContentAddressedStore(tmp_path / "objects")
    first = store.put_bytes(b"same bytes")
    second = store.put_bytes(b"same bytes")
    assert first.content_hash == second.content_hash
    assert first.storage_uri == second.storage_uri
    assert store.get_bytes(first.content_hash) == b"same bytes"
