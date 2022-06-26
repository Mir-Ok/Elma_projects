from flask import Flask
import json
from utils import get_json_response, det_img_url, get_parameters, \
    split_rename_get_files_report
from service import sort_list_names, split_pdf_to_png, split_img_to_png
from settings import SUFFIX_LIST
import tempfile

app = Flask(__name__)  # создаем приложение и сервер


@app.route('/split_to_files_byQR',
           methods=['POST'])  # разрешаем принятие POST и GET
def split_to_files_byQR():
    """ Функция принимает на вход json вида
    { "s3uid":"", "filename":"sample_stream.tiff", "regexp":"SAP-" },
        проверить тип файла.
        Допустимыми являются: jpg, jpeg, png, bmp,tiff, tif, pdf
        если тип не является допустимым, возвращать
        {data:null, error:"file has extension ${фактическое расширение}"}
    """

    finished = {'data': None, 'error': None}

    try:
        try:
            # принимаем входящие параметры
            file_name, file_suffix, file_s3uid, file_pattern = get_json_response()

            # проверяем
            if file_suffix not in SUFFIX_LIST:
                finished['error'] = f"file has extension .{file_suffix}"
                return json.dumps(finished, ensure_ascii=False)
            print(file_name, file_suffix)
        except ValueError:
            return {"error": "Неполный входящий запрос"}

        try:
            # получаем ссылку на объект ИМПОРТИРОВАННАЯ ФУНКЦИЯ
            img_url = det_img_url(file_s3uid)
            print(img_url)

        except KeyError:
            return {"error": "Некорректный идентификатор файла"}

        # для фрагментов
        temp_png_dir = tempfile.TemporaryDirectory(prefix="temp_png_dir_")

        # для конечных файлов
        temp_pdf_dir = tempfile.TemporaryDirectory(prefix="temp_pdf_dir_")

        # разделяем входящий документ на отдельные файлы
        try:
            if file_suffix == 'pdf':
                split_pdf_to_png(img_url, temp_png_dir.name)
            else:
                split_img_to_png(img_url, temp_png_dir.name)

        except ValueError:
            return {"error": "Не удалось разделить документ на страницы"}

        # создаем упорядоченный список фрагментов документа ИМПОРТИРУЕТСЯ
        sorted_png_list = sort_list_names(temp_png_dir.name)
        print(sorted_png_list)

        qr_data_list, qr_data_list_01, image_list, totally_pages =  \
            get_parameters(sorted_png_list, temp_png_dir.name, file_pattern)

        print('Cписок кодов        ', qr_data_list)
        print('Список кодов Boolean', qr_data_list_01)
        print('Cписок файлов       ', image_list)

        qr_list = [el for el in qr_data_list if el]
        print(qr_list)

        # ----------------------------
        # если все страницы БЕЗ кодов
        if sum(qr_data_list_01) == 0:

            documents = split_rename_get_files_report(image_list,
                                                      qr_data_list_01,
                                                      temp_pdf_dir.name,
                                                      file_name,qr_list)
            finished['data'] = {"totally_pages": totally_pages,
                                "documents": documents}

            return json.dumps(finished, ensure_ascii=False)

        # ----------------------------
        # если страницы С кодами
        else:
            # игнор страниц без QR-кода в начале
            i = 0
            while i < len(qr_data_list_01):
                if qr_data_list_01[0] == 0:
                    del (qr_data_list_01[0])
                    del (image_list[0])
                i += 1

            qr_list = qr_data_list
            # теперь список точно стартует с кода, разбиваем на части
            documents = split_rename_get_files_report(image_list,
                                                      qr_data_list_01,
                                                      temp_pdf_dir.name,
                                                      file_name,qr_list)
            finished['data'] = {"totally_pages": totally_pages,
                                "documents": documents}

            return json.dumps(finished, ensure_ascii=False)

    except Exception as e:

        finished['error'] = str(e)

        return json.dumps(finished, ensure_ascii=False)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
