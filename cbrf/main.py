import requests
import xmltodict
from datetime import datetime
import re
from flask import Flask, jsonify, request
import json
from collections import OrderedDict

app = Flask(__name__)  # создаем приложение и сервер


@app.route('/get_cbrf_currencies', methods=['POST'])
def get_cbrf_currencies():
    # источник справочника валют
    n_url = 'https://cbr.ru/scripts/XML_val.asp?d=0'

    finished = {}

    try:
        my_xml = requests.post(n_url).text
        my_dict = xmltodict.parse(my_xml)

        # Извлечем кортеж с котировками
        ValCurs = my_dict['Valuta'].popitem(last=True)

        all = []  # создаем общий список для словарей
        qv_v = len(ValCurs[1])  # количество валют
        kv_p = len(ValCurs[1][0])  # количество параметров валюты

        for j in range(qv_v):

            new_dict = dict()  # создаем словарь
            # перебираем один элемент списка котировок, в нем 6 кортежей
            for i in range(kv_p):
                k, v = ValCurs[1][j].popitem(last=False)  # помещаем значения пары в переменную
                new_dict[k] = v  # помещаем в словарь как ключ и значение
            all.append(new_dict)

        # создаем пустой список для словарей
        val_list_all = []

        # перебираем все валюты
        for i in range(qv_v):
            # создаем пустой упорядоченный словарь
            val_list = OrderedDict()

            # заполняем его парами в нужном порядке
            val_list["ID"] = all[i]["ParentCode"]
            val_list["Name"] = all[i]["Name"]
            val_list["EngName"] = all[i]["EngName"]
            val_list["Nominal"] = all[i]["Nominal"]

            # добавляем в общий список словарей
            val_list_all.append(val_list)

        finished['data'] = val_list_all
        finished['error'] = None

    except Exception as e:

        finished['error'] = str(e)
        finished['data'] = None

    return json.dumps(finished, ensure_ascii=False)


@app.route('/get_cbrf_rates', methods=['POST'])
def get_cbrf_rates():
    URL = 'https://cbr.ru/scripts/XML_daily.asp?date_req='

    # получение текущей даты
    current_datetime = datetime.now()
    day_cur = str(current_datetime.day).zfill(2)
    month_cur = str(current_datetime.month).zfill(2)
    year_cur = current_datetime.year
    date_cur = f'{day_cur}/{month_cur}/{year_cur}'

    # принимаем переменные от входящего POST-запроса в словарь
    request_data = request.get_json()

    finished = {}
    finished['data'] = None
    finished['error'] = ''

    try:

        # если дата не пришла в запросе - подставляем текущую
        if 'date' not in request_data:
            date_in = date_cur
            n_url = f'{URL}{date_in}'

        else:  # если пришла - проверяем
            date_in = request_data['date']

            # проверяем на соответствие шаблону, возвращает None при несовпадении
            result = re.match(r'\d{2}/\d{2}/\d{4}', date_in)

            if date_in == date_cur:  # если дата текущая - оставляем
                n_url = f'{URL}{date_in}'
            elif date_in == "":  # если дата пустая - вставляем текущую
                n_url = f'{URL}{date_cur}'
            elif date_in != date_cur and result != None:  # если в дате другое - проверяем формат на корректность
                n_url = f'{URL}{date_in}'
            else:  # если в дате не пусто, не текущая дата, не другая дата - ошибка
                raise ValueError('Введите дату в формате dd/mm/yyyy, пожалуйста')

            # делаем из полученной текстовой даты объект datetime
            date_in_list = (date_in.split('/'))
            date_in_datetime = datetime(int(date_in_list[2]), int(date_in_list[1]), int(date_in_list[0]))
            date_cur_int = datetime(year_cur, int(month_cur), int(day_cur))

            # проверяем, что дата в настоящем или из прошлого
            if date_cur_int < date_in_datetime:
                raise ValueError('Вы ввели дату из будущего, курс неизвестен')

    except Exception as e:

        finished['data'] = None
        finished['error'] = str(e)

        return json.dumps(finished, ensure_ascii=False)

    # -------------
    # ссылка готова
    # -------------

    # проверяем корректность исходящего запроса
    try:

        my_xml = requests.post(n_url).text
        my_dict = xmltodict.parse(my_xml)

        # Извлечем кортеж с котировками
        ValCurs = my_dict['ValCurs'].popitem(last=True)

        all = []  # создаем общий список для словарей
        qv_v = len(ValCurs[1])  # количество валют
        kv_p = len(ValCurs[1][0])  # количество параметров валюты

        for j in range(qv_v):

            new_dict = dict()  # создаем словарь
            # перебираем один элемент списка котировок, в нем 6 кортежей
            for i in range(kv_p):
                k, v = ValCurs[1][j].popitem(last=False)  # помещаем значения пары в переменную
                new_dict[k] = v  # помещаем в словарь как ключ и значение

            # меняем ключ и восстанавливаем порядок
            new_dict['ID'] = new_dict.pop('@ID')
            new_dict['NumCode'] = new_dict.pop('NumCode')
            new_dict['CharCode'] = new_dict.pop('CharCode')
            new_dict['Nominal'] = int(str(new_dict.pop('Nominal')))
            new_dict['Name'] = new_dict.pop('Name')
            new_dict['Value'] = float(str(new_dict.pop('Value')).replace(',', '.'))

            # собираем словари в общий список
            all.append(new_dict)

        # ------ проверка кода валюты

        # собираем список ключей всех валют
        id_list = []
        for i in range(qv_v):
            id_list.append(all[i]['ID'])

        # если ключ даты существует
        if 'ID' in request_data:
            id = request_data['ID']

            # если ID в списке, выборочно
            if id in id_list:
                val_list_all = []
                for i in range(qv_v):
                    if all[i]['ID'] == id:
                        val_list = OrderedDict()
                        val_list["ID"] = all[i]["ID"]
                        val_list["NumCode"] = all[i]["NumCode"]
                        val_list["CharCode"] = all[i]["CharCode"]
                        val_list["Nominal"] = all[i]["Nominal"]
                        val_list["Name"] = all[i]["Name"]
                        val_list["Value"] = all[i]["Value"]

                        val_list_all.append(val_list)

                finished['data'] = val_list_all
                finished['error'] = None

            else:  # если ID НЕ в списке - ошибка
                finished['data'] = None
                raise ValueError('Вы ввели некорректный ключ')
        else:
            finished['data'] = all
            finished['error'] = None

    except Exception as e:
        finished['data'] = None
        finished['error'] = str(e)

    return json.dumps(finished, ensure_ascii=False)


# запускаем сервер, в браузере открываем http://127.0.0.1:5000
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
