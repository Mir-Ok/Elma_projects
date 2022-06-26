from typing import List, Any, Optional

from pydantic import BaseModel, Field, validator


class PageModel(BaseModel):
    """Модель страницы файла."""
    number: int
    name: str
    s3uid: str


class FileModel(BaseModel):
    """Модель файла."""
    uid: str = Field(alias="doc_uid")
    file_name: str = Field(alias="pdfname") # noqa
    pages: List[PageModel]
    link: Optional[str] = ""


class RequestBodyModel(BaseModel):
    """Модель запроса на объединение изображений."""
    __root__: List[FileModel]


class ResponseModel(BaseModel):
    """Модель ответа."""
    data: Any = None
    error: Optional[List[Any]] = None

    @validator('error')
    def check_error(cls, value):  # noqa
        return value or None
