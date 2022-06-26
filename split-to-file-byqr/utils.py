from settings import ELMA_STAND, ELMA_TOKEN
import requests
from PIL import Image
import cv2
import os
from uuid import uuid4
from pathlib import Path
from service import create_documents, sort_list_names, convert_to_pdf
import random
import string
from flask import request


def det_img_url(file_s3uid):
    """ Получает ссылку на скачивание файла в ответ на запрос"""

    file_url = f'{ELMA_STAND}/pub/v1/disk/file/{file_s3uid}/get-link'
    headers = {"X-Token": f'{ELMA_TOKEN}'}

    try:
        get_file = requests.post(file_url, headers=headers, stream=True)
        img_url = get_file.json()['Link']

        return img_url

    except ValueError:
        return {"error": "Ответ сервера на запрос не получен"}


def send_to_elma_get_uid(full_path):
    """ Размещает файл на ELMA и возвращает его s3uid"""

    file_size = os.path.getsize(full_path)
    data_pdf = open(full_path, 'rb')
    files = {'file': data_pdf}
    header = {"X-Token": ELMA_TOKEN,
              "Content-Range": f"bytes 0-{file_size}/{file_size}"
              }
    uid_file = str(uuid4())
    directory_id = 'b8e5e30f-1e31-4a68-a11e-0e95b9ef8549'
    query = f'/pub/v1/disk/directory/{directory_id}/upload?hash='
    url = f"{ELMA_STAND}{query}{uid_file}"

    try:
        response = requests.post(url, headers=header, files=files)
        result = response.json()
        file_uid = result["file"]["__id"]

    except ValueError:
        return {"error": "Файл не отправлен"}

    return file_uid


def get_parameters(path_to_files, tmp_png_path, file_pattern):
    """ Создает:
        qr_data_list - исходный список кодов
        image_list - список страниц
        qr_data_list_01 - дубликат списка файлов в булевых значениях
        totally_pages - общее количество страниц """

    qr_data_list = []  # исходный список кодов
    image_list = []  # список изображений
    print(path_to_files)

    for path in path_to_files:

        temp_path = f'{Path(tmp_png_path, path)}'
        img = cv2.imread(temp_path)  # читаю  QRCODE
        # img = cv2.imread(Path(tmp_png_path, path))  # читаю  QRCODE

        # инициализируем детектор QRCode cv2
        detector = cv2.QRCodeDetector()

        # обнаружить и декодировать
        qr_data, bbox, straight_qrcode = detector.detectAndDecode(img)

        if file_pattern:
            if qr_data == '':
                qr_data_list.append(qr_data)
            elif qr_data != '' and 'SAP-' in qr_data:
                qr_data_list.append(qr_data)
            else:
                pass
        else:
            qr_data_list.append(qr_data)

        image = Image.open(temp_path)
        # image = Image.open(Path(tmp_png_path, path))
        im = image.convert('RGB')
        image_list.append(im)

        qr_data_list_01 = []  # исходный список кодов ДА/НЕТ
        for i in range(len(qr_data_list)):
            qr_data_list_01.append(1) if qr_data_list[
                i] else qr_data_list_01.append(0)

    totally_pages = len(image_list)  # общее количество страниц

    return qr_data_list, qr_data_list_01, image_list, totally_pages


def split_rename_get_files_report(image_list, qr_data_list_01,
                                  dir_name, file_name, qr_list):
    """ Функция разделяет файл на части по QR, именует, отправляет на сервер
        и готовит текстовый отчет """

    end_path_list = []  # финальный список путей
    pages = []  # список списков страниц (от, до) [[0,1], [1,4]

    slice_image_list = [image_list[0]]  # срез (первый лист с QR в начале)
    page_list = [0]  # счетчик количества листов

    for i in range(1, len(qr_data_list_01)):

        page_list.append(i)
        # если нет нового кода
        if qr_data_list_01[i] - qr_data_list_01[0] == -1:

            # присоединяем к текущему списку
            slice_image_list.append(image_list[i])

        # если есть
        else:
            # закрываем пополнение текущего
            end_path_list, pages = convert_to_pdf(dir_name, file_name,
                                                  slice_image_list, i,
                                                  end_path_list, page_list,
                                                  pages)
            # Начинаем новый
            slice_image_list.clear()
            page_list.clear()
            slice_image_list.append(image_list[i])
            page_list.append(i)

    end_path_list, pages = convert_to_pdf(dir_name, file_name,
                                          slice_image_list, i+1, end_path_list,
                                          page_list, pages)
    # сортировка списка имен файлов
    end_name_list = sort_list_names(dir_name)
    print(end_name_list)

    # переименование файлов
    for i in range(len(end_name_list)):
        now = random.sample(string.ascii_letters, 3)
        now_str = "".join(now)
        p = Path(dir_name, f'{end_name_list[i]}')
        p.rename(Path(dir_name, f'{file_name}_{now_str}_({i}).pdf'))

    # сортировка переименованных файлов
    rename_end_name_list = sort_list_names(dir_name)

    # отправка на сервер, получение идентификатора
    uid_list = []
    for ful in rename_end_name_list:
        uid = send_to_elma_get_uid(Path(dir_name, ful))
        uid_list.append(uid)

    # подготовка отчета
    documents = []

    for i in range(len(uid_list)):
        document = create_documents(pages[i][0], pages[i][1], uid_list[i],
                                    rename_end_name_list[i], qr_list[i], i)
        documents.append(document)

    # подготовка отчета
    return documents


def get_json_response():
    """" Функция принимает json и разбирает его """
    request_data = request.get_json()

    file_name = request_data["filename"].split('.')[0]
    print(file_name)
    file_suffix = request_data["filename"].split('.')[-1]
    file_suffix.lower()
    print(file_suffix)

    if "regexp" in request_data:  # если есть QR - сохраняем
        if "SAP-" in request_data["regexp"]:
            file_pattern = request_data["regexp"]
    else:
        file_pattern = "SAP-"

    file_s3uid = request_data["s3uid"]  # получаем s3uid и скачиваем

    return file_name, file_suffix, file_s3uid, file_pattern


