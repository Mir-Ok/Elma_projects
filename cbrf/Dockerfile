FROM python:3.9

WORKDIR /temp

ADD . /temp/

RUN pip install -r requirements.txt

EXPOSE 3000
CMD ["python","/temp/main.py"]