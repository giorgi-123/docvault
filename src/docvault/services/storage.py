import boto3
import logging

from docvault.config import settings

_logger = logging.getLogger(__name__)

def get_client():
    s3_client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        region_name=settings.aws_region_name,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    return s3_client

def upload(file_content: bytes, s3_key: str, content_type: str) -> bool:
    s3_client = get_client()
    try:
        response = s3_client.put_object(Bucket=settings.bucket_name,
                             Key=s3_key, 
                             Body=file_content, 
                             ContentType=content_type)
        return bool(response)
    except Exception as e:
        _logger.error(f"Exception raised: {e}")
        return False

def download(s3_key: str) -> bytes | None:
    s3_client = get_client()
    try:
        response = s3_client.get_object(Bucket=settings.bucket_name, Key=s3_key)
        content = response["Body"].read()
        return content or None
    except Exception as e:
        _logger.error(f"Exception raised: {e}")
        return False

def delete(s3_key: str) -> bool:
    s3_client = get_client()
    try:
        response = s3_client.delete_object(Bucket=settings.bucket_name, Key=s3_key)
        return bool(response)
    except Exception as e:
        _logger.error(f"Exception raised {e}")
        return False

