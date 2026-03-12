from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from docvault.schemas.file import FileResponse
from docvault.models.file import File

async def create_file(session: AsyncSession, user_id: int, file_data: FileResponse) -> File:
    file = File(
        name=file_data.name,
        s3_key=file_data.s3_key,
        file_type=file_data.file_type,
        file_size=file_data.file_size,
        user_id=user_id,
        folder_id=file_data.folder_id,
    )
    session.add(file)
    result = await session.flush()
    return file

async def get_user_files():
    pass

async def get_file_by_id():
    pass

async def delete_file():
    pass
