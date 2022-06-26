import json
import os
import random
import re
import string
import tempfile
from pathlib import Path
import cv2
import requests
from PIL import Image, ImageSequence
from pdf2image import convert_from_path
import elma
from settings import ELMA_QR_DIRECTORY, logger
from .models import (
    TempPDFModel,
    ParametersModel,
    FinalPDFModel,
    FinalPDFManyModel
)


def split_pdf_to_png(img_url: str, directory: str) -> True:
    """ Разделяет входящий pdf на отдельные png-файлы"""
    try:
        pdf_file = requests.get(img_url)

        temp_pdf = tempfile.TemporaryDirectory(prefix="temp_pdf_")
        # pdf_obj = TempPDFModel(path=temp_dir.name)
        temp_file = Path(temp_pdf.name, 'temp.pdf')
        logger.debug(f'Входящий pdf {temp_file}')

        with open(temp_file, 'wb') as f:
            f.write(pdf_file.content)
        # for Win
        # poppler_path = 'C:\Program Files\poppler-0.68.0_x86\\bin'
        # convert_from_path(temp_file, dpi=200, fmt="png",
        #                   poppler_path=poppler_path, output_folder=directory,
        #                   output_file='png')

        # for Unix
        convert_from_path(temp_file, dpi=200, fmt="png",
                          output_folder=directory, output_file='png')
        logger.debug(f'Входящий pdf {os.listdir(directory)}')

    except Exception:
        return False

    return True


def split_img_to_png(img_url: str, directory: str) -> bool:
    """ Разделяет входящий многостраничник на отдельные png-файлы"""

    try:
        tiff_file_raw = Image.open(requests.get(img_url, stream=True).raw)
        number = 0
        for fr in ImageSequence.Iterator(tiff_file_raw):
            fr.save(Path(directory, f'png_{number}' + '.png'))
            number += 1
    except ValueError:
        return False

    return True


def create_parameters(directory: str) -> ParametersModel:
    logger.debug(f'Начинаем извлечение информации')

    all_png = os.listdir(directory)
    all_png.sort(key=lambda f: int(re.sub('\D', '', f)))

    s_path_to_png_list = []
    for n in range(len(all_png)):
        s_path_to_png_list.append(Path(directory, all_png[n]))

    qr_data_list = []
    image_list = []

    for path in s_path_to_png_list:
        path = f'{path}'
        # собираем все QR в список
        img = cv2.imread(path)
        detector = cv2.QRCodeDetector()
        qr_data, bbox, straight_qrcode = detector.detectAndDecode(img)
        qr_data_list.append(qr_data)

        # собираем все объекты изображений в список
        image = Image.open(path)
        im = image.convert('RGB')
        image_list.append(im)

    qr_data_list_01 = [0 if n == '' else 1 for n in qr_data_list]
    totally_pages = len(image_list)

    # помещаем параметры в атрибуты класса
    par = ParametersModel(
        s_path_to_png_list=s_path_to_png_list,
        qr_data_list=qr_data_list,
        qr_data_list_01=qr_data_list_01,
        image_list=image_list,
        totally_pages=totally_pages  # общее количество страниц
    )

    return par


def merge_pdf(image_list: list, name: str, directory: str,
              i: int) -> FinalPDFModel:
    """ Конвертит изображения в pdf и сохраняет по указанному пути """

    logger.debug(f'Начинаем сборку файла')

    # создаем уникальное имя и путь к файлу
    now = random.sample(string.ascii_letters, 3)
    now_str = "".join(now)
    new_name = name + f'_{now_str}_{i}_.pdf'
    directory = Path(directory)
    end_path = directory / new_name

    logger.debug(f'Список файлов {image_list}')
    logger.debug(f'Куда сохранить {end_path}')

    # склеиваем файлы
    try:
        if len(image_list) == 1:  # если страница одна
            image_list[0].save(end_path)
        else:  # если страниц много
            image_list[0].save(end_path, save_all=True,
                               append_images=image_list[1:])
    except Exception as err:
        logger.exception(err)

    finished_pdf = FinalPDFModel(
        path=str(end_path),
        new_name=str(new_name)
    )

    return finished_pdf


