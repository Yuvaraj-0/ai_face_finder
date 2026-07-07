from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ImageCreate(BaseModel):
    cloudinary_url: str
    cloudinary_public_id: str


class ImageResponse(BaseModel):
    id: str
    cloudinary_url: str
    cloudinary_public_id: str

    class Config:
        from_attributes = True


class BulkImageUploadResponse(BaseModel):
    success_count: int
    failed_count: int
    images: List[ImageResponse]
    errors: Optional[List[str]] = None


class ImageListResponse(BaseModel):
    total: int
    images: List[ImageResponse]


class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: Optional[int] = None


class EventCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    images: List[ImageResponse] = []

    class Config:
        from_attributes = True