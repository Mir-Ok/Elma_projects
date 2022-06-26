from pathlib import Path
from typing import Optional

import requests

import elma
from create_zip.models import UploadedFile
from settings import logger


def get_link(uid: str):
    """Получить ссылку на файл."""

    elma_file_link = elma.get_file_link(uid)
    if not elma_file_link.success:
        logger.error(elma_file_link.error)
        return None, elma_file_link.error
    return elma_file_link.link, None


def get_file_by_link(link: str) -> Optional[bytes]:
    """Получить файл по ссылке."""
    logger.debug(f"upload file, url: {link}")
    try:
        response = requests.get(link, stream=True)
    except Exception as err:
        logger.error(err)
        return None

    if response.ok:
        logger.success(f"file uploaded, url:{link}")
        return response.content
    logger.warning(response.text)
    return None


def send_file_to_elma(path, directory):
    """Отправить файл в Elma."""
    try:
        upload = elma.send_file(path, directory)
    except Exception as err:
        logger.error(err)
        file_name = Path(path).name
        error = f"file {file_name} not sent to Elma"
        return None, error

    file_uid = upload.file.id
    file_name = upload.file.original_name
    error = upload.error or None
    logger.success(f"zip file uploaded: {file_name}")
    return UploadedFile(s3uid=file_uid, name=file_name), error