def recompose(image_list: list, qr_data_list_01: list,
              dir_name: str, file_name: str) -> FinalPDFManyModel:
    """ Функция разделяет файл на части по QR, именует, отправляет на сервер
        и готовит текстовый отчет """

    end_path_list = []  # финальный список путей
    end_names_list = []  # финальный список имен
    end_pages = []  # финальный список списков (от, до) [[0,1], [1,4]

    # создаем первые элементы списков
    slice_image_list = [image_list[0]]  # срез (первый лист с QR в начале)
    page_list = [0]  # счетчик количества листов
    logger.debug(f'Списки подготовлены')

    for i in range(1, len(qr_data_list_01)):

        # если нет нового кода
        if qr_data_list_01[i] - qr_data_list_01[0] == -1:

            # присоединяем к текущему списку
            slice_image_list.append(image_list[i])
            page_list.append(i)

        # если есть
        else:
            # закрываем пополнение текущего
            logger.debug(f'Список путей к файлам {slice_image_list}')
            finished_pdf = merge_pdf(slice_image_list, file_name, dir_name, i)

            end_path_list.append(finished_pdf.path)
            end_names_list.append(finished_pdf.new_name)
            end_pages.append([page_list[0], page_list[-1]])

            # Начинаем новый
            slice_image_list.clear()
            page_list.clear()
            slice_image_list.append(image_list[i])
            page_list.append(i)

    finished_pdf = merge_pdf(slice_image_list, file_name, dir_name, i + 1)

    end_path_list.append(finished_pdf.path)
    end_names_list.append(finished_pdf.new_name)
    end_pages.append([page_list[0], page_list[-1]])

    logger.debug(f'Список путей к файлам {end_path_list}')
    logger.debug(f'Список имен файлов {end_names_list}')
    logger.debug(f'Страницы {end_pages}')

    # переименование файлов
    for i in range(len(end_names_list)):
        now = random.sample(string.ascii_letters, 3)
        now_str = "".join(now)

        p = Path(dir_name, f'{end_names_list[i]}')
        p.rename(Path(dir_name, f'{file_name}_{now_str}_({i}).pdf'))

    # упорядоченный список переименованных файлов
    new_end_names_list = os.listdir(dir_name)
    new_end_names_list.sort(key=lambda f: int(re.sub('\D', '', f)))

    # отправка на сервер, получение идентификатора
    uid_list = []
    try:
        for ful in new_end_names_list:
            file_path = str(Path(dir_name) / ful)
            uploaded = elma.send_file(file_path, ELMA_QR_DIRECTORY)
            uid_list.append(uploaded.file.id)
        logger.debug(f'Идентификаторы {uid_list}')

    except Exception as err:
        logger.exception(err)

    # создаем новый объект модели
    recomposed_pdf = FinalPDFManyModel()
    recomposed_pdf.end_names_list = new_end_names_list
    recomposed_pdf.end_pages = end_pages
    recomposed_pdf.files_uid = uid_list

    return recomposed_pdf


def create_documents(d: int, qr_list: str, from_page: int, to_page: int,
                     file_uid: str, file_name: str) -> dict:
    """ Создает отчет об отправленном на сервер файле """
    documents = {"sequence": d,
                 "qr_value": qr_list,
                 "pages": {"from": from_page, "to": to_page},
                 "s3uid": file_uid,
                 "filename": file_name
                 }
    return documents


