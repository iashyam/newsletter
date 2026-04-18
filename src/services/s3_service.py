from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.core.config import settings
from src.core.exceptions import ImageUploadError

_CONTENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def upload_image(local_path: str, newsletter_date: str) -> str:
    """
    Upload a local image to S3 and return its public URL.
    Raises ImageUploadError on failure.
    """
    path = Path(local_path)
    key = f"newsletters/{newsletter_date}/{path.name}"
    content_type = _CONTENT_TYPES.get(path.suffix.lower(), "image/jpeg")

    try:
        s3 = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        s3.upload_file(
            local_path,
            settings.s3_bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
    except (BotoCoreError, ClientError) as e:
        raise ImageUploadError(local_path, str(e))

    return f"{settings.s3_public_base_url.rstrip('/')}/{key}"
