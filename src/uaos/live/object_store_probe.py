from __future__ import annotations

from dataclasses import dataclass
import hashlib
import uuid

from uaos.state.s3_artifacts import S3ContentAddressedStore


@dataclass(frozen=True, slots=True)
class ObjectStoreProbeResult:
    bucket: str
    content_hash: str
    roundtrip_verified: bool
    cleanup_verified: bool


def run_object_store_probe(*, endpoint_url: str, bucket: str, region: str = "us-east-1") -> ObjectStoreProbeResult:
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import ClientError
    except ImportError as exc:
        raise RuntimeError("object-store probe requires boto3; install .[live]") from exc

    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region,
        config=Config(s3={"addressing_style": "path"}),
    )
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as exc:
        code = str((exc.response or {}).get("Error", {}).get("Code", ""))
        if code not in {"404", "NoSuchBucket", "NotFound"}:
            raise
        client.create_bucket(Bucket=bucket)

    content = f"uaos-object-store-live-probe:{uuid.uuid4().hex}".encode()
    expected = hashlib.sha256(content).hexdigest()
    store = S3ContentAddressedStore(client=client, bucket=bucket, prefix="live-probe")
    stored = store.put_bytes(content)
    roundtrip = stored.content_hash == expected and store.get_bytes(expected) == content
    store.delete_hash(expected)
    cleanup = False
    try:
        client.head_object(Bucket=bucket, Key=stored.key)
    except ClientError as exc:
        code = str((exc.response or {}).get("Error", {}).get("Code", ""))
        cleanup = code in {"404", "NoSuchKey", "NotFound"}
    if not roundtrip or not cleanup:
        raise RuntimeError("S3-compatible object-store probe failed")
    return ObjectStoreProbeResult(bucket, expected, roundtrip, cleanup)
