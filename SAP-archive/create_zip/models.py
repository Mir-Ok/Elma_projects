from datetime import datetime
from typing import Optional, Union, List, Any

from pydantic import BaseModel, Field


class CounteragentModel(BaseModel):
    """Контрагент."""
    id: str = Field(alias="__id", default="")
    inn: str = ""
    shortname: str = ""


class TypeModel(BaseModel):
    """Тип документа."""
    id: str = Field(alias="__index")
    name: str


class FileModel(BaseModel):
    """Файл."""
    s3uid: str
    name: str = Field(alias="__name")


class FileEntityModel(BaseModel):
    """Сущность файла."""
    file: FileModel
    # user_uid: List[str] = ""
    counteragent: CounteragentModel
    filetype: TypeModel = Field(alias="type")
    doc_date: datetime = None
    doc_number: Optional[Union[int, str]] = ""
    doc_amount: Optional[int] = -1
    b_file: Optional[bytes] = None


class UploadedFile(BaseModel):
    """Загруженный файл."""
    s3uid: str
    name: str
    link: str = ""


class RequestBodyModel(BaseModel):
    """Модель запроса."""
    __root__: List[FileEntityModel]


class ResponseModel(BaseModel):
    """Модель ответа сервера."""
    data: Optional[UploadedFile] = None
    error: Any = None
