from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    title: str


class DocumentOut(DocumentBase):
    id: int
    filename: str
    upload_date: datetime
    page_count: int
    tags: List[TagOut] = []

    class Config:
        from_attributes = True


class DocumentDetail(DocumentOut):
    full_text: str


class PaginatedDocuments(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[DocumentOut]


class TagRequest(BaseModel):
    tag: str
