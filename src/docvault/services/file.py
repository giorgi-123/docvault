from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from docvault.models.file import File

async def create_file(
    session: AsyncSession,
    user_id: int, 
    name: str,
    s3_key: str,
    file_type: str | None,
    file_size: int | None,
    folder_id: int | None,
) -> File:
    file = File(
        name=name,
        s3_key=s3_key,
        file_type=file_type,
        file_size=file_size,
        user_id=user_id,
        folder_id=folder_id,
    )
    session.add(file)
    result = await session.flush()
    return file

async def get_user_files(
    session: AsyncSession,
    user_id: int,
    folder_id: int = None,
) -> List[File]:
    query = select(File).where(
        File.user_id==user_id,
        File.folder_id==folder_id,
    )
    result = await session.execute(query)
    files = result.scalars().all()
    return files

async def get_file_by_id(
    session: AsyncSession,
    file_id: int,
    user_id: int,
) -> File | None:
    query = select(File).where(
        File.id==file_id,
        File.user_id==user_id,
    )
    result = await session.execute(query)
    file = result.scalar_one_or_none()
    return file

async def delete_file(
    session: AsyncSession,
    file_id: int,
    user_id: int,
) -> bool:
    query = delete(File).where(
        File.id==file_id,
        File.user_id==user_id
    )
    result = await session.execute(query)
    return result.rowcount > 0
