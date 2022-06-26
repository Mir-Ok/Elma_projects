from typing import Optional

import requests

from settings import logger


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
