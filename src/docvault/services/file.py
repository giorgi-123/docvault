from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from docvault.schemas.file import FileResponse
from docvault.models.file import File

async def create_file(session: AsyncSession, file_data: FileResponse) -> File:
    pass

async def get_user_files():
    pass

async def get_file_by_id():
    pass

async def delete_file():
    pass
