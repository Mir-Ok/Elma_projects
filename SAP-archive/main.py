from flask import Flask

from img_to_pdf.views import img_to_pdf_api
from create_zip.views import create_zip_api
from split_by_QR.views import split_to_files_by_qr_api

app = Flask(__name__)

app.register_blueprint(create_zip_api)
app.register_blueprint(img_to_pdf_api)
app.register_blueprint(split_to_files_by_qr_api)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
