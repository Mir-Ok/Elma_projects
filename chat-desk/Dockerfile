FROM python:3.8-slim-buster

ENV TZ="Europe/Moscow"
RUN date

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

WORKDIR /code

COPY ./requirements.txt .

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD python main.py
