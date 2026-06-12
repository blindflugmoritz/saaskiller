# === FEATURE: s3 ===
from storages.backends.s3boto3 import S3Boto3Storage


class PrivateS3Storage(S3Boto3Storage):
    """
    Storage backend for private files.

    ACL is disabled (None) — bucket policy controls access.
    URLs are generated as presigned S3 URLs with a default expiry of 1 hour.
    """

    default_acl = None
    querystring_auth = True  # generates presigned GET URLs
    querystring_expire = 3600  # seconds


class PublicS3Storage(S3Boto3Storage):
    """
    Storage backend for public-read assets (e.g. user avatars, public downloads).

    Files are stored without ACL; the bucket/object policy should allow public reads.
    URLs are plain (no signature).
    """

    default_acl = None
    querystring_auth = False  # plain, unsigned URLs
# === END FEATURE: s3 ===
