from flask import Flask
from models import RequestBodyModel
from services import get_messages
from validate_request.core import validate
from validate_request.models import ResponseModel


app = Flask(__name__)  # создаем приложение и сервер


@app.route('/crm_chats', methods=['POST'])
@validate()
def report_creation(body: RequestBodyModel):
    """ Функция собирает историю всех переписок с одним клиентом """

    result, errors = get_messages(body)

    if not result:
        return ResponseModel(data=result, error=errors), 501

    return ResponseModel(data=result, error=errors), 201


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
