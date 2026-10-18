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


@pytest.mark.parametrize("invalid_hash", [
    "", "abc", "0" * 63, "0" * 65, "F" * 64,
    "g" * 64, "../" + "0" * 61, None, b"0" * 64,
])
def test_s3_noncanonical_identity_rejected_before_any_provider_call(invalid_hash):
    invoked = []

    class GuardClient:
        def get_object(self, **kwargs):
            invoked.append(("read", kwargs))
            raise AssertionError("must not read provider")
        def delete_object(self, **kwargs):
            invoked.append(("delete", kwargs))
            raise AssertionError("must not delete provider")

    store = S3ContentAddressedStore(client=GuardClient(), bucket="uaos", prefix="live-probe")
    for action in (store.key_for, store.get_bytes, store.delete_hash):
        with pytest.raises(ValueError, match="lowercase SHA-256"):
            action(invalid_hash)
    assert not invoked


def test_s3_valid_digest_delete_only_targets_its_content_address():
    client = Client()
    store = S3ContentAddressedStore(client=client, bucket="uaos", prefix="live-probe")
    obj = store.put_bytes(b"temporary probe")
    extra_key = ("uaos", "live-probe/not-a-hash/other-object")
    client.objects[extra_key] = b"keep"
    store.delete_hash(obj.content_hash)
    assert ("uaos", obj.key) not in client.objects
    assert client.objects[extra_key] == b"keep"
