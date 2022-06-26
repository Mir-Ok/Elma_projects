import datetime
from typing import Any
import psycopg2 as psycopg2
from psycopg2 import Error
from flask import request
from models import RequestBodyModel, ParseModel
from settings import SECRET, logger, SECRET2
from pymongo import MongoClient


def validation(request_data) -> RequestBodyModel:
    """ Парсит входящий запрос и валидирует его """

    parse_data = RequestBodyModel(**request_data)
    return parse_data


def secret_parse(secret: str) -> ParseModel:
    """ Парсит переменную окружения """
    logger.debug(f'secret {secret}, {type(secret)}')

    bd_parse = ParseModel()

    try:
        bd_parse.user = secret.split('://')[1].split(':')[0]
        bd_parse.password = secret.split(':')[2].split('@')[0]
        bd_parse.host1 = secret.split('@')[1].split(':')[0]
        bd_parse.port1 = secret.split(':')[3].split('/')[0]
        bd_parse.finish = secret.split('/')[3]

        return bd_parse

    except Exception as e:
        logger.debug(f"Mongo connect failed: {e}")
        return bd_parse


def secret_parse_replicated(secret: str) -> ParseModel:
    """ Парсит переменную окружения """
    logger.debug(f'secret {secret}, {type(secret)}')

    bd_parse = ParseModel()

    try:
        bd_parse.user = secret.split('://')[1].split(':')[0]
        logger.debug(f'bd_parse.user {bd_parse.user}')
        bd_parse.password = secret.split(':')[2].split('@')[0]
        logger.debug(f'bd_parse.password {bd_parse.password}')
        hosts_ports = secret.split('@')[1].split('/')[0]
        logger.debug(f'hosts_ports {hosts_ports}')
        bd_parse.host1, bd_parse.port1 = hosts_ports.split(',')[0].split(':')
        logger.debug(f'bd_parse.host1 {bd_parse.host1}')
        logger.debug(f'bd_parse.port1 {bd_parse.port1}')
        bd_parse.host2, bd_parse.port2 = hosts_ports.split(',')[1].split(':')
        logger.debug(f'bd_parse.host2 {bd_parse.host2}')
        logger.debug(f'bd_parse.port2 {bd_parse.port2}')
        bd_parse.finish = secret.split('/')[3]
        logger.debug(f'bd_parse.finish {bd_parse.finish}')

        return bd_parse

    except Exception as e:
        logger.debug(f"Mongo connect failed: {e}")
        return bd_parse


def secret_parse_sql(secret):
    try:
        user = secret.split('://')[1].split(':')[0]
        password = secret.split(':')[2].split('@')[0]
        dbname = secret.split('/')[3].split('?')[0]
        host = secret.split('@')[1].split(':')[0]
        port = secret.split(':')[3].split('/')[0]
        print('{} {} {} {} {}'.format(user, password, dbname, host, port))
        return user, password, dbname, host, port
    except Exception as e:
        return f'Postgres connect failed: {e}'


def connect_db(SECRET) -> tuple:
    data, error = None, None

    try:
        if 'replicaSet' not in SECRET:
            logger.debug(f"Ветка без реплик")
            prsd = secret_parse(SECRET)
            conn = MongoClient(
                f"mongodb://{prsd.user}:{prsd.password}@{prsd.host1}:{prsd.port1}/{prsd.finish}")
        else:
            prsd = secret_parse_replicated(SECRET)
            logger.debug(f"Ветка C репликами")
            conn = MongoClient(
                f"mongodb://{prsd.user}:{prsd.password}@{prsd.host1}:{prsd.port1},{prsd.host2}:{prsd.port2}/{prsd.finish}")

        db = conn["elma365"]
        db.list_collection_names()
        data = conn
        logger.debug("[+] Database connected!")
        return data, error

    except Exception as err:
        logger.debug("[+] Database NOT connected!")
        error = str(err)
        return data, error


