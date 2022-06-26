import requests
from flask import Flask, request
import json
from PIL import Image, ImageSequence
import os
import shutil
import pathlib

app = Flask(__name__)  # создаем приложение и сервер

@app.route('/tiff_to_pdf', methods=['POST'])  # разрешаем принятие POST и GET
def tiff_to_pdf():
    """ Функция принимает на вход json вида {filename:"some_name",url: "long-long-url"},
        где url - это ссылка на скачивание изображений
        Скачивает, конвертирует в pdf (одно- или многостраничный), загружает на
        сервер ('http://spb.proactor.pro:9000/shared/{filename}.pdf')
        Возвращает отчет вида:
        {data:
            {filename:"{filename}.pdf",
            url:"http://spb.proactor.pro:9000/shared/{filename}.pdf"
        }
    """
    finished = {}
    finished['data'] = None
    finished['error'] = None

    try:
        # принимаем и проверяем входящие параметры запроса
        try:
            request_data = request.get_json()
        except ValueError:
            return {"error": "Пустой входящий запрос"}

        # получаем имя и файла и путь к нему
        try:
            file_name = request_data["filename"]
            file_url = request_data["url"]

            # удаляем формат файла из названия, если есть
            img_fmts = ["tiff", "jpeg", "bmp", "jpg", "png"]
            file_suffix = file_name.split('.')[-1]
           
            if file_suffix in img_fmts:
                file_name = file_name.replace(f".{file_suffix}", "")
            
        except KeyError:
            return {"error": "Некорректные ключи запроса"}

        # --------------- ссылка сформирована
        try:
            tiff_file_raw_rgba = Image.open(requests.get(file_url, stream=True).raw)

            i = 1
            image_list = []

            if not os.path.exists('temp'):
                os.mkdir('temp')
            
            png_path = pathlib.Path('temp', 'part.png')
            pdf_path = pathlib.Path('temp', 'my_pdf.pdf')

            for fr in ImageSequence.Iterator(tiff_file_raw_rgba):
                fr.save(png_path)
                image = Image.open(png_path)
                im = image.convert('RGB')
                image_list.append(im)
                i += 1
            
            if len(image_list) == 1:
                zero_list = []
                image_list.save(pdf_path, save_all=True, append_images=zero_list)
            else:
                image_list_0 = image_list[0]
                image_list_1 = image_list[1:]
                image_list_0.save(pdf_path, save_all=True, append_images=image_list_1)

        except ValueError:
            return {"error": "В ответ на запрос не пришло изображение"}
        
        try:
            # формирование запроса загрузки на сервер
            url_end = f'http://spb.proactor.pro:9000/shared/{file_name}.pdf'
            headers = {"Content-Type": "application/pdf"}
            
            with open(pdf_path, 'rb') as f:
                data_pdf = f         
                # отправка файла на сервер
                getting_file = requests.put(url_end, headers=headers, data=data_pdf)

            # отчет о работе
            finished['data'] = {"filename": f'{file_name}.pdf',
                                "url": url_end
                                }
        except ValueError:
            return {"error": "Файл не отправлен"}

        # shutil.rmtree('temp')

        return json.dumps(finished, ensure_ascii=False)

    except Exception as e:

        finished['error'] = str(e)
        return json.dumps(finished, ensure_ascii=False)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)

