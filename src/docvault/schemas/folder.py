from pydantic import BaseModel
from datetime import datetime
from typing import List

class FolderCreate(BaseModel):
    name: str
    parent_id: int = None 


class FolderResponse(BaseModel):
    id: int
    name: str
    parent_id: int = None
    created_at: datetime


class FolderList(BaseModel):
    folders: List[FolderResponse]

