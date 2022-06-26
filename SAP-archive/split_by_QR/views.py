from flask import Blueprint
from validate_request.core import validate
from validate_request.models import ResponseModel
from .models import RequestBodyModel
from .services import split_to_files_by_qr

split_to_files_by_qr_api = Blueprint('split_to_files_by_qr_api', __name__)


@split_to_files_by_qr_api.route('/api/v1/split_by_qr', methods=['POST'])
@validate()
def split_by_qr(body: RequestBodyModel):
    """ Функция принимает на вход словарь вида

       request = {
           "s3uid": "050c9bbd-d8bf-413a-b7ef-7a184190ddf9",
           "filename": "stream_sample.tiff",
           "regexp": "SAP-"
           }

       Проверяет соответствие формата, разбирает документ на страницы
       (если многостраничник), проверяет наличие QR-кода, разбивает на части,
       отправляет созданные срезы на сервер, возвращает отчет вида

       {"data": {"totally_pages": 15,
                 "documents": [{"sequence": 0, "qr_value": "SAP-1",
                                "pages": {"from": 0, "to": 6},
                                "s3uid": "e805d626-e3c8-42c2-a84b-538c49e9b1fe",
                                "filename": "2_штук_ovU_(0).pdf"},
                                ...
                                {"sequence": 0, "qr_value": "SAP-1",
                                "pages": {"from": 0, "to": 6},
                                "s3uid": "e805d626-e3c8-42c2-a84b-538c49e9b1fe",
                                "filename": "2_штук_ovU_(0).pdf"},
                 "error": null}
       """

    result, errors = split_to_files_by_qr(body)  # noqa

    if not result:
        return ResponseModel(data=result, error=errors), 501

    return ResponseModel(data=result, error=errors), 201
