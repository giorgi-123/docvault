import boto3

from docvault.config import settings


async def upload(file_content: bytes, s3_key: str) -> bool:
    pass

async def download(s3_key: str) -> bytes | None:
    pass

async def delete(s3_key: str) -> bool:
    pass