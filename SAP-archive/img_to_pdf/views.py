from flask import Blueprint

from validate_request.core import validate
from validate_request.models import ResponseModel
from .models import RequestBodyModel
from .services import create_pdf_from_request

img_to_pdf_api = Blueprint('img_to_pdf_api', __name__)


@img_to_pdf_api.route('/api/v1/joinjpg', methods=['POST'])
@validate()
def convert_to_pdf(body: RequestBodyModel):
    """
    Преобразовать изображения из запроса в один PDF файл
    и загрузить его в Elma.

    request: [
              {
                "doc_uid": "222aeab0-76d5-4b97-9c9f-1ce8ea3085e2",
                "pdfname": "OFFER_502068_2022-02-24.pdf",
                "pages": [
                  {
                    "number": 1,
                    "name": "OFFER_502068_2022-02-24_p1.jpg",
                    "s3uid": "7b5cddeb-07f1-4766-9dfa-67196b4cfbd6"
                  },
                  {
                    "number": 2,
                    "name": "OFFER_502068_2022-02-24_p2.jpg",
                    "s3uid": "bc9dadf9-fa08-4782-81dc-588e54166b5c"
                  }
                ]
              },
              ...
            ]

    response: {
              "data": [
                {
                  "doc_uid": "222aeab0-76d5-4b97-9c9f-1ce8ea3085e2",
                  "pdfname": "OFFER_502068_2022-02-24(2022-05-21_06:41).pdf",
                  "pages": [
                    {
                      "number": 1,
                      "name": "OFFER_502068_2022-02-24_p1.jpg",
                      "s3uid": "7b5cddeb-07f1-4766-9dfa-67196b4cfbd6"
                    },
                    {
                      "number": 2,
                      "name": "OFFER_502068_2022-02-24_p2.jpg",
                      "s3uid": "bc9dadf9-fa08-4782-81dc-588e54166b5c"
                    }
                  ],
                  "link": "https://elma.gmcs.ru/s3elma365/65265fee-b...."
                },
                ...
              ],
              "error": null
            }
    """

    result, errors = create_pdf_from_request(body)  # noqa:

    if not result:
        return ResponseModel(data=result, error=errors), 501

    return ResponseModel(data=result, error=errors), 201
