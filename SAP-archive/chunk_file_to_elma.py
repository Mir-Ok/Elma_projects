import os
import tempfile

# temp_dir = tempfile.TemporaryDirectory(prefix="temp_files_", dir="my_temp_dir")
# print("name tem dir")
# print(temp_dir.name)
# # temp_dir.cleanup()
import time
from uuid import uuid4

import requests
from pathlib import Path

from codetiming import Timer

from settings import logger, ELMA_TOKEN, ELMA_STAND, ELMA_ZIP_DIRECTORY


def read_in_chunks(file_object, CHUNK_SIZE):
    while True:
        data = file_object.read(CHUNK_SIZE)
        if not data:
            break
        yield data


def send_chunk_file_to_elma(file_path):
    """Отправляет файл в Elma."""
    file_size = os.path.getsize(file_path)
    file_to_send = open(file_path, 'rb')

    index = 0
    offset = 0
    headers = {
        "X-TOKEN": ELMA_TOKEN,
    }
    response = None

    uid_file = str(uuid4())
    url = f"{ELMA_STAND}/pub/v1/disk/directory/{ELMA_ZIP_DIRECTORY}/upload?hash={uid_file}"

    for chunk in read_in_chunks(file_to_send, 7000000):
        offset = index + len(chunk)
        logger.info(f"{offset}, {len(chunk)}")
        headers['Content-Range'] = f"bytes {index}-{offset}/{file_size}"
        index = offset
        logger.warning(headers)

        file = {"file": (file_path.name, chunk)}

        logger.debug(f"try: {uid_file}, File_size: {file_size}")
        response = requests.post(url, headers=headers, files=file)
        logger.debug(f"response: {response.text[:-2]}, {response.status_code}")
        if not response.ok:
            break

    if not response:
        error = {
            "url": url,
            "text": f"File not sent to Elma"
        }
        logger.error(error)
        return None, error

    if not response.ok:
        error = {
            "url": url,
            "text": f"{response.status_code}: {response.text}"
        }
        logger.error(error)
        return None, error

    result = response.json()

    if not result.get("success"):
        error = result.get("error")
        logger.error(error)
        return None, error

    logger.debug(f"file_upload: {result}")
    # file_uid = result.get("hash")
    file_uid = result.get("file")["__id"]
    file_name = result.get("file")["name"]
    result = {
        "s3uid": file_uid,
        "name": file_name
    }

    return result, None


def send_file_to_elma(file_path):
    """Отправляет файл в Elma."""
    file_size = file_path.stat().st_size
    # file_size = 317936
    file_to_send = open(file_path, 'rb')

    headers = {
        "X-TOKEN": ELMA_TOKEN,
    }
    response = None

    uid_file = str(uuid4())
    url = f"{ELMA_STAND}/pub/v1/disk/file/upload?hash={uid_file}"
    url = f"{ELMA_STAND}/pub/v1/disk/directory/{ELMA_ZIP_DIRECTORY}/upload?hash={uid_file}"


    headers['Content-Range'] = f'bytes {0}-{file_size}/{file_size}'
    logger.warning(headers)

    file = {"file": (file_path.name + "10", file_to_send)}

    logger.info(len(file_to_send.read()))
    file_to_send.seek(0)

    logger.debug(f"try: {uid_file}, File_size: {file_size}")
    response = requests.post(url, headers=headers, files=file)
    logger.debug(f"response: {response.text[:-2]}, {response.status_code}")
    if not response.ok:
        pass

    if not response:
        error = {
            "url": url,
            "text": f"File not sent to Elma"
        }
        logger.error(error)
        return None, error

    if not response.ok:
        error = {
            "url": url,
            "text": f"{response.status_code}: {response.text}"
        }
        logger.error(error)
        return None, error

    result = response.json()

    if not result.get("success"):
        error = result.get("error")
        logger.error(error)
        return None, error

    logger.success(f"file_upload: {result}")
    # file_uid = result.get("hash")
    # file_uid = result.get("file")["__id"]
    # file_name = result.get("file")["name"]
    # result = {
    #     "s3uid": file_uid,
    #     "name": file_name
    # }

    return result, None


parth = Path("pdf", "test_45.tiff")
# parth = Path("pdf", "zip_file.z")
# parth = Path("pdf", "zip_file2.zip")

# print(parth.name)

tic = time.perf_counter()
# res, err = send_chunk_file_to_elma(parth)
# res, err = send_file_to_elma(parth)
toc = time.perf_counter()
try:
    a = requests.get("http://ya.ru")
except Exception as e:
    logger.exception(e)
timer = Timer(
    logger=logger.error,
    text="{milliseconds} Время выполнения: {:0.2f} секунд"
)

with timer:
    a = 254**100540

