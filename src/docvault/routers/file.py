from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from docvault.schemas.file import FileResponse, FileList
from docvault.database import get_db
from docvault.services.auth import get_current_user
from docvault.models.user import User
from docvault.services import file as file_service 
from docvault.services import storage

file_router = APIRouter(
    prefix="/files",
    tags=["file"],
)

@file_router.post("/", response_model=FileResponse)
async def upload_file_endpoint(
    file: UploadFile = File(),
    folder_id: int | None = None,
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user),
):
    filename = file.filename
    s3_key = f"users/{current_user.id}/files/{uuid.uuid4()}_{filename}"
    content = await file.read()
    content_type = file.content_type
    file_size = len(content)
    upload_file = storage.upload(
        file_content=content,
        s3_key=s3_key,
        content_type=content_type
    )
    if not upload_file:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong, please contact support!"
        )
    file_creation = await file_service.create_file(
        session=session,
        user_id=current_user.id,
        name=filename,
        s3_key=s3_key,
        file_type=content_type,
        file_size=file_size,
        folder_id=folder_id,
    )
    return FileResponse.model_validate(file_creation)


@file_router.get("/", response_model=FileList)
async def list_files_endpoint(
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user),
    folder_id: int | None = Query(default=None),
) -> FileList | None:
    files = await file_service.get_user_files(
        session=session,
        user_id=current_user.id,
        folder_id=folder_id,
    )

    file_responses = [FileResponse.model_validate(file) for file in files]
    return FileList(
        files=file_responses
    )

@file_router.get("/{file_id}", response_model=FileResponse)
async def get_file_by_id_endpoint(
    file_id: int,
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user),
) -> FileResponse | None:
    file = await file_service.get_file_by_id(
        session=session,
        file_id=file_id,
        user_id=current_user.id,
    )
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found!"
        )
    return FileResponse.model_validate(file)

@file_router.get("/{file_id}/download")
async def download_file_endpoint(
    file_id: int,
    session: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user),
) -> StreamingResponse:
    file = await file_service.get_file_by_id(
        session=session,
        file_id=file_id,
        user_id=current_user.id
    )
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File was not found!",
        )
    content = storage.download(
        s3_key=file.s3_key
    )
    return StreamingResponse(
        iter([content]),
        media_type=file.file_type,
        headers={"Content-Disposition": f"attachment; filename={file.name}"}
    )

@file_router.delete("/{file_id}")
async def delete_file_endpoint(
    file_id: int,
    current_user: User=Depends(get_current_user),
    session: AsyncSession=Depends(get_db)
):
    file = await file_service.get_file_by_id(
        session=session,
        file_id=file_id,
        user_id=current_user.id
    )
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File was not found!"
        )
    delete_file_s3 = storage.delete(
        s3_key=file.s3_key
    )

    if not delete_file_s3:
        raise HTTPException(
            status_code=404,
            detail="File was not found in the bucket or Something went wrong!"
        )

    delete_file = await file_service.delete_file(
        session=session,
        file_id=file.id,
        user_id=current_user.id
    )
    
    if not delete_file:
        raise HTTPException(
            status_code=404,
            detail="File was not found or Something went wrong!",
        )
    
    return Response(
        status_code=204
    )
