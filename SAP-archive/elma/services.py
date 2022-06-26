from pathlib import Path
from time import sleep
from typing import Optional, BinaryIO
from uuid import uuid4

import requests

from elma.models import ElmaLinkModel, ElmaUploadModel
from settings import ELMA_STAND, ELMA_TOKEN, logger


def get_file_link(uid: str) -> ElmaLinkModel:
    """Получить ссылку на файл из ELMA."""
    url = f"{ELMA_STAND}/pub/v1/disk/file/{uid}/get-link"
    header = {
        "X-TOKEN": ELMA_TOKEN
    }

    try:
        response = requests.get(url, headers=header)
    except Exception as err:
        logger.error(err)
        model = ElmaLinkModel(success=False,
                              error=f"url: {url}, {err.__class__.__name__}",
                              link="")
        return model

    if not response.ok:
        logger.error(response.text)
        return ElmaLinkModel(
            success=False,
            error=f"url: {url}, not found file",
            link=""
        )
    logger.debug(f"elma link response: {response.json()}")
    result = ElmaLinkModel.parse_obj(response.json())
    logger.debug(f"link received: {uid}")
    return result


def send_file(
        file_path: str,
        directory: str,
        file_name: Optional[str] = None,
        chunk_custom_size: Optional[str] = None,
) -> ElmaUploadModel:
    """Отправляет файл в Elma."""

    def read_in_chunks(file_object: BinaryIO, size: Optional[int]):
        """Разбивает фал на части."""
        chunk_size = size or 30000000
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    file_path: Path = Path(file_path)
    file_name = file_name or file_path.name
    file_size = file_path.stat().st_size
    file_to_send = open(file_path, 'rb')

    headers = {
        "X-TOKEN": ELMA_TOKEN,
    }

    url = ""
    response = None
    response_error = None
    index_size = 0

    for i in range(5):
        hash_file = str(uuid4())
        url = (
            f"{ELMA_STAND}/pub/v1/disk/directory/"
            f"{directory}/upload?hash={hash_file}"
        )
        for chunk in read_in_chunks(file_to_send, chunk_custom_size):
            offset_size = index_size + len(chunk)
            headers['Content-Range'] = (
                f"bytes {index_size}-{offset_size}/{file_size}"
            )
            index_size = offset_size
            file = {'file': (file_name, chunk)}
            try:
                logger.debug(f"try: {hash_file}, File_size: {file_size}")
                response = requests.post(url, headers=headers, files=file)
                logger.debug(f"response: {response.text}")
            except Exception as err:
                logger.error(err)
                response_error = str(err)
                break

        if response and response.ok:
            break
        else:
            file_to_send.seek(0)

    if not response:
        error = {
            "url": url,
            "text": response_error
        }
        logger.error(error)
        raise Exception(error)

    if not response.ok:
        error = {
            "url": url,
            "text": f"{response.status_code}: {response.text}"
        }
        logger.error(error)
        raise Exception(error)

    result = ElmaUploadModel.parse_obj(response.json())

    logger.success(f"file uploaded: {result.file.original_name}")
    return result
