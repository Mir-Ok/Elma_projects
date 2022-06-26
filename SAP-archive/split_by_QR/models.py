from pydantic.types import constr, Optional
from pydantic import BaseModel, Field


class ElmaLinkModel(BaseModel):
    """ Ответ со ссылкой на файл."""
    success: bool
    error: str = ""
    link: str = Field(alias="Link", default="")


class TempPDFModel(BaseModel):
    """ Ответ со ссылкой на файл."""
    path: Optional[str]
    parts: Optional[str]
    out: Optional[str]


class ParametersModel(BaseModel):
    """  Извлечение информации из png-файлов"""
    s_path_to_png_list: Optional[list]  # сорт. файлов директории
    qr_data_list: Optional[list]  # исходный список кодов в 10
    qr_data_list_01: Optional[list]  # исходный список кодов в 10
    image_list: Optional[list]  # список страниц (объекты)
    totally_pages: Optional[int]  # общее количество страниц


class FinalPDFModel(BaseModel):
    """ Параметры склееного pdf """
    path: Optional[str]
    pages: Optional[list]
    new_name: Optional[str]
    qr_list: Optional[list]
    file_uid: Optional[str]


class FinalPDFManyModel(BaseModel):
    """ Параметры списка склеенных pdf """
    end_path_list: Optional[list]
    end_pages: Optional[list]
    end_names_list: Optional[str]
    end_qr_list: Optional[list]
    files_uid: Optional[list]


# для красивого вывода
class RequestBodyModel(BaseModel):
    """Модель запроса."""
    s3uid: constr(regex=r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}")
    filename: constr(regex=r"[а-яА-Яa-zA-Z0-9_. ]{1,}[.](jpg|jpeg|png|bmp|tiff|tif|pdf)\b")
    regexp: constr(regex=r"SAP-")
    suffix: Optional[str]


