# === FEATURE: s3 ===
from __future__ import annotations

import boto3
from django.conf import settings


def _s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def generate_presigned_upload_url(
    key: str,
    content_type: str,
    expires: int = 3600,
) -> dict:
    """
    Return a presigned POST payload for a direct browser-to-S3 upload.

    Returns a dict with keys:
        url    – the POST endpoint
        fields – form fields that must be included in the multipart upload
    """
    client = _s3_client()
    return client.generate_presigned_post(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[{"Content-Type": content_type}],
        ExpiresIn=expires,
    )


def generate_presigned_get_url(
    key: str,
    expires: int = 3600,
) -> str:
    """
    Return a presigned GET URL for a private S3 object.
    """
    client = _s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": key,
        },
        ExpiresIn=expires,
    )
# === END FEATURE: s3 ===
