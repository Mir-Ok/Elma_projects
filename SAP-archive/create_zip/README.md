# Объединение нескольких файлов в zip архив


## Задача

Собрать zip архив из файлов в запросе, отправить его в Elma, вернуть ссылку на файл.

### Тело запроса

Скрипт начинает работу с приема параметров из входящего POST-запроса, который
содержит в себе имена файлов, их идентификаторы на сайте. При помощи библиотеки
Pydantic данные проходят валидацию. Формат json:

```json
[
  {
    "file": {
      "s3uid": "888d2404-f4c0-49f5-a5eb-9345a1221561",
      "__name": "resp2.json"
    },
    "counteragent": {
      "__id": "9d92b623-e572-4b80-a3cb-9e6f8c58650a",
      "inn": "7802860613",
      "shortname": "\"НЕВАРЕСУРС\", ООО"
    },
    "type": {
      "name": "Акт выполненных работ",
      "__index": 4
    },
    "doc_date": "2022-05-25T00:00:00.000Z",
    "doc_number": null,
    "doc_amount": 700
  },
  ...
]
```

### endpoint

Упакованные в архив файлы отправляются на Elma

- [**POST**] ```api/v1/create-zip``` отправить запрос на сервер.

## Примеры ответа сервера

#### HTTP 201 - архив успешно загружен

```json
{
  "data": {
    "s3uid": "69446af3-8691-4388-9ecd-b254954507d5",
    "name": "Выгрузка_2022-05-31_17:02.zip",
    "link": "https://elma.gmcs.ru/s3elma365/688bde20-eb07-42eb-8b7c-12e3b14f628e?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=PZSF73JG72Ksd955JKU1HIA%2F20220531%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220531T140203Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3D%25D0%2592%25D1%258B%25D0%25B3%25D1%2580%25D1%2583%25D0%25B7%25D0%25BA%25D0%25B0_2022-05-31_17%3A02.zip&X-Amz-Signature=03f38966bd3907a31cdffa0c76818259165437c2a835a770e7d4d22f8a101f7d"
  },
  "error": null
}
```

#### HTTP 501 - ошибка создания файла

```json
{
  "data": null,
  "error": [
    "no upload files",
    "url: https://elma.gmcs.ru/pub/v1/disk/file/888d2404-f4c0-49f5-a5eb-9345a1221561/get-link1, not found file",
    "url: https://elma.gmcs.ru/pub/v1/disk/file/6cdbde8b-5c9e-4580-9169-5473ffb4e79e/get-link1, not found file"
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
            "root",
            0,
            "type",
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
