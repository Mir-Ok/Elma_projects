import requests
import re
import os
from pathlib import Path
import tempfile
from pdf2image import convert_from_path
from PIL import Image, ImageSequence


def get_file_by_link(link):
    """Получить файл по ссылке"""
    try:
        response = requests.get(link, stream=True)
    except ValueError:
        return {"error": "Пустой входящий запрос"}

    if response.ok:  # аналог response == 200
        return response.content
    return None


def create_documents(from_page, to_page, file_uid, file_name, qr_list, d=0):
    """ Создает отчет об отправленном на сервер файле """
    documents = {"sequence": d,
                 "qr_value": qr_list,
                 "pages": {"from": from_page, "to": to_page},
                 "s3uid": file_uid,
                 "filename": file_name
                 }
    return documents


def sort_list_names(png_dir):
    """ Создает список из имен файлов директории по указанному пути,
    сортирует его по возрастанию """

    all_png_dir = os.listdir(png_dir)
    all_png_dir.sort(key=lambda f: int(re.sub('\D', '', f)))

    return all_png_dir


def convert_to_pdf(dir, file_name, slice_image_list, i, end_path_list,
                   page_list, pages):
    """ Конвертит изображения в pdf и сохраняет по указанному пути """

    end_path = Path(dir, file_name + f'_{i}_.pdf')

    if len(slice_image_list) == 1:  # если страница одна
        slice_image_list[0].save(end_path, save_all=True)
    else:  # если страниц много
        slice_image_list[0].save(end_path, save_all=True,
                                 append_images=slice_image_list[1:])

    # пополняем список путей
    end_path_list.append(end_path)
    # пополняем список страниц (от, до)
    pages.append([page_list[0], page_list[-1]])

    return end_path_list, pages


def split_pdf_to_png(img_url, temp_png_dir_name):
    """ Разделяет входящий pdf на отдельные png-файлы"""

    try:
        pdf_file = requests.get(img_url)

        # для входящего pdf
        temp_in_dir = tempfile.TemporaryDirectory(prefix="temp_in_dir_")
        temp_file = Path(temp_in_dir.name, 'temp.pdf')
        with open(temp_file, 'wb') as f:  #
            f.write(pdf_file.content)

        # for Win
        #poppler_path = 'C:\Program Files\poppler-0.68.0_x86\\bin'
        #convert_from_path(temp_file, dpi=200, fmt="png", poppler_path=poppler_path, output_folder=temp_png_dir_name,               output_file='png')

        # for Unix
        convert_from_path(temp_file, dpi=200, fmt="png", output_folder=temp_png_dir_name, output_file='png')

    except ValueError:
        return {"error": "Файл не получен"}

    return True


def split_img_to_png(img_url, temp_png_dir_name):
    """ Разделяет входящий tiff на отдельные png-файлы"""

    try:
        tiff_file_raw = Image.open(requests.get(img_url, stream=True).raw)

        number = 0
        for fr in ImageSequence.Iterator(tiff_file_raw):
            fr.save(Path(temp_png_dir_name, f'png_{number}' + '.png'))
            number += 1

    except ValueError:
        return {"error": "Файл не получен"}

    return True

