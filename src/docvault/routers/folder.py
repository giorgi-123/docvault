from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from docvault.schemas.folder import FolderCreate, FolderResponse, FolderList
from docvault.database import get_db
from docvault.services.auth import get_current_user
from docvault.services.folder import create_folder, delete_folder, get_folder_by_id, get_user_folders
from docvault.models.user import User

folder_router = APIRouter(
    prefix="/folder",
    tags=["folder"]
)

def raise_unauthorized():
    raise HTTPException(
                status_code=401,
                detail="Unauthorized",
                headers={"WWWW-Authenticate": "Bearer"})

@folder_router.post("/folders", response_model=FolderResponse)
async def create_folder_endpoint(
    data: FolderCreate,
    session: AsyncSession=Depends(get_db), 
    current_user: User=Depends(get_current_user)
):  
    folder = await create_folder(
        session=session,
        user_id=current_user.id,
        folder_data=data,
    )
    return FolderResponse(
        id=folder.id,
        name=folder.name,
        parent_id=folder.parent_id,
        created_at=folder.created_at
    )

@folder_router.get("/folders", response_model=FolderList)
async def user_folders_endpoint(
    parent_id: int = None,
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user)
):
    folders = await get_user_folders(
        session=session,
        user_id=current_user.id,
        parent_id=parent_id,
    )
    
    if not folders:
        raise HTTPException(
            status_code=404,
            detail="No folder exists on current user!"
            )

    return FolderList(
        folders=folders
    )

@folder_router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_single_folder_endpoint(
    folder_id: int,
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user)
):
    folder = await get_folder_by_id(
        session=session,
        folder_id=folder_id,
        user_id=current_user.id
    )

    if not folder:
        raise HTTPException(
            status_code=404,
            detail="Folder not found!",
        )

    return FolderResponse(
        id=folder.id,
        name=folder.name,
        parent_id=folder.parent_id,
        created_at=folder.created_at
    )

@folder_router.delete("/folders/{folder_id}")
async def delete_folder_endpoint(
    folder_id: int,
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user)
):
    folder_delete = await delete_folder(
        session=session,
        folder_id=folder_id,
        user_id=current_user.id
    )
    if not folder_delete:
        raise HTTPException(
            status_code=404,
            detail="Resource has not been found",
        )
    return Response(
        Content="Delete Successful",
        status_code=204
        )

