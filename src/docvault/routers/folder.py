from fastapi.routing import APIRoute, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from docvault.schemas.folder import FolderCreate, FolderResponse, FolderList
from docvault.database import get_db
from docvault.services.auth import get_current_user
from docvault.services.folder import create_folder, delete_folder, get_folder_by_id, get_user_folders
from docvault.models.user import User


folder_router = APIRoute(
    prefix="/folder",
    tags=["folder"]
)


@folder_router.post("/folders", response_model=FolderResponse)
async def create_folder(
    data: FolderCreate,
    session: AsyncSession=Depends(get_db), 
    current_user: User=Depends(get_current_user)
):
    pass

@folder_router.get("/folders", response_model=FolderList)
async def user_folders(
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user)
):
    pass

@folder_router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_single_folder(
    folder_id: int,
    current_user: User=Depends(get_current_user)
):
    pass

@folder_router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    current_user: User=Depends(get_current_user)
):
    pass

