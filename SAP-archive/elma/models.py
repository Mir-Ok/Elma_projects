from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ElmaLinkModel(BaseModel):
    """Ответ со ссылкой на файл."""
    success: bool
    error: str = ""
    link: str = Field(alias="Link", default="")


class ElmaFileModel(BaseModel):
    """Модель файла при загрузке."""
    id: str = Field(alias="__id")
    name: str
    original_name: str = Field(alias="originalName")
    directory: str
    size: int
    version: int
    created_at: datetime = Field(alias="__createdAt")
    updated_at: datetime = Field(alias="__updatedAt")
    deleted_at: Optional[datetime] = Field(alias="__deletedAt")
    created_by: str = Field(alias="__createdBy")
    updated_by: str = Field(alias="__updatedBy")


class ElmaUploadModel(BaseModel):
    """Ответ со ссылкой на файл."""
    success: bool
    error: str = ""
    file: ElmaFileModel
    