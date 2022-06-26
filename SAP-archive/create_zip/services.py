import datetime
import tempfile
import zipfile
from pathlib import Path
from typing import List

from settings import logger, ELMA_ZIP_DIRECTORY
from .models import FileEntityModel
from .repositories import get_link, get_file_by_link, send_file_to_elma


def upload_files():
    pass


def create_file_name(file: FileEntityModel) -> str:
    """Создать имя дял файла."""
    file_name = (
        f"{file.filetype.name}_{file.doc_number}({file.filetype.id})"
    )
    file_name += Path(file.file.name).suffix
    return file_name


def create_zip(dir_path):
    """Создать архив из файлов по url."""
    now = f'{datetime.datetime.now():%Y-%m-%d_%H:%M}'

    dir_path = Path(dir_path)
    files_dir = [file for file in dir_path.glob("**/*") if file.is_file()]
    zip_path = Path(dir_path, f'Выгрузка_{now}.zip')
    with zipfile.ZipFile(zip_path, mode='w') as zf:
        for path in files_dir:
            zf.write(path, arcname=path.name)

    return zip_path


def create_zip_end_send_to_elma(entity_list: List[FileEntityModel]):
    """Создать архив из файлов и отправить в ELMA."""
    temp_dir = tempfile.TemporaryDirectory(prefix="temp_img2zip_")
    temp_dir_path = temp_dir.name

    error_list = []
    for entity in entity_list:

        file_link, error = get_link(entity.file.s3uid)
        if error:
            logger.error("link not received!")
            logger.error(error)
            error_list.append(error)
            continue

        b_file: bytes = get_file_by_link(file_link)
        if not b_file:
            error = f"url: {file_link}, don't load file"
            logger.error(error)
            error_list.append(error)
            continue

        file_name = create_file_name(entity)
        file_path = Path(temp_dir_path, file_name)
        with open(file_path, mode='wb') as f:
            f.write(b_file)
        logger.success(f"file saved: {file_name}")

    dir_files_exists = any(Path(temp_dir_path).iterdir())
    if not dir_files_exists:
        logger.warning(f"dir: {temp_dir_path} is empty")
        error_list.insert(0, "no upload files")
        return None, error_list

    try:
        logger.info("start create zip file")
        zip_path = create_zip(temp_dir_path)
        logger.success(f"zip created: {zip_path}")
    except Exception as err:
        logger.error(err)
        error_list.append(str(err))
        return None, error_list

    zip_uploaded, error = send_file_to_elma(zip_path, ELMA_ZIP_DIRECTORY)
    if not zip_uploaded:
        logger.error("Zip file not uploaded")
        return None, [error]

    zip_link, error = get_link(zip_uploaded.s3uid)

    if not zip_link:
        return None, [error]

    logger.success(f"elma link for zip received: {zip_uploaded.name}")
    zip_uploaded.link = zip_link
    logger.success(f"Zip created and sent to ELMA: {zip_uploaded.name}")

    return zip_uploaded, error_list
