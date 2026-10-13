from __future__ import annotations

from io import BytesIO
import hashlib
import pytest

from uaos.state.s3_artifacts import S3ContentAddressedStore


class Missing(Exception):
    def __init__(self):
        self.response = {"Error": {"Code": "NoSuchKey"}}


class Client:
    def __init__(self): self.objects={}
    def get_object(self, *, Bucket, Key):
        if (Bucket,Key) not in self.objects: raise Missing()
        return {"Body": BytesIO(self.objects[(Bucket,Key)])}
    def put_object(self, *, Bucket, Key, Body, Metadata, ContentType):
        self.objects[(Bucket,Key)] = bytes(Body)
    def delete_object(self, *, Bucket, Key): self.objects.pop((Bucket,Key), None)


def test_s3_content_addressed_roundtrip_is_immutable():
    client=Client(); store=S3ContentAddressedStore(client=client,bucket="uaos")
    content=b"artifact"
    first=store.put_bytes(content); second=store.put_bytes(content)
    assert first.content_hash == hashlib.sha256(content).hexdigest()
    assert first == second
    assert store.get_bytes(first.content_hash) == content


def test_s3_store_detects_corruption():
    client=Client(); store=S3ContentAddressedStore(client=client,bucket="uaos")
    obj=store.put_bytes(b"artifact")
    client.objects[("uaos",obj.key)] = b"corrupt"
    with pytest.raises(RuntimeError, match="collision|corrupted|hash mismatch"):
        store.put_bytes(b"artifact")
