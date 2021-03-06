# Сервисы для наполнения электронного архива. 

   Доступ к файлам в S3-хранилище elma365 по постоянной ссылке

## Технологии

    Python 3.8, Flask, requests, pydantic, opencv-python, Pillow, pdf2image, 
    PyPDF2, zipfile, imghdr, img2pdf

## Задачи

Может применяться для хранения ссылок на файл во внешних системах. 
Для ограничения доступа проверяется авторизация пользователя в Elma365

### Переменные окружения

Приложение может функционировать на разных стендах, это достигается за счет 
использования переменных окружения.

```dotenv
ELMA_TOKEN 
ELMA_STAND 
ELMA_ZIP_DIRECTORY 
ELMA_PDF_DIRECTORY 
ELMA_QR_DIRECTORY 

LOGURU_LEVEL=INFO
```

### Описание сущностей с пометками что, как и где хранится

Каждый метод имеет свой набор классов и функций, так же есть общие для всех
в корневой папке.

Директории:
- [X] create_zip - пакетная архивация файлов. 
   [Подробнее](/create_zip/README.md)
- [X] img_to_pdf - преобразование изображения в PDF. 
   [Подробнее](/img_to_pdf/README.md)
- [X] split_by_QR - разделение документа по QR-кодам. 
   [Подробнее](/split_by_QR/README.md)
