# Конвертация изображений в pdf-формат

## Задача

Принять файлы img формата, конвертировать в PDF, отправить его в Elma,
вернуть ссылку на файл.

### endpoint

Упакованные в архив файлы отправляются на Elma

- [**POST**] ```api/v1/joinjpg``` отправить запрос на сервер.

### Тело запроса

Скрипт начинает работу с приема параметров из входящего POST-запроса, который
содержит в себе ???. При помощи библиотеки
Pydantic данные проходят валидацию. Формат json:

```json
{
  "data": [
    {
      "doc_uid": "7b3d522b-2b16-4efe-8c33-e9ed68dcf2a2",
      "pdfname": "OFFER_52_2022-02-26(2022-05-31_17:02).pdf",
      "pages": [
        {
          "number": 1,
          "name": "OFFER_52_2022-02-26_p1.jpg",
          "s3uid": "bff10b41-b302-4947-aedf-7957699eb435"
        }
      ],
      "link": "https://elma.gmcs.ru/s3elma365/69a71144-1192-4786-a8d2-d9cc6b0b4de0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=PZSF73JG72Ksd955JKU1HIA%2F20220531%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220531T140209Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3DOFFER_52_2022-02-26%25282022-05-31_17%3A02%2529.pdf&X-Amz-Signature=ce8072bdd9a25c3e239a6ab84d7f6a05f2d5382a836e22d5012c2e60d8778f8f"
    },
    ...
  ],
  "error": null
}
```

## Примеры ответа сервера

#### HTTP 201 - PDF успешно создан и загружен

```json
{
  "data": [
    {
      "doc_uid": "7b3d522b-2b16-4efe-8c33-e9ed68dcf2a2",
      "pdfname": "OFFER_52_2022-02-26(2022-05-31_17:02).pdf",
      "pages": [
        {
          "number": 1,
          "name": "OFFER_52_2022-02-26_p1.jpg",
          "s3uid": "bff10b41-b302-4947-aedf-7957699eb435"
        }
      ],
      "link": "https://elma.gmcs.ru/s3elma365/69a71144-1192-4786-a8d2-d9cc6b0b4de0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=PZSF73JG72Ksd955JKU1HIA%2F20220531%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220531T140209Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3DOFFER_52_2022-02-26%25282022-05-31_17%3A02%2529.pdf&X-Amz-Signature=ce8072bdd9a25c3e239a6ab84d7f6a05f2d5382a836e22d5012c2e60d8778f8f"
    },
    ...
  ],
  "error": null
}
```

#### HTTP 501 - ошибка создания файла

```json
{
  "data": null,
  "error": [
    {
      "file": "OFFER_52_2022-02-26.pdf",
      "errors": [
        "url: https://elma.gmcs.ru/pub/v1/disk/file/bff10b41-b302-4947-aedf-7957699eb435/get-link1, not found file"
      ]
    },
    {
      "file": "OFFER_30_2022-02-28.pdf",
      "errors": [
        "url: https://elma.gmcs.ru/pub/v1/disk/file/49a404f8-396d-4282-86ce-1f283b4ff1ab/get-link1, not found file"
      ]
    },
    {
      "file": "OFFER_502068_2022-02-24.pdf",
      "errors": [
        "url: https://elma.gmcs.ru/pub/v1/disk/file/7b5cddeb-07f1-4766-9dfa-67196b4cfbd6/get-link1, not found file",
        "url: https://elma.gmcs.ru/pub/v1/disk/file/bc9dadf9-fa08-4782-81dc-588e54166b5c/get-link1, not found file"
      ]
    }
  ]
}
```

#### HTTP 400 - некорректные параметры входящего запроса

```json
{
  "data": null,
  "error": [
    {
      "body_params": [
        {
          "loc": [
            "__root__",
            0,
            "pages",
            0,
            "name"
          ],
          "msg": "field required",
          "type": "value_error.missing"
        }
      ]
    }
  ]
}
```
