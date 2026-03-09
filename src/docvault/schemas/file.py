from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    s3_key: str
    file_type: str | None = None
    file_size: int | None = None
    folder_id: int | None = None
    created_at: datetime


class FileList(BaseModel):
    files: list[FileResponse]

