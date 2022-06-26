import tempfile
from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image
import re
from pdf2image import convert_from_path
from models import ElmaLinkModel
from settings import ELMA_STAND, ELMA_TOKEN, logger
import requests
from models import RequestBodyModel, VariablesModel, TempDirModel


def validation(request_data) -> RequestBodyModel:
    """ Парсит входящий запрос и валидирует его """

    parse_data = RequestBodyModel(**request_data)
    return parse_data


def get_file_link(uid: str) -> ElmaLinkModel:
    """Получить ссылку на файл из ELMA."""
    url = f"{ELMA_STAND}/pub/v1/disk/file/{uid}/get-link"
    header = {"X-TOKEN": ELMA_TOKEN}

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


def get_file_content_by_link(link: str) -> Optional[bytes]:
    """Получить документ по ссылке."""

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


def convert_pdf_to_png(pdf_file: Optional[bytes], pdf_path, png_path) -> tuple:
    """ Конвертирует входящий файл в набор PNG, выбирает первый """

    resp = {'data': None, 'error': None}

    temp_pdf_file = str(Path(pdf_path, 'temp.pdf'))
    logger.debug(f'Файл для сохранения pdf {temp_pdf_file}')

    with open(temp_pdf_file, 'wb') as f:
        f.write(pdf_file)

        # for Win
        # poppler_path = 'C:\Program Files\poppler-0.68.0_x86\\bin'
        # pages = convert_from_path(temp_pdf_file, dpi=200, fmt="png",
        #                           poppler_path=poppler_path,
        #                           output_folder=png_path,
        #                           output_file='png')
        # logger.debug(f"Список изображений: {pages}")
        # logger.debug(f"Первое изображение: {pages[0]}")

        # for Unix
        pages = convert_from_path(temp_pdf_file, dpi=200, fmt="png",
                          output_folder=png_path,
                          output_file='png')
        logger.debug(f"Список изображений: {pages}")
        logger.debug(f"Первое изображение: {pages[0]}")

        resp['data'] = pages[0]
        return resp['data'], resp['error']


def convert_pdf_to_jpg(page, jpg_path) -> tuple:
    """ Конвертирует входящий файл в JPEG """

    resp = {'data': None, 'error': None}
    logger.debug(f'Временная для jpg {jpg_path}')
    logger.debug(f'  ')

    try:
        img = Path(jpg_path, 'out.jpg')
        page.save(img, 'JPEG')
        resp['data'] = img
        return resp['data'], resp['error']

    except Exception as err:
        logger.error(err)
        resp['error'] = err
        return resp['data'], resp['error']


def recognize_jpg(img: Image) -> tuple:
    """ Распознает текст с изображения, возвращает последовательность строк """
    resp = {'data': None, 'error': None}

    try:
        # распознаем, помещаем в переменную
        data = pytesseract.image_to_string(Image.open(img), lang='rus')

        # строки собираем в список по разделителям
        data_split = re.split("\n|' '", data)

        # чистим от мусора
        clear_data_split = []
        for data in data_split:  # чистим мусор
            clear_data = re.sub("^\s+|\n|\(|\)|\r|\[|\||\\s+$", ' ', data)
            if clear_data:
                clear_data_split.append(clear_data)

        resp['data'] = clear_data_split
        return resp['data'], resp['error']

    except Exception as err:
        logger.error(err)
        resp['error'] = err
        return resp['data'], resp['error']


def extract_variables(finish: list) -> VariablesModel:
    """ Извлечение искомых значений из договора """

    inn_list = []
    vars = VariablesModel()

    for i in range(len(finish)):

        # Получение номера счета и даты
        if re.findall(r"[с|С][ч|Ч][е|Е|ё|Ё][т|Т] \D*№", finish[i]):
            logger.debug(f"Счет и дата: {finish[i]}")
            vars.date = finish[i].split(' от ')[1]
            logger.debug(f"Дата: {vars.date}")

            num = finish[i].split(' от ')[0]
            logger.debug(f"Счет ДО: {str(num)}")
            num2 = num.split('№')[-1]
            # for x, y in ("Счет на оплату № ", ""), ("Счет № ", ""), (
            # "СЧЕТ № ", ""):
            #     num = num.replace(x, y)
            vars.num = str(num2.replace(' ', ''))
            logger.debug(f"Счет: {vars.num}")

        # Получение полной суммы
        if re.findall(r"Всего к оплате|Итого с НДС", finish[i]):
            logger.debug(f"Всего к оплате: {finish[i]}")
            pattern = '[а-яА-Я: ]+'
            vars.price = re.sub(pattern, '', finish[i])
            logger.debug(f"Только сумма: {vars.price}")

        # Основание
        if re.findall(r"Основание: ", finish[i]):
            logger.debug(f"Основание: {finish[i]}")
            vars.foundation = finish[i].split(': ')[1]

        # все ИНН
        if re.findall(r"ИНН", finish[i]):
            inn_list.append(finish[i])

    # частные ИНН
    logger.debug(f"Все строки с ИНН: {inn_list}")
    if len(inn_list):
        inn = []
        for i in inn_list:
            logger.debug(f"Все ИНН: {i}")
            match = re.findall(r'\b[0-9]{10}\b', i)
            inn.append(match)

        logger.debug(f"Все ИНН: {inn}")
        vars.provider = inn[0][0]
        vars.buyer = inn[-1][0]

    return vars


def data_extraction(inner_data: RequestBodyModel) -> tuple:

    resp = {'data': None, 'error': None}

    # получаем модель со ссылкой на скачивание
    url = get_file_link(inner_data.uid)
    logger.debug(f"Ссылка на скачивание: {url.link}")

    # скачиваем файл
    file = get_file_content_by_link(url.link)
    if not file:
        resp['error'] = 'Файл не скачивается с сервера'
        return resp['data'], resp['error']
    logger.debug(f"Скачанный файл: {file[:50]}")

    # создаем временные папки
    t_pdf = tempfile.TemporaryDirectory(prefix="temp_pdf_")
    t_png = tempfile.TemporaryDirectory(prefix="temp_png_")
    t_jpg = tempfile.TemporaryDirectory(prefix="temp_jpg_")
    t_path = TempDirModel(pdf=t_pdf.name, png=t_png.name, jpg=t_jpg.name)

    # конвертируем файл в PNG
    img_png, err = convert_pdf_to_png(file, t_path.pdf, t_path.png)
    logger.debug(f"Полученный объект: {img_png}")

    # конвертируем в JPG
    img_jpg, err = convert_pdf_to_jpg(img_png, t_path.jpg)
    logger.debug(f"Изображение: {img_jpg}")

    # распознаем текст изображения и выводим список
    finish, err = recognize_jpg(img_jpg)
    logger.debug(f"Список строк: {finish}")

    # извлекаем значения
    extracted_vars = extract_variables(finish)
    logger.debug(f"Извлеченные данные: {extracted_vars}")

    # формируем отчет
    answer = {'Счет №: ': extracted_vars.num,
              'Дата: ': extracted_vars.date,
              'Сумма документа: ': extracted_vars.price,
              'Основание: ': extracted_vars.foundation,
              'Поставщик: ': extracted_vars.provider,
              'Покупатель: ': extracted_vars.buyer
              }

    resp['data'] = answer
    return resp['data'], resp['error']



