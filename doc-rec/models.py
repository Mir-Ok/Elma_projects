from pydantic import BaseModel, Field, validator
from pydantic.types import Optional
import re


class ElmaLinkModel(BaseModel):
    """ Ответ со ссылкой на файл."""
    success: bool
    error: str = ""
    link: str = Field(alias="Link", default="")


class RequestBodyModel(BaseModel):
    """Модель запроса."""

    uid: Optional[str]
    filename: Optional[str]

    @validator('uid')
    def check_len(cls, v):
        ptn = r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
        if not re.match(ptn, v):
            raise ValueError('Неверный uid')
            # return 'Неверный uid'
        return v

    @validator('filename')
    def name_len(cls, v):
        ptn = r"[а-яА-Яa-zA-Z0-9_. ]{1,}[.](pdf)\b"
        if not re.match(ptn, v):
            raise ValueError('Неверное имя файла')
            # return 'Неверное имя файла'
        return v


class TempDirModel(BaseModel):
    """ Временные папки для файлов """
    pdf: Optional[str]
    png: Optional[str]
    jpg: Optional[str]


class VariablesModel(BaseModel):
    """ Извлеченные данные """
    date: Optional[str]
    num: Optional[str]
    provider: Optional[str]
    buyer: Optional[str]
    foundation: Optional[str]
    price: Optional[str]



