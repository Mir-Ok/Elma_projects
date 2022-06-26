from pydantic import BaseModel, Field, validator
from pydantic.types import Optional
import re


class RequestBodyModel(BaseModel):
    """Модель запроса."""

    mongo_uid: Optional[str]
    postgres_id: Optional[str]

    @validator('postgres_id')
    def check_len(cls, v):
        ptn = r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
        if not re.match(ptn, v):
            raise ValueError('Неверный uid')
        return v


class ParseModel(BaseModel):
    """Модель данных для доступа к БД """

    user: Optional[str]
    password: Optional[str]
    host1: Optional[str]
    host2: Optional[str]
    port1: Optional[str]
    port2: Optional[str]
    finish: Optional[str]