from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from docvault.models.folder import Folder
from docvault.schemas.folder import FolderCreate


async def create_folder(session: AsyncSession, user_id: int, folder_data: FolderCreate) -> Folder:
    """Create new folder in database"""
    folder = Folder(
        name=folder_data.name,
        user_id=user_id,
        parent_id=folder_data.parent_id
    )
    session.add(folder)
    await session.flush()
    return folder

async def get_user_folders(session: AsyncSession, user_id: int, parent_id: int = None) -> List[Folder]:
    """Select all the folders assigned to the user provided in arguments"""
    query = select(Folder).where(
        Folder.user_id==user_id,
        Folder.parent_id==parent_id
    )
    result = await session.execute(query)
    folders = result.scalars().all()
    return folders

async def get_folder_by_id(session: AsyncSession, folder_id: int, user_id: int = None) -> Folder | None:
    """Select and return Folder with the provided folder_id and user_id"""
    query = select(Folder).where(
        Folder.id==folder_id,
        Folder.user_id==user_id,
    )
    result = await session.execute(query)
    folder = result.scalar_one_or_none()
    return folder

async def delete_folder(session: AsyncSession, folder_id: int, user_id: int) -> bool:
    """Delete the folder"""
    query = delete(Folder).where(
        Folder.id==folder_id,
        Folder.user_id==user_id,
    )
    result = await session.execute(query)
    return result.rowcount > 0
