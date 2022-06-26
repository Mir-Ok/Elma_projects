FROM python:3.8-slim-buster

ENV TZ="Europe/Moscow"
RUN date

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y poppler-utils

WORKDIR /code

COPY ./requirements.txt .

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD python main.py
