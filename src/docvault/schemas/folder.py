from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class FolderCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Test Folder"
            }
        }
    )
    name: str
    parent_id: int | None = None


class FolderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    parent_id: int | None = None
    created_at: datetime


class FolderList(BaseModel):
    folders: List[FolderResponse]

