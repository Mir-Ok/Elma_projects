import datetime
import imghdr
import tempfile
from pathlib import Path
from typing import List

import img2pdf

import elma
from settings import logger, ELMA_PDF_DIRECTORY
from .models import FileModel, PageModel
from .repositories import get_file_by_link


def get_pages_for_file(pages: List[PageModel], path):
    """Получить и сохранить страницы для файла."""
    error_list = []
    result = []
    for page in pages:
        elma_link = elma.get_file_link(page.s3uid)

        if not elma_link.success:
            logger.error(elma_link.error)
            error_list.append(elma_link.error)
            continue

        b_file = get_file_by_link(elma_link.link)

        if not b_file:
            error = f"url: {elma_link.link}, don't load file"
            logger.error(error)
            error_list.append(error)
            continue

        is_img = imghdr.what(file="", h=b_file)
        if not is_img:
            img_error = {
                "file": page.name,
                "error": "unsupported image"
            }
            logger.error(img_error)
            error_list.append(img_error)
            continue

        file_path = Path(path, page.name)
        with open(file_path, mode='wb') as f:
            f.write(b_file)
            logger.success(f"file created {file_path}")
        result.append(str(file_path))

    return result, error_list


def get_pdf_file_name(file_name: str):
    """Создать имя для PDF файла."""
    file_name = Path(file_name).stem
    now = f'{datetime.datetime.now():%Y-%m-%d_%H:%M}'
    pdf_name = f"{file_name}({now}).pdf"
    return pdf_name


def create_pdf_a4_file(file_name, pages_path_list, dir_path):
    """Создать A4 pdf файл из изображений."""

    a4_page_size = (img2pdf.in_to_pt(8.3), img2pdf.in_to_pt(11.7))
    layout_function = img2pdf.get_layout_fun(a4_page_size)

    new_file_name = get_pdf_file_name(file_name)
    path = Path(dir_path, new_file_name)
    with open(path, "wb") as f:
        try:
            f.write(
                img2pdf.convert(
                    pages_path_list, layout_fun=layout_function
                )
            )
        except Exception as e:
            err = {
                "file": file_name,
                "errors": str(e)
            }
            logger.error(err)
            return None, err

    logger.success(f"{path}: pdf created")
    return {"new_name": new_file_name, "path": path}, None


def send_file_to_elma(path):
    """Отправить файл в Elma."""
    try:
        upload = elma.send_file(path, ELMA_PDF_DIRECTORY)
    except Exception as err:
        logger.error(err)
        file_name = Path(path).name
        error = f"file {file_name} not sent to Elma"
        return None, error

    file_uid = upload.file.id
    file_name = upload.file.original_name
    error = upload.error
    result = {
        "s3uid": file_uid,
        "name": file_name
    }
    return result, error


def create_pdf_from_request(files: List[FileModel]):
    """Создать pdf файлы по параметрам из запроса."""
    temp_dir = tempfile.TemporaryDirectory(prefix="temp_img2pdf_")
    temp_dir_path = temp_dir.name

    result = []
    error_list = []

    for file in files:

        file.pages.sort(key=lambda x: x.number)
        pages_img_path_list, errors = (
            get_pages_for_file(file.pages, temp_dir_path)
        )

        if errors:
            logger.error("file pages with error")
            err = {
                "file": file.file_name,
                "errors": errors
            }
            error_list.append(err)

        if not pages_img_path_list:
            logger.error("images of the file pages were not received")
            continue

        pdf, error = create_pdf_a4_file(
            file.file_name, pages_img_path_list, temp_dir_path
        )
        if error:
            logger.error("don't create pdf")
            error_list.append(error)
            continue

        file.file_name = pdf["new_name"]

        upload_result, error = send_file_to_elma(pdf["path"])

        if error:
            logger.error("pdf file has not been sent to elma")
            error_list.append(error)
            continue

        elma_link = elma.get_file_link(upload_result["s3uid"])
        if not elma_link.success:
            logger.error(elma_link.error)
            error_list.append(elma_link.error)
            continue

        file.link = elma_link.link

        result.append(file)

    if error_list:
        logger.error(f"all errors: {error_list}")

    result = result or None
    return result, error_list
