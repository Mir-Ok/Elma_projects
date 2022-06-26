from flask import Blueprint

from validate_request import validate
from validate_request.models import ResponseModel
from .models import RequestBodyModel
from .services import create_zip_end_send_to_elma

create_zip_api = Blueprint('create_zip_api', __name__)


@create_zip_api.route('/api/v1/create-zip', methods=['POST'])
@validate()
def files_to_zip(body: RequestBodyModel):
    """
    Собирает файлы из запроса в один ZIP архив
    и загружает в ELMA.

    request: [{
              "file": {
                "s3uid": "888d2404-f4c0-49f5-a5eb-9345a12215612",
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
            }...]

    response: {
                "data": {
                    "s3uid": "29cf72d4-2ae2-4f7d-8376-4b71e124fe37",
                    "name": "Выгрузка_2022-05-26_13:04.zip",
                    "link": "https://elma.gmcs.ru/s3elma365/d5c9faff-205e-48
                },
                "error": [
                    "url: https://elma.gmcs.ru/pub/v1/disk/file/888d2404-f4c0-49f5-a5eb-9345a12215612/get-link, not found file"
                ]
            }
    """

    result, error = create_zip_end_send_to_elma(body)
    if not result:
        return ResponseModel(error=error), 501

    return ResponseModel(data=result, error=error), 201