def split_to_files_by_qr(body):
    """ Разбирает документ на страницы
    (если многостраничник), проверяет наличие QR-кода, разбивает на части,
    отправляет созданные срезы на сервер, возвращает отчет вида

    ("data": {"totally_pages": 15,
              "documents": [{"sequence": 0, "qr_value": "SAP-1",
                             "pages": {"from": 0, "to": 6},
                             "s3uid": "e805d626-e3c8-42c2-a84b-538c49e9b1fe",
                             "filename": "2_штук_ovU_(0).pdf"},
                             ...
                             {"sequence": 0, "qr_value": "SAP-1",
                             "pages": {"from": 0, "to": 6},
                             "s3uid": "e805d626-e3c8-42c2-a84b-538c49e9b1fe",
                             "filename": "2_штук_ovU_(0).pdf"},
              "error": null)
    """

    finished = {'data': None, 'error': None}

    name = body.filename.split('.')[0].lower()
    suffix = body.filename.split('.')[-1].lower()

    body.filename = name
    body.suffix = suffix

    logger.debug(f'Входящий s3uid {body.s3uid}')

    img_url = elma.get_file_link(body.s3uid)
    logger.debug(f'Ссылка для скачивания {img_url.link}')

    if img_url.link == '':
        finished['error'] = 'Ссылка на скачивание файла не получена'
        return finished['data'], finished['error']

    temp_parts = tempfile.TemporaryDirectory(prefix="temp_parts_")
    temp_out = tempfile.TemporaryDirectory(prefix="temp_out_")

    pdf_obj = TempPDFModel(
        parts=temp_parts.name,
        out=temp_out.name
    )
    # разделяем входящий документ на отдельные файлы

    if body.suffix == 'pdf':
        split = split_pdf_to_png(img_url.link, pdf_obj.parts)
    else:
        split = split_img_to_png(img_url.link, pdf_obj.parts)

    logger.debug(f'Разделение документа на страницы {split}')

    # извлекаем информацию из файлов
    param = create_parameters(pdf_obj.parts)

    logger.debug(f'Сорт. список путей к файлам {param.s_path_to_png_list}')
    logger.debug(f'Соотв. списку QR-коды: {param.qr_data_list}')
    logger.debug(f'Соотв. списку QR-коды 01: {param.qr_data_list_01}')
    logger.debug(f'Список объектов: {param.image_list}')
    logger.debug(f'Общее кол-во страниц: {param.totally_pages}')

    # ----------------------------
    # если все страницы БЕЗ кодов
    if sum(param.qr_data_list_01) == 0:

        # склеиваем в один файл
        merged = merge_pdf(
            param.image_list, body.filename, pdf_obj.parts, 0
        )

        # отправляем на сервер, получаем идентификатор
        try:
            uploaded = elma.send_file(merged.path, ELMA_QR_DIRECTORY)
        except Exception as err:
            logger.error(f"file not send to ELMA: {str(err)}")
            return None, str(err)

        file_uid = uploaded.file.id

        merged.file_uid = file_uid

        logger.debug(f'Файл собран и отправлен')
        logger.debug(f'Путь к файлу {merged.path}')
        logger.debug(f'Начальная и конечная страницы {merged.pages}')
        logger.debug(f'Идентификатор на сайте {merged.file_uid}')
        logger.debug(f'Имя файла {merged.new_name}')

        documents = create_documents(0, param.qr_data_list[0],
                                     0, param.totally_pages - 1,
                                     merged.file_uid,
                                     merged.new_name)

        finished['data'] = {
            "totally_pages": param.totally_pages,
            "documents": documents
        }

        logger.debug(f'Отчет {finished["data"]}')

        return finished['data'], finished['error']

    # ----------------------------
    # если страницы С кодами

    # игнор страниц без QR-кода в начале
    i = 0
    while i < len(param.qr_data_list_01):
        if param.qr_data_list_01[0] == 0:
            del (param.qr_data_list_01[0])
            del (param.image_list[0])
        i += 1

    # теперь список точно стартует с кода, разбиваем на части
    rcmpsd = recompose(param.image_list,
                       param.qr_data_list_01,
                       pdf_obj.out,
                       body.filename)

    end_qr_data_list = [el for el in param.qr_data_list if el]
    rcmpsd.end_qr_list = end_qr_data_list
    logger.debug(f'QR-коды {end_qr_data_list}')

    # подготовка отчета
    try:
        documents = []
        for i in range(len(end_qr_data_list)):
            document = create_documents(i, rcmpsd.end_qr_list[i],
                                        rcmpsd.end_pages[i][0],
                                        rcmpsd.end_pages[i][1],
                                        rcmpsd.files_uid[i],
                                        rcmpsd.end_names_list[i])
            documents.append(document)
        finished['data'] = {"totally_pages": param.totally_pages,
                            "documents": documents}

    except Exception as err:
        finished['error'] = str(err)
        logger.exception(err)

    logger.debug(f'Отчет {finished["data"]}')

    return finished['data'], finished['error']
