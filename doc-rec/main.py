from flask import Flask
from models import RequestBodyModel
from services import data_extraction
from validate_request.core import validate
from validate_request.models import ResponseModel


app = Flask(__name__)


@app.route('/pdf_recognition', methods=['POST'])
@validate()
def pdf_recognition(body: RequestBodyModel):
    """ Функция распознает PDF-файл и извлекает из него
        основную информацию о поставщике, покупателе, счете для оплаты """

    result, errors = data_extraction(body)

    if not result:
        return ResponseModel(data=result, error=errors), 501

    return ResponseModel(data=result, error=errors), 201


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
