from typing import Any

from pydantic import BaseModel, validator


class ResponseModel(BaseModel):
    """Модель ответа."""
    data: Any = None
    error: Any = None

    @validator('error')
    def check_error(cls, value):  # noqa
        return value or None