def get_sessions_id(sessions: Any, client_id: str) -> list:
    """ Получает список всех сессий в хронологическом порядке """

    sessions_id = [item['id'] for item in
                   sessions.find({"clientId": client_id})]
    return sessions_id


def create_chat(messages: Any, users_sessions_id: list) -> list:
    """ Собирает переписку пользователя и оператора """
    all_sessions_messages = []

    # переберем все сессии по id
    for sid in users_sessions_id:
        # подготовим список для диалога клиента и оператора в одной сессии
        sessions_messages = []

        for item in messages.find({"sessionId": sid}):
            sessions_messages.append({item['type']: (item['body'], item['createdAt'].strftime("%d-%m-%Y %H:%M:%S"))})
        all_sessions_messages.append(sessions_messages)

    return all_sessions_messages


def create_report(all_sessions_messages: list) -> dict:
    """ Создает итоговый отчет """

    report = {f'Обращение {i + 1}': messages
              for i, messages in enumerate(all_sessions_messages)}
    logger.debug(report)
    return report


def my_converter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()


def pg_select() -> tuple:
    """Запрос select к БД."""

    data, error = None, None

    request_data = request.get_json()
    logger.debug(f'request_data {request_data}')

    query = 'SELECT * FROM head."probnyi:kontakty_klientov_probnyi";'
    logger.debug(query)

    pg_user, pg_password, pg_db, pg_host, pg_port = secret_parse_sql(SECRET2)
    logger.debug(f'{pg_user, pg_password, pg_db, pg_host, pg_port}')

    try:
        conn = psycopg2.connect(user=pg_user, password=pg_password,
                                dbname=pg_db, host=pg_host, port=pg_port)
        logger.debug(f'Информация о PostgreSQL {conn.get_dsn_parameters()}')
        cursor = conn.cursor()
        cursor.execute(query)
        res = cursor.fetchall()

        data = res
        logger.debug(f'База клиентов {res}')

        cursor.close()
        conn.close()
        logger.debug(f"Соединение с PostgreSQL закрыто")

        return data, error

    except (Exception, Error) as err:
        logger.debug(err)
        error = err
        return data, error


def get_client_id(clients: Any, app_uid: str) -> tuple:
    """ Находит идентификатор клиента в МОНГО по идентификатору POSTGRES """
    data, error = None, None

    try:
        clnt_id = [item for item in clients.find({"app.id": app_uid}, {"id":1, "_id":0})]
        data = clnt_id[0]["id"]
        return data, error

    except Exception as err:
        logger.debug(f"Аккаунт на Elma и MONGO не связаны! {err}")
        error = "Аккаунт на Elma и MONGO не связаны!"
        return data, str(error)


def get_messages(inner_data: RequestBodyModel) -> tuple:

    data, error = None, None

    # устанавливаем соединение с МОНГО БД
    connect, err = connect_db(SECRET)
    if err:
        error = err
        return data, error

    # вытаскиваем нужные коллекции
    db_mongo = connect["elma365"]
    sessions = db_mongo["head.messengers.sessions"]
    messages = db_mongo["head.messengers.messages"]
    clients = db_mongo["head.messengers.clients"]

    # идентификатор клиента POSTGRES
    logger.debug(f"Идентификатор в POSTGRES {inner_data.postgres_id}")

    # по идентификатору приложения находим идентификатор клиента MONGO
    inner_data.mongo_uid, err = get_client_id(clients, inner_data.postgres_id)
    logger.debug(f"Идентификатор в МОНГО {inner_data.mongo_uid}")
    if err:
        error = err
        return data, error

    # соберем все сессии пользователя в хронологическом порядке
    users_sessions_id = get_sessions_id(sessions, inner_data.mongo_uid)
    logger.debug(f"Все сессии пользователя {users_sessions_id}")

    # соберем диалоги всех сессий
    all_sessions_messages = create_chat(messages, users_sessions_id)
    logger.debug(f"Диалоги всех сессий {all_sessions_messages}")

    # создадим отчет
    data = create_report(all_sessions_messages)

    return data, error
